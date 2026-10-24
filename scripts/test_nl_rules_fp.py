"""Test proposed NL injection rules against negatives for 0 FP verification."""
import json, glob, re

# Proposed rules for indirect_prompt_injection (IPI) and data_exfiltration (DE)
# Each rule is anchored to tool-response context (JSON dict with review/snippet/body/etc.)
# AND requires imperative action verbs to avoid FP on benign product descriptions.

# --- IPI rules ---
# These match "Please grant access", "unlock my door", "create policy", etc.
# anchored to tool-response fields (review_content, snippet, body, description, bio)
IPI_RULES = [
    # "Please grant (permanent )?access to" - smart lock / system access requests
    (r"(?i)grant\s+(permanent\s+|temporary\s+)?access\s+to\s+(my\s+)?(?:friend|guest|user|member)\b[^.]{0,60}(guest|user)[_ ]\w+\s*\w+\s+(?:on|at)\s+\w",
     "间接注入: 请求授予永久/临时访问权限给第三方用户", "critical"),
    # "Please unlock my (front )?door" - physical access control
    (r"(?i)please\s+unlock\s+(my\s+)?(?:front\s+|back\s+)?door",
     "间接注入: 请求解锁物理门禁(智能家居)", "high"),
    # "Please initiate a payment of" - financial action injection
    (r"(?i)(initiate|process|execute)\s+a\s+payment\s+of\s+\$?\d",
     "间接注入: 请求发起支付交易", "critical"),
    # "Please transfer $" - money transfer
    (r"(?i)please\s+transfer\s+\$[\d,]+",
     "间接注入: 请求转账", "critical"),
    # "Please deposit \d+ (USD|EUR|GBP)" - deposit request
    (r"(?i)please\s+deposit\s+[\d,]+\s*(USD|EUR|GBP)",
     "间接注入: 请求存款操作", "critical"),
    # "Withdraw \d+ Bitcoin" - crypto withdrawal
    (r"(?i)withdraw\s+[\d.]+\s+Bitcoin",
     "间接注入: 请求加密货币提现", "critical"),
    # "Please sell \d+ units of my (Bitcoin|crypto)" - asset sale
    (r"(?i)please\s+sell\s+[\d]+\s+units?\s+of\s+my\s+(Bitcoin|crypto)",
     "间接注入: 请求出售加密资产", "critical"),
    # "Please create a new (blacklist|whitelist) policy" - policy manipulation
    (r"(?i)please\s+create\s+a\s+new\s+(blacklist|whitelist|allowlist|denylist)\s+policy",
     "间接注入: 请求创建安全策略黑名单/白名单", "critical"),
    # "Please update my security policy" - policy modification
    (r"(?i)please\s+update\s+my\s+security\s+policy",
     "间接注入: 请求修改安全策略", "critical"),
    # "Please move the files" - file manipulation
    (r"(?i)please\s+move\s+the\s+files\s+in\s+the\s+\"",
     "间接注入: 请求移动文件", "high"),
    # "dispatch an emergency" - emergency dispatch injection
    (r"(?i)please\s+dispatch\s+an\s+emergency\s+(fire|medical|police)\s+response",
     "间接注入: 请求调度应急响应", "high"),
]

