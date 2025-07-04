import pandas as pd

def get_summary(df):
    total = len(df)
    active = df[df['Status'] == 'Active'].shape[0]
    resigned = df[df['Status'] == 'Resigned'].shape[0]
    return total, active, resigned

def department_distribution(df):
    return df['Department'].value_counts()

def gender_ratio(df):
    return df['Gender'].value_counts()

def average_salary_by_dept(df):
    return df.groupby('Department')['Salary'].mean()
