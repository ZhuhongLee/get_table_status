#!/usr/bin/python
# coding:utf-8
"""
Description:    收集数据库表的信息：表行数，表数据大小，表索引大小，当前自增ID值，自增Id使用率
                写入MySQL
Author:
Date:
"""

import schedule
import time
import pymysql as  MySQLdb
from settings import DBLIST_INFO, MONITORDB_INFO


MAX_INT = {"tinyint": 127,
           "unsigned_tinyint": 255,  # 2**8-1
           "smallint": 32767,
           "unsigned_smallint": 65535,  # 2**16-1
           "mediumint": 8388607,
           "unsigned_mediumint": 16777215,  # 2**24-1
           "int": 2147483647,
           "unsigned_int": 4294967295,  # 2**32-1
           "bigint": 9223372036854775807,
           "unsigned_bigint": 18446744073709551615  # 2**64-1
           }


def migrate_table_and_columns_info(*dbinfo):
    '''
    清除临时表数据，然后从各个被监控实例迁移数据过来
    :return:
    '''
    sql_del_tables_info = '''truncate table dba_monitor_grafna.tables'''
    sql_del_columns_info = '''truncate table dba_monitor_grafna.table_columns'''

    try:
        db_conn = MySQLdb.Connect(host=MONITORDB_INFO['host'], port=MONITORDB_INFO['port'],
                                  user=MONITORDB_INFO['username'], passwd=MONITORDB_INFO['password'], connect_timeout=5)
        cur = db_conn.cursor(MySQLdb.cursors.DictCursor)

        cur.execute(sql_del_tables_info)
        cur.execute(sql_del_columns_info)

    except MySQLdb.Error as e:
        print("Error by execute truncate sql %s" % (e))
        exit(-1)

    finally:
        db_conn.commit()
        cur.close()
        db_conn.close()

    '''
    获取被监控实例的表及列数据
    '''
    sql_get_tables = '''
        SELECT @@SERVER_ID as SERVER_ID,TABLE_SCHEMA,TABLE_NAME,TABLE_ROWS,DATA_LENGTH,INDEX_LENGTH,AUTO_INCREMENT from information_schema.TABLES WHERE TABLE_SCHEMA NOT IN('mysql','information_schema','performance_schema','sys') AND TABLE_TYPE = 'BASE TABLE' and table_name not like 'bak%' and table_name not like 'tmp%' and table_name not like 'temp%'
    '''

    sql_get_columns = '''
        SELECT TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME,COLUMN_TYPE,DATA_TYPE,LOCATE('unsigned',COLUMN_TYPE) COL_UNSIGNED FROM information_schema.COLUMNS WHERE EXTRA = 'auto_increment' and TABLE_SCHEMA NOT IN ('mysql','information_schema','performance_schema','sys') AND table_name NOT LIKE 'bak%' AND table_name NOT LIKE 'tmp%' AND table_name NOT LIKE 'temp%'
    '''

    try:
        db_conn = MySQLdb.Connect(host=dbinfo[0], port=dbinfo[1], user=dbinfo[2], passwd=dbinfo[3], connect_timeout=5)
        cur = db_conn.cursor(MySQLdb.cursors.DictCursor)

        cur.execute(sql_get_tables)
        rs_tables = cur.fetchall()

        cur.execute(sql_get_columns)
        rs_columns = cur.fetchall()

    except MySQLdb.Error as e:
        print("Error by execute select sql: %s" % (e))
        exit(-1)

    finally:
        cur.close()
        db_conn.close()

    '''
    写入数据到监控服务器MySQL实例
    '''
    try:
        db_conn = MySQLdb.Connect(host=MONITORDB_INFO['host'], port=MONITORDB_INFO['port'],
                                  user=MONITORDB_INFO['username'], passwd=MONITORDB_INFO['password'],
                                  connect_timeout=5)
        cur = db_conn.cursor(MySQLdb.cursors.DictCursor)

        for row_table in rs_tables:
            sql_insert_table = '''
                INSERT INTO dba_monitor_grafna.tables(SERVER_ID,SERVER_NAME,TABLE_SCHEMA,TABLE_NAME,TABLE_ROWS,DATA_LENGTH,INDEX_LENGTH,AUTO_INCREMENT) values('%s','%s:%d','%s','%s','%s','%s','%s',%s)
            ''' % (row_table['SERVER_ID'], dbinfo[0], dbinfo[1],
                   row_table['TABLE_SCHEMA'], row_table['TABLE_NAME'], row_table['TABLE_ROWS'],
                   row_table['DATA_LENGTH'],
                   row_table['INDEX_LENGTH'], row_table['AUTO_INCREMENT'] or 'NULL')
            cur.execute(sql_insert_table)

        for row_column in rs_columns:
            sql_insert_column = '''
                INSERT INTO dba_monitor_grafna.table_columns(TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME,COLUMN_TYPE,DATA_TYPE,COL_UNSIGNED) values('%s','%s','%s','%s','%s','%s')
            ''' % (
                row_column['TABLE_SCHEMA'], row_column['TABLE_NAME'], row_column['COLUMN_NAME'],
                row_column['COLUMN_TYPE'],
                row_column['DATA_TYPE'], row_column['COL_UNSIGNED'])
            cur.execute(sql_insert_column)

    except MySQLdb.Error as e:
        print("Error by execute insert sql: %s" % (e))
        exit(-1)

    finally:
        db_conn.commit()
        cur.close()
        db_conn.close()

    '''
    关联查询得到监控数据写入监控库表
    '''
    sql_insert_monitor = '''
        insert into dba_monitor_grafna.mysql_info_schema(time,server_id,server_name,table_schema,table_name,table_rows,data_length,index_length,autoincr_column,autoincr_value,autoincr_usage)
            SELECT  now(),t.server_id,t.SERVER_NAME,t.TABLE_SCHEMA,t.TABLE_NAME,t.TABLE_ROWS,t.DATA_LENGTH,t.INDEX_LENGTH,c.COLUMN_NAME,t.AUTO_INCREMENT,
               case when data_type = 'tinyint' and c.col_unsigned = 0 then AUTO_INCREMENT/%s
                    when data_type = 'tinyint' and c.col_unsigned <> 0 then AUTO_INCREMENT/%s
                    when data_type = 'smallint' and c.col_unsigned = 0 then AUTO_INCREMENT/%s
                    when data_type = 'smallint' and c.col_unsigned <> 0 then AUTO_INCREMENT/%s
                    when data_type = 'mediumint' and c.col_unsigned = 0 then AUTO_INCREMENT/%s
                    when data_type = 'mediumint' and c.col_unsigned <> 0 then AUTO_INCREMENT/%s
                    when data_type = 'int' and c.col_unsigned = 0 then AUTO_INCREMENT/%s
                    when data_type = 'int' and c.col_unsigned <> 0 then AUTO_INCREMENT/%s
                    when data_type = 'bigint' and c.col_unsigned = 0 then AUTO_INCREMENT/%s
                    when data_type = 'bigint' and c.col_unsigned <> 0 then AUTO_INCREMENT/%s
               end as  autoincr_usage
            FROM dba_monitor_grafna.TABLES t LEFT JOIN dba_monitor_grafna.table_columns c ON t.TABLE_SCHEMA = c.TABLE_SCHEMA AND t.TABLE_NAME = c.TABLE_NAME
    ''' % (MAX_INT['tinyint'], MAX_INT['unsigned_tinyint'], MAX_INT['smallint'], MAX_INT['unsigned_smallint'],
           MAX_INT['mediumint'], MAX_INT['unsigned_mediumint'], MAX_INT['int'], MAX_INT['unsigned_int'],
           MAX_INT['bigint'],
           MAX_INT['unsigned_bigint'])

    try:
        db_conn = MySQLdb.Connect(host=MONITORDB_INFO['host'], port=MONITORDB_INFO['port'],
                                  user=MONITORDB_INFO['username'], passwd=MONITORDB_INFO['password'],
                                  connect_timeout=5)
        cur = db_conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(sql_insert_monitor)

    except MySQLdb.Error as e:
        print("Error by execute insert monitor sql: %s" % (e))
        exit(-1)

    finally:
        db_conn.commit()
        cur.close()
        db_conn.close()


def main():
    for db in DBLIST_INFO:
        migrate_table_and_columns_info(*db)


if __name__ == '__main__':
    # main()

    schedule.every(5).minutes.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
