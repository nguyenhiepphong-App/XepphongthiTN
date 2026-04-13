import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Xếp Phòng Thi 2026", layout="centered")
st.title("📑 Phần mềm Xếp Phòng Thi THPT 2026")

uploaded_file = st.file_uploader("Chọn file Excel (Cột 'Hoten' và 'Tohop')", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    if 'Hoten' in df.columns and 'Tohop' in df.columns:
        def split_name(name):
            parts = str(name).strip().split()
            if len(parts) == 0: return "", ""
            ten = parts[-1].lower()
            ho_dem = " ".join(parts[:-1]).lower()
            return ten, ho_dem

        # 1. Gán SBD theo ABC Tên > Họ đệm
        df[['Ten_T', 'Ho_T']] = df['Hoten'].apply(lambda x: pd.Series(split_name(x)))
        df = df.sort_values(by=['Ten_T', 'Ho_T']).reset_index(drop=True)
        df['Số báo danh'] = [str(i).zfill(3) for i in range(1, len(df) + 1)]

        # 2. Xử lý tổ hợp và ca thi
        df[['Môn thi ca 1', 'Môn thi ca 2']] = df['Tohop'].str.split('-', expand=True)
        counts = df['Tohop'].value_counts().reset_index()
        counts.columns = ['Tohop', 'SoLuong']
        df = df.merge(counts, on='Tohop')

        # 3. Sắp xếp chia phòng (Tổ hợp đông nhất -> SBD)
        df_sorted = df.sort_values(by=['SoLuong', 'Tohop', 'Số báo danh'], ascending=[False, True, True]).reset_index(drop=True)
        df_sorted['Phòng'] = (df_sorted.index // 24) + 1
        
        df_final = df_sorted.drop(columns=['Ten_T', 'Ho_T', 'SoLuong'])

        st.success("✅ Đã xử lý xong!")
        st.dataframe(df_final.head(10))

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False)
        st.download_button(label="📥 Tải file kết quả", data=output.getvalue(), file_name="ket_qua_2026.xlsx")
    else:
        st.error("Lỗi: File thiếu cột 'Hoten' hoặc 'Tohop'.")
