# 亚马逊多站点销售数据分析平台

> 基于 MySQL + Python + Power BI 的跨境电商数据分析项目

## 📋 项目简介

模拟跨境电商公司在 **Amazon US / UK / DE** 三个站点的销售数据，从数据建模、脏数据清洗、数仓分层到可视化分析全流程独立完成。

**核心目标**：清洗脏数据、搭建四层数仓、产出多站点销售分析看板。

## 🛠 技术栈

| 层 | 技术 |
|----|------|
| 存储 | MySQL 8.0（ODS / DWD / DWS / ADS 四层数仓）|
| 处理 | Python（pandas、SQLAlchemy、Faker）|
| 可视化 | Power BI Desktop |

## 📊 数据规模

- **订单明细**：50,000 条
- **广告记录**：36,500 条
- **商品（ASIN）**：465 个
- **站点**：3 个（US / UK / DE）
- **时间跨度**：12 个月

## ✨ 项目亮点

1. **完整数仓分层**：ODS → DWD → DWS → ADS
2. **10 种脏数据清洗**：金额符号、日期格式、多币种、状态拼写、重复订单、异常值、缺失值等
3. **多币种换算**：USD / GBP / EUR 按汇率统一换算成 USD
4. **数据质量看板**：清洗前后对比，脏数据比例 6.97%，质量评分 93.03%

## 📈 分析结论

- **3 站点营收**：UK 578 万 > DE 564 万 > US 513 万
- **商品集中度**：Top 10 商品贡献 4.66% 营收，长尾效应明显
- **数据质量**：清洗掉 6.97% 的脏数据

## 📂 项目文件

| 文件 | 说明 |
|------|------|
| `etl_clean.py` | ETL 数据清洗脚本 数据分析脚本 |
| `analytics.py` | 生成数据脚本 |
| `amazon_analytics_ods_amazon_orders.sql` | 原始订单脚本 |
| `amazon_analytics_dwd_amazon_orders.sql` | 清洗后的订单脚本 |
| `亚马逊多站点销售分析.pbix` | Power BI 仪表板 |

## 🚀 使用方法

### 1. 环境准备

- MySQL 8.0
- Python 3.10+（pandas、SQLAlchemy、pymysql、Faker）
- Power BI Desktop

### 2. 建库建表

```bash
mysql -u root -p < amazon_analytics_ods_amazon_orders.sql
```

### 3. 生成原始数据 + 脏数据 

```bash
python analytics.py
```

### 4. ETL清洗 + 数据分析

```bash
python etl_clean.py
```

### 5. 打开 Power BI

用 **Power BI Desktop** 打开 `amazon_dashboard.pbix`

---

## 📷 仪表板预览

**4 个分析页面**：

1. **销售总览** — KPI 卡片、月度趋势、3 站点对比、订单状态分布
2. **站点对比** — 站点 × 月份矩阵、站点营收占比、订单状态堆积图
3. **商品分析** — Top 10 商品、品类占比、价格 vs 销量散点图
4. **数据质量看板** — 清洗前后对比、脏数据类型、数据质量评分

---

## 💡 技术难点与解决

| 难点 | 解决方案 |
|------|---------|
| pandas `to_sql(replace)` 丢表结构 | 表结构用 SQL 建，Python 只 `append` |
| SQLAlchemy 2.0 语法变更 | SQL 用 `text()` 包装 |
| 外键约束导致删表失败 | 先删子表再删父表，或 `SET FOREIGN_KEY_CHECKS=0` |
| 变量名与函数名冲突 | DataFrame 变量改名 `rfm_df` |
| 汇率被乘两次导致数据失真 | 分离 `price_rate`（定价）和 `to_usd_rate`（换算）|
| 3 站点价格不一致 | `base_price` 移到站点循环外，3 站点共用 |

---

## 📧 联系方式

- GitHub：[@je295](https://github.com/je295)
- 邮箱：ab3_0926@qq.com

---

## 📄 License

MIT License
