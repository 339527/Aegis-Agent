import json
import os
from datetime import datetime
from config.log_config import logger
from ai_core.trace_context import get_trace_id

class DefectManager:
    def __init__(self, platform="ZenTao"):
        self.platform = platform

    async def run_post_mortem(self, attack_payload, blue_team_log, trace_id):
        """
        [尸检报告] 当红队击穿防线时触发
        """
        # 这里模拟调用 LLM 进行深度‘内审’
        analysis = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "trace_id": trace_id,
            "attack_vector": attack_payload,
            "root_cause": "Tier 1 正则库缺失特定混淆字符匹配，且 Tier 2 语义审计因上下文窗口截断未能识别越权意图。",
            "severity": self._calculate_severity(attack_payload),
            "remediation": f"建议补齐正则：re.compile(r'env\\s*\\|', re.I)"
        }
        return analysis

    def _calculate_severity(self, payload):
        """
        [自动定级]
        """
        # 确保 payload 是字符串类型
        payload_str = str(payload).lower()
        if any(kw in payload_str for kw in ["rm ", "drop", "env"]):
            return "CRITICAL (危)"
        return "HIGH (高)"

    def push_to_issue_tracker(self, analysis_report):
        """
        [自动提单与持久化] 记录溯源日志并落地 JSONL
        """
        trace_id = analysis_report.get('trace_id', 'UNKNOWN')
        issue_json = {
            "title": f"🚨 [Security-Leak] AI 防御失效告警 - {trace_id}",
            "body": analysis_report,
            "assignee": "Security-Dev-Team"
        }

        json_str = json.dumps(issue_json, ensure_ascii=False)

        # 1. 消除幽灵日志：将核心 payload 强制注入日志流
        logger.warning(f"📤 [缺陷管家] 提单成功 | 级别: {analysis_report['severity']} | 载荷: {json_str}")

        # 2. 数据血汗工厂落盘：使用追加模式写入本地 JSONL 文件 (数据库的平替)
        # 使用绝对路径，确保文件总是写入到项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_root, "security_defects.jsonl")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json_str + "\n")

        return json_str