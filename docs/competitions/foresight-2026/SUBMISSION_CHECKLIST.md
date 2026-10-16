# Foresight Submission Checklist

**Deadline:** 2026-10-31 23:59 PDT (= 2026-11-01 06:59 UTC = **2026-11-01 14:59 Beijing time**)
**Decisions expected:** January 2027 (stated verbatim on the application form)

Submit at (single public Airtable form — **no login, no account needed**):
https://airtable.com/appyVXc5SMPAvIKpP/pagp7takV26cG6JY1/form

> **Read [`PLAYBOOK.md`](PLAYBOOK.md) first.** It contains the verified field-by-field form structure,
> the character limits (**350 chars, zero jargon** for the core pitch), and the grantee comparison.
>
> **Corrigendum 2026-09-23** — the following claims in earlier versions of this checklist were
> **unverified or wrong** and have been removed. Do not reinstate them:
>
> | Removed claim | Why |
> |---|---|
> | "Log in at foresight.org…" | It is a public Airtable form; there is no login |
> | "Track 1 — AI Insurance and Open Governance" | No such label. Correct: **Call II, focus area 4** |
> | "Foresight typically accepts up to 10MB per submission" | Invented. The form has *character* limits, not a file size limit |
> | "Foresight processes applications in receipt order in a tie" | Invented. Not stated anywhere |
> | "Foresight explicitly asks that applicants not run parallel applications to competing grants" | **Not in the RFP.** Do not withhold other applications on this basis |
> | "If stars < 100, run a marketing push" | Stars are **2**, not ~100. See `APPLICATION.md §7` correction |
> | "Foresight loves to see a letter-of-intent" | Unverified, and the form has **no attachment field** |

---

## Pre-submission (Days 1–10, i.e. now through 2026-10-02)

- [ ] **Decide applicant identity**
  - Individual → use [BUDGET_INDIVIDUAL.md](BUDGET_INDIVIDUAL.md) ($35K request)
  - Corporate → use [BUDGET_CORPORATE.md](BUDGET_CORPORATE.md) ($62K request)
  - If you want to explore third options (UK Ltd, Japanese K.K.), fork the corporate template and adapt

- [ ] **Decide on Foresight Node attendance**
  - Skip both → reallocate $5K travel to contingency/infrastructure
  - SF only → individual variant as-is
  - Berlin only → individual variant as-is, change "$5K travel" to Berlin trip
  - Both → must use corporate variant (SF + Berlin)

- [ ] **Fill in personal info placeholders**
  - `APPLICATION.md §5 Team` → Principal investigator name, bio, availability
  - `APPLICATION.md §1 Executive Summary` → applicant name in the header

- [ ] **Sanity-check the rule counts against live API**
  ```bash
  curl -s https://aishield.tools/api/v1/health | python -c "
  import json, sys
  d = json.load(sys.stdin)
  print('Rules breakdown:', d.get('rules_breakdown'))
  print('Version:', d.get('version'))
  "
  ```
  The application claims 235 MCP + 262 Skill. If the live numbers drift, update `APPLICATION.md §2.3`.

- [ ] **Verify the GitHub repo state**
  ```bash
  curl -s https://api.github.com/repos/lm203688/aishield | python -c "
  import json, sys
  d = json.load(sys.stdin)
  print('Stars:', d['stargazers_count'])
  print('Forks:', d['forks_count'])
  print('License:', d['license']['spdx_id'] if d.get('license') else 'MISSING')
  "
  ```
  Actual figures (verified 2026-09-23): **2 stars, 0 forks.** There is no "existing community" signal
  to strengthen, and inflating it is not an option. Either earn a real distribution number (npm
  downloads, Glama installs) before submitting, or drop the community claim entirely and lead with the
  technical artifact. **Do not write a star target into the application.**

