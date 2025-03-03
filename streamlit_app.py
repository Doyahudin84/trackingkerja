import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Daftar nama bulan dalam bahasa Indonesia
bulan_indonesia = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni", 
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

# Mendapatkan bulan sekarang
current_month = datetime.now().month  # Mengambil bulan dalam angka (1-12)

# Global variable for storing the dataframe
df = None

st.title("Project Plan Management Doyahudin")
# Menampilkan bulan sekarang dengan nama bulan dalam bahasa Indonesia dan bold
st.markdown(f"### **{bulan_indonesia[current_month - 1]}**")

# Sidebar
st.sidebar.title("Menu")
sidebar_option = st.sidebar.radio("", ['Lihat Data', 'Tambah Plan', 'Edit & Hapus Plan', 'Export Data', "Dashboard"])

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

def save_data_to_excel(df):
    # Pastikan file ditulis dengan benar
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

# Upload Excel file
uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])
if uploaded_file:
    # Read the uploaded file into a dataframe
    df = pd.read_excel(uploaded_file)

# If no file is uploaded, show a message
if df is None:
    st.error("Please upload an Excel file to proceed.")
    st.stop()

# Check the dataframe columns
if not all(col in df.columns for col in ['ID', 'Judul Plan', 'Kelas', 'Jenis Plan', 'Status', 'Nama Koordinasi']):
    st.error("Excel file must contain the following columns: 'ID', 'Judul Plan', 'Kelas', 'Jenis Plan', 'Status', 'Nama Koordinasi'.")
    st.stop()

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
            new_id = df['ID'].max() + 1 if not df.empty else 1
            new_plan = {
                'ID': new_id,
                'Judul Plan': judul,
                'Kelas': kelas,
                'Jenis Plan': jenis_plan,
                'Status': status,
                'Nama Koordinasi': nama_koordinasi
            }
            df = df.append(new_plan, ignore_index=True)
            st.success("Project plan berhasil ditambahkan!")

elif sidebar_option == 'Edit & Hapus Plan':
    st.subheader("Edit atau Hapus Project Plan")
    
    # Edit
    edit_id = st.number_input("Masukkan ID Project Plan yang ingin diedit", min_value=1, step=1)
    if edit_id:
        project_plan = df[df['ID'] == edit_id]
        
        if not project_plan.empty:
            edit_judul = st.text_input("Judul Plan", value=project_plan['Judul Plan'].iloc[0])
            edit_kelas = st.text_input("Kelas", value=project_plan['Kelas'].iloc[0])  
            status_options = ['Done', 'Revision', 'OK', 'On Progress', 'Not Yet']
            edit_status = st.selectbox("Status", status_options, index=status_options.index(project_plan['Status'].iloc[0]))
            edit_jenis_plan = st.selectbox("Jenis Plan", ['Dev', 'QC'], index=['Dev', 'QC'].index(project_plan['Jenis Plan'].iloc[0]))
            edit_nama_koordinasi = st.text_input("Nama Koordinasi", value=project_plan['Nama Koordinasi'].iloc[0])
            
            edit_button = st.button("Simpan Perubahan")
            
            if edit_button:
                df.loc[df['ID'] == edit_id, ['Judul Plan', 'Kelas', 'Jenis Plan', 'Status', 'Nama Koordinasi']] = \
                    [edit_judul, edit_kelas, edit_jenis_plan, edit_status, edit_nama_koordinasi]
                st.success(f"Project plan dengan ID {edit_id} berhasil diperbarui!")
        else:
            st.error(f"Project plan dengan ID {edit_id} tidak ditemukan!")
    
    # Hapus
    delete_id = st.number_input("Masukkan ID Project Plan yang ingin dihapus", min_value=1, step=1)
    if st.button("Hapus Project Plan"):
        if delete_id in df['ID'].values:
            df = df[df['ID'] != delete_id]
            st.success(f"Project plan dengan ID {delete_id} berhasil dihapus!")
        else:
            st.error("ID tidak valid!")

elif sidebar_option == 'Lihat Data':
    # Menampilkan data project plan
    if not df.empty:
        # Terapkan warna ke setiap baris berdasarkan status
        styled_df = df.style.applymap(lambda status: row_color(status), subset=['Status'])
        st.write(styled_df)
    else:
        st.error("No data available!")

elif sidebar_option == 'Export Data':
    st.subheader("Download file dalam bentuk excel")
    # Export data ke Excel
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
        st.error("No data to export!")

elif sidebar_option == 'Dashboard':
    st.subheader("Dashboard Persentase Status Berdasarkan Jenis Plan")

    if not df.empty:
        # Menghitung persentase setiap status untuk masing-masing jenis plan
        status_jenis_counts = df.groupby(['Jenis Plan', 'Status']).size().unstack(fill_value=0)
        total_per_jenis_plan = status_jenis_counts.sum(axis=1)
        status_jenis_percentage = status_jenis_counts.divide(total_per_jenis_plan, axis=0) * 100

        st.write("Persentase Status Berdasarkan Jenis Plan:")
        st.write(status_jenis_percentage)

        # Grafik bar per status dan jenis plan
        st.bar_chart(status_jenis_percentage)
    else:
        st.error("No data available for dashboard!")
