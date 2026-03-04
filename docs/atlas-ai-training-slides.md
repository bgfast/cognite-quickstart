---
layout: cover
background: https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1920
---

# Atlas AI Training

Cognite Data Fusion · Industrial AI agents

<!--
Welcome. This session covers how to build, prompt, and evaluate Atlas AI agents in CDF. We'll keep slides minimal; the detail is in your speaker notes and in the Cognite docs. Timing: about 2 hours with hands-on. If anyone doesn't have Atlas AI enabled yet, note that it requires a separate license—see the prerequisites slide.
-->

---

# Goal

By the end you will:
- Understand what Atlas AI agents are and how they use the knowledge graph
- Build an agent in the Agent builder
- Write effective prompts and run evaluations

<!--
Our goal is practical: you leave with a working agent or draft, clear instructions, and at least one evaluation run. The deliverable is something you can keep refining in your own CDF project. We'll align each section to the 2-hour agenda.
-->

---

# Prerequisites

- CDF project with **Atlas AI** enabled (separate license)
- Access to **Agent builder** and **Evaluate agents** in CDF
- (Optional) Some modeled data to query

<!--
Atlas AI requires a separate license; contact Cognite or use the request form at cognite.com/en/contact. You need to see Atlas AI in the CDF nav and be able to open Agent builder and Evaluate agents. Having assets, equipment, maintenance orders, or time series in your project helps the hands-on parts but isn't required to follow the flow.
-->

---

# Agenda (1/7)

**0:00–0:20** · Atlas AI overview & concepts

<!--
First block: we define what Atlas AI is, language models, knowledge graph, prompts and instructions, tools, and runtime versions. Reference: docs.cognite.com/cdf/atlas_ai and docs.cognite.com/cdf/atlas_ai/concepts.
-->

---

# Agenda (2/7)

**0:20–0:35** · Language models & tools reference

<!--
Quick tour of the language model library (stable, legacy, retired) and the three tool families: query, analysis, and integration. Good moment to open the Language model library and Agent tools docs if people want to skim.
-->

---

# Agenda (3/7)

**0:35–0:55** · Build and publish an agent

<!--
Hands-on block. We follow the Build and publish agents guide: scope, create, configure, prompting, tools, test, publish. Each participant will create or edit one agent and test in the chat preview.
-->

---

# Agenda (4/7)

**0:55–1:15** · Effective prompting

<!--
How to write prompts that get accurate, relevant responses: be specific, add context, define output format. We'll use examples from the prompting guide, including the "with detailed context" section.
-->

---

# Agenda (5/7)

**1:15–1:30** · Evaluations: overview & workflow

**1:30–1:50** · Configure and run evaluations

<!--
Why evaluations matter and how they work (test cases, run, compare). Then we configure an evaluation, add test cases, run it, and view results. Second hands-on: add 2–3 test cases and run against the agent you built.
-->

---

# Agenda (6/7)

**1:50–2:00** · Wrap-up & next steps

<!--
Quick recap and stretch goals: optimize data models for AI search, add custom tools, run evaluations after each change.
-->

---

# What is Atlas AI?

Industrial AI agents that combine:
- GenAI **language models**
- CDF **knowledge graph**
- **Prompts** and **tools**

to solve specific business problems.

<!--
Atlas AI is not a generic chatbot. Agents are configured for specific industrial use cases—e.g. maintenance insights, time series analysis, document Q&A. They use your CDF data and your instructions so responses are contextual and traceable. See docs.cognite.com/cdf/atlas_ai and concepts.
-->

---

# Language models

- **Understand** and **generate** language
- Choose by **speed**, **quality**, and **context length**
- Atlas AI offers multiple models (Azure, GCP, AWS)

<!--
LLMs are the "brain" of the agent. Different models trade off latency vs quality and have different context windows. The Language model library lists stable, legacy, and retired models with release and retirement dates so you can plan upgrades. Link: docs.cognite.com/cdf/atlas_ai/references/atlas_ai_agent_language_models.
-->

---

# Knowledge graph

- CDF **data models** and **core / process-industry** models
- Give agents **context**, **access control**, and **up-to-date** data
- Decisions are **traceable** and **transparent**

<!--
The knowledge graph is why agents can answer with your real data instead of generic text. CDF's data modeling and out-of-the-box models structure the data; the agent queries it. Access control and freshness come from the graph. See Concepts – Knowledge graphs in the Atlas AI concepts doc.
-->

---

# Prompts and instructions

- **Goals** = what to achieve
- **Instructions** = how (workflow, scope, output format)

