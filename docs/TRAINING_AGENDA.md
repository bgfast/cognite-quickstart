# Cognite Quickstart Training — 2-Hour Agenda

**Audience:** Developers using Cursor or GitHub Copilot with the Cognite Toolkit  
**Format:** Single 2-hour session  
**Repo:** [cognite-quickstart](.) (this project)

---

## Goal

Get the Hello World demo set running in your CDF project, walk through NEAT data modeling and two Streamlit patterns (HW and EDR/time series), then use Cursor/Copilot to ideate and generate a new Streamlit app that follows the project’s repeatable deployment patterns.

**Deliverable:** All Hello World modules deployed and verified; a new use-case idea and a Cursor/Copilot-generated Streamlit app scaffold that builds and deploys with the Cognite Toolkit.

---

## Agenda

| Time   | Topic | Details |
|--------|--------|--------|
| **0:00–0:15** | Intro & prerequisites | • What this quickstart is: Functions, NEAT, and Streamlit demos deployable with the Cognite Toolkit<br>• Ensure everyone has: CDF project access, IDP credentials (client ID/secret, token URL), Function and Streamlit deploy permissions<br>• Point to `README.md`, `readme.hw-all.md`, and `config.all-hw.yaml` |
| **0:15–0:35** | Environment setup | • Clone this repo and open in Cursor (or IDE with Copilot)<br>• Create env: copy `cdfenv.sh` → `cdfenv.local.sh` (or use `~/envs/…`); set `CDF_PROJECT`, `CDF_CLUSTER`, `IDP_*`, `FUNCTION_CLIENT_ID`/`FUNCTION_CLIENT_SECRET`, `TRANSFORMATION_CLIENT_*`, `USER_IDENTIFIER`, `SUPERUSER_SOURCEID_ENV`<br>• Build & deploy: `cdf build --env=all-hw` then `cdf deploy --env=all-hw --dry-run` and `cdf deploy --env=all-hw`<br>• Verify in CDF UI: Functions, Streamlit apps, and NEAT space/containers exist |
| **0:35–0:55** | NEAT (hw-neat) | • Purpose: Excel-based data model → CDF via NEAT and toolkit<br>• Open `modules/hw-neat/data_models/HWNeatBasic.xlsx` — source of truth for space, container, view<br>• Run `python generate_cdf_dm_yaml_files_via_neat.py` from `modules/hw-neat` to generate YAML under `data_models/data_models/`<br>• Redeploy if needed: `cdf build --env=hw-neat` and `cdf deploy --env=hw-neat`<br>• In CDF: open the **hw-neat** Streamlit app; create/read/update/delete instances (CRUD) to see the NEAT model in action |
| **0:55–1:15** | HW Streamlit demos | • **hw-function**: Open the Hello World Function Streamlit app in CDF; trigger the function from the UI and see request/response and logs — reinforces Function + Streamlit pattern<br>• **hw-neat**: Recap the NEAT Streamlit app as the second “HW” pattern: dataset, `*.Streamlit.yaml`, `streamlit/<app-name>/main.py` and `requirements.txt`<br>• Point out layout: `modules/<module>/streamlit/<app-name>.Streamlit.yaml`, `streamlit/<app-name>/`, and `data_sets/*.DataSet.yaml` for repeatable deployment |
| **1:15–1:35** | EDR Streamlit (hw-timeseries-streamlit) | • **hw-timeseries-streamlit** reads CDF time series (e.g. `edr_training_*`)<br>• Populate sample time series: `python scripts/populate_edr_timeseries.py` (from repo root; requires env and CDF credentials)<br>• Open the Time Series Streamlit app in CDF; select/filter time series and view charts<br>• Short code tour: `modules/hw-timeseries-streamlit/streamlit/hw-timeseries-streamlit/main.py` and `utils/cdf_data.py` — how it uses the Cognite client and follows the same module/streamlit layout |
| **1:35–2:00** | Exercise: New use case + Cursor/Copilot Streamlit | • **Ideate (5 min):** Each person/pair picks a simple new use case (e.g. “list and preview Files,” “simple asset tree browser,” “form that writes to a NEAT container,” “dashboard of one time series”)<br>• **Generate with Cursor/Copilot (15–20 min):** In this repo, create a **new module** (e.g. `modules/my-demo/`) that follows toolkit repeatable deployment:<br>  – `module.toml`<br>  – `data_sets/<name>-dataset.DataSet.yaml`<br>  – `streamlit/<app-name>.Streamlit.yaml`<br>  – `streamlit/<app-name>/main.py` and `requirements.txt`<br>  – Add the module to a config (e.g. new `config.my-demo.yaml` with `selected: [modules/my-demo]` and needed variables)<br>• Prompt Cursor/Copilot with: “Add a new Streamlit app that [use case]. Follow the structure of `modules/hw-timeseries-streamlit` and `modules/hw-neat/streamlit`: same YAML layout, dataset, and use the Cognite client from env.”<br>• **Build & verify (5–10 min):** `cdf build --env=my-demo` and `cdf deploy --env=my-demo --dry-run` then deploy; open the new app in CDF and confirm it runs |

