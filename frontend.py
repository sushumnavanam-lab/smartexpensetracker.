import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# --- 1️⃣ Setup SQLite database ---
conn = sqlite3.connect("expenses.db", check_same_thread=False)
c = conn.cursor()

# Create table if not exists
c.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    category TEXT,
    amount REAL,
    date TEXT
)
''')
conn.commit()

# --- 2️⃣ Functions to interact with DB ---
def add_expense(title, category, amount, date):
    c.execute("INSERT INTO expenses (title, category, amount, date) VALUES (?,?,?,?)",
              (title, category, amount, str(date)))
    conn.commit()

def get_expenses():
    c.execute("SELECT * FROM expenses")
    data = c.fetchall()
    df = pd.DataFrame(data, columns=["id","title","category","amount","date"])
    if not df.empty:
        df['amount'] = df['amount'].astype(float)
        df['date'] = pd.to_datetime(df['date'])
    return df

def delete_expense(expense_id):
    c.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()

# --- 3️⃣ Streamlit UI ---
st.set_page_config(page_title="Smart Expense Tracker", layout="wide")
st.title("💰 Smart Expense Tracker Dashboard")

# --- Add Expense Form ---
with st.form("add_expense"):
    st.subheader("Add New Expense")
    title = st.text_input("Title")
    amount = st.number_input("Amount", min_value=0.0, step=0.1)
    category = st.selectbox("Category", ["Food","Travel","Bills","Shopping","Others"])
    date = st.date_input("Date")
    submitted = st.form_submit_button("Add Expense")
    
    if submitted:
        if not title or amount <= 0:
            st.warning("Enter valid title and amount")
        else:
            add_expense(title, category, amount, date)
            st.success("✅ Expense added!")

# --- Fetch and display expenses ---
df = get_expenses()

if not df.empty:
    # --- Filters ---
    st.subheader("Filters")
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.selectbox("Filter by Category", ["All"] + df['category'].unique().tolist())
    with col2:
        start_date = st.date_input("Start Date", df['date'].min())
        end_date = st.date_input("End Date", df['date'].max())

    filtered_df = df.copy()
    if filter_category != "All":
        filtered_df = filtered_df[filtered_df['category'] == filter_category]
    filtered_df = filtered_df[(filtered_df['date'] >= pd.to_datetime(start_date)) & 
                              (filtered_df['date'] <= pd.to_datetime(end_date))]

    # --- Display Table ---
    st.subheader("All Expenses")
    st.dataframe(filtered_df[['id','title','category','amount','date']])

    # --- Delete Expense ---
    st.subheader("Delete Expense")
    if not filtered_df.empty:
        delete_id = st.selectbox("Select ID to Delete", filtered_df['id'])
        if st.button("Delete Expense"):
            delete_expense(delete_id)
            st.success("✅ Expense deleted!")
            st.experimental_rerun()  # Refresh app to show updates
    else:
        st.info("No expenses to delete in this filter.")

    # --- Total Spending ---
    total_spent = filtered_df['amount'].sum()
    st.subheader(f"💵 Total Spending: {total_spent:.2f}")

    # --- Category-wise Charts ---
    if not filtered_df.empty:
        cat_summary = filtered_df.groupby('category')['amount'].sum().reset_index()

        st.subheader("Category-wise Spending Table")
        st.dataframe(cat_summary)

        # Bar Chart
        fig_bar = px.bar(cat_summary, x='category', y='amount',
                         title="Spending by Category",
                         color='category', text='amount')
        st.plotly_chart(fig_bar, use_container_width=True)

        # Pie Chart
        fig_pie = px.pie(cat_summary, names='category', values='amount',
                         title="Category Distribution",
                         hole=0.3)  # Donut chart
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No data to display charts.")
else:
    st.info("No expenses recorded yet.")