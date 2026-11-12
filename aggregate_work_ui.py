"""Pay/work pages backed exclusively by precomputed group summaries."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from work_rules import evaluate_work, money

@st.cache_resource
def read_summary(path, stamp):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def percent(value):
    return "Withheld" if value is None else f"{value:.1f}%"

def render(root, quarters):
    st.subheader("Pay & work conditions")
    st.write("A job can still leave someone underutilised. Explore pay, the work people do, and the pay problems an hours-only measure can miss.")
    path = Path(root) / "artifacts" / "work_summaries.json"
    if not path.exists():
        st.info("The prepared aggregate summaries are missing. Restore the deployment artifacts to enable this page.")
        return
    work = read_summary(str(path), path.stat().st_mtime_ns)
    explorer, assessment = st.tabs(["Explore observed work", "Check a work situation"])
    with explorer:
        a, b, c = st.columns(3)
        q = a.selectbox("Quarter", list(quarters), format_func=quarters.get, key="work_q")
        scopes = work["quarters"][q]["scopes"]
        focus = b.selectbox("Focus on", list(scopes), key="work_focus")
        choice = c.selectbox("Group", sorted(scopes[focus]), key="work_group")
        mode = "weighted" if st.toggle("Use survey weights", value=True, key="work_weight") else "unweighted"
        selected = scopes[focus][choice]
        summary = selected["summary"]
        values = summary[mode]
        threshold = work["quarters"][q]["threshold"]
        st.caption(f"{quarters[q]} · {focus}: {choice} · approximately {summary['n']:,} employed survey respondents. "
                   "Prepared summaries from the cleaned model sample; no individual survey records are loaded.")
        a, b, c, e = st.columns(4)
        a.metric("Typical monthly pay · paid workers", money(values["median_pay"]))
        b.metric("Unpaid workers", percent(values["unpaid"]))
        c.metric("Typical weekly hours", "Withheld" if values["median_hours"] is None else f"{values['median_hours']:.1f}")
        e.metric("Quarter's low-pay threshold", money(threshold))
        st.caption("Medians were calculated locally for each published group, not averaged from other medians. "
                   "Pay medians are rounded to ₦500 and counts to five. Groups need at least 30 respondents; "
                   "small indicator cells and some companion values are withheld. The quarter's original threshold stays fixed.")
        st.markdown("### What does looking beyond short hours reveal?")
        comparison = pd.DataFrame({"Measure": ["Hours condition alone", "Broader project definition", "Pay issues without hours condition"],
            "Share of employed respondents (%)": [values["time"], values["broad"], values["beyond"]]})
        st.bar_chart(comparison.dropna(), x="Measure", y="Share of employed respondents (%)", color="#228577", horizontal=True)
        if values["beyond"] is not None:
            st.write(f"**{values['beyond']:.1f}%** of employed youth in this group meet an unpaid-work or low-pay condition without meeting the hours condition.")
        if values["long_pay"] is not None:
            st.caption(f"{values['long_pay']:.1f}% work at least 40 hours and still meet a pay-related condition. "
                       "The hours condition also requires wanting and being available for additional work.")
        left, right = st.columns(2)
        with left:
            st.markdown("### How much are workers paid?")
            pay = pd.Series({"No payment": values["pay_none"], "Paid below threshold": values["pay_low"],
                "Paid at/above threshold": values["pay_adequate"], "Pay not established": values["pay_unknown"]}, dtype=float)
            st.bar_chart(pay.dropna().rename("Share (%)"), color="#d39b47", horizontal=True)
            if pay.isna().any():
                st.caption("Some pay categories are withheld; displayed shares may not add to 100%.")
            st.caption("Monthly pay uses the notebook's reviewed conversions and earnings-band estimates. Unknown pay is not zero.")
        with right:
            st.markdown("### What work do they do?")
            category = st.selectbox("Describe work by", list(selected["breakdowns"]), key="work_breakdown")
            breakdown = selected["breakdowns"][category]
            rows = breakdown["rows"]
            jobs = pd.DataFrame({category: [r["label"] for r in rows], "Share (%)": [r[mode]["share"] for r in rows]})
            if not jobs.empty:
                st.bar_chart(jobs.sort_values("Share (%)", ascending=False).head(12), x=category, y="Share (%)", horizontal=True, color="#228577")
            else:
                st.info("No work groups meet the publication threshold for this selection.")
            st.caption("Up to 12 largest published groups. Residence refers to where people live; workplace type describes the physical setting.")
        st.markdown("### Pay and shortfalls by work group")
        table = pd.DataFrame([{category: r["label"], "Respondents (rounded)": r["n"],
            "Median monthly pay (paid)": r[mode]["median_pay"], "Unpaid (%)": r[mode]["unpaid"],
            "Low-paid (%)": r[mode]["low_paid"], "Hours condition (%)": r[mode]["time"],
            "Broader underemployment (%)": r[mode]["broad"]} for r in rows])
        if not table.empty:
            st.dataframe(table, hide_index=True, width="stretch", column_config={
                "Median monthly pay (paid)": st.column_config.NumberColumn(format="₦%.0f"),
                **{col: st.column_config.NumberColumn(format="%.1f") for col in table.columns if col.endswith("(%)")}})
            st.download_button("Download this summary", table.to_csv(index=False), "work_conditions_summary.csv", "text/csv")
        if breakdown["withheld"]:
            st.caption("Small groups and, where needed, a companion group are omitted. Shares use all employed respondents in the selected group as denominator, so published rows may not total 100%.")
        st.caption("Counts are unweighted and rounded. Conditions may overlap. Medians exclude unknown pay and unpaid workers. "
                   "Blank statistics are withheld or unavailable. These are project-sample summaries, not official national rates. "
                   "Focus on one group at a time; arbitrary combinations of filters are not published.")
    with assessment:
        st.markdown("### Explain an actual work situation")
        st.write("Enter pay and hours to see how the project's rules apply. This explains the label rules; the machine-learning prediction still uses background details only.")
        with st.form("work_assessment"):
            a, b = st.columns(2)
            aq = a.selectbox("Survey quarter for the pay benchmark", list(quarters), format_func=quarters.get, key="assessment_q")
            employed = b.checkbox("Has a job", value=True)
            payment = a.selectbox("Payment status", ["Paid", "Unpaid", "Unknown"])
            pay = b.number_input("Monthly pay in naira (paid work)", min_value=0.0, value=40000.0, step=1000.0)
            hours = a.number_input("Usual weekly working hours", min_value=0.0, max_value=168.0, value=45.0)
            known = b.checkbox("Weekly hours are known", value=True)
            wants = a.checkbox("Wants additional working hours")
            can = b.checkbox("Available for additional hours")
            searching = a.checkbox("If no job: actively searching")
            available = b.checkbox("If no job: available to start")
            submitted = st.form_submit_button("Explain this situation", type="primary")
        if submitted:
            threshold = work["quarters"][aq]["threshold"]
            label, reasons = evaluate_work(employed, searching, available, payment, pay, hours if known else None, wants, can, threshold)
            st.info(f"Rule-based result: {label}")
            for reason in reasons:
                st.write(f"• {reason}")
            if employed and known and hours >= 40 and label.startswith("Underemployed"):
                st.write("**Beyond the hours shortfall:** this person works at least 40 hours, but pay still establishes underemployment.")
            st.caption(f"Benchmark: {quarters[aq]}, {money(threshold)} per month. This research threshold is not a minimum wage or poverty line. "
                       "Entries are used for this calculation and are not written to a file by the app.")
