import streamlit as st
import pandas as pd
from datetime import datetime
import openpyxl
import io

# Daftar nama bulan dalam bahasa Indonesia
bulan_indonesia = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni", 
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

# Mendapatkan bulan sekarang
current_month = datetime.now().month  # Mengambil bulan dalam angka (1-12)

st.title("Project Plan Management Doyahudin")
# Menampilkan bulan sekarang dengan nama bulan dalam bahasa Indonesia dan bold
st.markdown(f"### **{bulan_indonesia[current_month - 1]}**")

# Sidebar
st.sidebar.title("Menu")
sidebar_option = st.sidebar.radio("", ['Lihat Data', 'Tambah Plan', 'Edit & Hapus Plan', 'Export Data', 'Dashboard'])

# Path to Excel file
EXCEL_FILE = 'project_plans.xlsx'

# Load data from Excel into DataFrame
def load_data_from_excel():
    try:
        # If file doesn't exist, create one
        df = pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['ID', 'Judul Plan', 'Kelas', 'Jenis Plan', 'Status', 'Nama Koordinasi'])
    return df

# Function to save data back to Excel
def save_data_to_excel(df):
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

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
            df = load_data_from_excel()
            new_id = df['ID'].max() + 1 if not df.empty else 1  # Create new ID
            new_row = {
                'ID': new_id,
                'Judul Plan': judul,
                'Kelas': kelas,
                'Jenis Plan': jenis_plan,
                'Status': status,
                'Nama Koordinasi': nama_koordinasi
            }
            df = df.append(new_row, ignore_index=True)
            save_data_to_excel(df)
            st.success("Project plan berhasil ditambahkan!")

elif sidebar_option == 'Edit & Hapus Plan':
    # Edit dan Hapus Project Plan
    st.subheader("Edit atau Hapus Project Plan")
    
    # Edit
    edit_id = st.number_input("Masukkan ID Project Plan yang ingin diedit", min_value=1, step=1)
    if edit_id:
        df = load_data_from_excel()
        project_plan = df[df['ID'] == edit_id]
        
        if not project_plan.empty:
            edit_judul = st.text_input("Judul Plan", value=project_plan['Judul Plan'].values[0])
            edit_kelas = st.text_input("Kelas", value=project_plan['Kelas'].values[0])  # Menggunakan text_input
            
            # Menambahkan pengecekan untuk memastikan nilai status_valid
            status_options = ['Done', 'Revision', 'OK', 'On Progress', 'Not Yet']
            status_value = project_plan['Status'].values[0]
            edit_status = st.selectbox("Status", status_options, index=status_options.index(status_value))
            edit_jenis_plan = st.selectbox("Jenis Plan", ['Dev', 'QC'], index=['Dev', 'QC'].index(project_plan['Jenis Plan'].values[0]))
            edit_nama_koordinasi = st.text_input("Nama Koordinasi", value=project_plan['Nama Koordinasi'].values[0])
            
            edit_button = st.button("Simpan Perubahan")
            
            if edit_button:
                df.loc[df['ID'] == edit_id, ['Judul Plan', 'Kelas', 'Jenis Plan', 'Status', 'Nama Koordinasi']] = \
                    [edit_judul, edit_kelas, edit_jenis_plan, edit_status, edit_nama_koordinasi]
                save_data_to_excel(df)
                st.success(f"Project plan dengan ID {edit_id} berhasil diperbarui!")
        else:
            st.error(f"Project plan dengan ID {edit_id} tidak ditemukan!")
    
    # Hapus
    delete_id = st.number_input("Masukkan ID Project Plan yang ingin dihapus", min_value=1, step=1)
    if st.button("Hapus Project Plan"):
        if delete_id:
            df = load_data_from_excel()
            if delete_id in df['ID'].values:
                df = df[df['ID'] != delete_id]
                save_data_to_excel(df)
                st.success(f"Project plan dengan ID {delete_id} berhasil dihapus!")
            else:
                st.error(f"Project plan dengan ID {delete_id} tidak ditemukan!")
        else:
            st.error("ID tidak valid!")

elif sidebar_option == 'Lihat Data':
    # Menampilkan data project plan
    df = load_data_from_excel()
    if not df.empty:
        # Terapkan warna ke setiap baris berdasarkan status
        styled_df = df.style.applymap(lambda status: row_color(status), subset=['Status'])
        
        # Tampilkan tabel dengan warna
        st.write(styled_df)
    else:
        st.warning("Tidak ada data yang tersedia!")

elif sidebar_option == 'Export Data':
    st.subheader("Download file dalam bentuk excel")
    
    # Export data ke Excel
    df = load_data_from_excel()
    
    if not df.empty:
        excel_file = io.BytesIO()
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Project Plans')

        # Kembalikan pointer file ke awal
        excel_file.seek(0)

        # Tombol untuk download file Excel
        st.download_button(
            label="Download",
            data=excel_file,
            file_name="project_plans.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Tidak ada data untuk di-export!")

elif sidebar_option == 'Dashboard':
    # Dashboard Persentase Status dan Jenis Plan
    st.subheader("Dashboard Persentase Status Berdasarkan Jenis Plan")

    # Ambil data dari Excel
    df = load_data_from_excel()

    if not df.empty:
        # Menghitung persentase setiap status untuk masing-masing jenis plan
        status_jenis_counts = df.groupby(['Jenis Plan', 'Status']).size().unstack(fill_value=0)

        # Hitung total per jenis plan
        total_per_jenis_plan = status_jenis_counts.sum(axis=1)

        # Hitung persentase per status untuk tiap jenis plan
        status_jenis_percentage = status_jenis_counts.divide(total_per_jenis_plan, axis=0) * 100

        st.write("Persentase Status Berdasarkan Jenis Plan:")
        st.write(status_jenis_percentage)

        # Grafik bar per status dan jenis plan
        st.bar_chart(status_jenis_percentage)
    else:
        st.warning("Tidak ada data untuk ditampilkan di dashboard!")