<!--
When you build an agent, you set goals and instructions. Goals define the outcome; instructions define the process—role, format, constraints, edge cases. Good instructions make prompts from users more effective. Reference: Concepts – Prompts and prompt engineering.
-->

---

# Tools

- **Query:** KG, time series, assets, maintenance orders, files, etc.
- **Analysis:** Answer document questions, summarize, analyze time series
- **Integration:** REST API, Python code, Cognite Functions

<!--
Tools are how the agent acts on the world. Query tools pull from the knowledge graph and time series. Analysis tools work on documents and time series. Integration tools (beta) call APIs or run code. You choose which tools to enable per agent. See Agent tools library.
-->

---

# Runtime versions

- Each agent is **pinned** to a runtime version
- You **control when** to upgrade
- Ensures **stable** behavior for production

<!--
Runtime versions bundle system prompt, agent tools, and features. Pinning avoids surprise changes when Cognite ships updates. When you're ready, you upgrade the agent to a newer runtime. Mention Agent runtime versions in the docs for details.
-->

---

# Language models: stable vs legacy

- **Latest stable** = recommended for new agents
- **Legacy stable** = still supported; migrate when ready
- **Retired** = no longer supported; upgrade before retirement date

<!--
The Language model library table shows release and retirement dates. Use latest stable for new work. If you're on a legacy model, plan a migration to the recommended upgrade. Retired models are auto-upgraded if you don't migrate in time.
-->

---

# Query tools

- Query knowledge graph · Find assets, equipment, time series
- Find maintenance orders, activities, files, notifications, operations
- Query time series data points

<!--
Query tools use CDF query features to retrieve instances from the knowledge graph. You configure data model, view, and access scope (location, user rights, or manual spaces). List is in Agent tools library under Query tools.
-->

---

# Analysis tools

- Answer document questions (semantic search on files)
- Summarize documents
- Analyze time series (preview)
- Examine data semantically (preview)

<!--
Analysis tools work on data you've already retrieved or identified—e.g. files from a query, or time series by ID. Combine with query tools so the agent finds the right assets or files first, then runs analysis. See Agent tools library – Analysis tools.
-->

---

# Integration tools (beta)

- Call REST API (Cognite API endpoints)
- Run Python code
- Call Function (deployed Cognite Functions)

<!--
Integration tools extend agents to external systems and custom logic. Beta means they may change. Useful for workflows that need to trigger actions or call your own APIs. Reference: Agent tools library – Integration tools and the linked Python tool / Call Function pages.
-->

---

# Build and publish: before you start

1. **Scope** your use case
2. **Identify** an evaluation dataset
3. **Choose** a language model

<!--
Before opening the Agent builder, have a clear problem or workflow in mind. Gather sample data or scenarios to test with. Pick a model that fits latency and quality needs. This sets you up for the rest of the steps. See Build and publish agents – Before you start.
-->

---

# Build and publish: create agent

- In CDF: **Atlas AI** → **Agent builder**
- **+ Create agent** or start from a **template**

<!--
Navigate to Atlas AI, then Agent builder. You can create from scratch or use a template. Templates give you a starting point for common industrial use cases. We're in the 0:35–0:55 block; hands-on starts after we cover the steps.
-->

---

# Build and publish: configure basics

- **Name** — clear and descriptive
- **Description** — what problems it solves
- **Sample prompts** — show users how to interact

<!--
Name and description help others find and understand the agent in the Agent library. Sample prompts appear as suggestions in the chat UI so users know what to ask. Make sample prompts specific and representative of real use cases.
-->

---

# Build and publish: set up prompting

- Select **language model**
- Write **instructions**: role, output format, constraints, edge cases

<!--
Instructions are the main lever for quality. Define the agent's role and expertise, how you want answers formatted, and how to handle edge cases or missing data. Clear instructions reduce ambiguity when users type free-form prompts. See Prompts and prompt engineering in the concepts doc.
-->

---

# Build and publish: configure tools

- Add only the **tools you need**
- For data retrieval: set **data model**, **view**, **access scope**

<!--
More tools can mean noisier behavior; enable only what the use case requires. For query tools, you must specify which data model and view to use, and how to scope access: by user location, by user access rights, or by manually selected spaces.
-->

---

# Build and publish: test and refine

- Use the **chat preview** in the builder
- Refine **model**, **instructions**, and **tools** as needed
- Test typical cases, edge cases, and errors

