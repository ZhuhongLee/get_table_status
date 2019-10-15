'''

监控的DB列表
仅支持MySQL
账号需要有所有库的读权限

'''

DBLIST_INFO = [('192.168.211.1', 3306, 'root', 'root123'), ('192.168.211.1', 3307, 'root', 'root123')]




'''

监控数据写入的数据库
仅支持MySQL

'''
MONITORDB_INFO = {'host': '192.168.211.1',
                  'port': 3306,
                  'username': 'root',
                  'password': 'root123',
                  'database': 'dba_monitor'}
