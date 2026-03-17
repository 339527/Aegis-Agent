# common/crypto_util.py
import hashlib
import base64


class CryptoUtil:
    """
    企业级加密/解密工具箱
    专门用于处理接口自动化中的密码加密、鉴权签名 (Sign) 等场景
    """

    @staticmethod
    def md5_encrypt(text: str) -> str:
        """MD5 摘要加密 (常用于密码、参数防篡改签名)"""
        hl = hashlib.md5()
        hl.update(text.encode(encoding='utf-8'))
        return hl.hexdigest()

    @staticmethod
    def base64_encode(text: str) -> str:
        """Base64 编码 (常用于图片流、简单的 Authorization 头部传输)"""
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')

    @staticmethod
    def create_api_signature(params: dict, secret_key: str) -> str:
        """
        🔥 高级面试杀手锏：API 接口签名算法 (Sign)
        模拟大厂极其常见的鉴权方式：将参数按字典序排序 -> 拼接 SecretKey -> 做 MD5 摘要
        """
        # 1. 过滤掉空值，并按字典 Key 首字母排序
        sorted_keys = sorted(params.keys())
        sign_str = "&".join([f"{k}={params[k]}" for k in sorted_keys if params[k]])

        # 2. 尾部拼接盐值 (SecretKey)
        sign_str += f"&key={secret_key}"

        # 3. 返回 MD5 大写字符串作为最终签名
        return CryptoUtil.md5_encrypt(sign_str).upper()