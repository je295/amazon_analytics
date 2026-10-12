#从ods读取原始数据，清洗数据（金额，日期，状态，数量），换算多种货币，删除异常订单，写入dwd层
import re
import pandas as pd
from sqlalchemy import create_engine,text
from urllib.parse import quote_plus

pwd = quote_plus('123456')
engine = create_engine(f'mysql+pymysql://root:123456@localhost:3306/amazon_analytics?charset=utf8')

# ============ 第二步：定义汇率表 ============
# 把 3 种货币统一换算成美元
FX_RATES = {
    'USD': 1.0,    # 美元
    'GBP': 1.27,   # 英镑 → 美元
    'EUR': 1.08,   # 欧元 → 美元
}

# ============ 第三步：定义清洗函数 ============
def clean_price(value, currency='USD'):
    """
    清洗金额
    输入：$29.99 / 29.99 USD / 29,99 / " 29.99 " / 29.99
    输出：29.99（DECIMAL）
    """
    if pd.isna(value) or value == '': #是空值或者是空字符串‘’，返回none
        return None
    s = str(value).strip() #转为字符串，并去掉前后空格
    # 去掉货币符号
    s = re.sub(r'[\$£€]', '', s)
    # 去掉币种代码（USD/GBP/EUR）
    s = re.sub(r'(USD|GBP|EUR)', '', s)
    # 欧洲格式：1.234,56 → 1234.56
    if ',' in s and '.' in s:   #,是小数点 .是千位分隔符 同时有`.`和`,`：先把`.`全部删掉，再把逗号换成小数点
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.') #只有逗号：直接逗号替换小数点
    s = s.strip() #去除前后多余空格
    try:
        return round(float(s), 2) #清洗后的字符串转成小数
    except ValueError:
        return None  #s是每一次都覆盖的值，每一次的值都是新值，是string 用s缩写


def clean_date(value):
    """
    清洗日期
    输入：2025-03-15T14:22:15+00:00 / 03/15/2025 14:22 / 15-Mar-2025
    输出：pandas Timestamp
    """
    if pd.isna(value):
        return None
    s = str(value).strip()
    formats = [ #列表
        '%Y-%m-%dT%H:%M:%S+00:00', # 例：2025-10-01T16:30:00+00:00 带时区ISO格式
        '%m/%d/%Y %H:%M', # 例：10/05/2025 14:20 月/日/年 时分（美式）
        '%d-%b-%Y', # 例：05-Oct-2025 日-月份英文缩写-年（亚马逊常用）
        '%Y-%m-%d', # 例：2025-10-05 标准年月日
    ]
    for fmt in formats:
        try:
            return pd.to_datetime(s, format=fmt)
        except ValueError:
            continue
    # 全部失败就强制转换
    return pd.to_datetime(s, errors='coerce') #识别不了，返回NaT


def clean_status(value):
    """
    清洗订单状态
    输入：Shipped / shiped / SHIPPED / Shiped
    输出：Shipped（统一标准）
    """
    if pd.isna(value):
        return 'Unknown'
    s = str(value).strip().lower() #转成字符串，删除前后空格，全部转小写。
    mapping = { #映射字典，字典 = 一张对照表，`key: value`，就是「左边内容 → 映射成右边内容」
        'shipped': 'Shipped', 'shiped': 'Shipped', 'shippd': 'Shipped',
        'pending': 'Pending', 'pendig': 'Pending',
        'canceled': 'Canceled', 'cancelled': 'Canceled',
        'delivered': 'Delivered',
    }
    return mapping.get(s, 'Unknown') #字典.get(要查找的key, 找不到时的默认值)



def clean_quantity(value):
    """清洗数量：去掉空格，转 INT"""
    if pd.isna(value):
        return None
    s = str(value).strip()
    try:
        return int(s)
    except ValueError:
        return None


def marketplace_from_channel(sales_channel):
    """
    从销售网址提取站点代码
    Amazon.com    → US
    Amazon.co.uk  → UK
    Amazon.de     → DE
    """
    if not sales_channel:
        return 'Unknown'
    if 'co.uk' in sales_channel:
        return 'UK'
    if '.de' in sales_channel:
        return 'DE'
    if '.com' in sales_channel:
        return 'US'
    return 'Unknown'

# ============ 第四步：读取 ODS 数据 ============
print(">>> 读取 ODS 订单数据...")
with engine.connect() as conn:
    df = pd.read_sql(text("SELECT * FROM ods_amazon_orders"), conn)
