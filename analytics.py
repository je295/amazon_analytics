#生成500个商品，生成50000条订单数据（包括脏数据），生成100条广告，500条库存数据
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker
from sqlalchemy import create_engine,text
from urllib.parse import quote_plus

pwd = quote_plus('123456')
engine = create_engine(f'mysql+pymysql://root:123456@localhost:3306/amazon_analytics?charset=utf8')
# ============ 跑之前先清空 ODS 表 ============
print(">>> 清空旧数据...")
with engine.connect() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;")) #关闭外键约束检查，临时关掉这个校验
    #表与表之间关联约束。默认情况下，如果你要清空主表，子表有外键引用，`TRUNCATE` 会直接报错。

    conn.execute(text("TRUNCATE TABLE ods_amazon_orders;"))   #TRUNCATE = 清空整张表，重置自增主键
    conn.execute(text("TRUNCATE TABLE ods_amazon_ads;"))
    conn.execute(text("TRUNCATE TABLE ods_amazon_inventory;"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;")) #重新打开外键约束检查，防止后续插入脏数据
    conn.commit()
print("    清空完成")

# 三种语言环境：美国英语、英国英语、德语
fake_en = Faker('en_US')
fake_uk = Faker('en_GB')
fake_de = Faker('de_DE')

# 固定随机种子：保证每次运行结果一样
random.seed(42)
Faker.seed(42)

# ============ 第二步：定义亚马逊真实商品池 ============
# 品类：商品名列表
CATEGORIES = {
    'Electronics': ['无线耳机', '蓝牙音箱', 'USB-C 数据线', '手机壳',
                    '充电宝', '摄像头', '键盘'],
    'Home & Kitchen': ['咖啡机', '搅拌机', '空气炸锅', '刀具套装',
                       '储物盒', '砧板'],
    'Sports': ['瑜伽垫', '哑铃', '弹力带', '水壶',
               '跑鞋', '背包'],
    'Beauty': ['精华液', '保湿霜', '防晒霜', '润唇膏',
               '护发油', '面膜'],
    'Toys': ['乐高积木', '手办', '拼图', '桌游',
             '遥控车', '娃娃'],
}

# 3 个站点的配置：货币、汇率、网址、税率
MARKETPLACES = {
    'US': {'currency': 'USD', 'price_rate': 1.0,  'to_usd_rate': 1.0,  'domain': 'Amazon.com',   'tax_rate': 0.08},
    'UK': {'currency': 'GBP', 'price_rate': 0.79, 'to_usd_rate': 1.27, 'domain': 'Amazon.co.uk', 'tax_rate': 0.20},
    'DE': {'currency': 'EUR', 'price_rate': 0.92, 'to_usd_rate': 1.08, 'domain': 'Amazon.de',    'tax_rate': 0.19},
}

# 订单状态的"真实拼错版本"（模拟人工录入错误）
STATUS_VARIANTS = {
    'Shipped': ['Shipped', 'shipped', 'SHIPPED', 'Shiped', 'Shippd'],
    'Pending': ['Pending', 'pending', 'PENDING', 'Pendig'],
    'Canceled': ['Canceled', 'Cancelled', 'canceled', 'CANCELED'],
    'Delivered': ['Delivered', 'delivered', 'DELIVERED'],
}

FULFILLMENT = ['Amazon', 'Merchant']  # FBA / FBM
SHIP_SERVICE = ['Standard', 'Expedited']  # 配送等级


# ============ 1. 生成商品池 ============
print(">>> 生成商品池...")

# ⭐ 新增：商品变体（真实亚马逊商品有颜色/尺寸变体）
VARIANTS = ['Red', 'Blue', 'Black', 'White', 'Green']

products = []
for category, names in CATEGORIES.items():
    for name in names:
        for variant in VARIANTS:   # ⭐ 加这层循环
            base_price = round(random.uniform(9.99, 199.99), 2) #跳出内循环，以便3站点价格一致
            for marketplace in MARKETPLACES:
                asin = 'B0' + ''.join(
                    random.choices('0123456789ABCDEFGHJKLMNPQRSTUVWXYZ', k=8)#从给定字符里面随机选8个
                )
                #生成asin（亚马逊商品编码），规则大多以B0开头，加8位字符（字符池里去掉了容易混淆的I，O）

                sku = f"SKU-{category[:3].upper()}-{variant[:2].upper()}-{random.randint(100, 999)}"
                #生成商家sku,商品类取前三个字母，转大写；变体名称取前两个字母，转大写；随机3位数字。例如：SKU-ELE-BL-452

                products.append({ #把这一条商品所有字段打包成字典，加到`products`商品列表里
                    'asin': asin,
                    'sku': sku,
                    'product_name': f"{name}-{variant}",   # ⭐ 商品名带变体
                    'category': category,
                    'marketplace': marketplace,
                    'base_price': base_price,
                })
print(f"    商品数：{len(products)}")

# ============ 第四步：定义脏数据生成函数 ============
def dirty_price(price, currency):
    """
    故意把金额搞脏
    返回：$29.99 / 29.99 USD / 29,99 / " 29.99 " / 29.99
    """
    style = random.random() #生成 0 ~ 1 之间随机小数，用来随机选一种脏数据格式
    symbol = {'USD': '$', 'GBP': '£', 'EUR': '€'}[currency] #字典映射：根据币种拿到对应的货币符号 USD → `$` GBP → `£`EUR → `€`
    if style < 0.3:
        return f"{symbol}{price}"              # $29.99
    elif style < 0.5: #（0.3-0.5之间）
        return f"{price} {currency}"            # 29.99 USD
    elif style < 0.6: #（0.5-0.6之间，小数点换逗号）
        return f"{price:.2f}".replace('.', ',') # 29,99（欧洲格式）
    elif style < 0.7:
        return f" {price} "                     # 前后带空格
    else: #（0.7-1之间）
        return str(price)                       # 正常


def dirty_date(dt):
    """
    故意把日期搞脏
    返回：2025-03-15T14:22:15+00:00 / 03/15/2025 14:22 / 15-Mar-2025
    """
    style = random.random() #生成 0 ~ 1 之间随机小数
    if style < 0.4:
        return dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')  # ISO 8601，2025-03-15T14:22:15+00:00 亚马逊标准时间格式
    elif style < 0.7:
        return dt.strftime('%m/%d/%Y %H:%M')  # 美式，03/15/2025 14:22
    else:
        return dt.strftime('%d-%b-%Y')  # 15-Mar-2025


def dirty_status(canonical):
    """故意把状态拼错"""
    variants = STATUS_VARIANTS.get(canonical, [canonical])
    return random.choice(variants)
#`.get(canonical, [canonical])`去字典里找 `canonical` 对应的变体列表；如果找不到这个 key，就返回 `[canonical]`

def dirty_quantity(qty):
    """数量偶尔带空格"""
    if random.random() < 0.15:
        return f" {qty} "
    return str(qty)
#ODS 原始层：原始来源是文本，有可能带空格、异常字符，所以存字符串（varchar）
# DWD 清洗层：清洗完成后，确定是合法数量，才转成 int

# ============ 第五步：生成订单数据 ============
print(">>> 开始生成订单数据...")
#限定订单生成时间范围：过去 1 年之内的订单
start_date = datetime.now() - timedelta(days=365) #`datetime.now()`：获取当前电脑本地时间
end_date = datetime.now()                         #`timedelta(days=365)`：时间间隔，365 天
                                                #`start_date` = 今天往前推 365 天（一年前的此刻），`end_date` = 当前时间

orders = [] #存全部订单数据，循环每次生成的数据都append进orders
N_ORDERS = 50000 #目标条数，一共要生成的数据
seen_orders = [] #记录已经出现的订单号，用来保证订单号不重复

for _ in range(N_ORDERS):  #循环 N_ORDERS（50000 次），逐条生成订单
    # ⭐ 3% 概率：复制一条之前生成的完整订单--生成重复订单
    if seen_orders and random.random() < 0.03: #seen_orders不为空且随机命中3%，
        orders.append(random.choice(seen_orders).copy()) #random.choice(seen_orders)随机挑seen_orders里面订单，
                                                        # 复制一份，放入orders.append，最终放入orders。
        continue

    # ========== 正常生成逻辑 ==========
    # 1. 挑商品
    product = random.choice(products)
    mkt = MARKETPLACES[product['marketplace']]

    # 2. 算本地价格
    local_price = round(
        product['base_price'] * mkt['price_rate'] * random.uniform(0.9, 1.1), 2
    ) #价格浮动 ±10%，模拟不同商品 / 变体定价波动，random.uniform随机系数

    # 3. 生成订单时间
    days_ago = int(random.expovariate(1 / 180)) #指数分布随机数，参数 `1/180`：均值 = 180 天
                                                #模拟订单时间 ——大部分订单是最近的，少量订单很早之前
                                                #`int(...)` 得到整数天数 `days_ago`，代表「多少天前下的单」
    order_dt = end_date - timedelta(
        days=min(days_ago, 365), #限制最大天数不能超过 365 天，往前推n天
        hours=random.randint(0, 23),#随机小时
        minutes=random.randint(0, 59) #随机分钟
    ) #这条订单的下单时间= 当前时间减去（n天+随机小时+随机分钟

    # 4. 生成订单状态
    canonical_status = random.choices(
        ['Shipped', 'Pending', 'Canceled', 'Delivered'],
        weights=[0.6, 0.1, 0.15, 0.15]             #带权重随机挑选
    )[0]
#`random.choice()` 单数 choice，一次选 1 个，直接返回单个值，不用加 [0]
#`random.choices()` 👉 复数 choices，支持权重、支持一次选出多条，永远返回列表，必须 [0]
#[0] 相当于把列表转换成字符串，['shipped]---'shipped'



    # 5. 生成收货地址
    if product['marketplace'] == 'US':
        city, state, country = fake_en.city(), fake_en.state_abbr(), 'US' #美国站点 有state字段，美国州缩写
    elif product['marketplace'] == 'UK':
        city, state, country = fake_uk.city(), '', 'GB'
    else:
        city, state, country = fake_de.city(), '', 'DE'

    # 6. 生成数量
    qty = random.randint(1, 5)

    #  7. 生成订单号
    # 亚马逊真实订单号就是三段数字，用短横线 `-` 分隔。 XXX-XXXXXXX-XXXXXXX（二三段都是七位数字）
    order_id = f"{random.randint(100, 999)}-{random.randint(1000000, 9999999)}-{random.randint(1000000, 9999999)}"

    # 8. 组装完整订单字典
    order_record = {
        'amazon_order_id': order_id,
        'purchase_date': dirty_date(order_dt),
        'order_status': dirty_status(canonical_status),
        'fulfillment_channel': random.choice(FULFILLMENT),
        'sales_channel': mkt['domain'],
        'sku': product['sku'],
        'asin': product['asin'],
        'product_name': product['product_name'],
        'category': product['category'],
        'quantity': dirty_quantity(qty),
        'currency': mkt['currency'],
        'item_price': dirty_price(local_price * qty, mkt['currency']),
        'item_tax': dirty_price(
            round(local_price * qty * mkt['tax_rate'], 2), mkt['currency']
        ), #税费=当地价格*数量*站点税率  传给 `dirty_price`，变成带符号 / 逗号 / 空格的脏字符串，存入 ODS 原始表
        'shipping_price': dirty_price(
            round(random.uniform(0, 9.99), 2), mkt['currency']
        ), #运费，随机0-9.99，保留2位小数，加上货币 包装成脏价格字符串
        'ship_city': city if random.random() > 0.05 else '', #5% 概率把城市改成空字符串`''`，制造脏数据
                                                            #后面 ETL 清洗：`fillna('Unknown').replace('', 'Unknown')` 专门处理这种空
        'ship_state': state,
        'ship_country': country,
        'buyer_email': f"{random.choice(['abc', 'xyz', 'user', 'buyer'])}{random.randint(100, 999)}@marketplace.amazon.com",
    }  #从`abc/xyz/user/buyer`随机挑，拼接 3 位随机数字

    # 9. 加入两个列表
    orders.append(order_record) #把order_record里面所有订单加到orders 列表
    seen_orders.append(order_record)

# ⭐ 打印验证
print(f"    生成订单数：{len(orders)}")
print(f"    唯一订单号数：{len(set(o['amazon_order_id'] for o in orders))}")
#o['amazon_order_id'] for o in orders，遍历 orders 里每一条订单`o`，取出它的亚马逊订单号`amazon_order_id`
#`set( ... )`把所有订单号放进集合 set。集合的特性：自动剔除重复值，只保留不重复的订单号。
print(f"    重复订单数：{len(orders) - len(set(o['amazon_order_id'] for o in orders))}")

#  4% 概率制造异常
for i in range(len(orders)):
    if random.random() < 0.04:
        anomaly_type = random.choice([
            'negative_price', 'zero_quantity',
            'empty_date', 'unknown_marketplace',
        ])
        if anomaly_type == 'negative_price':
            orders[i]['item_price'] = f"-{random.uniform(1, 100):.2f}"
        elif anomaly_type == 'zero_quantity':
            orders[i]['quantity'] = '0'
        elif anomaly_type == 'empty_date':
            orders[i]['purchase_date'] = ''
        elif anomaly_type == 'unknown_marketplace':
            orders[i]['sales_channel'] = 'UnknownChannel'
# 写入 MySQL
df_orders = pd.DataFrame(orders)
df_orders.to_sql('ods_amazon_orders', engine, if_exists='append', index=False)
print(f"    生成订单数：{len(df_orders)}")

# ============ 第六步：生成广告数据 ============
print(">>> 开始生成广告数据...")

# 先生成 100 个广告活动
campaigns = []
for i in range(100):
    marketplace = random.choice(list(MARKETPLACES.keys())) #从你站点字典（MARKETPLACES，US/UK/DE）随机选一个站点。
    campaigns.append({
        'campaign_id': f"C{random.randint(1000000, 9999999)}", #广告活动 ID，C 开头 + 7 位随机数字
        'campaign_name': f"SP-Auto-{random.choice(['耳机', '瑜伽垫', '搅拌机'])}-{marketplace}",
        #SP-Auto：亚马逊 Sponsored Products 自动广告，末尾带上站点
        'marketplace': marketplace,
    })

# 每个活动 × 365 天 = 36500 条广告记录
ads = []
for campaign in campaigns: #外层循环，遍历前面生成好的100 个广告活动 campaign
    for day in range(365): #每个广告活动，生成连续 365 天的广告日报数据
        date = start_date + timedelta(days=day) #从起始日期开始，逐日累加，生成广告报表日期
        impressions = random.randint(500, 50000)  # 曝光量，随机 500~50000 次
        clicks = int(impressions * random.uniform(0.005, 0.03)) # 点击量=曝光 × CTR，转整数
                                                                        #0.005~0.03 就是CTR（点击率）
        spend = round(clicks * random.uniform(0.3, 1.5), 2)  # 花费=点击量 * CPC
                                                                    #0.3~1.5 就是CPC（单次成本）
        sales = round(spend * random.uniform(2, 8), 2)  # 销售额
                                                                #2--ACOS=二分之一=50%，8=12.5%
                                                                #ACOS=spend / sales

        ads.append({
            'campaign_id': campaign['campaign_id'],
            'campaign_name': campaign['campaign_name'],
            'keyword': random.choice(['无线耳机', '瑜伽垫', '搅拌机',  #投放关键词
                                      '蓝牙音箱', '哑铃']),
            'match_type': random.choice(['broad', 'phrase', 'exact']),#关键词匹配方式，广泛匹配，短语匹配，精确匹配
            'impressions': str(impressions),
            'clicks': str(clicks),
            'spend': dirty_price(spend, 'USD'),
            'sales': dirty_price(sales, 'USD'),
            'report_date': dirty_date(date),
        })  #`impressions`、`clicks` 转 `str()`
#真实亚马逊导出的 CSV 里，数字经常是文本格式；放到 ODS 原始库存 varchar，后面 ETL 清洗的时候再转回 int
#spend、sales、report_date 调用脏数据函数，ODS 原始数据全部是脏的
df_ads = pd.DataFrame(ads)
df_ads.to_sql('ods_amazon_ads', engine, if_exists='append', index=False)
print(f"    生成广告记录：{len(df_ads)}")

# ============ 第七步：生成库存数据 ============
print(">>> 开始生成库存数据...")
inventory = []
for product in products:
    inventory.append({
        'sku': product['sku'],
        'asin': product['asin'],
        'product_name': product['product_name'],
        'available': str(random.randint(0, 500)), #可售库存，随机 0~500，转字符串`str()`
        'reserved': str(random.randint(0, 50)), #预留库存（客户下单但还没发货，占用库存），随机 0~50
        'unfulfillable': str(random.randint(0, 10)), #不可售库存（破损、瑕疵，无法发货），随机 0~10
        'snapshot_date': dirty_date(end_date), #库存快照日期，就是某一个时间点一次性拍下来的库存状态
    })

df_inv = pd.DataFrame(inventory)
df_inv.to_sql('ods_amazon_inventory', engine, if_exists='append', index=False)
print(f"    生成库存记录：{len(df_inv)}")

# ============ 完成 ============
print("\n>>> 脏数据生成完成！")
print(f"    订单：{len(df_orders)} 条")
print(f"    广告：{len(df_ads)} 条")
print(f"    库存：{len(df_inv)} 条")
print(f"    商品池：{len(products)} 个")