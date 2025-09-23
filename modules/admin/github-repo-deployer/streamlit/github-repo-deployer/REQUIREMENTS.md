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
   - Load environment variables (from uploaded file or repo path), show debug availability, but do not request manual inputs.
   - **File Upload Requirements:**
     - Accept ALL file types for environment file uploads (no file type restrictions)
     - Support .env, .txt, .config, or any text file containing environment variables
     - Parse files with KEY=VALUE format regardless of file extension
   - accept a repo url - use this as default: https://github.com/bgfast/cognite-quickstart
   - Use gh api to download all files in the repo. The zip download does not work because of cors issues. 
   - future requirement - connect to a private repo 
   - future requirement - download a zip from the current cdf project
   - Download repo 
   - extract, set `st.session_state['extracted_path']`.
   - Discover `config.*.yaml` and store list in `st.session_state['config_files']`.
   - provide a download button
   - show logging information from download
   - When complete, enable Step 2.

2. Step 2: Select Configuration
   - Render sub-tabs, one per `config.*.yaml` file; show associated README if present.
   - Selecting a config sets `st.session_state['selected_config']` and `st.session_state['selected_env']`.
   - step 3 is always enabled because no action is required on step 2. one is selected by default. the user can change it if they want but are not required to

3. Step 3: Build and Deploy
   - show the name of the selected config
   - use the toolkit libraries to build and deploy.
   - Show build detailed log/output within this step only.
   - Show deploy detailed logs within this step only.
   - On success, advance to Step 5.

future 4. Step 4: Verify
   - Run each of the verify tests from each module.
   - Summarize results (selected config, env, versions, success status).
   - Offer "Start New Deployment" to reset state and return to Step 1.

### 3) Architecture & Refactor Plan
- `main()` should:
  1) Render step-tabs header (clickable) 
  2) `if step == n: render_step_n()` exclusively
- Eliminate any UI outside these functions that belongs to steps (e.g., the current `Environment Configuration` header outside the step gate).

### 4) Non-Functional
- Minimize UI flicker: prefer containers and forms; only rerun on step change or long op completion.
- Persist critical state in `st.session_state`; avoid recomputation when navigating back to earlier steps.
- use verbose debug=true during development

### 5) Acceptance Criteria
- Switching steps shows no content leakage from other steps.
- Uploading environment files (any file type) and downloading/extracting repo occur only in Step 1.
- **File Upload Acceptance:**
  - File uploader accepts ALL file types without restrictions
  - Environment files with any extension (.env, .txt, .config, etc.) are accepted
  - Files are parsed correctly regardless of file extension
- Config selection UI is visible only in Step 2.
- Build logs are confined to Step 3; deploy summary to Step 4; verification to Step 5.
- Tabs at the top reliably navigate between completed steps.


