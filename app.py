import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_lottie import st_lottie
import requests

# Load Lottie JSON
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

hr_animation = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_jcikwtux.json")  # HR team animation

st_lottie(hr_animation, speed=1, height=180, key="hr")

# ---------- PAGE STYLING ----------
st.markdown("""
    <style>
        body {
            background: linear-gradient(to right, #fdfbfb, #ebedee);
            font-family: 'Segoe UI', sans-serif;
        }
        .main {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 14px;
            box-shadow: 0px 4px 20px rgba(0,0,0,0.08);
        }
        h1, h2, h3 {
            color: #2f3542;
            text-align: center;
        }
        .metric-box {
            background: linear-gradient(to right, #f0f4ff, #dff2ff);
            padding: 1.2rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            margin: 10px 0;
            text-align: center;
            font-weight: 600;
        }
        .stButton>button {
            background: linear-gradient(to right, #6a82fb, #fc5c7d);
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 10px;
            padding: 0.6em 1.4em;
            transition: 0.4s ease-in-out;
        }
        .stButton>button:hover {
            background: linear-gradient(to right, #4facfe, #00f2fe);
            transform: scale(1.05);
        }
    </style>
""", unsafe_allow_html=True)

# ---------- APP TITLE ----------
st.markdown("""
    <h1 style='text-align: center; font-size: 2.8em; color: #2c3e50;'>💼 HR Skill Gap Dashboard</h1>
    <p style='text-align: center; font-size: 1.1em; color: #636e72;'>Built by Akanksha Sahani • Powered by Python + Streamlit</p>
    <hr style='border-top: 2px dashed #dfe6e9; margin-bottom: 2rem;'>
""", unsafe_allow_html=True)

# ---------- FILE UPLOAD ----------
emp_file = st.file_uploader("Upload Employee Skills CSV", type=["csv"])
req_file = st.file_uploader("Upload Required Skills CSV", type=["csv"])

if emp_file and req_file:
    df = pd.read_csv(emp_file)
    required = pd.read_csv(req_file)

    df.columns = df.columns.str.strip()
    required.columns = required.columns.str.strip()

    merged = pd.merge(df, required, on=['Role', 'Skill'])
    merged['Gap'] = merged['Required Rating'] - merged['Self Rating']
    merged = merged.loc[:, ~merged.columns.str.contains('^Unnamed')]

    course_dict = {
        'Excel': {
            'Title': 'Advanced Excel – Coursera',
            'Summary': 'Covers pivot tables, advanced formulas & dashboards.'
        },
        'Communication': {
            'Title': 'Effective Communication – Udemy',
            'Summary': 'Improve verbal/written communication & public speaking.'
        },
        'Python': {
            'Title': 'Python for Beginners – Coursera',
            'Summary': 'Intro to Python, data structures, scripting.'
        },
        'Safety': {
            'Title': 'Industrial Safety – NPTEL',
            'Summary': 'Covers plant safety, PPE & hazard prevention.'
        },
        'Leadership': {
            'Title': 'Leadership Essentials – LinkedIn Learning',
            'Summary': 'Learn team management, delegation, decision-making.'
        }
    }

    merged['Recommended Course'] = merged['Skill'].map(lambda x: course_dict.get(x, {}).get('Title', ''))
    merged['Course Summary'] = merged['Skill'].map(lambda x: course_dict.get(x, {}).get('Summary', ''))

    st.sidebar.header("Filter Employees")
    dept_filter = st.sidebar.multiselect("Select Department", options=merged["Department"].unique())
    role_filter = st.sidebar.multiselect("Select Role", options=merged["Role"].unique())

    filtered_data = merged.copy()
    if dept_filter:
        filtered_data = filtered_data[filtered_data["Department"].isin(dept_filter)]
    if role_filter:
        filtered_data = filtered_data[filtered_data["Role"].isin(role_filter)]

    gap_df = filtered_data[filtered_data["Gap"] > 0]

    tabs = st.tabs(["📊 Skill Gaps", "📥 Training Plan", "📌 Summary Stats", "📈 Charts"])

    with tabs[0]:
        st.subheader("Employees with Skill Gaps")
        st.dataframe(gap_df[['Employee Name', 'Emp ID', 'Role', 'Skill', 'Gap', 'Recommended Course']], use_container_width=True)

    with tabs[1]:
        st.subheader("Download Training Plan")
        plan_df = gap_df[['Employee Name', 'Emp ID', 'Role', 'Skill', 'Gap', 'Recommended Course', 'Course Summary']]
        st.download_button(
            label="📥 Download Training Plan (Excel)",
            data=plan_df.to_csv(index=False, encoding='utf-8'),
            file_name="training_plan.csv",
            mime="text/csv"
        )

    with tabs[2]:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='metric-box'>Total Employees<br><span style='font-size: 28px;'>{len(df)}</span></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-box'>Employees with Gaps<br><span style='font-size: 28px;'>{gap_df['Emp ID'].nunique()}</span></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-box'>Training Interventions<br><span style='font-size: 28px;'>{gap_df.shape[0]}</span></div>", unsafe_allow_html=True)

    with tabs[3]:
        st.subheader("Visual Analysis")
        skill_gap_chart = gap_df.groupby('Skill').size().reset_index(name='Gap Count')
        fig1 = px.bar(skill_gap_chart, x='Skill', y='Gap Count', title='Skill-Wise Gaps', color='Gap Count', color_continuous_scale='peach')
        st.plotly_chart(fig1, use_container_width=True)

        dept_gap_chart = gap_df.groupby('Department').size().reset_index(name='Employees with Gaps')
        fig2 = px.bar(dept_gap_chart, x='Department', y='Employees with Gaps', title='Department-wise Gaps', color='Employees with Gaps', color_continuous_scale='teal')
        st.plotly_chart(fig2, use_container_width=True)

        role_chart = gap_df.groupby('Role').size().reset_index(name='Training Gaps')
        fig3 = px.pie(role_chart, names='Role', values='Training Gaps', title='Role-Wise Skill Gaps', hole=0.4)
        st.plotly_chart(fig3, use_container_width=True)
