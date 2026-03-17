# common/mysql_util.py
import pymysql
import logging

class MysqlUtil:
    def __init__(self, host, port, user, password, db, charset="utf8mb4"):
        try:
            self.conn = pymysql.connect(
                host=host, port=port, user=user, password=password,
                db=db, charset=charset,
                cursorclass=pymysql.cursors.DictCursor # 核心：让查询结果变成字典格式
            )
            self.cursor = self.conn.cursor()
            logging.info(f"🟢 MySQL 数据库直连成功 [{host}:{port} - {db}]")
        except Exception as e:
            logging.error(f"❌ MySQL 数据库连接失败: {e}")
            raise e

    def query_one(self, sql, args=None):
        """查询单条数据"""
        self.cursor.execute(sql, args)
        return self.cursor.fetchone()

    def query_all(self, sql, args=None):
        """查询多条数据"""
        self.cursor.execute(sql, args)
        return self.cursor.fetchall()

    def close(self):
        """用完必须关闭，防止连接池爆炸"""
        self.cursor.close()
        self.conn.close()