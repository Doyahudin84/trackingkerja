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
    kelas = st.text_input("Kelas")  # Menggunakan text_input
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

# Fitur Delete (Hapus)
st.subheader("Hapus Project Plan")
delete_id = st.number_input("Masukkan ID Project Plan yang ingin dihapus", min_value=1, step=1)
if st.button("Hapus Project Plan"):
    if delete_id:
        c.execute("DELETE FROM project_plans WHERE id=?", (delete_id,))
        conn.commit()
        st.success(f"Project plan dengan ID {delete_id} berhasil dihapus!")
    else:
        st.error("ID tidak valid!")

# Fitur Edit (Ubah)
st.subheader("Edit Project Plan")
edit_id = st.number_input("Masukkan ID Project Plan yang ingin diedit", min_value=1, step=1)
if edit_id:
    c.execute("SELECT * FROM project_plans WHERE id=?", (edit_id,))
    project_plan = c.fetchone()
    
    if project_plan:
        edit_judul = st.text_input("Judul Plan", value=project_plan[1])
        edit_kelas = st.text_input("Kelas", value=project_plan[2])  # Menggunakan text_input
        edit_jenis_plan = st.selectbox("Jenis Plan", ['Dev', 'QC'], index=['Dev', 'QC'].index(project_plan[3]))
        edit_status = st.selectbox("Status", ['Done', 'Revision', 'OK'], index=['Done', 'Revision', 'OK'].index(project_plan[4]))
        edit_nama_koordinasi = st.text_input("Nama Koordinasi", value=project_plan[5])
        
        edit_button = st.button("Simpan Perubahan")
        
        if edit_button:
            c.execute('''
                UPDATE project_plans 
                SET judul_plan = ?, kelas = ?, jenis_plan = ?, status = ?, nama_koordinasi = ?
                WHERE id = ?
            ''', (edit_judul, edit_kelas, edit_jenis_plan, edit_status, edit_nama_koordinasi, edit_id))
            conn.commit()
            st.success(f"Project plan dengan ID {edit_id} berhasil diperbarui!")
    else:
        st.error(f"Project plan dengan ID {edit_id} tidak ditemukan!")

# Export data ke CSV dengan download button
csv = df.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='project_plans.csv',
    mime='text/csv'
)

