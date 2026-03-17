# config/env_config.py

class Config:
    # 模拟多环境切换开关 (local: 本地开发环境, test: 测试服务器环境)
    ENV = "local"

    # 1. 业务系统路由
    URLS = {
        "local": "http://localhost:8080",  # 若依本地默认后端端口
        "test": "http://192.168.1.100:8080"  # 假设的测试环境
    }

    # 2. 默认超管账号密码 (用于自动化脚本获取全局最高权限 Token)
    ADMIN_USER = {
        "username": "admin",
        "password": "admin123"
    }

    # 3. Redis 缓存配置 (若依本地默认配置)
    REDIS_CONFIG = {
        "host": "localhost",
        "port": 6379,
        "password": "",  # 若依本地默认无密码，如有请填入
        "db": 0
    }

    # 4. MySQL 数据库配置 (为后续的深度断言做准备)
    MYSQL_CONFIG = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "root",  # 替换为你本地 MySQL 的真实密码
        "db": "ryvue"  # 若依默认数据库名
    }

    @classmethod
    def get_base_url(cls):
        return cls.URLS.get(cls.ENV)