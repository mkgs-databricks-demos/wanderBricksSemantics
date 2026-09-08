# L200-B — Genie Agent Standup

## Design Document — Create, Curate, Benchmark, and Hand Off a Genie Agent with Genie Code

**Author:** Matthew Giglia
**Status:** Draft
**Last Updated:** 2026-09-01
**References:** L100 (pending), go/aireadysemantics, Genie Agents best practices docs
**Reference Implementation:** `github.com/mkgs-databricks-demos/wanderBricksSemtantics` → `wb-genie-agent` bundle
**Input from:** L200-A (Metric View Standup) — certified Metric Views are the input artifact

---

### Overview

L200-B covers the **Genie Agent creation and curation workstream** of the Rapid Ontology Standup: from Agent resource creation through side-by-side evaluation, benchmarking, regression testing, UAT, and customer handoff. It operates in the `wb-genie-agent` bundle on its own feature branch.

The Agent's input contract is: **include all certified Metric Views for this domain.** This is the handoff from L200-A. The Agent process does not create or modify Metric View formulas — it consumes them.

---

### Dependencies

| Dependency | Description |
|---|---|
| **Genie Code (Bundle Editor)** | All sessions run in the Genie Code bundle editor on the `wb-genie-agent` bundle |
| **DAB Repo** | Monorepo with `wb-genie-agent` as the target bundle |
| **Feature Branch** | `<initials>-agent-<short-description>` (e.g., `mg-agent-supply-chain`) — never work directly on `main` |
| **Certified Metric Views** | Output of L200-A. The Agent only references certified MVs — this is the handoff contract. |
| **Unity Catalog** | Customer's data and certified Metric Views registered in UC |
| **SQL Warehouse** | Serverless or Pro warehouse for Genie Code execution and Agent testing |
| **Genie Code Permissions** | Set to "Always allow" in the active thread |

---

### Foundational Constraint: Repo-First, DAB-Native, Branch-Controlled

All work is performed inside the `wb-genie-agent` bundle using the Genie Code bundle editor.

**Before Phase 1 begins:**
1. Confirm that L200-A has delivered **certified Metric Views** for the target domain — these must be merged to `main` and deployed
2. Create a feature branch on the `wb-genie-agent` bundle (e.g., `<initials>-agent-initial-curation`)
3. Open the bundle in the Genie Code bundle editor

**Git workflow:** Feature branches named `<initials>-agent-<short-description>` (e.g., `mg-agent-add-benchmarks`), conventional commits (`feat:`, `fix:`, `docs:`), push branch → PR → merge to `main`.

**Branch naming convention distinction:**
- `<initials>-mv-*` branches → L200-A (Metric View Standup) on `wb-metric-views`
- `<initials>-agent-*` branches → L200-B (Genie Agent Standup) on `wb-genie-agent`

This makes it immediately clear which workstream a branch belongs to.

---

### Design

L200-B consists of **three phases** plus an ongoing semantics feedback loop back to L200-A.

---

#### Phase 1: Create and Deploy the Genie Agent

**Goal:** Define the Genie Agent as a DAB resource and deploy it with all certified Metric Views for the domain.

**Genie Code Session:**

1. Open a new Genie Code session in the **bundle editor** (feature branch active).
2. **Define the Genie Agent as a DAB resource** — create a resource YAML file in `resources/` (e.g., `resources/genie_agent.yml`), not ad-hoc in the UI.
3. **Wire in all certified Metric Views** for the domain. The rule: the Agent should include every Metric View in the target schema that carries the `certified` system tag for this domain.
4. **Do NOT include raw base tables or views** — only Metric Views. Keeping both creates redundancy and confusion. The Metric View pre-defines aggregation logic; raw tables contain unaggregated row-level data that increases hallucination risk.
5. Include a **space description** in the resource definition — critical for multi-agent routing. Genie One and future multi-agent systems use the name AND description to route questions to the correct Agent.
6. Keep to **≤30 items** per Agent; split by sub-domain if needed.
7. Deploy the bundle to the dev (or test) target.

**Artifact:** `resources/genie_agent.yml`

---

#### Phase 2: Side-by-Side Curation

