import sys, json, time, threading, urllib.request, urllib.error
sys.path.insert(0, '.')
import os
os.environ['AISHIELD_PORT'] = '18454'
os.environ['PYTHONUNBUFFERED'] = '1'

from eco.dispatcher import init as eco_init
from eco import identity, payment, badge, marketplace, a2a_gateway
eco_init({'identity': identity, 'payment': payment, 'badge': badge, 'marketplace': marketplace, 'a2a_gateway': a2a_gateway})
from api.server import AIShieldHandler
from http.server import HTTPServer
from socketserver import ThreadingMixIn

class TS(ThreadingMixIn, HTTPServer):
    daemon_threads = True

s = TS(('127.0.0.1', 18454), AIShieldHandler)
t = threading.Thread(target=s.serve_forever, daemon=True)
t.start()
time.sleep(2)

B = 'http://127.0.0.1:18454'
ok = 0; total = 0

def test(name, m, p, body=None, exp=200):
    global ok, total; total += 1
    try:
        url = B + p
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, method=m,
            headers={'Content-Type': 'application/json'} if body else {})
        with urllib.request.urlopen(req, timeout=15) as r:
            ct = r.headers.get('Content-Type', '')[:50]
            print(f'  [OK] {name} -> {r.status} ({ct})')
            ok += 1
    except urllib.error.HTTPError as e:
        status = 'OK' if e.code == exp else 'FAIL'
        print(f'  [{status}] {name} -> {e.code}')
        if e.code == exp: ok += 1
    except Exception as e:
        print(f'  [FAIL] {name} -> {e}')

print('=== Core ===')
test('Health', 'GET', '/api/v1/health')
test('Root', 'GET', '/api/v1')

print('\n=== Static Pages ===')
test('Banned-words', 'GET', '/banned-words')
test('Report page', 'GET', '/report')
test('Tool profile', 'GET', '/tool/profile?name=test&score=85&level=gold&findings=3')

print('\n=== Security ===')
test('Prompt safe', 'POST', '/api/v1/prompt-check', {'prompt': 'write a python function to read csv'})
test('Banned words', 'POST', '/api/v1/banned-words', {'text': 'normal content here'})

print('\n=== Eco ===')
test('List agents', 'GET', '/api/v1/identity/agents')
test('Plans', 'GET', '/api/v1/billing/plans')
test('Market', 'GET', '/api/v1/market/tools')
test('A2A discover', 'GET', '/api/v1/a2a/discover')

print('\n=== Monitor (P2 NEW) ===')
test('Monitor list', 'GET', '/api/v1/monitor/list')
test('Monitor add', 'POST', '/api/v1/monitor/add', {
    'source_url': 'https://github.com/modelcontextprotocol/servers',
    'name': 'mcp-official'
})
test('Monitor check', 'POST', '/api/v1/monitor/check', {
    'source_url': 'https://github.com/modelcontextprotocol/servers'
})
test('Monitor list after', 'GET', '/api/v1/monitor/list')

print('\n=== MCP Protocol ===')
test('MCP init', 'POST', '/api/v1/mcp', {
    'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
    'params': {'protocolVersion': '2025-03-26', 'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '1.0'}}
})

print('\n=== Badge ===')
test('Badge SVG', 'GET', '/api/v1/badge/awesome-tool?score=92&level=gold')

print('\n=== Error Cases ===')
test('Empty audit', 'POST', '/api/v1/audit', {}, 400)
test('Short prompt', 'POST', '/api/v1/prompt-check', {'prompt': 'hi'}, 400)

s.shutdown()
print(f'\n{"="*50}')
print(f'Result: {ok}/{total} passed')
if ok == total:
    print('ALL TESTS PASSED')
else:
    print(f'Failed: {total - ok}')