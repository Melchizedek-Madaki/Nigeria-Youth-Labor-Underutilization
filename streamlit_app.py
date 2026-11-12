"""Beginner-friendly explorer for the G1 notebook's trained pipeline."""
from pathlib import Path
import json
import os
for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"
import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "artifacts"
LABELS = {0: "Unemployed", 1: "Underemployed", 2: "Adequately employed"}
QUARTERS = {"2024q3": "Q3 2024", "2025q1": "Q1 2025", "2025q2": "Q2 2025"}
FIELDS = {"dc3": "Sex", "education_level": "Education", "id2_state": "State",
          "id5_sector": "Place of residence", "quarter": "Survey quarter"}

st.set_page_config(page_title="Youth Labour Explorer", page_icon="🌿", layout="wide")
st.markdown("""<style>
.stApp {background: #f4f6f2;color:#223e36;}
.block-container {max-width:1380px;padding-top:2rem;}
h1,h2,h3 {color:#164c41;letter-spacing:-.025em;}
div[data-testid="stMetric"] {background:#fffef9;padding:20px;border-radius:16px;border:1px solid #e0e6dc;box-shadow:0 5px 18px #183d3010;}
div[data-testid="stMetricLabel"] {color:#607267;}
div[data-testid="stMetricValue"] {color:#164c41;}
section[data-testid="stSidebar"] {background:#e7ede4;border-right:1px solid #d5dfd2;}
/* Explicit sidebar contrast also applies when Streamlit uses its dark theme. */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] * {color:#183f34 !important;}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {color:#485d50 !important;}
.hero {background:linear-gradient(115deg,#103f36,#226b56);color:white;padding:34px 38px;border-radius:22px;margin-bottom:28px;border-bottom:5px solid #d8ad62;}
.hero h1 {color:#fffef7;margin:8px 0;font-size:2.8rem;font-weight:750;}
.hero small {color:#e3c68d;letter-spacing:.16em;font-weight:700;}
.hero p {color:#e0eee4;margin-bottom:0;max-width:760px;font-size:1.05rem;}
div[data-testid="stForm"] {background:#fffef9;border:1px solid #dce4d8;border-radius:18px;padding:24px;}
button[kind="primary"] {background:#1d6a54;border:0;border-radius:10px;}
div[data-testid="stTabs"] {margin-top:14px;}
@media(max-width:640px){.hero{padding:24px}.hero h1{font-size:2rem}}
</style>""", unsafe_allow_html=True)
st.markdown('<div class="hero"><small>NIGERIA · AGES 15–34</small><h1>Youth Labour Explorer</h1>'
            '<p>Look beyond having a job. Explore pay, working hours and the quality of youth employment.</p></div>',
            unsafe_allow_html=True)

with st.sidebar:
    st.title("🌿 Labour Explorer")
    page = st.radio("Choose a page", ["Try a prediction", "Pay & work conditions", "Explore the data", "Model performance", "How it works"])
    st.caption("Based on the G1 research notebook. Survey periods: Q3 2024, Q1 2025 and Q2 2025.")

required = ["ui_metadata.json", "youth_labour_underutilisation_model.joblib",
            "class_summaries.json", "model_comparison.csv", "confusion_matrix.csv", "work_summaries.json"]
missing = [name for name in required if not (OUT / name).is_file()]
if missing:
    st.info("The deployment artifacts are incomplete. Please restore the saved model and aggregate summaries.")
    with st.expander("Missing artifacts"):
        st.write(", ".join(missing))
    st.stop()

@st.cache_resource
def load_model(stamp):
    return joblib.load(OUT / "youth_labour_underutilisation_model.joblib")

@st.cache_data
def load_data(stamp):
    return json.loads((OUT / "class_summaries.json").read_text(encoding="utf-8"))["quarters"]

try:
    meta = json.loads((OUT / "ui_metadata.json").read_text(encoding="utf-8"))
    if page == "Try a prediction":
        model = load_model((OUT / required[1]).stat().st_mtime_ns)
    if page == "Explore the data":
        data = load_data((OUT / required[2]).stat().st_mtime_ns)
except Exception as error:
    st.error("The deployment artifacts could not be loaded. Please restore a matching model and summary bundle.")
    with st.expander("Technical details"):
        st.exception(error)
    st.stop()

if page == "Try a prediction":
    st.subheader("What might the model predict for this profile?")
    st.write("Choose a few background details. The model estimates which employment group resembles "
             "this profile in the survey; it does not ask about actual earnings or working hours.")
    with st.form("profile"):
        left, right = st.columns(2)
        values = {"dc5": float(left.number_input("Age", min_value=15, max_value=34, value=24))}
        for i, (field, label) in enumerate(FIELDS.items()):
            with (left if i % 2 else right):
                values[field] = st.selectbox(label, meta["choices"][field],
                    format_func=lambda v, f=field: QUARTERS.get(v, v) if f == "quarter" else v)
        submitted = st.form_submit_button("Show prediction", type="primary", width="stretch")
    if submitted:
        row = pd.DataFrame([values], columns=meta["features"])
        prediction = int(model.predict(row)[0])
        probabilities = model.predict_proba(row)[0]
        st.success(f"Predicted group: {LABELS[prediction]}")
        probs = pd.DataFrame({"Employment group": [LABELS[int(c)] for c in model.classes_],
                              "Model probability (%)": probabilities * 100})
        st.bar_chart(probs, x="Employment group", y="Model probability (%)", color="#2a9d8f")
        st.caption("These are model probability estimates, not a guarantee or a measured personal employment status. "
                   "Class balancing and survey weights can affect their calibration.")
        st.write({0: "The model associates this background profile most strongly with the unemployed group.",
                  1: "In this project, underemployment includes insufficient hours, unpaid work or low pay.",
                  2: "This group contains workers who meet none of the project's confirmed underemployment conditions."}[prediction])
        st.caption("For actual survey pay, occupations and workplace conditions, choose Pay & work conditions in the sidebar. "
                   "The model predicts a class; it does not estimate this person's salary or occupation.")
    st.info("Use this as a learning tool. Background characteristics alone cannot establish a person's actual employment status.")

