# Atlas AI Training Agenda

**Audience:** CDF users building and evaluating industrial AI agents  
**Format:** Single session (adjust timing to fit 2–3 hours)  
**Docs:** [Atlas AI](https://docs.cognite.com/cdf/atlas_ai) | [Concepts](https://docs.cognite.com/cdf/atlas_ai/concepts) | [Agent building](https://docs.cognite.com/cdf/atlas_ai/guides/atlas_ai_agent_building) | [Prompting](https://docs.cognite.com/cdf/atlas_ai/guides/atlas_ai_agent_prompting) | [Language models](https://docs.cognite.com/cdf/atlas_ai/references/atlas_ai_agent_language_models) | [Agent tools](https://docs.cognite.com/cdf/atlas_ai/references/atlas_ai_agent_tools) | [Evaluation overview](https://docs.cognite.com/cdf/atlas_ai/concepts/atlas_ai_agent_evaluation_overview) | [Evaluate agents](https://docs.cognite.com/cdf/atlas_ai/guides/atlas_ai_agent_evaluating)

---

## Goal

Understand what Atlas AI agents are, how they use language models and the CDF knowledge graph, and how to build, prompt, and evaluate agents in CDF. By the end, participants can create an agent in the Agent builder, write effective prompts, configure tools, and run evaluations to verify behavior.

**Deliverable:** A working agent (or draft) in your CDF project, with clear instructions and at least one evaluation run.

---

## Prerequisites

- **CDF project** with Atlas AI enabled (separate license; contact Cognite or [request access](https://www.cognite.com/en/contact)).
- **Access** to Atlas AI > Agent builder and Atlas AI > Evaluate agents in CDF.
- **Data context (optional but helpful):** Some modeled data (e.g. assets, equipment, maintenance orders, time series) so agents have something to query.

---

## Agenda

| Time | Topic | Details |
|------|--------|--------|
| **0:00–0:20** | **Atlas AI overview & concepts** | • **What Atlas AI is:** Industrial AI agents that use GenAI language models + CDF knowledge graph + prompts and tools to solve specific business problems ([Atlas AI](https://docs.cognite.com/cdf/atlas_ai), [Concepts](https://docs.cognite.com/cdf/atlas_ai/concepts))<br>• **Language models:** Understand, generate language; choose by speed, quality, context length ([Language model library](https://docs.cognite.com/cdf/atlas_ai/references/atlas_ai_agent_language_models))<br>• **Knowledge graph:** CDF data models and core/process-industry models give agents context; access control and up-to-date data ([Concepts – Knowledge graphs](https://docs.cognite.com/cdf/atlas_ai/concepts#knowledge-graphs))<br>• **Prompts & instructions:** Goals = what to achieve; instructions = how (workflow, scope, format) ([Concepts – Prompts](https://docs.cognite.com/cdf/atlas_ai/concepts#prompts-and-prompt-engineering))<br>• **Tools:** Query KG, time series, files; analysis (e.g. answer document questions, summarize, analyze time series); integrations (REST, Python, Functions) ([Agent tools](https://docs.cognite.com/cdf/atlas_ai/references/atlas_ai_agent_tools))<br>• **Runtime versions:** Agents are pinned to a runtime (stability); you control upgrades |
| **0:20–0:35** | **Language models & tools reference** | • **Language models:** Stable (latest vs legacy), retirement dates, recommended upgrades; choose model that fits use case and latency ([Language model library](https://docs.cognite.com/cdf/atlas_ai/references/atlas_ai_agent_language_models))<br>• **Query tools:** Query knowledge graph, Find assets/equipment/time series/maintenance orders/activities/files/notifications/operations; Query time series data points<br>• **Analysis tools:** Answer document questions, Summarize documents, Analyze time series (preview), Examine data semantically (preview)<br>• **Integration tools (beta):** Call REST API, Run Python code, Call Function |
| **0:35–0:55** | **Build and publish an agent** | Follow [Build and publish agents](https://docs.cognite.com/cdf/atlas_ai/guides/atlas_ai_agent_building):<br>• **Before:** Scope use case, identify evaluation dataset, choose language model<br>• **Create agent:** Atlas AI > Agent builder > + Create agent (or template)<br>• **Configure:** Name, description, sample prompts<br>• **Prompting:** Select language model; write **instructions** (role, output format, constraints, edge cases)<br>• **Tools:** Add tools; for data retrieval set data model, view, access scope (location / user rights / manual spaces)<br>• **Test:** Use chat preview; refine model, instructions, tools<br>• **Publish:** Publish to Agent library for project users<br>• **Hands-on:** Each participant creates or edits one agent and tests in chat |
| **0:55–1:15** | **Effective prompting** | Use [About prompting Atlas AI agents](https://docs.cognite.com/cdf/atlas_ai/guides/atlas_ai_agent_prompting):<br>• **Config impact:** Model choice, goals/instructions, and tools shape how prompts are interpreted<br>• **Be specific and clear:** Action verbs; avoid vague (“Tell me about Pump P-101”) vs specific (“What is the current operational status of Pump P-101?”) or highly specific (“List all open high-priority work orders for Compressor C-205 in the last 30 days”)<br>• **Provide context:** Equipment, sensor, time range; e.g. “temperature trend for Reactor R-301, sensor TI-301A, past 7 days”; with detailed context: “Considering recent maintenance on HE-502, any anomalous pressure readings in connected lines in the past 48 hours?” ([With detailed context](https://docs.cognite.com/cdf/atlas_ai/guides/atlas_ai_agent_prompting#with-detailed-context))<br>• **Define output:** Format (bullets, table), level of detail, precision (e.g. max/min vibration on a date)<br>• **Understanding responses:** Use reasoning field and tool calls to refine prompts |
| **1:15–1:30** | **Evaluations: overview & workflow** | [About AI agent evaluations](https://docs.cognite.com/cdf/atlas_ai/concepts/atlas_ai_agent_evaluation_overview):<br>• **Purpose:** Test how agents respond to specific prompts; measure performance and verify behavior<br>• **How:** Test cases = prompt + expected response; run evaluation → agent responds → compare to expected → view results<br>• **Why:** Check regression, test before deployment, document expected behavior, track performance over time<br>• **What to test:** Response accuracy, consistency, edge cases (unclear questions, missing data) |
| **1:30–1:50** | **Configure and run evaluations** | [Evaluate Atlas AI agents](https://docs.cognite.com/cdf/atlas_ai/guides/atlas_ai_agent_evaluating):<br>• **Create evaluation:** Atlas AI > Evaluate agents > + Create new evaluation; name and description<br>• **Test cases:** Prompt + expected response (optional: use “Generate answer” from an agent to draft expected response)<br>• **Run:** Evaluation overview > Run evaluation > select agent > Confirm and run (allow code tool access if prompted)<br>• **Monitor:** Do not close the tab; cancel if needed<br>• **View results:** Compare agent response to expected per test case; use insights to refine instructions, tools, or test cases<br>• **Hands-on:** Add 2–3 test cases to an evaluation and run it against the agent built earlier |
| **1:50–2:00** | **Wrap-up & next steps** | • Recap: Agent = model + instructions + tools + knowledge graph; prompting = specific + context + output format; evaluations = test cases + run + compare<br>• **Stretch:** Optimize data models for AI search; add custom tools; run evaluations after each change |

---

## Key concepts (cheat sheet)

| Concept | Summary |
|--------|---------|
| **Agent** | GenAI + instructions + tools + CDF knowledge graph; solves a specific business problem. |
| **Instructions** | Define *what* the agent should accomplish and *how* (role, format, constraints). |
| **Tools** | Query (KG, time series, assets, etc.), analysis (documents, time series), integration (API, Python, Functions). |
| **Prompting** | Be specific, add context (equipment, time, scope), define desired output format. |
| **Evaluation** | Test cases (prompt + expected response) → run against agent → compare results to improve agent. |

---

## Documentation quick links

- [Atlas AI](https://docs.cognite.com/cdf/atlas_ai) — Overview and entry point  
- [About Atlas AI agents (concepts)](https://docs.cognite.com/cdf/atlas_ai/concepts) — Language models, knowledge graphs, prompts, tools, runtime  
- [Build and publish agents](https://docs.cognite.com/cdf/atlas_ai/guides/atlas_ai_agent_building) — Step-by-step builder guide  
- [About prompting Atlas AI agents](https://docs.cognite.com/cdf/atlas_ai/guides/atlas_ai_agent_prompting) — Effective prompts, context, output format  
- [Language model library](https://docs.cognite.com/cdf/atlas_ai/references/atlas_ai_agent_language_models) — Stable/legacy/retired models  
- [Agent tools library](https://docs.cognite.com/cdf/atlas_ai/references/atlas_ai_agent_tools) — Query, analysis, integration tools  
- [About AI agent evaluations](https://docs.cognite.com/cdf/atlas_ai/concepts/atlas_ai_agent_evaluation_overview) — How evaluations work and why they matter  
- [Evaluate Atlas AI agents](https://docs.cognite.com/cdf/atlas_ai/guides/atlas_ai_agent_evaluating) — Configure, run, and analyze evaluations  

---

## Slides and export

A markdown-driven slide deck with detailed speaker notes is in **`docs/atlas-ai-training-slides.md`**. It follows this agenda with minimal content per slide and full notes for presenters. Full process (edit, run, export, Google Slides) is in **[docs/atlas-ai-training-slides-README.md](atlas-ai-training-slides-README.md)**.

**Run slides (Slidev):** From the **`slidev/`** folder (Slidev build/export tooling), install deps and start the deck:

```bash
cd slidev
npm install
npm run slides
```

**Export to PPTX:** Speaker notes are preserved in the exported file. Run from **`slidev/`**:

```bash
npm run export:pptx
```

The PPTX is written to `docs/slides/atlas-ai-training-slides.pptx`. Use it for presenting in PowerPoint or for importing into Google Slides.

**Use in Google Slides:** Upload the exported PPTX to Google Drive, then open it with Google Slides. Alternatively, in an existing Google Slides presentation use **File → Import slides** and upload the PPTX to merge the Atlas AI training slides into that deck.

**Export to PDF:** `npm run export:pdf` for a PDF handout (no presenter notes in PDF unless you use presenter view separately).

---

## Optional adjustments

- **Shorter session:** Focus on overview + build one agent + one evaluation run; skim tools reference and deep prompting.
- **No CDF data yet:** Build agents with minimal tools and use sample prompts that don’t depend on real instances; emphasize instructions and evaluation workflow.
- **Advanced:** Add a segment on runtime versions and upgrading; or on custom tools / Python/Function integration.
