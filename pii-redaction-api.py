"""
AIShield PII脱敏API
集成Rampart模型 + 确定性规则 + 自研训练框架
"""

from flask import Flask, request, jsonify
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pii_engine import PIIRedactor, PIITrainer

app = Flask(__name__)
redactor = PIIRedactor(use_model=False)  # 先用确定性规则，后续加载ONNX模型
trainer = PIITrainer()


@app.route("/api/v1/pii/scan", methods=["POST"])
def scan_pii():
    """扫描文本中的PII（不脱敏，只报告）"""
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Missing 'text' field"}), 400
    
    result = redactor.scan(text)
    return jsonify(result)


@app.route("/api/v1/pii/redact", methods=["POST"])
def redact_pii():
    """PII脱敏
    Body: {"text": "...", "mode": "replace|mask|remove"}
    """
    data = request.get_json() or {}
    text = data.get("text", "")
    mode = data.get("mode", "replace")
    
    if not text:
        return jsonify({"error": "Missing 'text' field"}), 400
    
    result = redactor.redact(text, mode=mode)
    return jsonify(result)


@app.route("/api/v1/pii/types", methods=["GET"])
def pii_types():
    """支持的PII类型"""
    from pii_engine import PII_TYPES
    return jsonify({"types": PII_TYPES})


@app.route("/api/v1/pii/health", methods=["GET"])
def health():
    return jsonify({
        "service": "AIShield PII Redaction",
        "status": "healthy",
        "engine": "rampart+deterministic" if redactor.use_model else "deterministic",
        "model_loaded": redactor.use_model,
        "supported_types": len(redactor.scan("") if False else 8),
    })


@app.route("/api/v1/pii/train", methods=["POST"])
def train_model():
    """自研模型训练（生成标注数据）"""
    data = request.get_json() or {}
    count = data.get("count", 100)
    
    samples = trainer.generate_training_data(count=count)
    return jsonify({
        "status": "training_data_generated",
        "samples": len(samples),
        "next_step": "BERT fine-tuning + ONNX export",
    })


if __name__ == "__main__":
    print("AIShield PII脱敏API服务")
    print("端点:")
    print("  POST /api/v1/pii/scan   — 扫描PII")
    print("  POST /api/v1/pii/redact  — PII脱敏")
    print("  GET  /api/v1/pii/types   — PII类型")
    print("  GET  /api/v1/pii/health  — 健康检查")
    print("  POST /api/v1/pii/train   — 训练自研模型")
    app.run(host="0.0.0.0", port=8468, debug=False)
