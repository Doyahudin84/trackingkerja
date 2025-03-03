import streamlit as st
import pandas as pd
from datetime import datetime
import openpyxl
import io


# Definisikan path untuk file Excel
EXCEL_FILE = "project_plans.xlsx"

# Fungsi untuk memuat data dari Excel
def load_data_from_excel():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        return df
    else:
        # Jika file tidak ada, buat dataframe kosong
        return pd.DataFrame(columns=['ID', 'Judul Plan', 'Kelas', 'Jenis Plan', 'Status', 'Nama Koordinasi'])

# Fungsi untuk menyimpan data ke Excel
def save_data_to_excel(df):
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

# Fungsi utama untuk aplikasi Streamlit
def main():
    st.title("Project Plan Manager")

    # Sidebar untuk navigasi
    sidebar_option = st.sidebar.selectbox('Pilih Menu', ['Tambah Plan', 'Tampil Plan', 'Edit & Hapus Plan'])

    if sidebar_option == 'Tambah Plan':
        # Tambah Project Plan Baru
        st.subheader("Tambah Project Plan")
        judul_plan = st.text_input("Judul Plan")
        kelas = st.text_input("Kelas")
        jenis_plan = st.selectbox("Jenis Plan", ['Dev', 'QC'])
        status = st.selectbox("Status", ['Done', 'Revision', 'OK', 'On Progress', 'Not Yet'])
        nama_koordinasi = st.text_input("Nama Koordinasi")

        if st.button("Simpan Plan"):
            # Load data dari file Excel
            df = load_data_from_excel()

            # Menentukan ID otomatis berdasarkan jumlah data
            new_id = df['ID'].max() + 1 if not df.empty else 1

            # Menambahkan baris baru ke dataframe
            new_plan = {
                'ID': new_id,
                'Judul Plan': judul_plan,
                'Kelas': kelas,
                'Jenis Plan': jenis_plan,
                'Status': status,
                'Nama Koordinasi': nama_koordinasi
            }

            df = df.append(new_plan, ignore_index=True)

            # Simpan ke file Excel
            save_data_to_excel(df)

            st.success(f"Project plan '{judul_plan}' berhasil ditambahkan!")

    elif sidebar_option == 'Tampil Plan':
        # Tampilkan Semua Project Plan
        st.subheader("Tampil Semua Project Plan")

        df = load_data_from_excel()
        if not df.empty:
            st.dataframe(df)
        else:
            st.warning("Tidak ada data untuk ditampilkan!")

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
                edit_kelas = st.text_input("Kelas", value=project_plan['Kelas'].values[0])
                
                status_value = project_plan['Status'].values[0]
                edit_status = st.selectbox("Status", ['Done', 'Revision', 'OK', 'On Progress', 'Not Yet'], index=['Done', 'Revision', 'OK', 'On Progress', 'Not Yet'].index(status_value))
                edit_jenis_plan = st.selectbox("Jenis Plan", ['Dev', 'QC'], index=['Dev', 'QC'].index(project_plan['Jenis Plan'].values[0]))
                edit_nama_koordinasi = st.text_input("Nama Koordinasi", value=project_plan['Nama Koordinasi'].values[0])
                
                edit_button = st.button("Simpan Perubahan")
                
                if edit_button:
                    # Update data dalam dataframe
                    df.loc[df['ID'] == edit_id, ['Judul Plan', 'Kelas', 'Jenis Plan', 'Status', 'Nama Koordinasi']] = \
                        [edit_judul, edit_kelas, edit_jenis_plan, edit_status, edit_nama_koordinasi]
                    
                    # Simpan kembali ke Excel
                    save_data_to_excel(df)
                    
                    # Berikan umpan balik ke user
                    st.success(f"Project plan dengan ID {edit_id} berhasil diperbarui!")
                    
                    # Muat ulang halaman untuk memperbarui data yang ditampilkan
                    st.experimental_rerun()  # Ini akan me-refresh tampilan agar data yang baru muncul

        # Hapus
        delete_id = st.number_input("Masukkan ID Project Plan yang ingin dihapus", min_value=1, step=1)
        if st.button("Hapus Project Plan"):
            if delete_id:
                df = load_data_from_excel()
                if delete_id in df['ID'].values:
                    df = df[df['ID'] != delete_id]
                    save_data_to_excel(df)
                    st.success(f"Project plan dengan ID {delete_id} berhasil dihapus!")
                    st.experimental_rerun()  # Muat ulang halaman setelah penghapusan
                else:
                    st.error(f"Project plan dengan ID {delete_id} tidak ditemukan!")
            else:
                st.error("ID tidak valid!")

if __name__ == "__main__":
    main()

