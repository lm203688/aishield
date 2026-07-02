"""
AIShield PII脱敏引擎
1. 集成Rampart模型（ONNX token-classification）
2. 确定性规则匹配（正则+关键词）
3. 自研模型训练框架（基于z-ai SDK）

模型来源: https://huggingface.co/nationaldesignstudio/rampart
许可证: 开源
大小: 14.7MB ONNX
"""

import os, re, json, time
from typing import Dict, List, Tuple, Optional

# PII类型定义
PII_TYPES = {
    "PERSON": "人名",
    "EMAIL": "邮箱",
    "PHONE": "电话",
    "SSN": "社保号",
    "CREDIT_CARD": "信用卡",
    "ADDRESS": "地址",
    "IP_ADDRESS": "IP地址",
    "DATE": "日期",
    "ID_NUMBER": "身份证号",
    "BANK_ACCOUNT": "银行账号",
}

# 确定性规则（正则匹配，不依赖模型，去掉\b适配中文文本）
DETERMINISTIC_RULES = {
    "EMAIL": re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'),
    "PHONE": re.compile(r'1[3-9]\d{9}'),
    "SSN": re.compile(r'\d{3}-\d{2}-\d{4}'),
    "CREDIT_CARD": re.compile(r'(?:\d[ -]*?){13,16}'),
    "IP_ADDRESS": re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'),
    "ID_NUMBER": re.compile(r'\d{17}[\dXx]'),
    "DATE": re.compile(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}'),
    "BANK_ACCOUNT": re.compile(r'622\d{14,17}'),  # 银行卡以62开头
}

class PIIRedactor:
    """PII脱敏引擎"""
    
    def __init__(self, use_model: bool = False):
        self.use_model = use_model
        self.model = None
        self.tokenizer = None
        
        if use_model:
            self._load_model()
    
    def _load_model(self):
        """加载Rampart ONNX模型"""
        try:
            import onnxruntime as ort
            model_path = os.path.join(os.path.dirname(__file__), "rampart.onnx")
            if os.path.exists(model_path):
                self.model = ort.InferenceSession(model_path)
                print(f"✅ Rampart模型已加载: {model_path}")
            else:
                print(f"⚠️ Rampart模型文件不存在: {model_path}")
                print("   使用确定性规则模式（无模型）")
                self.use_model = False
        except ImportError:
            print("⚠️ onnxruntime未安装，使用确定性规则模式")
            self.use_model = False
        except Exception as e:
            print(f"⚠️ 模型加载失败: {e}")
            self.use_model = False
    
    def redact(self, text: str, mode: str = "replace") -> Dict:
        """
        PII脱敏
        mode: replace(替换为[PII类型]) / mask(部分遮罩) / remove(删除)
        """
        start_time = time.time()
        
        findings = []
        redacted_text = text
        
        # 1. 确定性规则匹配
        for pii_type, pattern in DETERMINISTIC_RULES.items():
            for match in pattern.finditer(text):
                findings.append({
                    "type": pii_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "source": "rule"
                })
        
        # 2. 模型推理（如果加载了模型）
        if self.use_model and self.model:
            model_findings = self._model_inference(text)
            findings.extend(model_findings)
        
        # 3. 去重（按位置）
        findings = self._dedup_findings(findings)
        
        # 4. 应用脱敏
        if mode == "replace":
            redacted_text = self._apply_replace(text, findings)
        elif mode == "mask":
            redacted_text = self._apply_mask(text, findings)
        elif mode == "remove":
            redacted_text = self._apply_remove(text, findings)
        
        elapsed = time.time() - start_time
        
        return {
            "original_length": len(text),
            "redacted_text": redacted_text,
            "findings_count": len(findings),
            "findings": [{"type": f["type"], "source": f["source"]} for f in findings],
            "pii_types_found": list(set(f["type"] for f in findings)),
            "mode": mode,
            "processing_time_ms": round(elapsed * 1000, 2),
            "engine": "rampart+deterministic" if self.use_model else "deterministic",
        }
    
    def _model_inference(self, text: str) -> List[Dict]:
        """Rampart模型推理"""
        # TODO: 实现ONNX模型推理
        # 需要下载rampart.onnx模型文件
        return []
    
    def _dedup_findings(self, findings: List[Dict]) -> List[Dict]:
        """按位置去重"""
        findings.sort(key=lambda x: x["start"])
        result = []
        last_end = -1
        for f in findings:
            if f["start"] >= last_end:
                result.append(f)
                last_end = f["end"]
        return result
    
    def _apply_replace(self, text: str, findings: List[Dict]) -> str:
        """替换为[PII类型]"""
        for f in reversed(findings):
            placeholder = f"[{PII_TYPES.get(f['type'], f['type'])}]"
            text = text[:f["start"]] + placeholder + text[f["end"]:]
        return text
    
    def _apply_mask(self, text: str, findings: List[Dict]) -> str:
        """部分遮罩"""
        for f in reversed(findings):
            value = f["value"]
            if len(value) <= 2:
                masked = "*" * len(value)
            else:
                masked = value[0] + "*" * (len(value) - 2) + value[-1]
            text = text[:f["start"]] + masked + text[f["end"]:]
        return text
    
    def _apply_remove(self, text: str, findings: List[Dict]) -> str:
        """删除PII"""
        for f in reversed(findings):
            text = text[:f["start"]] + text[f["end"]:]
        return text
    
    def scan(self, text: str) -> Dict:
        """只扫描不脱敏，返回PII位置"""
        findings = []
        for pii_type, pattern in DETERMINISTIC_RULES.items():
            for match in pattern.finditer(text):
                findings.append({
                    "type": pii_type,
                    "type_cn": PII_TYPES.get(pii_type, pii_type),
                    "start": match.start(),
                    "end": match.end(),
                    "preview": match.group()[:10] + "..." if len(match.group()) > 10 else match.group(),
                })
        
        return {
            "text_length": len(text),
            "pii_count": len(findings),
            "findings": findings,
            "risk_level": "high" if len(findings) > 5 else "medium" if len(findings) > 0 else "safe",
            "engine": "rampart+deterministic" if self.use_model else "deterministic",
        }


