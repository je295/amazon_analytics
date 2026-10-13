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
-- Table structure for table `ods_amazon_orders`
--

DROP TABLE IF EXISTS `ods_amazon_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ods_amazon_orders` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `amazon_order_id` varchar(50) DEFAULT NULL COMMENT '亚马逊订单号',
  `purchase_date` varchar(50) DEFAULT NULL COMMENT '下单时间（字符串，脏）',
  `order_status` varchar(50) DEFAULT NULL COMMENT '订单状态（有拼写错误）',
  `fulfillment_channel` varchar(20) DEFAULT NULL COMMENT '配送渠道',
  `sales_channel` varchar(50) DEFAULT NULL COMMENT '销售站点',
  `sku` varchar(50) DEFAULT NULL COMMENT '商家货号',
  `asin` varchar(20) DEFAULT NULL COMMENT '亚马逊商品号',
  `product_name` varchar(500) DEFAULT NULL COMMENT '商品名',
  `category` varchar(50) DEFAULT NULL,
  `quantity` varchar(20) DEFAULT NULL COMMENT '数量（字符串！）',
  `currency` varchar(10) DEFAULT NULL COMMENT '货币',
  `item_price` varchar(50) DEFAULT NULL COMMENT '商品价格（$29.99 带符号）',
  `item_tax` varchar(50) DEFAULT NULL COMMENT '商品税',
  `shipping_price` varchar(50) DEFAULT NULL COMMENT '运费',
  `ship_city` varchar(100) DEFAULT NULL COMMENT '收货城市',
  `ship_state` varchar(50) DEFAULT NULL COMMENT '收货州',
  `ship_country` varchar(10) DEFAULT NULL COMMENT '收货国家',
  `buyer_email` varchar(100) DEFAULT NULL COMMENT '买家邮箱',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='亚马逊订单原始数据（脏）';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-13  9:04:12
