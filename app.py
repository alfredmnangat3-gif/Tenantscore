import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- DATABASE SETUP ---
conn = sqlite3.connect('tenants.db', check_same_thread=False)
c = conn.cursor()

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS tenants 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, unit TEXT, phone TEXT, email TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS maintenance 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, unit TEXT, issue TEXT, status TEXT, date TEXT)''')
conn.commit()

# --- APP UI ---
st.set_page_config(page_title="Tenant Management System", layout="wide")
st.title("🏢 Tenant Management System")

menu = ["Dashboard", "Manage Tenants", "Maintenance Log"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Dashboard":
    st.subheader("Overview")
    c.execute("SELECT COUNT(*) FROM tenants")
    tenant_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM maintenance WHERE status='Open'")
    open_issues = c.fetchone()[0]
    
    col1, col2 = st.columns(2)
    col1.metric("Total Tenants", tenant_count)
    col2.metric("Open Maintenance Issues", open_issues)

elif choice == "Manage Tenants":
    st.subheader("Add New Tenant")
    with st.form("tenant_form"):
        name = st.text_input("Tenant Name")
        unit = st.text_input("Unit Number")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email Address")
        submitted = st.form_submit_button("Add Tenant")
        
        if submitted:
            c.execute("INSERT INTO tenants (name, unit, phone, email) VALUES (?, ?, ?, ?)",
                      (name, unit, phone, email))
            conn.commit()
            st.success(f"Added {name} to Unit {unit}!")

    st.subheader("Current Tenants")
    df = pd.read_sql_query("SELECT * FROM tenants", conn)
    st.dataframe(df, use_container_width=True)

elif choice == "Maintenance Log":
    st.subheader("Report an Issue")
    with st.form("maint_form"):
        unit = st.text_input("Unit Number")
        issue = st.text_area("Describe the issue")
        submitted = st.form_submit_button("Log Issue")
        
        if submitted:
            date = datetime.now().strftime("%Y-%m-%d")
            c.execute("INSERT INTO maintenance (unit, issue, status, date) VALUES (?, ?, 'Open', ?)",
                      (unit, issue, date))
            conn.commit()
            st.success("Issue logged!")

    st.subheader("Maintenance History")
    df_maint = pd.read_sql_query("SELECT * FROM maintenance", conn)
    st.dataframe(df_maint, use_container_width=True)