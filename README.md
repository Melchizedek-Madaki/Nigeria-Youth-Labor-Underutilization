# Nigeria Youth Labor Underutilization

**Youth Labour Explorer** is an interactive Streamlit app exploring unemployment, insufficient working hours, unpaid work, and low pay among Nigerians aged **15–34**.

## What you can explore

- **Try a prediction:** enter background details to see the saved model's predicted employment group.
- **Pay & work conditions:** explore pay, occupations, industries and workplaces, and see what an hours-only measure misses.
- **Explore the data:** compare employment-class shares with or without survey weights.
- **Model performance:** inspect model comparisons, errors, and predictor importance.
- **How it works:** understand the research definitions and limitations.

The pay page includes a rule-based pay-and-hours assessment. It explains the project's labels separately from the machine-learning prediction.

## Data and model

The project uses NBS Nigeria Labour Force Survey quarters **Q3 2024, Q1 2025 and Q2 2025**: 38,792 youth records before exclusions and 27,358 in the cleaned modelling sample. Q4 2024 is excluded because the source notebook reports an unreadable file.

The model uses age, sex, education, state, urban/rural residence, and quarter. It excludes hours, pay, job-search answers and identifiers from its inputs. Models were compared using a household-grouped train/test split, with additional robustness and later-quarter validation.

The selected random forest scored **60.3% accuracy**, **61.0% balanced accuracy**, and **0.513 macro-F1** in the completed local run. Scores are exploratory: the model comparison also informs selection. See the performance page for detailed results.

## Run locally

Use **Python 3.13** to match the environment used for the saved model.

Windows PowerShell or Git Bash:

```bash
py -3.13 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m streamlit run streamlit_app.py
```

On macOS/Linux:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run streamlit_app.py
```

Open the URL printed in the terminal, normally [localhost:8501](http://localhost:8501). Keep the terminal open; **Ctrl+C** stops the server. After setup on Windows, you can also double-click **Run Explorer.bat**.

**No survey download, notebook execution, or model training is needed to run this repository.** Required runtime files are already in `artifacts/`. Only load model files from a trusted source.

## Repository contents

| File | Purpose |
| --- | --- |
| `streamlit_app.py` | App entry point and navigation. |
| `aggregate_work_ui.py` | Aggregate-based pay/work explorer. |
| `work_rules.py` | Classification rules and helper functions. |
| `artifacts/` | Saved trained model, metadata, aggregate summaries and evaluation tables. |
| `requirements.txt` | Runtime versions matching the completed local run. |
| `Run Explorer.bat` | Windows launcher after environment setup. |
| `DEPLOYMENT.md` | Hosting instructions and aggregate preparation notes. |

Research notebooks, training scripts, survey files and respondent-level exports stay in the separate research workspace. This repository is the curated runtime application.

## Definitions and interpretation

- **Unemployed:** no recorded main job, actively searching, and available to start.
- **Underemployed:** has a recorded job and meets a confirmed hours, unpaid-work or low-pay condition.
- **Adequately employed:** has a recorded job, meets none of those confirmed conditions, and has no unresolved pay classification.

The hours condition requires fewer than 40 usual weekly hours, wanting more hours, and availability for them. Low pay means reviewed monthly earnings below two-thirds of the quarter's unweighted median among paid youth. That research threshold is not a minimum wage or poverty line.

**This is a project-defined underemployment measure, broader than official NBS time-related underemployment.** Earnings bands and pay-period conversions introduce approximations. Unknown pay is not treated as zero. Predictions are associations, not measured personal work status or salary estimates. Do not use them for individual hiring, benefit or credit decisions.

## Aggregate data and disclosure limits

This repository contains **no original Stata files or respondent-level CSVs**. Group statistics are precomputed locally. The app supports one focus dimension at a time instead of arbitrary narrow filter combinations.

Groups generally require 30 respondents; small indicator cells and some companion values are withheld. Counts are rounded to five, pay medians to ₦500, and percentages/hours to one decimal. Medians were computed directly for each released group, never averaged from subgroup medians. Displayed groups or percentages may not total 100% after withholding and rounding.

These measures reduce disclosure risk; they are not a formal anonymisation guarantee. NBS and dataset-specific publication terms still apply. The model is intended for learning and research, not causal conclusions or individual decisions. Survey weights only partly account for the sampling design.

## Deploy on Streamlit Community Cloud

Connect this GitHub repository, select its actual branch and **`streamlit_app.py`**, and choose **Python 3.13** in advanced settings. The root `requirements.txt` installs runtime packages. No application secrets or training step are currently required. Check the hosted app after deployment; a local check is not a Linux/cloud installation test.

See the [official deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) and [DEPLOYMENT.md](DEPLOYMENT.md).

## Troubleshooting

- **Model load error:** match Python and package versions in `requirements.txt`.
- **Missing artifacts:** restore the tracked `artifacts/` files from this repository.
- **Port occupied:** append `--server.port 8502` to the run command.
- **Memory error:** close unused applications and run one app instance at a time.
- **Old styling:** refresh the page or choose Streamlit's **Rerun**.

## Attribution and licence

Source: **National Bureau of Statistics, Nigeria Labour Force Survey**, Q3 2024, Q1 2025 and Q2 2025. NBS and the original data collectors do not endorse this app or its interpretations.

No software licence has been selected yet; do not assume an open-source licence. Code licensing is separate from the terms governing source data and derived outputs.

- [NBS Microdata Catalogue](https://microdata.nigerianstat.gov.ng/)
- [NBS terms and conditions](https://nigerianstat.gov.ng/page/terms)
- [NBS NLFS FAQ](https://nigerianstat.gov.ng/page/nlfs-faq)