- [ ] **Prepare the supporting document set** (must all exist before submission):
  - `APPLICATION.md` (main)
  - `PROJECT_PLAN.md` (milestones)
  - `BUDGET_INDIVIDUAL.md` or `BUDGET_CORPORATE.md`
  - `SUBMISSION_CHECKLIST.md` (this file, self-referential)
  - Optional: existing `docs/agent-security-benchmark-2026.md`, `docs/benchmark-report.md`

---

## Writing phase (Days 11–30, i.e. 2026-10-03 through 2026-10-21)

- [ ] **Fill in the Team section** of `APPLICATION.md §5`
  - Name, one-line bio, availability statement
  - Optional: 2–3 lines on prior open-source work, prior security work, prior AI work
  - Optional: advisory contacts with their consent

- [ ] **Strengthen the "why you" narrative** in `APPLICATION.md §1` and `§3`
  - What specific experience makes you able to deliver this in 6 months?
  - Have you published papers, written blog posts, or shipped tools in this space?
  - What have you learned that others haven't?

- [ ] **Get an independent peer review** (optional but recommended)
  - Ask a security engineer not involved in AIShield to read `APPLICATION.md` and give 15 minutes of feedback
  - Ask an AI-safety researcher (not involved) to review `§2` problem statement
  - Ask a Foresight Node member if you know one

- [ ] **Prepare a "reproducibility" appendix** (optional but recommended)
  - Include a 20-line bash script that reproduces the "22 real-harness files, 0 critical" claim
  - URL to the CI pipeline showing 1283 tests passing
  - URL to the live benchmark endpoint

- [ ] **Prepare the letter-of-intent (if applicable)**
  - If any potential governance body (insurer, procurement team, foundation) would adopt the assessment API, get a signed intent letter
  - Foresight loves to see this — it turns "we will build" into "we will build and 3 parties have already committed to use"

---

## Final review (Days 31–38, i.e. 2026-10-22 through 2026-10-29)

- [ ] **Re-run the rule-count sanity check**
  ```bash
  curl -s https://aishield.tools/api/v1/health | jq '.rules_breakdown, .version'
  ```
  Update the application if numbers have drifted.

- [ ] **Read APPLICATION.md aloud**
  - Any sentence a Foresight reviewer would have to Google to understand? Rewrite it.
  - Any sentence that sounds like marketing? Rewrite it.
  - Any sentence that could be true for any AI project? Rewrite it.

- [ ] **Check every URL**
  - `https://github.com/lm203688/aishield`
  - `https://aishield.tools/api/v1/health`
  - `https://aishield.tools/blog/agent-security-benchmark-2026/`
  - Any other link cited in the application

- [ ] **File size check**
  - There is no stated file size limit. The binding constraints are the form's **character limits**
    (350 chars for the core pitch, 500 for the RFP-fit answer). See `PLAYBOOK.md §2`.

- [ ] **Backup**
  - Save a copy of the full submission packet (all 4–5 files) to a location outside this directory (e.g. your personal Drive, a private GitHub gist, or a USB)
  - Note the exact submission timestamp for your own records (Airtable confirmation). Foresight does
    **not** state a receipt-order tie-break.

---

## Submission (Day 39, 2026-10-31)

- [ ] **Open the Airtable form** (no login required):
      https://airtable.com/appyVXc5SMPAvIKpP/pagp7takV26cG6JY1/form
  - Org type: select **`Individual - World`** if applying without a legal entity
  - Reference, region, and country fields are all required
  - Individual variant: use personal account (name + email + LinkedIn profile URL)
  - Corporate variant: use organisational account (registered entity name + contact)

- [ ] **Fill in the form fields** (typical Foresight form):
  1. Applicant name + email + country of residence
  2. Project title: `AIShield — Local-First AI Tool Security Scanner as Independent Assessment Infrastructure`
  3. Call/focus area: `Call II — Coordination and accountability` → `4. AI Insurance & Open Governance`
  4. Amount requested: `$35,000` (individual) or `$62,000` (corporate)
  5. Project duration: `6 months`
  6. Abstract: paste `APPLICATION.md §1` verbatim
  7. Detailed description: paste the entire `APPLICATION.md` (or attach as file, whichever Foresight prefers)
  8. Timeline: paste `PROJECT_PLAN.md` verbatim
  9. Budget: paste the appropriate BUDGET file verbatim
  10. Attachments: `APPLICATION.md`, `PROJECT_PLAN.md`, BUDGET file, plus optional supporting docs