elif page == "Pay & work conditions":
    from aggregate_work_ui import render
    render(ROOT, QUARTERS)

elif page == "Explore the data":
    st.subheader("Explore the model's study sample")
    st.caption("These charts describe the cleaned model sample, after exclusions. They are not official national rates.")
    a, b, c = st.columns(3)
    a.metric("Youth records before exclusions", f"{meta['youth_records']:,}")
    b.metric("Records used for modelling", f"{meta['model_records']:,}")
    c.metric("Unresolved screening records", f"{meta['screening_unresolved']:,}")
    q = st.selectbox("Survey quarter", list(QUARTERS), format_func=QUARTERS.get)
    weighted = st.toggle("Use survey weights", value=True)
    group = st.selectbox("Compare by", ["Overall", "Sex", "Education", "State", "Place of residence"])
    mode = "weighted" if weighted else "unweighted"
    rows = data[q][group]
    published = [row for row in rows if not row["suppressed"]]
    if group == "Overall":
        chart = pd.DataFrame({"Share (%)": published[0][mode]}, index=list(LABELS.values())) if published else pd.DataFrame()
    else:
        chart = pd.DataFrame([row[mode] for row in published], index=[row["label"] for row in published], columns=list(LABELS.values()))
    st.bar_chart(chart, stack=True)
    st.dataframe(chart.round(1), width="stretch")
    st.caption(f"{'Weighted' if weighted else 'Unweighted'} percentages within the selected quarter and group. "
               "Precomputed aggregate shares, rounded to one decimal place. No respondent records are loaded.")
    if len(published) < len(rows):
        st.caption("Some groups are withheld because they contain fewer than 30 respondents or an employment-class cell with fewer than 10 respondents.")

elif page == "Model performance":
    st.subheader("How well does the model perform?")
    st.write(f"Selected model: **{meta['best_model']}**. Results below come from this notebook execution.")
    scores = pd.read_csv(OUT / "model_comparison.csv")
    st.dataframe(scores.round(3), hide_index=True, width="stretch")
    st.write("**Macro-F1** gives each class equal importance. **Balanced accuracy** averages recall across classes. "
             "**Recall** measures how many actual members of a class the model finds. Higher scores are better.")
    st.caption("The majority baseline always predicts the largest class. Household groups are kept separate "
               "between training and test data. The same test set also guides model selection, so these scores are exploratory.")
    st.markdown("### Where does the model make mistakes?")
    matrix = pd.read_csv(OUT / "confusion_matrix.csv", index_col=0)
    st.dataframe(matrix.style.background_gradient(cmap="Greens"), width="stretch")
    st.caption("Rows = actual groups. Columns = predicted groups. Diagonal entries are correct predictions.")
    path = OUT / "permutation_importance.csv"
    if path.exists():
        importance = pd.read_csv(path, index_col=0)
        st.markdown("### Which background details help prediction?")
        st.bar_chart(importance.set_index("Predictor")[["Drop in macro-F1 when shuffled"]])
        st.caption("A larger drop means the model relies more on that feature. This does not show cause and effect.")

else:
    st.subheader("From survey responses to a prediction")
    st.write("The notebook combines three Nigeria Labour Force Survey quarters and selects people aged 15–34 "
             "from the main survey samples. Q4 2024 is excluded because the notebook reports that its file cannot be read.")
    st.markdown("""
1. **Create the research labels.** Job search and availability identify unemployment. Working hours, payment and reviewed earnings identify underemployment.
2. **Handle uncertainty.** Unresolved earnings and conflicting screening evidence are excluded where required by the notebook. People outside the labour force receive no model label.
3. **Learn from background details.** Age, sex, education, state, urban/rural residence and quarter are the inputs. Pay and job-search answers are excluded to avoid giving the model the answer.
4. **Compare models.** Logistic regression, decision tree and random forest are compared with a majority baseline.
""")
    st.info("The project's underemployed class includes low pay and unpaid work as well as insufficient hours. "
            "It is broader than the official NBS time-related definition.")
    st.write("Low pay means less than two-thirds of the quarter's median reviewed monthly earnings among paid youth. "
             "Earnings bands and reporting periods require approximations. Survey weights help account for unequal sampling, "
             "but the analysis does not fully account for the survey design.")
    with st.expander("Notebook illustrations"):
        images = sorted((ROOT / "IMAGES").glob("*.png"))
        if images:
            chosen = st.selectbox("Choose an explanation", images, format_func=lambda p: p.stem.replace('_', ' ').replace('-', ' ').title())
            st.image(str(chosen))
    st.caption("Source notebook: Nigeria_Youth_Labour_Underutilisation_G1.ipynb. "
               "This app uses a saved model and aggregate summaries; original survey records are not included in its deployment artifacts.")
