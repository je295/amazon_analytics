USE amazon_analytics;

-- DWS 表：按天 + 站点 + 品类汇总
CREATE TABLE IF NOT EXISTS dws_daily_marketplace_sales (
    stat_date DATE COMMENT '统计日期',
    marketplace VARCHAR(10) COMMENT '站点',
    category VARCHAR(50) COMMENT '品类',
    order_count INT COMMENT '订单数',
    item_count INT COMMENT '商品件数',
    gmv_usd DECIMAL(12,2) COMMENT '销售额（美元）',
    avg_order_value DECIMAL(10,2) COMMENT '客单价',
    PRIMARY KEY (stat_date, marketplace, category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='按天+站点+品类汇总';

-- ADS 表 1：站点月度销售
CREATE TABLE IF NOT EXISTS ads_marketplace_monthly(
    `year_month` VARCHAR(7) COMMENT '年月',
    marketplace VARCHAR(10) COMMENT '站点',
    gmv_usd DECIMAL(12,2) COMMENT '销售额',
    order_count INT COMMENT '订单数',
    avg_order_value DECIMAL(10,2) COMMENT '客单价',
    PRIMARY KEY (`year_month`, marketplace)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='站点月度销售';

-- ADS 表 2：ASIN 销售排行
CREATE TABLE IF NOT EXISTS ads_asin_performance (
    asin VARCHAR(20) COMMENT '亚马逊商品号',
    product_name VARCHAR(500) COMMENT '商品名',
    marketplace VARCHAR(10) COMMENT '站点',
    total_gmv_usd DECIMAL(12,2) COMMENT '总销售额',
    total_qty INT COMMENT '总销量',
    ad_spend_usd DECIMAL(10,2) COMMENT '广告花费',
    acos DECIMAL(5,2) COMMENT 'ACOS',
    roas DECIMAL(5,2) COMMENT 'ROAS',
    PRIMARY KEY (asin, marketplace)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='ASIN 销售排行';

