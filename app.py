# HR Skill Gap Dashboard with Enhanced UI: Floating Sidebar, Animated Charts, Tab Icons, and Dropdown Navigation

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_lottie import st_lottie
import requests

# ---------- Load Lottie Animation ----------
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

hr_animation = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_jcikwtux.json")  # Safe HR animation

# ---------- Page Style ----------
st.set_page_config(page_title="HR Skill Gap Dashboard", layout="wide")

st.markdown("""
    <style>
    .block-container {
        padding: 2rem 2rem 1rem 2rem;
        background: linear-gradient(to right, #f5f7fa, #c3cfe2);
    }
    .st-emotion-cache-1avcm0n {
        background-color: rgba(255, 255, 255, 0.7);
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        padding: 2rem 1.5rem;
        margin: 1rem;
    }
    .metric-box {
        background: #ffffffcc;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.06);
        text-align: center;
    }
    h1, h4 {
        text-align: center;
        color: #2f3542;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Header with Animation ----------
if hr_animation:
    st_lottie(hr_animation, speed=1, height=180, key="hr-header")
else:
    st.warning("⚠️ Animation failed to load. Check your internet connection.")

st.markdown("""
    <h1>💼 HR Skill Gap Dashboard</h1>
    <h4>Engineered by Akanksha Sahani • Empowering People Through Data</h4>
    <hr style='border: 1px solid #dfe6e9;'>
""", unsafe_allow_html=True)

# ---------- File Upload ----------
st.markdown("### 📄 Upload Skill Data")
emp_file = st.file_uploader("Upload Employee Skills CSV", type=["csv"])
req_file = st.file_uploader("Upload Required Skills CSV", type=["csv"])

# ---------- Process Data ----------
if emp_file and req_file:
    df = pd.read_csv(emp_file)
    required = pd.read_csv(req_file)

    df.columns = df.columns.str.strip()
    required.columns = required.columns.str.strip()

    merged = pd.merge(df, required, on=['Role', 'Skill'])
    merged['Gap'] = merged['Required Rating'] - merged['Self Rating']
    merged = merged.loc[:, ~merged.columns.str.contains('^Unnamed')]

    # ✅ Dynamic Sidebar Filters
    st.sidebar.markdown("## 🔍 Filter Employees")
    dept_options = ['All'] + sorted(merged['Department'].dropna().unique().tolist())
    role_options = ['All'] + sorted(merged['Role'].dropna().unique().tolist())

    dept_filter = st.sidebar.selectbox("Select Department", options=dept_options)
    role_filter = st.sidebar.selectbox("Select Role", options=role_options)

    # Apply filters
    if dept_filter != "All":
        merged = merged[merged["Department"] == dept_filter]
    if role_filter != "All":
        merged = merged[merged["Role"] == role_filter]

    gap_df = merged[merged['Gap'] > 0]

    # ---------- Tabs with Icons ----------
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Skill Gaps", "📥 Training Plan", "📌 Summary", "📈 Charts"])

    # ---------- Skill Gaps ----------
    with tab1:
        st.subheader("🚨 Employees with Skill Gaps")
        st.dataframe(gap_df[['Employee Name', 'Emp ID', 'Role', 'Skill', 'Gap']], use_container_width=True)

    # ---------- Training Plan ----------
    with tab2:
        course_dict = {
            'Excel': 'Advanced Excel – Coursera',
            'Communication': 'Effective Communication – Udemy',
            'Python': 'Python for Beginners – Coursera',
            'Safety': 'Industrial Safety – NPTEL',
            'Leadership': 'Leadership Essentials – LinkedIn Learning'
        }
        gap_df['Recommended Course'] = gap_df['Skill'].map(lambda x: course_dict.get(x, ''))

        st.dataframe(gap_df[['Employee Name', 'Skill', 'Gap', 'Recommended Course']], use_container_width=True)
        st.download_button("📥 Download Training Plan", gap_df.to_csv(index=False), file_name="training_plan.csv")

    # ---------- Summary ----------
    with tab3:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Employees", len(df))
        col2.metric("Employees with Gaps", gap_df['Emp ID'].nunique())
        col3.metric("Total Gaps Found", gap_df.shape[0])

    # ---------- Animated Charts ----------
    with tab4:
        st.subheader("📈 Visual Analysis")

        skill_chart = px.bar(
            gap_df.groupby('Skill').size().reset_index(name='Gap Count'),
            x='Skill', y='Gap Count', color='Gap Count',
            color_continuous_scale='sunset',
            title="Skill-Wise Gaps with Animation"
        )
        skill_chart.update_traces(marker_line_width=1.5)
        st.plotly_chart(skill_chart, use_container_width=True)

        dept_chart = px.bar(
            gap_df.groupby('Department').size().reset_index(name='Employees with Gaps'),
            x='Department', y='Employees with Gaps',
            color='Employees with Gaps', color_continuous_scale='teal',
            title="Department-wise Gaps"
        )
        st.plotly_chart(dept_chart, use_container_width=True)

        pie_chart = px.pie(
            gap_df.groupby('Role').size().reset_index(name='Count'),
            names='Role', values='Count', hole=0.4,
            title="Role-Wise Training Needs"
        )
        st.plotly_chart(pie_chart, use_container_width=True)