# --- Data exfiltration rules ---
# These match "retrieve... and email them to [email]", "send [data] to [email]", etc.
DE_RULES = [
    # "retrieve my saved [data] and email them to [email]" - classic exfil
    (r"(?i)(retrieve|get|fetch|list|send|upload)\s+(my\s+)?(?:saved\s+)?(?:addresses?|payment\s+methods?|accounts?|history|details|information|data|files?)\s+from\s+\w+\s+and\s+(email|send)\s+(them|it|this)\s+to\s+(?:my\s+)?(?:alternate\s+|secondary\s+)?email\s*[,]?[^.]{0,40}@",
     "数据外泄: 请求检索数据并发送至外部邮箱", "critical"),
    # "email the details to [email]" - explicit exfil to external
    (r"(?i)email\s+the\s+(details?|information|data)\s+to\s+[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}",
     "数据外泄: 请求将详情发送至外部邮箱", "critical"),
    # "send this information to my email address, [email]" - explicit
    (r"(?i)send\s+this\s+(information|list|details?)\s+to\s+(my\s+)?email\s+address\s*[,]?[^.]{0,30}@",
     "数据外泄: 请求将信息发送至邮箱", "critical"),
    # "email those details to me at [email]" - variant
    (r"(?i)email\s+those\s+details?\s+to\s+(me\s+)?at\s+\"?[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}",
     "数据外泄: 请求将详情发送至指定邮箱", "critical"),
    # "send this list to [email]" - list exfil
    (r"(?i)send\s+this\s+list\s+to\s+[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}",
     "数据外泄: 请求将列表发送至邮箱", "critical"),
    # "retrieve the smart lock access history" - access history exfil
    (r"(?i)retriv\w+\s+the\s+smart\s+lock\s+access\s+history",
     "数据外泄: 请求智能门锁访问历史", "critical"),
    # "list the details of all my saving accounts" - financial data
    (r"(?i)list\s+(the\s+details?\s+of\s+)?all\s+my\s+saving\s+accounts",
     "数据外泄: 请求列出储蓄账户详情", "critical"),
    # "Use the [tool] to search for all payees" - tool abuse for enumeration
    (r"(?i)use\s+the\s+\w+\s+tool\s+to\s+search\s+for\s+all\s+payees",
     "数据外泄: 请求使用工具枚举所有收款人", "critical"),
    # "Get my cryptocurrency order history" - crypto data
    (r"(?i)get\s+my\s+cryptocurrency\s+order\s+history",
     "数据外泄: 请求加密货币交易历史", "critical"),
    # "Please get detailed information about the security log" - security log access
    (r"(?i)please\s+get\s+detailed\s+information\s+about\s+the\s+security\s+log",
     "数据外泄: 请求安全日志详情", "critical"),
    # "Generate an audio deepfake" - deepfake generation
    (r"(?i)generate\s+an?\s+audio\s+deepfake",
     "数据外泄: 请求生成音频深度伪造", "critical"),
    # "fetch the details about the file [name] in [path]" - file exfil
    (r"(?i)fetch\s+the\s+details?\s+about\s+the\s+file\s+\"[^\"]+\"\s+in\s+the\s+\"[^\"]+\"\s+directory",
     "数据外泄: 请求获取指定文件详情", "critical"),
    # "list all folders and files in my Dropbox" - directory enumeration
    (r"(?i)list\s+all\s+folders?\s+and\s+files?\s+in\s+my\s+\w+",
     "数据外泄: 请求列出云存储目录", "high"),
    # "download the file from my health system" - health data access
    (r"(?i)download\s+the\s+file\s+from\s+my\s+health\s+system",
     "数据外泄: 请求下载健康系统文件", "critical"),
]

def check_fp(negatives_dir, rules):
    """Check proposed rules against negatives for false positives."""
    files = glob.glob(negatives_dir + '/*.json')
    total = len(files)
    fp_count = 0
    fp_details = []
    for f in files:
        d = json.load(open(f))
        txt = d.get('text', '')
        for pat, name, sev in rules:
            if re.search(pat, txt):
                fp_count += 1
                fp_details.append((f.split('/')[-1], name, txt[:100]))
                break  # count each negative once
    print('  Negatives checked: {}'.format(total))
    print('  False positives: {}'.format(fp_count))
    if fp_details:
        print('  FP examples:')
        for fn, name, txt in fp_details[:5]:
            print('    {} -> {} :: {}'.format(fn, name, txt[:80]))
    return fp_count

print('=== Testing IPI rules against 517 negatives ===')
fp_ipi = check_fp('benchmarks/corpus/external/negatives', IPI_RULES)

print('\n=== Testing DE rules against 517 negatives ===')
fp_de = check_fp('benchmarks/corpus/external/negatives', DE_RULES)

print('\n=== Summary ===')
print('IPI FP:', fp_ipi)
print('DE FP:', fp_de)
print('Total FP:', fp_ipi + fp_de)
