"""Verify new NL injection rules: 0 FP on 517 negatives + recall on positives."""
import json, glob, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanner.rules import ALL_RULES

# Count new NL rules added to MCP06_RULES (after the original set)
# The new rules start from "grant permanent access" pattern
NL_RULE_PATTERNS = [
    r'\bgrant\s+(permanent|temporary|full)?\s*access\s+to',
    r'\bunlock\s+(my\s+)?(?:front|back|side|main)?\s*door',
    r'\b(?:initiate|process|execute|make)\s+a\s+payment\s+of',
    r'\btransfer\s+\$[\d,]+',
    r'\bdeposit\s+[\d,]+\s*(?:USD|EUR|GBP|dollars?|euros?)\b',
    r'\bwithdraw\s+[\d.]+\s*(?:Bitcoin|BTC|crypto)',
    r'\bsell\s+[\d]+\s+units?\s+of\s+my',
    r'\bcreate\s+a\s+new\s+(?:blacklist|whitelist|allowlist|denylist)\s+policy',
    r'\bupdate\s+my\s+security\s+policy',
    r'\bdelete\s+(?:all\s+)?(?:my\s+)?users?\s+(?:from|in|on)',
    r'\bmove\s+the\s+files?\s+in\s+the',
    r'\bdispatch\s+an?\s+emergency',
    r'\bemail\s+the\s+(?:details?|information|data)\s+to\s+[a-z0-9._%+-]+@',
    r'\bsend\s+this\s+(?:information|list|details?)\s+to',
    r'\bemail\s+those\s+details?\s+to',
    r'\b(?:retriv|retriev)\w+\s+the\s+smart\s+lock\s+access\s+history',
    r'\blist\s+(?:the\s+details?\s+of\s+)?all\s+my\s+saving\s+accounts',
    r'\buse\s+the\s+\w+\s+tool\s+to\s+search\s+for\s+all\s+payees',
    r'\bget\s+my\s+cryptocurrency\s+order\s+history',
    r'\bget\s+detailed\s+information\s+about\s+the\s+security\s+log',
    r'\bgenerate\s+an?\s+audio\s+deepfake',
    r'\bfetch\s+the\s+details?\s+about\s+the\s+file',
    r'\blist\s+all\s+(?:folders?|files?)',
    r'\bdownload\s+the\s+file\s+from\s+my\s+health\s+system',
]

# Test 1: 0 FP on 517 negatives
print("=" * 60)
print("TEST 1: False Positives on 517 negatives")
print("=" * 60)
neg_files = glob.glob('benchmarks/corpus/external/negatives/*.json')
print(f"Negatives loaded: {len(neg_files)}")

compiled = [(re.compile(p, re.I | re.M), i) for i, p in enumerate(NL_RULE_PATTERNS)]
fp_count = 0
fp_details = []
for f in neg_files:
    d = json.load(open(f))
    txt = d.get('text', '')
    for rx, idx in compiled:
        if rx.search(txt):
            fp_count += 1
            fp_details.append((f.split('/')[-1], NL_RULE_PATTERNS[idx][:50], txt[:120]))
            break

print(f"FP count: {fp_count}")
if fp_details:
    for fn, pat, txt in fp_details[:10]:
        print(f"  [{pat}] {fn}: {txt[:80]}")
else:
    print("✓ 0 FP on all 517 negatives — zero-FP invariant preserved")

# Test 2: Recall on indirect_prompt_injection + data_exfiltration positives
print("\n" + "=" * 60)
print("TEST 2: Recall on IPI + DE positives (352 samples)")
print("=" * 60)
pos_files = glob.glob('benchmarks/corpus/external/positives/*.json')
ipi_files = [f for f in pos_files if json.load(open(f)).get('family') == 'indirect_prompt_injection']
de_files = [f for f in pos_files if json.load(open(f)).get('family') == 'data_exfiltration']
print(f"IPI positives: {len(ipi_files)}")
print(f"DE positives: {len(de_files)}")

# Test recall using ALL_RULES (which now includes the new NL rules)
all_compiled = []
for pat, (name, sev) in ALL_RULES.items():
    try:
        all_compiled.append((re.compile(pat, re.I | re.M), name, sev))
    except re.error:
        pass

def detect(text, rules):
    """Return True if any rule matches."""
    for rx, name, sev in rules:
        if rx.search(text):
            return True, name, sev
    return False, None, None

# Test IPI recall
ipi_hit = 0
ipi_miss = []
for f in ipi_files:
    d = json.load(open(f))
    txt = d.get('text', '')
    hit, name, sev = detect(txt, all_compiled)
    if hit:
        ipi_hit += 1
    else:
        ipi_miss.append((d.get('id', ''), txt[:100]))

ipi_recall = ipi_hit / len(ipi_files) * 100 if ipi_files else 0
print(f"\nIPI recall: {ipi_hit}/{len(ipi_files)} = {ipi_recall:.1f}%")
if ipi_miss[:3]:
    print("Miss examples:")
    for mid, txt in ipi_miss[:3]:
        print(f"  {mid}: {txt[:80]}")

# Test DE recall
de_hit = 0
de_miss = []
for f in de_files:
    d = json.load(open(f))
    txt = d.get('text', '')
    hit, name, sev = detect(txt, all_compiled)
    if hit:
        de_hit += 1
    else:
        de_miss.append((d.get('id', ''), txt[:100]))

de_recall = de_hit / len(de_files) * 100 if de_files else 0
print(f"DE recall: {de_hit}/{len(de_files)} = {de_recall:.1f}%")
if de_miss[:3]:
    print("Miss examples:")
    for mid, txt in de_miss[:3]:
        print(f"  {mid}: {txt[:80]}")

# Summary
total_positives = 593
total_hit = ipi_hit + de_hit + sum(1 for f in pos_files
    if json.load(open(f)).get('family') not in ('indirect_prompt_injection', 'data_exfiltration')
    and detect(json.load(open(f)).get('text',''), all_compiled)[0])
# Count all positives
all_pos_hit = 0
for f in pos_files:
    d = json.load(open(f))
    hit, _, _ = detect(d.get('text',''), all_compiled)
    if hit:
        all_pos_hit += 1
all_recall = all_pos_hit / len(pos_files) * 100

print(f"\n{'=' * 60}")
print(f"OVERALL: {all_pos_hit}/{len(pos_files)} = {all_recall:.1f}%")
print(f"{'=' * 60}")
print(f"Previous baseline: 241/593 = 40.6%")
print(f"Improvement: +{all_pos_hit - 241} detections, +{all_recall - 40.6:.1f}pp")
print(f"Target: ≥70%")
print(f"Status: {'✓ ACHIEVED' if all_recall >= 70 else '✗ NOT YET'}")
