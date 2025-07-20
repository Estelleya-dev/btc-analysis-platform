/*
 Navicat MySQL Data Transfer

 Source Server         : 自己服务器
 Source Server Type    : MySQL
 Source Server Version : 50743
 Source Host           : 8.146.211.122:3306
 Source Schema         : jin10

 Target Server Type    : MySQL
 Target Server Version : 50743
 File Encoding         : 65001

 Date: 19/07/2025 20:24:22
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for latest_timestamp
-- ----------------------------
DROP TABLE IF EXISTS `latest_timestamp`;
CREATE TABLE `latest_timestamp`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `latest_time` datetime(0) NOT NULL,
  `updated_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7172 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
