"""Analyze InjecAgent sample phrases to design NL injection rules."""
import json, glob, re
from collections import Counter

files = glob.glob('benchmarks/corpus/external/positives/*.json')
ipi_texts = Counter()
de_texts = Counter()

# The text is a JSON-stringified Python dict. Extract the injection phrase
# that appears as a value in fields like review_content, snippet, body, etc.
# Strategy: find all quoted strings and look for imperative NL patterns.

FIELD_PATTERNS = [
    re.compile(r"'review_content'\s*:\s*'([^']+)'"),
    re.compile(r"'snippet'\s*:\s*'([^']+)'"),
    re.compile(r"'description'\s*:\s*'([^']+)'"),
    re.compile(r"'short_bio'\s*:\s*'([^']+)'"),
    re.compile(r"'body'\s*:\s*'([^']+)'"),
    re.compile(r"'notes'\s*:\s*\[.*?'([^']+)'", re.S),
]

for f in files:
    d = json.load(open(f))
    fam = d.get('family')
    txt = d.get('text', '')
    # Try all field patterns
    for pat in FIELD_PATTERNS:
        for m in pat.finditer(txt):
            phrase = m.group(1)
            # Filter: only keep phrases that look like imperative instructions
            if len(phrase) > 20 and len(phrase) < 500:
                if fam == 'indirect_prompt_injection':
                    ipi_texts[phrase] += 1
                elif fam == 'data_exfiltration':
                    de_texts[phrase] += 1

print('=== Unique IPI phrases ({} total occurrences) ==='.format(sum(ipi_texts.values())))
for p, c in ipi_texts.most_common(20):
    print('  [{}x] {}'.format(c, p[:200]))

print('\n=== Unique DE phrases ({} total occurrences) ==='.format(sum(de_texts.values())))
for p, c in de_texts.most_common(20):
    print('  [{}x] {}'.format(c, p[:200]))