<!--
The chat preview lets you iterate before publishing. Try different phrasings, missing data, and unclear questions. Adjust instructions or tools based on what you see. This is the loop that makes the agent reliable.
-->

---

# Build and publish: publish

- **Publish** to make the agent available in the **Agent library**
- All CDF project users can then run it

<!--
Publishing is the last step in the builder. After that, the agent appears in the Agent library and users can start conversations. You can continue to edit and republish; monitor usage and feedback and iterate. See Build and publish agents – Publish.
-->

---

# Build and publish: hands-on

- Each participant: **create or edit** one agent
- **Test** in the chat preview
- Use the steps we just covered

<!--
Hands-on time. Everyone goes into Agent builder, creates a new agent or edits an existing one, and runs through: name/description/sample prompts, instructions, tools, and chat preview. If you have modeled data, try a real question; otherwise use a sample prompt that doesn't depend on instances.
-->

---

# Effective prompting: config matters

- **Model** choice affects how prompts are interpreted
- **Goals and instructions** set the frame
- **Tools** you enable limit what the agent can do

<!--
Prompting doesn't happen in a vacuum. The agent's configuration—model, instructions, and tools—shapes how user prompts are understood. When improving responses, consider tuning the agent config as well as the prompt. See About prompting Atlas AI agents – How agent configuration affects prompting.
-->

---

# Effective prompting: be specific

- **Vague:** "Tell me about Pump P-101"
- **Specific:** "What is the current operational status of Pump P-101?"
- **Highly specific:** "List all open high-priority work orders for Compressor C-205 in the last 30 days"

<!--
Specific prompts get better results. Use action verbs and include criteria (status, priority, equipment, time range) so the agent knows exactly what to retrieve and present. The prompting guide has a full table of vague vs specific vs highly specific examples.
-->

---

# Effective prompting: provide context

- **Equipment**, **sensor**, **time range**
- Example: "Temperature trend for Reactor R-301, sensor TI-301A, past 7 days"
- With **detailed context**: "Considering recent maintenance on HE-502, any anomalous pressure readings in connected lines in the past 48 hours?"

<!--
Context narrows the scope so the agent doesn't search irrelevant data. Basic context is who/what/when; detailed context adds operational story (e.g. recent maintenance) so the agent can distinguish expected vs anomalous behavior. See the "With detailed context" tab in the prompting guide.
-->

---

# Effective prompting: define output

- **Format:** bullets, table, narrative
- **Level of detail** and **precision**
- Example: "List work orders in a table: ID, status, description, date"

<!--
Tell the agent how you want the answer structured. Requesting a table with specific columns, or max/min values for a date, or a bulleted summary, reduces back-and-forth and makes responses easier to use. The prompting guide has examples under "Define the desired output."
-->

---

# Effective prompting: understand responses

- Use the **reasoning** field to see how the agent decided
- Review **tool calls** (inputs and outputs) to see what was queried
- Refine **prompts** or **agent config** when results don't match intent

<!--
When the agent's response is wrong or surprising, the reasoning and tool calls show why. Check if the right tools were used with the right parameters, and whether the instructions are being followed. Use that to adjust either the user prompt or the agent's instructions and tools. See About prompting Atlas AI agents – Understanding agent responses.
-->

---

# Evaluations: purpose

- Test how agents respond to **specific prompts**
- **Measure** performance and **verify** behavior
- Find where to improve

<!--
Evaluations are regression and quality checks. You define test cases (prompt + expected response), run them against the agent, and compare results. Use them before deployment, after config changes, and over time to track quality. See About AI agent evaluations.
-->

---

# Evaluations: how they work

- **Test case** = prompt + expected response
- **Run** → agent responds → **compare** to expected → **view results**

<!--
You create an evaluation with a name and description, then add test cases. Each test case has a prompt and what you expect the response to include. When you run the evaluation, the agent answers each prompt and Atlas AI compares to your expected response. Results show pass/fail and let you drill into details. See the evaluation overview diagram and workflow.
-->

---

# Evaluations: why run them

- **Regression** — still works after changes
- **Before deployment** — verify behavior
- **Document** expected behavior
- **Track** performance over time

<!--
Run evaluations after updating instructions, adding tools, or changing the model. Run before publishing a new version so you don't ship regressions. Test cases also serve as living documentation of how the agent should behave. Over time, trends in results help you prioritize improvements. See About AI agent evaluations – Why evaluations matter.
-->

---

# Configure evaluation: create

- **Atlas AI** → **Evaluate agents** → **+ Create new evaluation**
- Enter **name** and **description**

