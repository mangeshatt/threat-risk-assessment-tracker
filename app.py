import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from pathlib import Path
from utils.calculate_cvss import calculate_cvss
from utils.threat_selection import get_threat_selection
from utils.visualization import show_mitigation_analysis, show_summary_stats, show_temporal_trends, show_threat_vector_analysis
from utils.sla_tracker import sla_tracker
from utils.pdf_exports import PDFSummary

DB_PATH = Path("data/tra_data.db")

# Create database connection
def get_connection():
    return sqlite3.connect(DB_PATH)

# Initialize table if not exists
def init_db():
    conn = get_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tra_entries (
            TRA_ID TEXT PRIMARY KEY,
            Asset_Name TEXT,
            Owner TEXT,
            Threat_Vector TEXT,
            Risk_Likelihood TEXT,
            Risk_Impact TEXT,
            Mitigation_Control TEXT,
            Mitigation_Description TEXT,
            Score REAL,
            Status TEXT,
            Timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()


# Page selector
st.sidebar.title("🔐 Cyber TRA Tracker")
st.sidebar.markdown("## Navigation Menu")

page = st.sidebar.radio("**Choose Action**", ["Submit New TRA", "View TRA Dashboard", "CISO Summary & SLA"])

# Initialize DB
init_db()

# 1. INSERT FORM
if page == "Submit New TRA":
    st.header("📥 Submit a New Threat & Risk Assessment")

    # Load mitigation controls from CSV
    @st.cache_data
    def load_controls():
        df = pd.read_csv("data/mitigation_controls.csv")
        return df

    controls_df = load_controls()

    # Create a list of control options 
    control_options = [
        f"{row['Control_ID'].upper()}" 
        for _, row in controls_df.iterrows()
    ]
    

    col1,col2 = st.columns([2,3])

    with col1:
        # Threat Vector Selection
        st.write("Select threat vector for TRA Form.")
        current_threat = get_threat_selection()

    with col2:
        with st.form("tra_form"):
            # Generate a unique form ID based on timestamp
            form_id = str(datetime.now().timestamp()).replace(".", "")
            tra_id = st.text_input("TRA ID", value=f"TRA{datetime.now().strftime('%y%m%d%H%M')}")
            asset = st.text_input("Asset Name")
            owner = st.text_input("Owner")
            # Threat Vector Selection
            threat = current_threat
            st.write(f"Selected threat: {threat}")    
            likelihood = st.selectbox("Risk Likelihood", ["Low", "Moderate", "High"])
            impact = st.selectbox("Risk Impact", ["Low", "Moderate", "High"])
            # Multi-selector for controls
            selected_controls = st.multiselect(
                "Mitigation Controls", 
                options=control_options,
                help="Select one or more controls from NIST SP 800-53."
            )
            # Text input for mitigation description
            mitigation_description = st.text_area(
            "Mitigation Description",
            placeholder="Describe how the selected controls mitigate the threat."
            )
            status = st.selectbox("Status", ["Open", "Mitigated", "Critical"])
            submit = st.form_submit_button("Submit TRA")

            if submit:
                score, _ = calculate_cvss(likelihood, impact)
                timestamp = datetime.now().strftime("%Y-%m-%d")
                conn = get_connection()
                conn.execute('''
                    INSERT OR REPLACE INTO tra_entries (
                        TRA_ID, Asset_Name, Owner, Threat_Vector, Risk_Likelihood, Risk_Impact,
                        Mitigation_Control, Mitigation_Description, Score, Status, Timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (tra_id, asset, owner, threat, likelihood, impact, selected_controls, mitigation_description, score, status, timestamp))
                conn.commit()
                conn.close()
                st.success(f"TRA submitted successfully with score {score}")


# 2. DASHBOARD
elif page == "View TRA Dashboard":
    st.header("📊 Threat & Risk Dashboard")
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM tra_entries", conn)

    with st.expander("🔍 Apply Filters"):
        assets = st.multiselect("Asset Name", sorted(df["Asset_Name"].unique()))
        statuses = st.multiselect("Status", sorted(df["Status"].unique()))
        score_range = st.slider("Risk Score Range", 0.0, 10.0, (0.0, 10.0))

        if assets:
            df = df[df["Asset_Name"].isin(assets)]
        if statuses:
            df = df[df["Status"].isin(statuses)]
        df = df[(df["Score"] >= score_range[0]) & (df["Score"] <= score_range[1])]

    # Visualization Section
    st.markdown("---")
    st.header("📈 Risk Visualization")
    
    col1, col2 = st.columns(2)
    with col1:
        show_threat_vector_analysis(df)
    with col2:
        show_mitigation_analysis(df)
    
    show_temporal_trends(df)
    show_summary_stats(df)

    conn.close()

# 3. CISO Summary & SLA

elif page == "CISO Summary & SLA":
    st.header("📄 CISO Summary Report & SLA Tracker")

    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM tra_entries", conn)
    conn.close()

    if df.empty:
        st.warning("No TRA entries found in the database.")
    else:
        # ---- SLA Tracking ----
        df = sla_tracker(df)

        st.subheader("📌 TRA Entries with SLA Breaches")
        st.dataframe(df[df["Overdue"]])

        # ---- CISO PDF Export ----
        st.subheader("📤 Export Top 5 Critical Risks to PDF")

        top_critical = df[df["Score"] >= 8.5].sort_values(by="Score", ascending=False).head(5)

        if st.button("Generate CISO Summary PDF"):

            pdf = PDFSummary()
            pdf.add_page()
            pdf.section_title("Top 5 Critical Risk Items")
            pdf.add_risk_table(top_critical)

            pdf.section_title("Mitigation Timeline Summary")
            for _, row in top_critical.iterrows():
                pdf.cell(0, 8, f"{row['TRA_ID']} - {row['Asset_Name']} => Control: {row['Mitigation_Control']} | Timestamp: {row['Timestamp'].strftime('%Y-%m-%d')}", ln=True)

            output_path = "data/ciso_summary_report.pdf"
            pdf.output(output_path)

            with open(output_path, "rb") as f:
                st.download_button("📥 Download PDF", f, file_name="CISO_Summary_Report.pdf")
    
    conn.close()