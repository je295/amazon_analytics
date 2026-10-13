USE amazon_analytics;

-- 清空旧数据
TRUNCATE TABLE dws_daily_marketplace_sales;
truncate table ads_marketplace_monthly;
truncate table ads_asin_performance;

-- DWD → DWS：按天 + 站点聚合
INSERT INTO dws_daily_marketplace_sales
SELECT 
    DATE(purchase_date) AS stat_date, #统计日期
    marketplace,
    'All' AS category,
    COUNT(DISTINCT amazon_order_id) AS order_count,
    SUM(quantity) AS item_count,
    ROUND(SUM(total_amount_usd), 2) AS gmv_usd,
    ROUND(AVG(total_amount_usd), 2) AS avg_order_value
FROM dwd_amazon_orders
WHERE order_status IN ('Shipped', 'Delivered')
  AND marketplace != 'Unknown'
GROUP BY DATE(purchase_date), marketplace;

#--ADS表1：月度销售站点
USE amazon_analytics;

TRUNCATE TABLE ads_marketplace_monthly;

INSERT INTO ads_marketplace_monthly
SELECT 
    DATE_FORMAT(purchase_date, '%Y-%m') AS `year_month`,
    marketplace,
    ROUND(SUM(total_amount_usd), 2) AS gmv_usd,
    COUNT(DISTINCT amazon_order_id) AS order_count,
    ROUND(AVG(total_amount_usd), 2) AS avg_order_value
FROM dwd_amazon_orders
WHERE order_status IN ('Shipped', 'Delivered')
  AND marketplace != 'Unknown'
GROUP BY `year_month`, marketplace;

#--ADS表2：ASIN销售排序
TRUNCATE TABLE ads_asin_performance;

INSERT INTO ads_asin_performance
SELECT 
    asin,
    product_name,
    marketplace,
    ROUND(SUM(total_amount_usd), 2) AS total_gmv_usd,
    SUM(quantity) AS total_qty,
    0 AS ad_spend_usd,
    0 AS acos,
    0 AS roas
FROM dwd_amazon_orders
WHERE order_status IN ('Shipped', 'Delivered')
GROUP BY asin, product_name, marketplace;

