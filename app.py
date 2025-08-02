import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth
import base64
from utils.pdf_export import generate_summary_pdf
from utils.analytics import *

# --- LOGIN SETUP ---
credentials = {
    "usernames": {
        "aarya": {
            "name": "Aarya Nikam",
            "password": "$2b$12$cTFh0Vukq08Rl/jv9ktxS.uXfnWRE2pG2mmc2yCerP7uCY9Bckiim",  # hashed password
            "role": "admin"
        }
    }
}

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name='workforce_dashboard',
    key='abcdef',
    cookie_expiry_days=1
)

# ✅ Login box
name, authentication_status, username = authenticator.login(form_name='Login', location='main')

# ✅ Show login messages
if authentication_status:
    st.success(f"Welcome {name}")
elif authentication_status is False:
    st.error("Incorrect username or password")
elif authentication_status is None:
    st.warning("Enter your credentials")

# ✅ Logged-in user content
if authentication_status:
    authenticator.logout("Logout", location="sidebar", key="logout-btn")
    st.sidebar.success(f"Welcome {name} 👋")

    st.title("👩‍💼 Workforce Analytics System")

    # --- Load data from CSV ---
    csv_file = 'data/workforce_data.csv'   # ✅ correct file name
    df = pd.read_csv(csv_file)

    # --- Sidebar filters ---
    st.sidebar.header("🔍 Filter Employee Data")
    dept_options = df['Department'].unique().tolist()
    selected_dept = st.sidebar.selectbox("Department", ["All"] + dept_options)

    status_options = df['Status'].unique().tolist()
    selected_status = st.sidebar.selectbox("Status", ["All"] + status_options)

    gender_options = sorted(df['Gender'].dropna().unique().tolist())
    selected_gender = st.sidebar.selectbox("Gender", ["All"] + gender_options)

    # --- Apply filters ---
    filtered_df = df.copy()
    if selected_dept != "All":
        filtered_df = filtered_df[filtered_df['Department'] == selected_dept]
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]
    if selected_gender != "All":
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]

    # --- Dashboard Sections ---
    st.header("1️⃣ Raw Employee Data")
    st.dataframe(filtered_df)

    st.header("2️⃣ Summary")
    total, active, resigned = get_summary(filtered_df)
    st.write(f"Total Employees: {total}")
    st.write(f"Active Employees: {active}")
    st.write(f"Resigned Employees: {resigned}")

    st.header("3️⃣ Department-wise Employee Count")
    st.bar_chart(department_distribution(filtered_df))

    st.header("4️⃣ Gender Ratio")
    gender = gender_ratio(filtered_df)
    fig, ax = plt.subplots()
    ax.pie(gender, labels=gender.index, autopct='%1.1f%%')
    st.pyplot(fig)

    st.header("5️⃣ Average Salary by Department")
    st.bar_chart(average_salary_by_dept(filtered_df))

    # --- Add New Employee Form ---
    st.sidebar.header("➕ Add New Employee")
    with st.sidebar.form("add_employee_form"):
        emp_id = st.number_input("Employee ID", step=1, format="%d")
        emp_name = st.text_input("Name")
        age = st.number_input("Age", step=1, format="%d")
        gender = st.selectbox("Gender", ["Male", "Female"])
        department = st.selectbox("Department", sorted(df['Department'].unique().tolist()))
        join_date = st.date_input("Join Date")
        resign_date = st.date_input("Resign Date (if resigned)", disabled=True)
        status = st.selectbox("Status", ["Active", "Resigned"])
        salary = st.number_input("Salary", step=1000, format="%d")
        location = st.text_input("Location")

        submit = st.form_submit_button("Add Employee")

        if submit:
            new_row = {
                'Emp_ID': emp_id,
                'Name': emp_name,
                'Age': age,
                'Gender': gender,
                'Department': department,
                'Join_Date': str(join_date),
                'Resign_Date': str(resign_date) if status == "Resigned" else "",
                'Status': status,
                'Salary': salary,
                'Location': location
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(csv_file, index=False)
            st.success(f"Employee {emp_name} added successfully!")
            st.experimental_rerun()

    # --- Export PDF ---
    st.subheader("📄 Export Summary Report")
    if st.button("Download Summary PDF"):
        pdf_path = "summary_report.pdf"
        generate_summary_pdf(pdf_path, total, active, resigned)
        with open(pdf_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
            href = f'<a href="data:application/pdf;base64,{base64_pdf}" download="summary_report.pdf">📥 Click here to download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
