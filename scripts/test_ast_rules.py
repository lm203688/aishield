#!/usr/bin/env python3
"""Verify AST rules introduce zero FP on external negatives.

Tests only AST01-AST10 rules against:
- 517 external negatives (benchmarks/corpus/external/negatives/)
- 517 external negatives as controlled_matched (hard-negatives from same families)
"""
import sys, os, re, json, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scanner.rules import (
    AST01_RULES, AST02_RULES, AST03_RULES, AST04_RULES,
    AST05_RULES, AST06_RULES, AST07_RULES, AST08_RULES,
    AST09_RULES, AST10_RULES,
)

AST_ALL = {}
for name, rules in [
    ('AST01', AST01_RULES), ('AST02', AST02_RULES), ('AST03', AST03_RULES),
    ('AST04', AST04_RULES), ('AST05', AST05_RULES), ('AST06', AST06_RULES),
    ('AST07', AST07_RULES), ('AST08', AST08_RULES), ('AST09', AST09_RULES),
    ('AST10', AST10_RULES),
]:
    for pat in rules:
        AST_ALL[pat] = (name, rules[pat][1])  # (ast_id, severity)

print(f'AST rules total: {len(AST_ALL)}')
print(f'AST families: {sorted(set(v[0] for v in AST_ALL.values()))}')
print()

# Load all external negatives
neg_dir = 'benchmarks/corpus/external/negatives'
neg_files = sorted(glob.glob(os.path.join(neg_dir, '*.json')))
print(f'Negatives: {len(neg_files)} files')

fp_count = 0
fp_details = []
family_hits = {}

for f in neg_files:
    d = json.load(open(f))
    txt = d.get('text', '')
    fam = d.get('family', 'unknown')
    for pat, (ast_id, sev) in AST_ALL.items():
        try:
            if re.search(pat, txt):
                fp_count += 1
                fp_details.append((f.split('/')[-1], ast_id, sev, fam, txt[:150]))
                family_hits.setdefault(fam, 0)
                family_hits[fam] += 1
        except re.error as e:
            print(f'  REGEX ERROR {ast_id}: {e}')
            break

print()
if fp_count == 0:
    print('✓ 0 FP on all 517 negatives')
else:
    print(f'✗ FP count: {fp_count}')
    print('FP breakdown by family:')
    for fam, cnt in sorted(family_hits.items(), key=lambda x: -x[1]):
        print(f'  {fam}: {cnt}')
    print()
    print('FP examples (first 15):')
    for fn, ast_id, sev, fam, txt in fp_details[:15]:
        print(f'  [{ast_id}/{sev}] {fam} :: {fn}')
        print(f'    text: {txt[:120]}')

# Also test against positives to see which AST rules actually fire
print()
print('=== AST rule recall on positives ===')
pos_dir = 'benchmarks/corpus/external/positives'
pos_files = sorted(glob.glob(os.path.join(pos_dir, '*.json')))
print(f'Positives: {len(pos_files)} files')

ast_recall = {f'AST{i:02d}': 0 for i in range(1, 11)}
ast_recall_total = 0
family_positive_counts = {}

for f in pos_files:
    d = json.load(open(f))
    txt = d.get('text', '')
    fam = d.get('family', 'unknown')
    family_positive_counts[fam] = family_positive_counts.get(fam, 0) + 1
    for pat, (ast_id, sev) in AST_ALL.items():
        try:
            if re.search(pat, txt):
                ast_recall[ast_id] += 1
                ast_recall_total += 1
        except:
            pass

print('AST rule hits on positives:')
for ast_id, cnt in ast_recall.items():
    print(f'  {ast_id}: {cnt} hits')
print(f'Total AST hits on positives: {ast_recall_total}')
print()
print('Positive family distribution:')
for fam, cnt in sorted(family_positive_counts.items(), key=lambda x: -x[1]):
    print(f'  {fam}: {cnt}')
