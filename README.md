# get_table_status
通过Python脚本监控MySQL数据库的表数据量、表大小、索引大小、自增主键等项目，并在Grafna中展示。及时发现数据量异常增长的库表及自增主键异常情况。

## 使用方法

##### 1.执行init.sql 初始化监控数据保存的数据库
##### 2.在setting.py 中填写被监控的MySQL实例及监控MySQL实例信息
##### 3.安装脚本依赖包,执行gather_schema_status.py即可，默认每5分钟收集一次
##### 4.导入grafna Dashboard 文件，查看





