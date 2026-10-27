from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote
import hashlib
import re

root = Path(__file__).resolve().parents[1]
report = root / "reports" / "aishield-deep-improvement-2026-10-27.md"
text = report.read_text(encoding="utf-8")
errors = []

for required in [
    "fe9a3cb30608f76119bddc583b3f44252a85bcbd",
    "94.27%（559/593）",
    "0/517",
    "34 个漏检",
    "不能据此声称全量测试通过",
    "建议验收目标（非当前成绩）",
    "不构成法律意见",
]:
    if required not in text:
        errors.append(f"missing required statement: {required}")

for match in re.finditer(r"!\[[^]]*\]\(([^)]+)\)", text):
    target = match.group(1)
    if not (report.parent / target).is_file():
        errors.append(f"missing image: {target}")

links = re.findall(r"\[[^]]*\]\((kimi-cite://[^)\s]+)(?:\s+\"citation\")?\)", text)
for link in links:
    parsed = urlparse(link)
    qs = parse_qs(parsed.query)
    if parsed.netloc == "web":
        url = qs.get("url", [""])[0]
        if not url.startswith(("https://", "http://")):
            errors.append(f"bad web citation: {link}")
        continue
    paths = qs.get("path", [])
    if not paths:
        errors.append(f"citation without path: {link}")
        continue
    path = Path(paths[0])
    if not path.is_absolute() or not path.is_file():
        errors.append(f"missing local citation: {path}")
        continue
    if "line" in qs:
        line = int(qs["line"][0])
        count = len(path.read_text(encoding="utf-8").splitlines())
        if not 1 <= line <= count:
            errors.append(f"bad line {line}/{count}: {path}")
    if "text" in qs:
        snippet = qs["text"][0]
        if snippet not in path.read_text(encoding="utf-8", errors="replace"):
            errors.append(f"snippet not found in {path}: {snippet}")

if re.search(r"\[[^]]+\]\(https?://", text):
    errors.append("bare web markdown link found")
if re.search(r"^##\s+(References?|Sources?|参考文献)", text, re.M | re.I):
    errors.append("unexpected bibliography section")
if len(re.findall(r"^##\s+\d+\.", text, re.M)) != 14:
    errors.append("expected 14 numbered sections")

payload = report.read_bytes()
print(f"report: {report}")
print(f"lines: {len(text.splitlines())}; chars: {len(text)}; bytes: {len(payload)}")
print(f"citations checked: {len(links)}")
print(f"sha256: {hashlib.sha256(payload).hexdigest()}")
if errors:
    print("VALIDATION: FAIL")
    for error in errors:
        print("-", error)
    raise SystemExit(1)
print("VALIDATION: PASS")