---

## Repeatable deployment patterns (for the exercise)

New Streamlit apps in this project should follow:

1. **Module under `modules/<module-name>/`**  
   `module.toml`; optional `data_sets/`, `data_models/`, etc.

2. **Streamlit layout**  
   - `streamlit/<app-name>.Streamlit.yaml` — app definition (name, dataset, entrypoint).  
   - `streamlit/<app-name>/main.py` — entrypoint.  
   - `streamlit/<app-name>/requirements.txt` — Python deps.

3. **Config**  
   - A `config.<env>.yaml` with `environment` and `selected: [modules/<module-name>]`.  
   - Any variables (e.g. space, dataset names) used in the module.

4. **Deploy**  
   - `cdf build --env=<env>` and `cdf deploy --env=<env>` (use `--env`, not `--config`).

Reference modules: `hw-neat` (NEAT + Streamlit), `hw-timeseries-streamlit` (time series Streamlit), `hw-function` (Function + Streamlit).

---

## Materials to have ready

- **Repo:** This project cloned and open in Cursor (or IDE with Copilot).
- **Docs:** `README.md`, `readme.hw-all.md`, `readme.hw-neat.md`, `docs/requirements.hw.md` (checklist).
- **CDF:** Project, IDP and Function credentials, and access to deploy Streamlit apps and data models.
- **Cursor or Copilot:** Enabled in the IDE for the exercise.
- **Many people deploying the same app:** See [One app per person (many trainees)](#one-app-per-person-many-trainees) below.

---

## One app per person (many trainees)

When many people (e.g. 20) each clone the repo and deploy the **hw-dm-crud-streamlit** app, they would all deploy to the same app in CDF (`externalId: hw-dm-crud-streamlit`) and overwrite each other. To give each person their own app in CDF (e.g. `hw-dm-crud-streamlit-jag`, `hw-dm-crud-streamlit-alice`):

**Per person (once):** From repo root, run with a **unique suffix** (e.g. first name or `user-01` … `user-20`):

```bash
python scripts/setup_personal_hw_crud_app.py <suffix>
```

**What the script does:** Creates a new **module** `modules/hw-dm-crud-streamlit-<suffix>/` (with module.toml, data_sets, and Streamlit app copied from the base) and a **config** `config.hw-dm-crud-streamlit-<suffix>.yaml` that selects both `modules/hw-dm-crud-streamlit` (shared base) and `modules/hw-dm-crud-streamlit-<suffix>` (personal app). The base module is not modified.

**Suffix rules:** Lowercase letters, numbers, or hyphens (e.g. `jag`, `alice`, `user-01`). Each person must use a different suffix.

**After running:** Build and deploy with the new config: `cdf build --env hw-dm-crud-streamlit-<suffix>`, `cdf deploy --env hw-dm-crud-streamlit-<suffix>`. In CDF, **use “Hello World CRUD (&lt;suffix&gt;)”** so you don’t overwrite others’ work on the shared default.

**Instructors:** Before the session, have everyone pick (or assign) a unique suffix. To switch suffix later, remove `modules/hw-dm-crud-streamlit-<old>/` and `config.hw-dm-crud-streamlit-<old>.yaml`, then run the script again with the new suffix.

---

## Optional adjustments

- **If the group is new to CDF:** Add 10–15 min at the start for a short “Tour of CDF: projects, datasets, Functions, Streamlit apps, data models.”
- **If setup is slow:** Do “deploy all” as a single group and skip individual `--env=hw-neat` redeploy; focus NEAT on “view Excel → generate YAML → use Streamlit app.”
- **If time is short:** Reduce the EDR section to “run `populate_edr_timeseries.py`, open the app, and skim the code”; use the saved time for the Cursor/Copilot exercise.
- **Multiple new apps:** If several pairs build different use cases, reserve the last 5–10 min for brief sharebacks: use case, one prompt that worked, and what they had to fix in the generated code.

---

## Stretch goals (post-session)

- Add a **Cognite Function** that the new Streamlit app calls (mirror `hw-function`).
- Store or read data from a **NEAT container** in the new app (mirror `hw-neat`).
- Add **tests** (e.g. `scripts/` or module-level) that run the app or validate CDF resources.
- Document the new module in a short `readme.<module>.md` and add it to the main `README.md` “Other configurations” or “Documentation” section.
