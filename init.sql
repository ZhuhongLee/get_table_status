'''
将被监控实例的数据抽到监控数据库中再进行关联计算
因为系统表较多时会导致关联查询时间长
'''


create database dba_monitor_grafna ;
use dba_monitor_grafna;




SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for mysql_info_schema
-- ----------------------------
DROP TABLE IF EXISTS `mysql_info_schema`;
CREATE TABLE `mysql_info_schema` (
  `id` bigint(11) NOT NULL AUTO_INCREMENT,
  `time` datetime DEFAULT NULL,
  `server_id` bigint(11) DEFAULT NULL,
  `server_name` varchar(100) DEFAULT NULL,
  `table_schema` varchar(50) DEFAULT NULL,
  `table_name` varchar(50) DEFAULT NULL,
  `table_rows` bigint(11) DEFAULT NULL,
  `data_length` bigint(11) DEFAULT NULL,
  `index_length` bigint(11) DEFAULT NULL,
  `autoincr_column` varchar(50) DEFAULT NULL,
  `autoincr_value` bigint(11) DEFAULT NULL,
  `autoincr_usage` decimal(4,4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_serverid_time_table_rows` (`server_id`,`time`,`table_rows`),
  KEY `idx_time_table_tblength` (`server_id`,`time`,`data_length`) USING BTREE,
  KEY `idx_time_table_idxlength` (`server_id`,`time`,`index_length`) USING BTREE,
  KEY `idx_time_table_incr` (`server_id`,`time`,`autoincr_usage`) USING BTREE,
  KEY `idx_time` (`time`)
) ENGINE=InnoDB   DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for table_columns
-- ----------------------------
DROP TABLE IF EXISTS `table_columns`;
CREATE TABLE `table_columns` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `TABLE_SCHEMA` varchar(64) DEFAULT NULL,
  `TABLE_NAME` varchar(64) DEFAULT NULL,
  `COLUMN_NAME` varchar(64) DEFAULT NULL,
  `COLUMN_TYPE` varchar(128) DEFAULT NULL,
  `DATA_TYPE` varchar(64) DEFAULT NULL,
  `COL_UNSIGNED` char(2) DEFAULT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_schema_table` (`TABLE_SCHEMA`,`TABLE_NAME`) USING BTREE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COMMENT='包含自增主键的业务库表';

-- ----------------------------
-- Table structure for tables
-- ----------------------------
DROP TABLE IF EXISTS `tables`;
CREATE TABLE `tables` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_id` bigint(11) DEFAULT NULL,
  `server_name` varchar(255) NOT NULL,
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `TABLE_ROWS` bigint(21) unsigned DEFAULT NULL,
  `DATA_LENGTH` bigint(21) unsigned DEFAULT NULL,
  `INDEX_LENGTH` bigint(21) unsigned DEFAULT NULL,
  `AUTO_INCREMENT` bigint(21) unsigned DEFAULT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB   DEFAULT CHARSET=utf8;

