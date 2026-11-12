# Research notebook

This folder contains the research code behind **Nigeria Youth Labor Underutilization**:

**[Nigeria_Youth_Labour_Underutilisation_G1.backup.ipynb](Nigeria_Youth_Labour_Underutilisation_G1.backup.ipynb)**

## About this copy

The notebook was taken from the original G1 **backup** file requested by the project owner. All **279 cells**, their order, code, and markdown source are preserved. Saved cell outputs, execution counts, attachments and execution/editor metadata have been cleared for publication. Some original outputs displayed individual survey records and identifiers, so publishing the executed file unchanged would expose respondent data.

The original backup remains unchanged in the private research workspace. This public file is a source-only copy; the `.backup.ipynb` filename identifies which source version it came from, not an additional executed backup in this repository.

## What the notebook covers

1. Problem statement and research questions.
2. NLFS data loading, age/sample filtering, and cleaning.
3. Construction of unemployment, project-defined underemployment, and adequate-employment labels.
4. Earnings harmonisation, low-pay thresholds, and employment-screening investigations.
5. Descriptive analysis and weighted comparisons.
6. Household-grouped splitting, preprocessing, and model comparison.
7. Feature importance, odds ratios, sensitivity checks, and later-quarter validation.
8. Findings, recommendations, limitations, and references.

The modelling population is Nigerian youth aged 15–34. The project combines hours shortfalls, unpaid work and low pay in its underemployment definition; this is broader than the official NBS time-related measure.

## Read or run it

GitHub can display the notebook for reading. For execution, open it in a notebook editor such as VS Code/Jupyter or its intended Google Colab environment.

This is the **original Colab-oriented research code**, not the local runner used to prepare the deployed app. Its first loading cell uses `google.colab.files`, `/content/NLFS_Dataset`, and a ZIP-upload workflow. Running locally requires adapting that loading step in a working copy; the published source has deliberately not been rewritten.

The three training files expected are:

```text
nlfs_2024q3_indiv.dta
nlfs_2025q1_indiv.dta
nlfs_2025q2_indiv.dta
```

Obtain these through NBS under the applicable terms. **They are not provided in this repository.** Q4 2024 is excluded by the research workflow because its source file was reported unreadable.

The notebook uses pandas, NumPy, scikit-learn, matplotlib, seaborn, pyreadstat and joblib. The repository-root `requirements.txt` records the deployed app's runtime versions, not a complete notebook development environment. Add a notebook kernel/editor and the additional research packages as needed. The app's saved pipeline was produced in Python 3.13; the public notebook's original execution metadata has been cleared rather than presented as a reproducible environment specification.

Run cells in order because later cells depend on variables created earlier. Execution can take several minutes and needs enough memory to load and process the survey files. Some markdown cells reference local `IMAGES/` illustrations; those images are not bundled here, and the written explanations remain available.

## Relationship to the deployed app

The app loads a saved model and precomputed aggregate summaries. It does not execute this notebook, retrain, or read survey records at startup. Adding this folder does not change the app's entry point or behaviour.

- [Live app](https://nigeria-youth-labor-underutilization-zrpvsbfkpsrqf8h2uefjqr.streamlit.app/)
- [Main project README](../README.md)
- [Deployment notes](../DEPLOYMENT.md)

## Data use and attribution

Source: **National Bureau of Statistics, Nigeria Labour Force Survey**, Q3 2024, Q1 2025 and Q2 2025. Research interpretations are the project's, not an endorsement by NBS.

Follow [NBS terms](https://nigerianstat.gov.ng/page/terms) and the dataset-specific access/publication terms. Keep newly generated respondent outputs, executed notebooks containing records, and source datasets out of public commits. Re-clear outputs before publishing changes to this notebook.
