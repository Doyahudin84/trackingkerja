import streamlit as st
import pandas as pd
import sqlite3
import os
import io
import openpyxl
import matplotlib.pyplot as plt

# Membuat koneksi ke database SQLite
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

st.title("Project Plan Management Doyahudin")

# Sidebar
st.sidebar.title("Menu")
sidebar_option = st.sidebar.radio("", [ 'Lihat Data','Tambah Plan', 'Edit & Hapus Plan', 'Export Data',"Dashboard"])

# Fungsi untuk menampilkan tabel dengan warna berdasarkan status
def row_color(status):
    if status == "Done":
        return 'background-color: #4CAF50; color: white;'  # Green
    elif status == "Revision":
        return 'background-color: #FFEB3B; color: black;'  # Yellow
    elif status == "OK":
        return 'background-color: #2196F3; color: white;'  # Blue
    elif status == "On Progress":
        return 'background-color: #FF9800; color: white;'  # Orange
    elif status == "Not Yet":
        return 'background-color: #f44336; color: white;'  # Red
    return ''  # Default

# Tampilan berdasarkan opsi sidebar yang dipilih
if sidebar_option == 'Tambah Plan':
    st.subheader("Tambah Project Plan Baru")
    with st.form(key='add_plan_form'):
        judul = st.text_input("Judul Plan")
        kelas = st.text_input("Kelas")  # Menggunakan text_input
        jenis_plan = st.selectbox("Jenis Plan", ['Dev', 'QC'])
        
        # Menambahkan status baru (On Progress dan Not Yet)
        status_options = ['Done', 'Revision', 'OK', 'On Progress', 'Not Yet']
        status = st.selectbox("Status", status_options)
        
        nama_koordinasi = st.text_input("Nama Koordinasi")
        
        submit_button = st.form_submit_button(label="Tambah Plan")

        if submit_button:
            c.execute('''
                INSERT INTO project_plans (judul_plan, kelas, jenis_plan, status, nama_koordinasi)
                VALUES (?, ?, ?, ?, ?)
            ''', (judul, kelas, jenis_plan, status, nama_koordinasi))
            conn.commit()
            st.success("Project plan berhasil ditambahkan!")

elif sidebar_option == 'Edit & Hapus Plan':
    # Edit dan Hapus Project Plan
    st.subheader("Edit atau Hapus Project Plan")
    
    # Edit
    edit_id = st.number_input("Masukkan ID Project Plan yang ingin diedit", min_value=1, step=1)
    if edit_id:
        c.execute("SELECT * FROM project_plans WHERE id=?", (edit_id,))
        project_plan = c.fetchone()
        
        if project_plan:
            edit_judul = st.text_input("Judul Plan", value=project_plan[1])
            edit_kelas = st.text_input("Kelas", value=project_plan[2])  # Menggunakan text_input
            
            # Menambahkan pengecekan untuk memastikan nilai status_valid
            status_options = ['Done', 'Revision', 'OK', 'On Progress', 'Not Yet']
            status_value = project_plan[4]
            
            if status_value not in status_options:
                status_value = 'Done'
            
            edit_status = st.selectbox("Status", status_options, index=status_options.index(status_value))
            edit_jenis_plan = st.selectbox("Jenis Plan", ['Dev', 'QC'], index=['Dev', 'QC'].index(project_plan[3]))
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
    
    # Hapus
    delete_id = st.number_input("Masukkan ID Project Plan yang ingin dihapus", min_value=1, step=1)
    if st.button("Hapus Project Plan"):
        if delete_id:
            c.execute("DELETE FROM project_plans WHERE id=?", (delete_id,))
            conn.commit()
            st.success(f"Project plan dengan ID {delete_id} berhasil dihapus!")
        else:
            st.error("ID tidak valid!")

elif sidebar_option == 'Lihat Data':
    # Menampilkan data project plan
    c.execute('SELECT * FROM project_plans')
    data_db = c.fetchall()
    df = pd.DataFrame(data_db, columns=['ID', 'Judul Plan', 'Kelas', 'Jenis Plan', 'Status', 'Nama Koordinasi'])

    # Terapkan warna ke setiap baris berdasarkan status
    styled_df = df.style.applymap(lambda status: row_color(status), subset=['Status'])
    
    # Tampilkan tabel dengan warna
    st.write(styled_df)



elif sidebar_option == 'Export Data':
    # Export data ke Excel
    # Buat file Excel menggunakan Pandas dan Openpyxl
    c.execute('SELECT * FROM project_plans')
    data_db = c.fetchall()
    df = pd.DataFrame(data_db, columns=['ID', 'Judul Plan', 'Kelas', 'Jenis Plan', 'Status', 'Nama Koordinasi'])

    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Project Plans')

    # Kembalikan pointer file ke awal
    excel_file.seek(0)

    # Tombol untuk download file Excel
    st.download_button(
        label="Download Excel",
        data=excel_file,
        file_name="project_plans.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif sidebar_option == 'Dashboard':
    # Dashboard Persentase Status Berdasarkan Jenis Plan
    st.subheader("Dashboard Persentase Status Berdasarkan Jenis Plan")

    # Ambil data dari database
    c.execute('SELECT status, jenis_plan FROM project_plans')
    data_db = c.fetchall()
    
    # Mengubah data menjadi DataFrame
    status_jenis_df = pd.DataFrame(data_db, columns=['Status', 'Jenis Plan'])

    # Filter status "OK" dan "Not Yet"
    status_filter = status_jenis_df[status_jenis_df['Status'].isin(['OK', 'Not Yet'])]

    # Hitung persentase OK dan Not Yet
    status_counts = status_filter['Status'].value_counts()
    total = status_counts.sum()

    # Menghitung persentase
    status_percentage = (status_counts / total) * 100

    # Tampilkan Persentase OK dan Not Yet dalam Pie Chart
    labels = status_percentage.index
    sizes = status_percentage.values
    colors = ['#4CAF50', '#f44336']  # Hijau untuk OK dan Merah untuk Not Yet

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')  # Equal aspect ratio ensures that pie chart is drawn as a circle.

    # Tampilkan pie chart
    st.pyplot(fig)