- [ ] **Check the confirmation screen**
  - Screenshot the confirmation email + submission ID
  - Add a calendar reminder for 2027-01-31 (approximate result date based on Foresight's 3-month review cycle)

- [ ] **Notify (optional)**
  - Email Foresight's grants team a copy of the submission (foresight.org contact form) — some cycles they appreciate a heads-up
  - Tweet the submission on X with `#ForesightNodes` hashtag if you have a public account — community visibility helps

---

## Post-submission (Days 40+, i.e. 2026-11-01 onwards)

- [ ] **Keep AIShield actively shipping**
  - Every week, push a new commit that adds to the "existing evidence" case
  - Do NOT go quiet — Foresight reviews active community signals
  - Keep the live API healthy, keep the test suite green, keep the blog publishing

- [ ] **Watch for Foresight's mid-cycle feedback requests**
  - Some years Foresight asks for mid-application clarification
  - Have a `docs/competitions/foresight-2026/FAQ.md` ready to answer common questions

- [ ] **Prepare for the three outcomes**
  - **Funded at full amount:** proceed with `PROJECT_PLAN.md` as-is
  - **Funded at partial amount:** use the "what we would cut" tables in BUDGET files
  - **Not funded:** the application becomes a public-facing project plan that other grants can reference. Move to `docs/competitions/foresight-2026/ARCHIVED.md` and consider submitting to alternate grants (see §below).

---

## Alternate grants if Foresight declines (pre-identified)

If the Foresight application is not funded by 2027-01-31, the same content can be adapted for:

- **Schmidt Sciences** — AI safety grants, annual cycle, similar scope
- **Epoch AI** — grants for AI measurement research (smaller, $5K–$30K)
- **Future of Life Institute** — AI safety program, similar mandate to Foresight
- **Catalyst Awards** — open-source security tools, 12-month cycles
- **Open Philanthropy** — AI risk reduction, application cycles vary

Each of these has different deadlines and evaluation criteria. **Note:** the RFP does *not* ask
applicants to withhold parallel applications — an earlier version of this file claimed it did. This is
a sequencing preference on our side (the Foresight application is the strongest version of this
material), not a Foresight rule.

---

## What the submission should NOT contain

- Do not include internal credentials, API keys, or private infrastructure details
- Do not include the AIShield source code (link to the public repo instead)
- Do not include personal financial details beyond what the form explicitly asks for
- Do not include political, national-security, or geopolitical commentary — this is a technical application

---

## Common mistakes to avoid

1. **Over-scoping.** Asking for $100K but only having $40K of concrete plan. Foresight rejects vague "we will do a lot of things" applications. Be specific.
2. **Under-scoping.** Asking for $30K and delivering less than what $30K buys. Be honest about the price of what you're asking for.
3. **Ignoring the focus-area requirements.** The relevant option is **Call II → focus area 4, "AI
   Insurance & Open Governance."** If the project doesn't address independent assessment, incident
   reporting, or governance infrastructure, it belongs under a different focus area — or in a
   different funder's call. Also note Foresight funds this focus area at the **smaller** end of
   $30K–$100K.
4. **Missing the "independent" angle.** Foresight funds work that's independent of the AI labs. If your plan sounds like it could be outsourced to Anthropic or OpenAI, it's not what they're looking for.
5. **Not verifying URLs.** Dead links in an application look unprofessional. Verify every one before submitting.

---

*This checklist is itself a living document. If a Foresight reviewer rejects the application with specific feedback, iterate on this checklist to make the next application stronger.*
