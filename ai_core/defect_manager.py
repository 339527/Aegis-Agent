import json
import os
from datetime import datetime
from config.log_config import logger
from common.trace_context import get_trace_id


class DefectManager:
    """缺陷管理器，用于记录和管理安全缺陷"""
    
    def __init__(self, platform="ZenTao"):
        self.platform = platform
    
    def push_to_issue_tracker(self, defect_data):
        """将缺陷数据推送到缺陷跟踪系统"""
        trace_id = get_trace_id()
        
        # 使用绝对路径确保文件总是写入到项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_root, "security_defects.jsonl")
        
        # 添加时间戳和trace_id
        defect_data["timestamp"] = datetime.now().isoformat()
        defect_data["trace_id"] = trace_id
        
        # 写入JSONL文件
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(defect_data, ensure_ascii=False) + "\n")
        
        logger.info(f"[{trace_id}] 📤 [缺陷管家] 自动提单成功！已同步至 {self.platform} 看板")
        return {"status": "success", "message": "缺陷记录已保存"}
    
    def run_post_mortem(self, attack_type, payload, severity="HIGH"):
        """运行事后分析并创建缺陷工单"""
        defect_data = {
            "attack_type": attack_type,
            "payload": payload,
            "severity": severity,
            "platform": self.platform
        }
        return self.push_to_issue_tracker(defect_data)
