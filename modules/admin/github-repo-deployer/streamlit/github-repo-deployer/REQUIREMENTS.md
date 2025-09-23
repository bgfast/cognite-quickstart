## GitHub Repo Deployer - UI/Flow Requirements

This document baselines the expected behavior and structure of the Streamlit app so we can refactor to a predictable, non-flickering workflow.

### 1) Global Rules
- There is a single source of truth for the current step: `st.session_state['workflow_step']` in {1..5}.
- Step tabs are clickable navigation:
  - Clicking a completed step moves to that step.
  - Clicking the current step does nothing.
  - Future steps are disabled until prerequisites are satisfied.
- Only content for the currently selected step is rendered. No cross-step content should appear.
- State required by later steps is stored in `st.session_state` (e.g., `extracted_path`, `config_files`, `selected_config`, `selected_env`, `env_vars_loaded`).
- Use `st.rerun()` only when changing steps or after finishes of long operations (download/extract/build/deploy) to reveal the next step.

### 2) Steps
1. Step 1: Download & Environment
   - Show Environment Configuration only in Step 1.
   - Load `.env` (from uploaded file or repo path), show debug availability, but do not request manual inputs.
   - Download repo (or accept ZIP upload), extract, set `st.session_state['extracted_path']`.
   - Discover `config.*.yaml` and store list in `st.session_state['config_files']`.
   - When complete, auto-advance to Step 2.

2. Step 2: Select Configuration
   - Render tabs, one per `config.*.yaml` file; show associated README if present.
   - Selecting a config sets `st.session_state['selected_config']` and `st.session_state['selected_env']`.
   - Continue button advances to Step 3. Back button returns to Step 1.

3. Step 3: Build
   - Build with Toolkit-first approach (`cdf build --env all`) or compatible fallback.
   - Show build log/output within this step only.
   - On success, advance to Step 4.

4. Step 4: Deploy
   - Deploy with `cdf deploy --env all` (Toolkit-first) or fallback.
   - Show deploy summary within this step only.
   - On success, advance to Step 5.

5. Step 5: Verify
   - Summarize results (selected config, env, versions, success status).
   - Offer "Start New Deployment" to reset state and return to Step 1.

### 3) Architecture & Refactor Plan
- Extract per-step renderers:
  - `render_step_1()` – environment, download, extract, discovery
  - `render_step_2()` – config selection + README tabs
  - `render_step_3()` – build
  - `render_step_4()` – deploy
  - `render_step_5()` – verify
- `main()` should:
  1) Render step-tabs header (clickable) 
  2) `if step == n: render_step_n()` exclusively
- Eliminate any UI outside these functions that belongs to steps (e.g., the current `Environment Configuration` header outside the step gate).

### 4) Non-Functional
- Minimize UI flicker: prefer containers and forms; only rerun on step change or long op completion.
- Persist critical state in `st.session_state`; avoid recomputation when navigating back to earlier steps.
- Keep verbose debug only when `debug_mode` is true.

### 5) Acceptance Criteria
- Switching steps shows no content leakage from other steps.
- Uploading `.env` and downloading/extracting repo occur only in Step 1.
- Config selection UI is visible only in Step 2.
- Build logs are confined to Step 3; deploy summary to Step 4; verification to Step 5.
- Tabs at the top reliably navigate between completed steps.


