import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# Function to fetch data from the SQLite database
def fetch_data():
    conn = sqlite3.connect('medicine_data.db')
    query = "SELECT * FROM detections"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Fetch data from the database
data = fetch_data()

# Check if data is available
if not data.empty:
    st.title("Detected Medicines")

    # Summary statistics
    st.subheader("Summary Statistics")
    total_detections = data.shape[0]
    most_frequent_medicine = data['nama_obat'].mode()[0]
    st.write(f"Total Detections: {total_detections}")
    st.write(f"Most Frequently Detected Medicine: {most_frequent_medicine}")

    # Date range filter
    st.subheader("Filter Data")
    start_date = st.date_input("Start Date", value=pd.to_datetime(data['timestamp']).min().date())
    end_date = st.date_input("End Date", value=pd.to_datetime(data['timestamp']).max().date())
    filtered_data = data[(pd.to_datetime(data['timestamp']).dt.date >= start_date) &
                         (pd.to_datetime(data['timestamp']).dt.date <= end_date)]

    # Interactive pie chart with Plotly
    st.subheader("Pie Chart of Detected Medicines")
    top_n = st.slider("Select Top N Medicines to Display", min_value=1, max_value=20, value=10)
    nama_obat_counts = filtered_data['nama_obat'].value_counts().nlargest(top_n)
    fig = px.pie(nama_obat_counts, values=nama_obat_counts, names=nama_obat_counts.index, title='Detected Medicines')
    st.plotly_chart(fig)

    # Table display with search functionality
    st.subheader("Detection Details")
    search_term = st.text_input("Search for a specific 'Nama Obat'")
    if search_term:
        filtered_data = filtered_data[filtered_data['nama_obat'].str.contains(search_term, case=False, na=False)]
    st.dataframe(filtered_data[['timestamp', 'nama_obat', 'jenis_takaran', 'efek_samping', 'indikasi']])

    # Download data as CSV
    st.subheader("Download Filtered Data")
    csv = filtered_data.to_csv(index=False)
    st.download_button(label="Download as CSV", data=csv, file_name='filtered_data.csv', mime='text/csv')
else:
    st.write("No data available in the database.")

# Run this script with `streamlit run streamlit_app.py`
