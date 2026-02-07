import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import random
import io
import tempfile
import re
from fpdf import FPDF, XPos, YPos
from datetime import datetime

# --- STREAMLIT CONFIGURATION ---
st.set_page_config(page_title="Probabilistic Delivery Suite", layout="wide", page_icon="🎲")

# --- CSS STYLING ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2c3e50; color: white; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #34495e; }
    [data-testid="stMetricValue"] { font-size: 28px; }
</style>
""", unsafe_allow_html=True)


# --- GOVERNANCE HELPERS ---
def get_molecular_status(data):
    if not data: return "No Data", "grey", 0
    avg = np.mean(data)
    if avg > 20:
        return "⚠️ ATOM ALERT: High volume suggests task-level slicing.", "orange", 40
    if avg < 1:
        return "⚠️ STAGNATION: Throughput is dangerously low.", "red", 20
    return "✅ MOLECULAR DATA: Throughput suggests value-item delivery.", "#2ecc71", 100


def clean_for_pdf(text):
    if not text: return ""
    return re.sub(r'[^\x00-\x7F]+', '', text).strip()


def load_data_from_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        return df.iloc[:, 0].dropna().astype(int).tolist()
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return []


# --- PDF GENERATOR ---
class RescueReport(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(100, 10, 'PROBABILISTIC DELIVERY AUDIT', align='L')
        self.set_font('helvetica', '', 10)
        self.cell(0, 10, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', align='R', new_x=XPos.LMARGIN,
                  new_y=YPos.NEXT)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} - Confidential Actuarial Report', align='C')


def create_enhanced_pdf(project_name, report_type, stats_dict, gate_info, commentary, chart_fig):
    pdf = RescueReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_fill_color(44, 62, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(190, 12, f" PROJECT: {clean_for_pdf(project_name).upper()}", align='L', fill=True, new_x=XPos.LMARGIN,
             new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # Section 1: Integrity (Fixed Alignment)
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(190, 10, "1. DATA INTEGRITY & GOVERNANCE", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("helvetica", '', 11)
    # Using specific widths to ensure Score stays on the same line but justified right
    pdf.cell(140, 8, f"Status: {clean_for_pdf(gate_info['msg'])}")
    pdf.cell(50, 8, f"Score: {gate_info['score']}/100", align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)

    # Section 2: Stats
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(190, 10, "2. ACTUARIAL FORECAST", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("helvetica", '', 11)
    for key, val in stats_dict.items():
        pdf.cell(95, 8, f"{key}:", border='B')
        pdf.cell(95, 8, f"{val}", border='B', align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if commentary.strip():
        pdf.ln(5)
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(190, 10, "3. SPECIALIST COMMENTARY", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("helvetica", 'I', 11)
        pdf.multi_cell(190, 7, clean_for_pdf(commentary))

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        chart_fig.savefig(tmpfile.name, format="png", bbox_inches='tight', dpi=150)
        if pdf.get_y() > 160: pdf.add_page()
        pdf.image(tmpfile.name, x=10, y=pdf.get_y() + 5, w=190)
    return bytes(pdf.output())


# --- VIEW 1: HOME ---
def show_home():
    st.title("🎲 Probabilistic Delivery Suite")
    st.markdown("## Fiduciary Governance for Software Capital")
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.info("### 1. The Strategy (Pre-Project)")
        st.markdown(
            "**'Can we afford this project?'**\n\nUse when you have a backlog range and need to set a budget before starting.")
        if st.button("Go to Delivery Forecast", key="h_f"):
            st.session_state['page'] = 'forecast';
            st.rerun()
    with c2:
        st.success("### 2. The Tactics (Active Project)")
        st.markdown(
            "**'When will we finish?'**\n\nUse during execution. Input actuals to see the 'Cone of Uncertainty' narrow.")
        if st.button("Go to Risk Horizon", key="h_h"):
            st.session_state['page'] = 'horizon';
            st.rerun()
    st.markdown("---")
    st.caption("A Project Rescue Instrument by Theo van Stratum, PhD")


# --- VIEW 2: FORECAST ---
def show_forecast():
    st.title("🔮 Strategy Forecast")
    if st.button("← Home"): st.session_state['page'] = 'home'; st.rerun()
    proj_name = st.text_input("Project Name", value="New Initiative")
    st.markdown("---")
    col_in, col_gr = st.columns([1, 3])
    with col_in:
        st.subheader("1. Scoping")
        s_min = st.number_input("Min Items", value=20)
        s_max = st.number_input("Max Items", value=30)
        st.subheader("2. Capability")
        t1, t2 = st.tabs(["Manual Pulse", "Upload Pulse"])
        pulse = []
        with t1:
            p_str = st.text_area("Pulse History", value="4, 5, 2, 6, 0, 4")
            try:
                pulse = [int(x.strip()) for x in p_str.split(',') if x.strip()]
            except:
                pulse = [1]
        with t2:
            p_file = st.file_uploader("Upload Pulse", type=['csv', 'xlsx'], key="f_up")
            if p_file: pulse = load_data_from_file(p_file)

        commentary = st.text_area("Specialist's Commentary")
        allow_zeros = st.checkbox("Include Black Swans (0s)", value=True)
        sims = st.number_input("Simulations", value=10000)
        run_btn = st.button("🚀 Run Monte Carlo")

    if run_btn:
        if not allow_zeros: pulse = [x for x in pulse if x > 0]
        msg, color, score = get_molecular_status(pulse)
        results = []
        for _ in range(sims):
            tot, w = random.randint(s_min, s_max), 0
            while tot > 0:
                tot -= random.choice(pulse if pulse else [1]);
                w += 1
            results.append(w)
        p50, p85, p95 = np.percentile(results, [50, 85, 95])
        with col_gr:
            st.markdown(f"<p style='color:{color}; font-weight:bold;'>{msg}</p>", unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.hist(results, bins=range(min(results), max(results) + 2), color='#34495e', alpha=0.7, edgecolor='white')
            ax.axvline(p50, color='orange', linestyle='--', label=f'Aggressive (50%): {int(p50)} wks')
            ax.axvline(p85, color='green', linestyle='--', label=f'Commercial (85%): {int(p85)} wks')
            ax.axvline(p95, color='blue', linestyle='--', label=f'Safe (95%): {int(p95)} wks')
            ax.legend();
            st.pyplot(fig)
            stats = {"Scope": f"{s_min}-{s_max}", "P50": f"{int(p50)} Weeks", "P85": f"{int(p85)} Weeks",
                     "P95": f"{int(p95)} Weeks"}
            pdf = create_enhanced_pdf(proj_name, "Strategy", stats, {"msg": msg, "score": score}, commentary, fig)
            st.download_button("📄 Download Audit Report", pdf, f"{proj_name}_audit.pdf")


# --- VIEW 3: HORIZON ---
def show_horizon():
    st.title("🛤️ Risk Horizon Tracking")
    if st.button("← Home"): st.session_state['page'] = 'home'; st.rerun()
    proj_name = st.text_input("Project Name", value="Active Rescue")
    st.markdown("---")
    col_in, col_gr = st.columns([1, 3])
    with col_in:
        st.subheader("1. The Engine")
        t1, t2 = st.tabs(["Manual Pulse", "Upload Pulse"])
        pulse = []
        with t1:
            p_str = st.text_area("History", value="4, 5, 3, 6")
            try:
                pulse = [int(x.strip()) for x in p_str.split(',') if x.strip()]
            except:
                pulse = [1]
        with t2:
            p_file = st.file_uploader("Upload History", type=['csv', 'xlsx'], key="h_up1")
            if p_file: pulse = load_data_from_file(p_file)

        st.subheader("2. The Road")
        t3, t4 = st.tabs(["Manual Actuals", "Upload Actuals"])
        actuals = []
        with t3:
            a_str = st.text_input("Project Actuals", value="3, 4, 2")
            try:
                actuals = [int(x.strip()) for x in a_str.split(',') if x.strip()]
            except:
                actuals = []
        with t4:
            a_file = st.file_uploader("Upload Actuals", type=['csv', 'xlsx'], key="h_up2")
            if a_file: actuals = load_data_from_file(a_file)

        total_scope = st.number_input("Total Scope", value=100)
        commentary = st.text_area("Specialist's Commentary")
        sims = st.number_input("Simulations", value=10000)
        run_btn = st.button("🚀 Update Forecast")

    if run_btn:
        msg, color, score = get_molecular_status(pulse)
        done, curr_w, horizon = sum(actuals), len(actuals), 40
        futures = np.zeros((sims, horizon))
        for i in range(sims):
            cd, path = done, []
            for _ in range(horizon):
                cd += random.choice(pulse if pulse else [1]);
                path.append(cd)
            futures[i] = path

        p_05, p_15, p_25, p_50, p_75, p_85, p_95 = np.percentile(futures, [5, 15, 25, 50, 75, 85, 95], axis=0)

        with col_gr:
            st.markdown(f"<p style='color:{color}; font-weight:bold;'>{msg}</p>", unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(range(curr_w + 1), [0] + list(np.cumsum(actuals)), color='black', linewidth=3, marker='o',
                    label='Actuals', zorder=5)
            ax.axhline(total_scope, color='blue', linestyle='--', label='Scope')

            cone_x = range(curr_w, curr_w + horizon)
            ax.fill_between(cone_x, p_05, p_95, color='green', alpha=0.1, label='Range (5-95%)')
            ax.fill_between(cone_x, p_25, p_75, color='green', alpha=0.2, label='Likely (25-75%)')

            def get_w(y, t):
                for i in range(len(y) - 1):
                    if y[i] <= t and y[i + 1] >= t:
                        return (i + curr_w) + (t - y[i]) / (y[i + 1] - y[i] + 1e-9)
                return None

            w50, w85, w95 = get_w(p_50, total_scope), get_w(p_15, total_scope), get_w(p_05, total_scope)

            if w50:
                ax.vlines(w50, 0, total_scope, colors='orange', linestyles='dotted')
                ax.text(w50, 10, f"Aggressive\n~W{int(np.ceil(w50))}", color='orange', ha='center', fontweight='bold',
                        fontsize=9)
            if w85:
                ax.vlines(w85, 0, total_scope, colors='green', linestyles='dotted')
                ax.text(w85, 30, f"Commercial\n~W{int(np.ceil(w85))}", color='green', ha='center', fontweight='bold',
                        fontsize=9)
            if w95:
                ax.vlines(w95, 0, total_scope, colors='blue', linestyles='dotted')
                ax.text(w95, 50, f"Safe\n~W{int(np.ceil(w95))}", color='blue', ha='center', fontweight='bold',
                        fontsize=9)

            ax.set_title(f"Risk Horizon: {proj_name}");
            ax.legend(loc='upper left');
            st.pyplot(fig)

            st.subheader("The Risk Menu")
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Aggressive (P50)", f"Week {int(np.ceil(w50)) if w50 else 'N/A'}")
                st.markdown("<p style='color:orange; font-size: 14px;'>↑ 50% Chance</p>", unsafe_allow_html=True)
            with m2:
                st.metric("Commercial (P85)", f"Week {int(np.ceil(w85)) if w85 else 'N/A'}")
                st.markdown("<p style='color:green; font-size: 14px;'>↑ 85% Chance</p>", unsafe_allow_html=True)
            with m3:
                st.metric("Safe (P95)", f"Week {int(np.ceil(w95)) if w95 else 'N/A'}")
                st.markdown("<p style='color:blue; font-size: 14px;'>↑ 95% Chance</p>", unsafe_allow_html=True)

            stats = {"Done": f"{done}/{total_scope}", "Commercial (P85)": f"Week {int(np.ceil(w85)) if w85 else 'N/A'}"}
            pdf = create_enhanced_pdf(proj_name, "Tactical", stats, {"msg": msg, "score": score}, commentary, fig)
            st.download_button("📄 Download Audit Report", pdf, f"{proj_name}_rescue.pdf")


# --- MAIN CONTROLLER ---
if 'page' not in st.session_state: st.session_state['page'] = 'home'
if st.session_state['page'] == 'home':
    show_home()
elif st.session_state['page'] == 'forecast':
    show_forecast()
elif st.session_state['page'] == 'horizon':
    show_horizon()