**Goal:** Iteratively improve the Genie Agent's accuracy by having Genie Code evaluate its answers, then feed semantics improvements back to L200-A.

**Genie Code Session (NEW session — separate from Phase 1):**

The evaluation session should not carry context from the creation session — it needs to evaluate the Agent fresh.

1. Open the **Genie Agent** and **Genie Code** side by side.
2. Give Genie Code the `@` context (the domain research and data model analysis markdowns from L200-A's `docs/semantics/`).
3. Prompt Genie Code to **evaluate the Genie Agent's answers** to a set of test questions.
4. Genie Code will identify issues and propose improvements. These fall into two categories:

**Improvements the Agent process owns (apply directly):**

| Action | Example |
|---|---|
| Add example SQL for validated queries | Simplified SQL using `WHERE` not `CASE` |
| Add structured instructions | (1) trigger condition, (2) required action, (3) example |
| Enable/disable prompt matching per column | Turn off on irrelevant columns to reduce noise |
| Add benchmarks | 2-4 phrasings per question with ground truth SQL |
| Tune knowledge store | Table/column descriptions, join relationships, SQL expressions scoped to the Agent |

**Improvements that go back to L200-A as semantics feedback (do NOT apply directly):**

| Feedback Type | Example | Why it goes back |
|---|---|---|
| Better or additional synonyms | "Users ask 'sales' but MV only has 'revenue'" | Synonyms are agent metadata in the MV YAML |
| Improved display names | "'Rev' is ambiguous — suggest 'Total Revenue (USD)'" | Display names are agent metadata in the MV YAML |
| Better comments | "Comment doesn't clarify it includes returns" | Comments are in the MV YAML |
| Missing format specifications | "Currency measure has no format" | Formats are agent metadata in the MV YAML |
| Synonym conflicts across MVs | "Two MVs both use 'margin' for different measures" | Requires MV-level disambiguation |

**What the Agent process CANNOT suggest back to L200-A:**

| Off-Limits | Why |
|---|---|
| Changing a measure's `expr` (aggregation logic) | Formula change — owned by the MV author/reviewer |
| Adding or removing dimensions | Data model change |
| Changing join logic or cardinality | Structural change |
| Adding or removing filters | Changes what data the measure includes |

**Semantics feedback flow:** Agent practitioner files a semantics feedback request (GitHub issue, PR comment, or session summary note) → MV practitioner creates a new `<initials>-mv-*` branch on `wb-metric-views` → applies the semantic fix → redeploys to dev/test → re-certifies → merges → Agent practitioner redeploys the Agent bundle to pick up the updated MV.

5. Repeat the evaluation loop **2-3 times** until the Agent is well-curated.

**Curation Checklist:**
- [ ] All certified Metric Views for the domain are wired in
- [ ] No raw tables or base views in the Agent
- [ ] Space description is set (for multi-agent routing)
- [ ] Prompt matching enabled on categorical columns
- [ ] Example SQL added for validated queries (simplified)
- [ ] Structured instructions added: (1) trigger, (2) action, (3) example
- [ ] Benchmarks added: 2-4 phrasings per question with ground truth SQL
- [ ] Regression tests pass after every change
- [ ] Semantics feedback requests filed for any MV issues discovered

---

#### Phase 3: Validation and Handoff

**Goal:** Confirm accuracy and hand off to the customer for ongoing curation.

**Steps:**

1. **Run full benchmark suite** — target ≥85-90% answer accuracy on in-scope questions.
2. **Regression test** — rerun all benchmarks after any change; if previously passing benchmarks fail, the new addition is the likely cause.
3. **User Acceptance Testing** — share with pilot business users:
   - Ensure conversations are marked "reviewable by space managers"
   - Collect feedback via the thumbs up/down feature
   - Use Genie Code to analyze usage trends and feedback
4. **Cross-Agent testing** (if multiple Agents) — test via Genie One chat to verify routing works correctly across Agents. The space description is what drives routing.
5. **Merge and hand off the repo** — the feature branch PR is the deliverable:
   - The entire DAB repo is the handoff artifact
   - Merge the feature branch to `main` after validation passes
   - The customer can extend the pattern by creating new feature branches for additional domains
   - Include a playbook in `docs/` for extending to additional domains and adding new certified Metric Views as they become available

**Completion criteria:** The Agent is "done" when benchmarks pass, UAT feedback is addressed, and the feature branch is merged to `main`.

---

### The Handoff Contract Between L200-A and L200-B

```
L200-A (Metric View Standup)          L200-B (Genie Agent Standup)
─────────────────────────────          ──────────────────────────────
                                       
Phase 1: Domain Research               
Phase 2: Data Model Analysis           
Phase 3: YAML Generation               
Phase 4: Deploy/Review/Certify         
         │                             
         │  certified Metric Views     
         ├────────────────────────────→ Phase 1: Create Agent + wire MVs
         │                             Phase 2: Side-by-Side Curation
         │                                      │
         │  semantics feedback only              │
         │  (synonyms, display names,            │
         │   comments, formats —                 │
         │   NOT formulas or logic)              │
         ←────────────────────────────────────────┘
         │                             Phase 3: Validation + Handoff
         │  re-certified MVs           
         ├────────────────────────────→ (Agent redeploys to pick up)
```

**Key rules:**
- The Agent includes **all certified Metric Views** for its domain — this is the standing rule, not a one-time wiring
- The feedback loop is **semantics only** — synonyms, display names, comments, formats
- Formula, dimension, join, and filter changes are **off-limits** for the Agent process — those are owned by the MV author/reviewer in L200-A
- Each workstream has its own feature branch convention: `<initials>-mv-*` vs. `<initials>-agent-*`

---

### Artifacts Summary

| Phase | Artifact | Location |
|---|---|---|
| 1 | Genie Agent resource YAML | `resources/genie_agent.yml` |
| 2 | Knowledge store, instructions, benchmarks, semantics feedback requests | Agent config + GitHub issues/PR comments |
| 3 | Validation report, merged repo, handoff playbook | Feature branch merged to `main` |

---

### Genie Agent Design Rules

1. **Include all certified Metric Views** for the domain — this is the standing rule
2. **Max 30 items** per Agent (tables + views + Metric Views); split by sub-domain if needed
3. **Always include a space description** — multi-agent systems use it for routing
4. **Domain-aligned, not report-aligned** — organize by business domain, not by existing report structure
5. **Remove raw tables** — only Metric Views in the Agent
6. **Semantics feedback only** — the Agent process suggests synonym/display name/comment/format improvements to L200-A, never formula or logic changes
7. **Defined as a DAB resource** — not created ad-hoc in the UI

---

### Testing Strategy

| Test Type | When | Method |
|---|---|---|
| **Benchmark suite** | Phase 2 (each iteration) | 2-4 phrasings per question with ground truth SQL |
| **Regression testing** | After every change | Rerun full benchmark suite |
| **User Acceptance Testing** | Phase 3 | Pilot business users with feedback collection |
| **Cross-Agent testing** | Phase 3 (if multiple Agents) | Test via Genie One chat to verify routing |

---

### Session Management

- All sessions run in the **Genie Code bundle editor** on the `wb-genie-agent` bundle's active feature branch.
- Use a **separate Genie Code session** for Phase 2 (evaluation) vs. Phase 1 (creation). The evaluation session should not carry context from the creation session.
- Set Genie Code permissions to **"Always allow"** in each thread.
- Write a **session summary** to `fixtures/sessions/YYYY-MM-DD_short-description.md` after each meaningful work session. Maintain `fixtures/sessions/INDEX.md` in reverse-chronological order.

---

### Open Questions

1. **Automation target:** Phase 2 (side-by-side curation) requires judgment and is the hardest to automate. Phase 1 (Agent creation + MV wiring) is mechanical and could be a Genie Code Task.
2. **Multi-agent topology:** For customers with many domains, what's the recommended Agent topology? One Agent per sub-domain? Per domain? How does Genie One route across them?
3. **Certified MV auto-inclusion:** Can the Agent resource YAML dynamically reference "all certified MVs in this schema" rather than listing them explicitly? This would make the standing rule self-enforcing.