print(f"    原始订单：{len(df)}")

# ============ 第五步：开始清洗 ============
print(">>> 清洗中...")

# 1. 去重（同一 amazon_order_id + sku 视为重复）
before = len(df)
df = df.drop_duplicates(subset=['amazon_order_id', 'sku'], keep='first')
print(f"    去重：{before} → {len(df)}（去除 {before - len(df)} 条）")

# 2. 清洗金额
df['item_price_clean'] = df.apply(
    lambda r: clean_price(r['item_price'], r['currency']), axis=1
) #拿这一行的 `item_price` 和 `currency`，传给 `clean_price` 清洗函数，返回清洗后的价格
#`df.apply(..., axis=1)` 代表按行遍历整张表，每一行都会把该行数据传给这个 lambda
#lambda 是匿名小函数 =def,语法：lambda 参数1，参数2 : 返回值
df['item_tax_clean'] = df.apply(
    lambda r: clean_price(r['item_tax'], r['currency']), axis=1
)
df['shipping_price_clean'] = df.apply(
    lambda r: clean_price(r['shipping_price'], r['currency']), axis=1
)

# 3. 清洗日期
df['purchase_date_clean'] = df['purchase_date'].apply(clean_date)
#遍历 `purchase_date` 这一列，每次只拿单元格里的一个值，直接丢进 `clean_date(value)`
#`df['列'].apply(函数名)`：只传这一列的单个值给函数
#`df.apply(lambda r: 函数(r['A'], r['B']), axis=1)`：按行，要同时拿多列的值
# 4. 清洗状态
df['order_status_clean'] = df['order_status'].apply(clean_status)

# 5. 清洗数量
df['quantity_clean'] = df['quantity'].apply(clean_quantity)

# 6. 清洗字段空格
df['sku'] = df['sku'].str.strip()
df['asin'] = df['asin'].str.strip()

# 7. 提取站点
df['marketplace'] = df['sales_channel'].apply(marketplace_from_channel)

# 8. 换算成美元
df['fx_rate'] = df['currency'].map(FX_RATES) #汇率
df['item_price_usd'] = (df['item_price_clean'] * df['fx_rate']).round(2)
#换算后成美元的商品单价 = 清洗完成的原始币种商品单价 * 汇率
df['total_amount_usd'] = (
    df['item_price_clean'] + df['item_tax_clean'] + df['shipping_price_clean']
) * df['fx_rate'] #总金额（美元）=（商品原价+税费+运费） * 汇率
df['total_amount_usd'] = df['total_amount_usd'].round(2)

# 9. 剔除异常（金额 < 0、数量 < 1、日期为空、站点未知）
before = len(df)
df = df[
    (df['item_price_clean'] > 0) &
    (df['quantity_clean'] >= 1) &
    (df['purchase_date_clean'].notna()) &
    (df['marketplace'] != 'Unknown')
]
print(f"    剔除异常：{before} → {len(df)}（去除 {before - len(df)} 条）")

# 10. 填充缺失
df['ship_city'] = df['ship_city'].fillna('Unknown').replace('', 'Unknown')
#.fillna--填充，NaN空值替换成字符串'Unknow',
#.replace('', 'Unknown') 把空字符串 `''`替换成 `'Unknown'`

# ============ 第六步：写入 DWD ============
print(">>> 写入 DWD...")
dwd = df[[
    'amazon_order_id', 'purchase_date_clean', 'order_status_clean',
    'fulfillment_channel', 'marketplace', 'sku', 'asin', 'product_name',
    'category',
    'quantity_clean', 'currency', 'item_price_clean', 'item_tax_clean',
    'shipping_price_clean', 'item_price_usd', 'total_amount_usd',
    'ship_city', 'ship_state', 'ship_country'
]].rename(columns={
    'purchase_date_clean': 'purchase_date',
    'order_status_clean': 'order_status',
    'quantity_clean': 'quantity',
    'item_price_clean': 'item_price',
    'item_tax_clean': 'item_tax',
    'shipping_price_clean': 'shipping_price',
})

dwd.to_sql('dwd_amazon_orders', engine, if_exists='append', index=False)
print(f"    写入 DWD：{len(dwd)} 行")

# ============ 完成 ============
print("\n>>> ETL 清洗完成！")
