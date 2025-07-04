import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth
from utils.analytics import *

# ✅ NEW FORMAT LOGIN SETUP
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

name, authentication_status, username = authenticator.login(location='main')


if authentication_status == False:
    st.error('Username/password is incorrect')

if authentication_status == None:
    st.warning('Please enter your username and password')

if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f'Welcome {name}! 👋')

    st.title("👩‍💼 Workforce Analytics System")

    df = pd.read_csv('data/workforce_data.csv')

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
