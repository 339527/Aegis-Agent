import json
import logging
from datetime import datetime

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
        if any(kw in payload.lower() for kw in ["rm ", "drop", "env"]):
            return "CRITICAL (危)"
        return "HIGH (高)"

    def push_to_issue_tracker(self, analysis_report):
        """
        [自动提单] 模拟向禅道/飞书推送 JSON
        """
        # 组装大厂标准的 Issue 报文
        issue_json = {
            "title": f"🚨 [Security-Leak] AI 防御失效告警 - {analysis_report['trace_id']}",
            "body": analysis_report,
            "assignee": "Security-Dev-Team"
        }
        # 实际开发中这里会是 requests.post(webhook_url, json=issue_json)
        logging.warning(f"📤 [缺陷管家] 自动提单成功！已同步至 {self.platform} 看板")
        return json.dumps(issue_json, ensure_ascii=False, indent=2)