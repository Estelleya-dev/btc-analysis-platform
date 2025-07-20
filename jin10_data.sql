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

 Date: 19/07/2025 20:24:13
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for jin10_data
-- ----------------------------
DROP TABLE IF EXISTS `jin10_data`;
CREATE TABLE `jin10_data`  (
  `record_id` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `fetch_time` datetime(0) NOT NULL,
  `data_type` int(11) NULL DEFAULT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `pic` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `title` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `source` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `source_link` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `important` int(11) NULL DEFAULT NULL,
  `tags` json NULL,
  `channel` json NULL,
  `remark` json NULL,
  PRIMARY KEY (`record_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
