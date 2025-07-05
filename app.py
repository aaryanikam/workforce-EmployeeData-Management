import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth
import base64
from utils.pdf_export import generate_summary_pdf
from utils.analytics import *
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import sqlite3

# --- LOGIN SETUP ---
credentials = {
    "usernames": {
        "aarya": {
            "name": "Aarya Nikam",
            "password": "12345"  # For production, use hashed password
        }
    }
}

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name='workforce_dashboard',
    key='abcdef',
    cookie_expiry_days=1
)

authenticator.login(location='main')
authentication_status = st.session_state["authentication_status"]

if authentication_status:
    name = st.session_state["name"]
    username = st.session_state["username"]
    authenticator.logout("Logout", "sidebar", key="logout-btn")
    st.sidebar.success(f"Welcome {name} \U0001F44B")

    # --- MAIN APP STARTS ---
    st.title("\U0001F469‍\U0001F4BC Workforce Analytics System")

    conn = sqlite3.connect('data/workforce.db')
    df = pd.read_sql_query("SELECT * FROM workforce", conn)

    st.sidebar.header("\U0001F50D Filter Employee Data")

    # Filter: Department
    dept_options = df['Department'].unique().tolist()
    selected_dept = st.sidebar.selectbox("Department", ["All"] + dept_options)

    # Filter: Status
    status_options = df['Status'].unique().tolist()
    selected_status = st.sidebar.selectbox("Status", ["All"] + status_options)

    # Filter: Gender
    gender_options = sorted(df['Gender'].dropna().unique().tolist())
    if "Male" not in gender_options:
        gender_options.append("Male")
    if "Female" not in gender_options:
        gender_options.append("Female")
    selected_gender = st.sidebar.selectbox("Gender", ["All"] + gender_options)

    # Apply filters
    if selected_dept != "All":
        df = df[df['Department'] == selected_dept]
    if selected_status != "All":
        df = df[df['Status'] == selected_status]
    if selected_gender != "All":
        df = df[df['Gender'] == selected_gender]

    # --- Dashboard Data ---
    st.header("1️⃣ Raw Employee Data")
    st.dataframe(df)

    st.header("2️⃣ Summary")
    total, active, resigned = get_summary(df)
    st.write(f"Total Employees: {total}")
    st.write(f"Active Employees: {active}")
    st.write(f"Resigned Employees: {resigned}")

    st.header("3️⃣ Department-wise Employee Count")
    st.bar_chart(department_distribution(df))

    st.header("4️⃣ Gender Ratio")
    gender = gender_ratio(df)
    fig, ax = plt.subplots()
    ax.pie(gender, labels=gender.index, autopct='%1.1f%%')
    st.pyplot(fig)

    st.header("5️⃣ Average Salary by Department")
    st.bar_chart(average_salary_by_dept(df))

    # --- Add New Employee ---
    st.sidebar.header("➕ Add New Employee")
    with st.sidebar.form("add_employee_form"):
        emp_id = st.number_input("Employee ID", step=1)
        name = st.text_input("Name")
        age = st.number_input("Age", step=1)
        gender = st.selectbox("Gender", ["Male", "Female"])
        department = st.selectbox("Department", ["HR", "IT", "Sales"])
        join_date = st.date_input("Join Date")
        resign_date = st.date_input("Resign Date", disabled=True)
        status = st.selectbox("Status", ["Active", "Resigned"])
        salary = st.number_input("Salary", step=1000)
        location = st.text_input("Location")

        submit = st.form_submit_button("Add Employee")

        if submit:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO workforce VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                emp_id, name, age, gender, department,
                str(join_date), str(resign_date) if resign_date else "",
                status, salary, location
            ))
            conn.commit()
            st.success(f"Employee {name} added successfully!")
            st.experimental_rerun()

    # --- Export Summary PDF ---
    st.subheader("📄 Export Summary Report")
    if st.button("Download Summary PDF"):
        pdf_path = "summary_report.pdf"
        generate_summary_pdf(pdf_path, total, active, resigned)
        with open(pdf_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
            href = f'<a href="data:application/pdf;base64,{base64_pdf}" download="summary_report.pdf">📥 Click here to download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

elif authentication_status is False:
    st.error("❌ Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
