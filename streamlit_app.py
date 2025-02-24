import streamlit as st
import pandas as pd
import sqlite3
import os

# Membuat koneksi ke database SQLite
# Pastikan file database tersimpan di direktori yang bisa diakses
db_path = "project_plans.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Membuat tabel jika belum ada
c.execute('''CREATE TABLE IF NOT EXISTS project_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul_plan TEXT,
                kelas TEXT,
                jenis_plan TEXT,
                status TEXT,
                nama_koordinasi TEXT
             )''')
conn.commit()

# Form untuk menambah project plan baru
st.subheader("Tambah Project Plan Baru")
with st.form(key='add_plan_form'):
    judul = st.text_input("Judul Plan")
    kelas = st.text_input("Kelas")
    jenis_plan = st.selectbox("Jenis Plan", ['Dev', 'QC'])
    status = st.selectbox("Status", ['Done', 'Revision', 'OK'])
    nama_koordinasi = st.text_input("Nama Koordinasi")
    
    submit_button = st.form_submit_button(label="Tambah Plan")

    if submit_button:
        c.execute('''
            INSERT INTO project_plans (judul_plan, kelas, jenis_plan, status, nama_koordinasi)
            VALUES (?, ?, ?, ?, ?)
        ''', (judul, kelas, jenis_plan, status, nama_koordinasi))
        conn.commit()
        st.success("Project plan berhasil ditambahkan!")

# Menampilkan data project plan
c.execute('SELECT * FROM project_plans')
data_db = c.fetchall()
df = pd.DataFrame(data_db, columns=['ID', 'Judul Plan', 'Kelas', 'Jenis Plan', 'Status', 'Nama Koordinasi'])
st.write(df)

# Fitur pencarian
search_term = st.text_input("Cari berdasarkan Judul Plan atau Koordinasi")
if search_term:
    filtered_data = df[df['Judul Plan'].str.contains(search_term, case=False) | df['Nama Koordinasi'].str.contains(search_term, case=False)]
else:
    filtered_data = df
st.write(filtered_data)

# Export data ke CSV dengan download button
csv = df.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='project_plans.csv',
    mime='text/csv'
)
