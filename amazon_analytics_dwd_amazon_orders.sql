-- MySQL dump 10.13  Distrib 8.0.27, for Win64 (x86_64)
--
-- Host: localhost    Database: amazon_analytics
-- ------------------------------------------------------
-- Server version	8.0.27

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `dwd_amazon_orders`
--

DROP TABLE IF EXISTS `dwd_amazon_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dwd_amazon_orders` (
  `order_id` bigint NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `amazon_order_id` varchar(50) NOT NULL COMMENT '亚马逊订单号',
  `purchase_date` datetime NOT NULL COMMENT '下单时间（已清洗）',
  `order_status` varchar(20) NOT NULL COMMENT '订单状态（已归一化）',
  `fulfillment_channel` varchar(20) DEFAULT NULL COMMENT '配送渠道',
  `marketplace` varchar(10) NOT NULL COMMENT '站点（US/UK/DE）',
  `sku` varchar(50) NOT NULL COMMENT '商家货号',
  `asin` varchar(20) NOT NULL COMMENT '亚马逊商品号',
  `product_name` varchar(500) DEFAULT NULL COMMENT '商品名',
  `category` varchar(50) DEFAULT NULL,
  `quantity` int NOT NULL COMMENT '数量（已清洗）',
  `currency` varchar(5) DEFAULT NULL COMMENT '货币',
  `item_price` decimal(10,2) DEFAULT NULL COMMENT '商品价格（已清洗）',
  `item_tax` decimal(10,2) DEFAULT NULL COMMENT '商品税',
  `shipping_price` decimal(10,2) DEFAULT NULL COMMENT '运费',
  `item_price_usd` decimal(10,2) DEFAULT NULL COMMENT '商品价格（换算成美元）',
  `total_amount_usd` decimal(10,2) DEFAULT NULL COMMENT '总金额（美元）',
  `ship_city` varchar(100) DEFAULT NULL COMMENT '收货城市',
  `ship_state` varchar(50) DEFAULT NULL COMMENT '收货州',
  `ship_country` varchar(10) DEFAULT NULL COMMENT '收货国家',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`order_id`),
  KEY `idx_order_date` (`purchase_date`),
  KEY `idx_marketplace` (`marketplace`),
  KEY `idx_asin` (`asin`)
) ENGINE=InnoDB AUTO_INCREMENT=46516 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='清洗后的订单明细';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-13  9:04:13
