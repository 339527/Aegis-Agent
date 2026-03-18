import os
import pymysql
import logging
from unittest.mock import MagicMock

class MysqlUtil:
    def __init__(self, host, port, user, password, db, charset="utf8mb4"):
        # 🛡️ 核心：云端环境感知与物理拦截
        if os.getenv("RUN_ENV") == "ci":
            logging.info("☁️ [企业级挡板] CI环境检测到：已拦截真实 MySQL 连接，启用 Mock 对象")
            self.conn = MagicMock()
            self.cursor = MagicMock()
            return

        # ============ 下面是本地真实的物理连接逻辑 ============
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
        self.cursor.execute(sql, args)
        return self.cursor.fetchone()

    def query_all(self, sql, args=None):
        self.cursor.execute(sql, args)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()