# 自研模型训练框架
class PIITrainer:
    """自研PII脱敏模型训练框架"""
    
    def __init__(self):
        self.training_data = []
    
    def generate_training_data(self, count: int = 1000) -> List[Dict]:
        """用z-ai SDK生成PII标注数据"""
        from shared.llm_client import call_llm
        import time
        
        samples = []
        prompt = """生成10条包含PII信息的中文文本，每条标注出PII位置。格式：
{"text": "原始文本", "entities": [{"start": 起始位置, "end": 结束位置, "type": "PII类型", "value": "PII值"}]}

PII类型：PERSON(人名), PHONE(电话), EMAIL(邮箱), ID_NUMBER(身份证), ADDRESS(地址), BANK_ACCOUNT(银行账号)

生成多样化场景：医疗记录、客服对话、合同文本、社交帖子等。

只输出JSON数组，不要其他文字。"""
        
        for i in range(count // 10):
            try:
                result = call_llm(prompt, model="glm-4-flash", max_tokens=800)
                import re
                match = re.search(r'\[.*\]', result, re.S)
                if match:
                    data = json.loads(match.group())
                    samples.extend(data)
            except:
                pass
            time.sleep(2)  # 防429
        
        self.training_data = samples
        return samples
    
    def train_model(self):
        """训练PII识别模型（BERT token-classification）"""
        # TODO: 实现BERT训练流程
        # 1. 数据预处理（BIO标注）
        # 2. BERT微调
        # 3. 导出ONNX
        pass


# 测试
if __name__ == "__main__":
    redactor = PIIRedactor(use_model=False)
    
    # 测试文本
    test_text = """
    患者：张三，身份证号：330102199001011234，联系电话：13812345678。
    紧急联系人：李四，邮箱：lisi@example.com，IP地址：192.168.1.100。
    银行账号：6222021234567890123，信用卡：4532 1234 5678 9012。
    就诊日期：2024-03-15，家庭住址：杭州市西湖区文三路100号。
    """
    
    print("=== PII扫描 ===")
    result = redactor.scan(test_text)
    print(f"PII数量: {result['pii_count']}")
    print(f"风险等级: {result['risk_level']}")
    for f in result["findings"]:
        print(f"  {f['type_cn']}: {f['preview']}")
    
    print("\n=== PII脱敏（替换模式）===")
    result = redactor.redact(test_text, mode="replace")
    print(f"脱敏后:\n{result['redacted_text']}")
    print(f"处理时间: {result['processing_time_ms']}ms")
    
    print("\n=== PII脱敏（遮罩模式）===")
    result = redactor.redact(test_text, mode="mask")
    print(f"脱敏后:\n{result['redacted_text']}")