<!--
Navigate to Atlas AI, then Evaluate agents. Create a new evaluation and give it a descriptive name (e.g. "Pump maintenance agent – v1") and a short description of what you're testing. See Evaluate Atlas AI agents – Configure evaluation.
-->

---

# Configure evaluation: test cases

- For each case: **Prompt** + **Expected response**
- Optional: use **Generate answer** (from an agent) to draft the expected response
- Be **specific** about what should be included (status, metrics, etc.)

<!--
Add test cases one by one. The prompt is what the user would ask; the expected response defines what a good answer contains. You can have an agent generate a draft expected response and then edit it. The more specific you are about required details, the more useful the comparison. See Evaluate Atlas AI agents – Define test cases.
-->

---

# Run evaluation: execute

- **Evaluation overview** → **Run evaluation**
- **Select** your agent → **Run with selected agent**
- If prompted, **Confirm** code tool access
- **Do not close** the browser tab while it runs

<!--
From the evaluation overview, start a run and pick the agent to test. If the agent uses code tools, you'll be asked to confirm. Evaluations run in the browser, so closing or navigating away will stop them. You can cancel the run if needed. See Evaluate Atlas AI agents – Run and monitor evaluation.
-->

---

# Run evaluation: view results

- **Completed** runs appear in the overview
- Open a run to see **test case status**
- **View details** to compare agent response vs expected response

<!--
After the run finishes, open it to see which test cases passed or failed. Use "View details" to see the actual vs expected response and the agent's reasoning/tool calls. Use these insights to refine instructions, tools, or test cases. See Evaluate Atlas AI agents – View and analyze results.
-->

---

# Evaluations: hands-on

- Add **2–3 test cases** to your evaluation
- **Run** it against the agent you built earlier
- **Review** results and one or two "View details"

<!--
Second hands-on. Everyone adds a few test cases (prompt + expected response), runs the evaluation against their agent, and looks at the results. Try at least one case you expect to pass and one edge case. Use the comparison view to see how the agent answered and where it diverged from expected.
-->

---

# Key concepts (cheat sheet)

| Concept | Summary |
|--------|---------|
| **Agent** | GenAI + instructions + tools + knowledge graph |
| **Instructions** | What to accomplish + how (role, format, constraints) |
| **Tools** | Query, analysis, integration |
| **Prompting** | Specific + context + output format |
| **Evaluation** | Test cases → run → compare → improve |

<!--
Quick recap. Agent is the full stack: model, instructions, tools, and data. Instructions are the main config for behavior. Tools are what the agent can do. Good prompting is specific, contextual, and format-conscious. Evaluations lock in expected behavior and catch regressions. You can share this slide or the agenda doc as a one-pager.
-->

---

# Wrap-up

- **Agent** = model + instructions + tools + knowledge graph
- **Prompting** = specific + context + output format
- **Evaluations** = test cases + run + compare

<!--
We've covered the full loop: build an agent with clear instructions and the right tools, prompt it with specificity and context, and validate with evaluations. Keep refining instructions and test cases based on real usage and evaluation results.
-->

---

# Next steps (stretch)

- Optimize **data models** for AI search
- Add **custom tools** (e.g. Python, Functions)
- Run **evaluations** after each change

<!--
Stretch goals: make your data model agent-friendly (see Optimizing data models for AI search in the docs), extend with custom tools, and make evaluations part of your change process so you always know when something breaks.
-->

---

# Documentation quick links

- [Atlas AI](https://docs.cognite.com/cdf/atlas_ai) · [Concepts](https://docs.cognite.com/cdf/atlas_ai/concepts)
- [Build and publish agents](https://docs.cognite.com/cdf/atlas_ai/guides/atlas_ai_agent_building) · [Prompting](https://docs.cognite.com/cdf/atlas_ai/guides/atlas_ai_agent_prompting)
- [Language models](https://docs.cognite.com/cdf/atlas_ai/references/atlas_ai_agent_language_models) · [Agent tools](https://docs.cognite.com/cdf/atlas_ai/references/atlas_ai_agent_tools)
- [Evaluation overview](https://docs.cognite.com/cdf/atlas_ai/concepts/atlas_ai_agent_evaluation_overview) · [Evaluate agents](https://docs.cognite.com/cdf/atlas_ai/guides/atlas_ai_agent_evaluating)

<!--
All eight docs we used today. Good for Q&A and for participants to bookmark. The training agenda in docs/atlas-ai-training-agenda.md has the same links plus the full table and optional adjustments. Thank the group and open for questions.
-->
