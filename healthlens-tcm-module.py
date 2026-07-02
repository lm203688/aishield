"""
HealthLens 中医AI诊断模块（支线）
基于14站中医药知识库，提供AI中医分析
"""
import json, urllib.request
from typing import Dict

TCM_KB_URL = "https://tcm-tools.pages.dev/api/entities.json"

def load_tcm_kb():
    """加载中医药知识库"""
    try:
        req = urllib.request.Request(TCM_KB_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data if isinstance(data, list) else data.get("entities", [])
    except:
        return []

def tcm_diagnose(symptoms: str, user_profile: dict) -> dict:
    """中医AI诊断"""
    from shared.llm_client import call_llm
    
    # 搜索相关知识
    kb = load_tcm_kb()
    kb_summary = f"中医药知识库{len(kb)}条实体" if kb else "知识库不可用"
    
    prompt = f"""你是中医AI诊断系统。基于以下信息做中医分析：

用户症状：{symptoms}
用户档案：{json.dumps(user_profile, ensure_ascii=False)[:200]}
知识库：{kb_summary}

请输出：
1. 体质辨识（湿热/气虚/阴虚等）
2. 证候分析
3. 调理建议（食疗+穴位+方剂）
4. 注意事项

注意：AI分析仅供参考，不替代中医师诊断。"""
    
    analysis = call_llm(prompt, model="glm-4-plus", max_tokens=500)
    
    return {
        "module": "tcm",
        "symptoms": symptoms,
        "analysis": analysis,
        "disclaimer": "AI分析仅供参考，不替代中医师诊断",
        "kb_source": "tcm-tools.pages.dev"
    }

def tcm_herb_search(query: str) -> list:
    """搜索中医药材"""
    kb = load_tcm_kb()
    results = []
    for item in kb:
        if query.lower() in json.dumps(item, ensure_ascii=False).lower():
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "category": item.get("category", ""),
                "description": item.get("description", "")[:100]
            })
    return results[:10]

# Flask路由
def register_tcm_routes(app):
    """注册中医模块路由"""
    
    @app.route("/api/tcm/diagnose", methods=["POST"])
    def api_tcm_diagnose():
        from flask import request, jsonify
        data = request.get_json() or {}
        result = tcm_diagnose(data.get("symptoms", ""), data.get("profile", {}))
        return jsonify(result)
    
    @app.route("/api/tcm/herbs")
    def api_tcm_herbs():
        from flask import request, jsonify
        q = request.args.get("q", "")
        return jsonify({"results": tcm_herb_search(q)})
    
    @app.route("/tcm")
    def tcm_page():
        from flask import send_from_directory
        return "TCM module ready. API: /api/tcm/diagnose, /api/tcm/herbs"
