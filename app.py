import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import random
import io
import tempfile
from fpdf import FPDF, XPos, YPos

# --- STREAMLIT CONFIGURATION ---
st.set_page_config(page_title="Probabilistic Delivery Suite", layout="wide", page_icon="🎲")

# --- CSS STYLING ---
st.markdown("""
<style>
    .big-font { font-size:20px !important; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .reportview-container { background: #0e1117; }
</style>
""", unsafe_allow_html=True)


# --- HELPER: DATA LOADER ---
def load_data_from_file(uploaded_file):
    """Parses a CSV/Excel file and extracts the first column as a list of integers."""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # We assume the data is in the first column
        first_col = df.iloc[:, 0]

        # Drop NaNs and convert to integers
        clean_data = first_col.dropna().astype(int).tolist()
        return clean_data
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return []


# --- HELPER: PDF GENERATOR ---
def create_pdf(report_type, stats_text, chart_fig):
    """Generates a PDF report with the stats and the chart."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)

    # Title
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(200, 10, text=f"Probabilistic Delivery Report: {report_type}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)

    # Stats Text
    pdf.set_font("helvetica", size=12)
    for line in stats_text.split('\n'):
        pdf.cell(200, 8, text=line, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

    # Chart Image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        chart_fig.savefig(tmpfile.name, format="png", bbox_inches='tight', dpi=100)
        pdf.image(tmpfile.name, x=10, y=pdf.get_y() + 10, w=190)

    # Output to bytes
    return bytes(pdf.output())


# --- VIEW 1: HOME ---
def show_home():
    st.title("🎲 Probabilistic Delivery Suite")
    st.markdown("### Stop Guessing. Start Calculating.")

    col1, col2 = st.columns(2)

    with col1:
        st.info("### 1. The Strategy (Pre-Project)")
        st.markdown("""
        **"Can we afford this project?"**

        Use the **Delivery Forecast** when you have a backlog range (e.g., 50-70 items) and need to set a budget or deadline *before* starting.

        * **Output:** A Probability Histogram.
        * **Answer:** "We are 85% sure this is a 12-week project."
        """)
        if st.button("Go to Delivery Forecast"):
            st.session_state['page'] = 'forecast'
            st.rerun()

    with col2:
        st.success("### 2. The Tactics (Active Project)")
        st.markdown("""
        **"When will we finish?"**

        Use the **Risk Horizon** when the project is running. Input your weekly actuals to see the "Cone of Uncertainty" narrow over time.

        * **Output:** A Dynamic Burn-up Chart.
        * **Answer:** "Based on the last 4 weeks, we will land on Nov 15th."
        """)
        if st.button("Go to Risk Horizon"):
            st.session_state['page'] = 'horizon'
            st.rerun()


# --- VIEW 2: DELIVERY FORECAST (The Histogram) ---
def show_forecast():
    st.title("🔮 Delivery Forecast (Pre-Project Strategy)")
    st.markdown("[Back to Home]", unsafe_allow_html=True)
    if st.button("← Home"):
        st.session_state['page'] = 'home'
        st.rerun()

    st.markdown("---")

    col_input, col_graph = st.columns([1, 3])

    with col_input:
        st.subheader("1. Scoping")
        scope_min = st.number_input("Min Items (Best Case)", value=12)
        scope_max = st.number_input("Max Items (Worst Case)", value=17)

        st.subheader("2. Capability")

        # --- INPUT TABS ---
        tab1, tab2 = st.tabs(["Manual Entry", "Upload Data"])

        pulse = []

        with tab1:
            throughput_str = st.text_input("Team History (Pulse)", value="6,5,4,6,3,6,5,4,7",
                                           help="Comma separated integers")
            try:
                pulse = [int(x.strip()) for x in throughput_str.split(',') if x.strip()]
            except:
                pulse = [1]

        with tab2:
            st.markdown("Upload a CSV/Excel with a single column of numbers (Throughput/Week).")
            uploaded_file = st.file_uploader("Upload Throughput File", type=['csv', 'xlsx'])
            if uploaded_file is not None:
                pulse = load_data_from_file(uploaded_file)
                if pulse:
                    st.success(f"Loaded {len(pulse)} weeks of history.")
                    st.write(f"Preview: {pulse[:5]}...")

        sims = st.number_input("Simulations", value=10000)

        run_btn = st.button("🚀 Run Monte Carlo")

    if run_btn:
        with col_graph:
            # Fallback if no data
            if not pulse: pulse = [1]

            # --- LOGIC ---
            results = []
            for i in range(sims):
                total_work = random.randint(scope_min, scope_max)
                weeks = 0
                while total_work > 0:
                    velocity = random.choice(pulse)
                    if velocity <= 0: velocity = 1
                    total_work -= velocity
                    weeks += 1
                results.append(weeks)

            data = np.array(results)
            p50 = np.percentile(data, 50)
            p85 = np.percentile(data, 85)
            p95 = np.percentile(data, 95)

            # --- VISUALIZATION ---
            fig, ax = plt.subplots(figsize=(10, 5))
            bins = np.arange(min(data), max(data) + 2) - 0.5
            ax.hist(data, bins=bins, color='#2c3e50', alpha=0.7, edgecolor='black')
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))

            # Lines
            ax.axvline(p50, color='orange', linestyle='--', linewidth=2, label=f'50% (Flip Coin): {int(p50)} wks')
            ax.axvline(p85, color='green', linestyle='--', linewidth=2, label=f'85% (Commercial): {int(p85)} wks')
            ax.axvline(p95, color='blue', linestyle='--', linewidth=2, label=f'95% (Safe): {int(p95)} wks')

            ax.set_title(f"Delivery Forecast ({sims} runs)")
            ax.set_xlabel("Weeks to Complete")
            ax.set_ylabel("Frequency")
            ax.legend()

            st.pyplot(fig)

            # --- METRICS & PDF ---
            pulse_preview = str(pulse[:10]) + "..." if len(pulse) > 10 else str(pulse)
            stats_text = (
                f"SCOPE: {scope_min} - {scope_max} items\n"
                f"TEAM PULSE: {pulse_preview}\n\n"
                f"Option A (Aggressive): {int(p50)} Weeks (50% Chance)\n"
                f"Option B (Likely):     {int(p85)} Weeks (85% Chance)\n"
                f"Option C (Safe):       {int(p95)} Weeks (95% Chance)"
            )

            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.info(f"**Likely Outcome (85%): {int(p85)} Weeks**")
            with col_res2:
                pdf_bytes = create_pdf("Strategy Forecast", stats_text, fig)
                st.download_button("📄 Download PDF Report", data=pdf_bytes, file_name="forecast_report.pdf",
                                   mime="application/pdf")


# --- VIEW 3: RISK HORIZON (The Burn-up) ---
def show_horizon():
    st.title("🛤️ The Risk Horizon (Active Project Tracking)")
    if st.button("← Home"):
        st.session_state['page'] = 'home'
        st.rerun()

    st.markdown("---")

    col_input, col_graph = st.columns([1, 3])

    with col_input:
        st.subheader("1. The Engine")

        # --- TABBED INPUT FOR PULSE ---
        tab_pulse1, tab_pulse2 = st.tabs(["Manual Pulse", "Upload Pulse"])
        pulse_data = []

        with tab_pulse1:
            pulse_str = st.text_input("Pulse (History)", value="2, 5, 4, 6, 4, 3, 5")
            try:
                pulse_data = [int(x.strip()) for x in pulse_str.split(',') if x.strip()]
            except:
                pulse_data = [1]

        with tab_pulse2:
            st.markdown("Upload history (e.g. last 50 weeks).")
            pulse_file = st.file_uploader("Upload Pulse CSV", type=['csv', 'xlsx'], key="pulse_up")
            if pulse_file:
                pulse_data = load_data_from_file(pulse_file)
                if pulse_data: st.success(f"Loaded {len(pulse_data)} weeks.")

        st.subheader("2. The Road")

        # --- TABBED INPUT FOR ACTUALS ---
        tab_act1, tab_act2 = st.tabs(["Manual Actuals", "Upload Actuals"])
        project_actuals = []

        with tab_act1:
            actuals_str = st.text_input("Project Actuals", value="2, 5, 4", placeholder="e.g. 3, 4")
            if actuals_str.strip() != "":
                try:
                    project_actuals = [int(x.strip()) for x in actuals_str.split(',') if x.strip()]
                except:
                    project_actuals = []

        with tab_act2:
            st.markdown("Upload progress (weeks done so far).")
            actuals_file = st.file_uploader("Upload Actuals CSV", type=['csv', 'xlsx'], key="act_up")
            if actuals_file:
                project_actuals = load_data_from_file(actuals_file)
                if project_actuals: st.success(f"Loaded {len(project_actuals)} weeks.")

        total_scope = st.number_input("Total Scope", value=100)
        sims = st.number_input("Simulations", value=10000)

        run_btn = st.button("🚀 Update Forecast")

    if run_btn:
        with col_graph:
            # Fallback
            if not pulse_data: pulse_data = [1]

            # --- LOGIC ---
            current_week = len(project_actuals)
            items_done = sum(project_actuals)
            remaining_weeks = 30  # Horizon

            simulation_pool = pulse_data + project_actuals
            if not simulation_pool: simulation_pool = [1]

            futures = np.zeros((sims, remaining_weeks))
            for i in range(sims):
                cumulative = items_done
                path = []
                for w in range(remaining_weeks):
                    cumulative += random.choice(simulation_pool)
                    path.append(cumulative)
                futures[i] = path

            # --- PERCENTILES ---
            # Fan Visuals
            p_optimistic_95 = np.percentile(futures, 95, axis=0)  # Top of Outer
            p_pessimistic_05 = np.percentile(futures, 5, axis=0)  # Bottom of Outer (Safe Line)
            p_fast_75 = np.percentile(futures, 75, axis=0)  # Top of Inner
            p_slow_25 = np.percentile(futures, 25, axis=0)  # Bottom of Inner

            # Risk Menu Lines
            p_median_50 = np.percentile(futures, 50, axis=0)  # Aggressive
            p_comm_15 = np.percentile(futures, 15, axis=0)  # Commercial (85%)

            # --- VISUALIZATION ---
            fig, ax = plt.subplots(figsize=(12, 6))

            # 1. Actuals (Black Line)
            past_weeks = [0] + list(range(1, current_week + 1))
            cum_actuals = [0]
            run_sum = 0
            for v in project_actuals:
                run_sum += v
                cum_actuals.append(run_sum)
            ax.plot(past_weeks, cum_actuals, color='black', linewidth=3, marker='o', label='Actuals', zorder=10)

            # 2. Scope (Blue Dashed)
            all_x = list(range(0, current_week + remaining_weeks + 1))
            ax.plot(all_x, [total_scope] * len(all_x), color='blue', linestyle='--', label='Scope')

            # 3. The Fan (Clouds)
            cone_x = [current_week] + list(range(current_week, current_week + remaining_weeks))

            y_out_top = [items_done] + list(p_optimistic_95)
            y_out_bot = [items_done] + list(p_pessimistic_05)
            y_in_top = [items_done] + list(p_fast_75)
            y_in_bot = [items_done] + list(p_slow_25)

            # Outer Cone (Range)
            ax.fill_between(cone_x, y_out_bot, y_out_top, color='green', alpha=0.1, label='Range (5-95%)')
            # Inner Cone (Likely)
            ax.fill_between(cone_x, y_in_bot, y_in_top, color='green', alpha=0.2, label='Likely (25-75%)')

            # Median Line (Center)
            y_med = [items_done] + list(p_median_50)
            ax.plot(cone_x, y_med, color='green', linestyle=':', alpha=0.6)

            # --- 4. PRECISE INTERCEPTORS (The Fix) ---
            # This function finds the EXACT visual crossing point (e.g. Week 26.3)
            # instead of snapping to the nearest integer.
            def get_exact_week(y_values, target):
                for i in range(len(y_values) - 1):
                    val_start = y_values[i]
                    val_end = y_values[i + 1]

                    # If the line crosses the target in this segment
                    if val_start <= target and val_end >= target:
                        # Linear Interpolation formula
                        fraction = (target - val_start) / (val_end - val_start + 1e-9)
                        return (i + current_week) + fraction
                return None

            y_comm = [items_done] + list(p_comm_15)

            w_50_exact = get_exact_week(y_med, total_scope)  # Aggressive
            w_85_exact = get_exact_week(y_comm, total_scope)  # Commercial
            w_95_exact = get_exact_week(y_out_bot, total_scope)  # Safe (Bottom of fan)

            # Plot Vertical Lines at precise locations
            if w_50_exact:
                ax.vlines(w_50_exact, 0, total_scope, colors='orange', linestyles='dotted')
                ax.text(w_50_exact, 10, f"Aggressive\n~W{int(w_50_exact)}", color='orange', ha='center',
                        fontweight='bold', fontsize=9)

            if w_85_exact:
                ax.vlines(w_85_exact, 0, total_scope, colors='green', linestyles='dotted')
                ax.text(w_85_exact, 30, f"Commercial\n~W{int(w_85_exact)}", color='green', ha='center',
                        fontweight='bold', fontsize=9)

            if w_95_exact:
                ax.vlines(w_95_exact, 0, total_scope, colors='blue', linestyles='dotted')
                ax.text(w_95_exact, 50, f"Safe\n~W{int(w_95_exact)}", color='blue', ha='center', fontweight='bold',
                        fontsize=9)

            ax.set_title(f"Risk Horizon (Week {current_week})")
            ax.legend(loc='upper left')
            st.pyplot(fig)

            # --- METRICS ---
            st.subheader("The Risk Menu")
            m1, m2, m3 = st.columns(3)

            # We display the rounded-up integer for the user (Business Dates),
            # but the graph uses the exact float for alignment.
            def fmt_week(w):
                return f"Week {int(np.ceil(w))}" if w else "N/A"

            with m1:
                st.metric("Option A (Aggressive)", fmt_week(w_50_exact), "50% Chance")
            with m2:
                st.metric("Option B (Commercial)", fmt_week(w_85_exact), "85% Chance")
            with m3:
                st.metric("Option C (Safe)", fmt_week(w_95_exact), "95% Chance")

            # --- PDF REPORT ---
            pulse_preview = str(pulse_data[:10]) + "..." if len(pulse_data) > 10 else str(pulse_data)
            stats_text = (
                f"PROJECT STATUS: Week {current_week}\n"
                f"ITEMS DONE: {items_done} / {total_scope}\n"
                f"PULSE DATA: {pulse_preview}\n\n"
                f"Option A (Aggressive): {fmt_week(w_50_exact)} (50% Chance)\n"
                f"Option B (Commercial): {fmt_week(w_85_exact)} (85% Chance)\n"
                f"Option C (Safe):       {fmt_week(w_95_exact)} (95% Chance)"
            )

            pdf_bytes = create_pdf("Risk Horizon Tracking", stats_text, fig)
            st.download_button("📄 Download PDF Report", data=pdf_bytes, file_name="risk_horizon_report.pdf",
                               mime="application/pdf")


# --- MAIN APP CONTROLLER ---
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'

if st.session_state['page'] == 'home':
    show_home()
elif st.session_state['page'] == 'forecast':
    show_forecast()
elif st.session_state['page'] == 'horizon':
    show_horizon()