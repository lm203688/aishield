# AIShield — Deployment & Verification

## Two deployment modes

| Mode | What runs | When to use |
|---|---|---|
| **Local (open-source)** | `python -m scanner` or `npx aishield-mcp-server` on your machine | Development, private CI, offline environments |
| **Remote (aishield.tools)** | Cloudflare Named Tunnel → VPS `:8450` → `api/server.py` | Multi-tenant SaaS, agent-native discovery |

The two modes share the **same scanner code** and the **same rule set**. The remote API just wraps the same functions over HTTP; no separate codebase.

## Local deployment

```bash
# Bare Python (no service)
python -m scanner --file ./mcp-config.json

# As an MCP server (stdio)
npx -y aishield-mcp-server

# As an HTTP API (self-host)
uvicorn api.server:app --port 8450
```

## Remote deployment (reference: production)

The live `aishield.tools` production instance is deployed via a Cloudflare Named Tunnel:

```
internet
  ↓  https://aishield.tools/api/v1/...
  Cloudflare Named Tunnel
  ↓  wss
  VPS :8450
  ↓  localhost
  api/server.py (HTTP server)
```

**Do not use `pkill -f cloudflared` to restart.** The tunnel is process-identifiable but not pid-stable across reboots. Stop by PID and restart with the same config.

## Deployment verification (three-step)

After any push, always confirm the live instance has caught up. Order matters:

1. **API health** — get the deployed commit:
   ```bash
   curl --ssl-no-revoke --tlsv1.3 -H "User-Agent: Mozilla/5.0" \
     https://aishield.tools/api/v1/health
   ```
   Look for `"commit"` in the response.

2. **Agent-card** — verify what agents actually discover:
   ```bash
   curl -s https://aishield.tools/.well-known/agent-card.json | jq '.service_version, .rules.total'
   ```

3. **Live rule count** — the only authoritative value:
   ```bash
   curl -s https://aishield.tools/api/v1/health | jq '.rules_breakdown'
   ```
   `rules_breakdown` should show `{static, generated, radar, total}` matching the sum on the deployed commit.

## Push discipline

- **Never skip CI silently.** `[skip ci]` is fine for docs-only changes but any commit that rewrites an external-facing asset (agent-card, llms.txt, feeds.xml) must go through `scripts/_push_batch.py` — it will run `rule_count_gate.py --check` before pushing and refuse on drift.
- **`bash scripts/git_push_safe.sh` failures must not be swallowed.** If it exits 1 (retry exhausted) or 3 (real conflict), that is signal — do not wrap in `|| echo` or `|| true`. If you genuinely need to degrade, add a comment `allow-push-degrade: <reason>` on the line above (E10 in `validate_workflows.py` enforces this).

## Local state isolation

The scanner never writes to paths that come from the configuration it scans. `scripts/prove_isolation.py` proves this by:

1. Patching `subprocess.Popen`, `os.system`, `subprocess.run` to raise on any call
2. Loading the scanner and running a scan against a malicious-looking config that would normally invoke `subprocess`
3. Asserting zero invocations of any spawn function

If the assertion fails, treat it as a security incident — the isolation invariant is broken.

## Rollback

The VPS deployment does not use a rollback tool; the rollback path is:

1. `git checkout <previous-commit>` locally
2. `bash scripts/_push_batch.py "rollback: revert to <sha>"`
3. Wait for the deployment pipeline (5–10 minutes)
4. Verify with the three-step check above
