import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ----------------------------------------------------
# Fungsi buat label Ranking
# ----------------------------------------------------
def get_rank_labels(n):
    if n <= 0:
        return []
    if n == 1:
        return ["Tertinggi"]
    if n == 2:
        return ["Tertinggi", "Terendah"]
    if n == 3:
        return ["Tertinggi", "Tertinggi ke-2", "Terendah"]
    if n == 4:
        return ["Tertinggi", "Tertinggi ke-2", "Tertinggi ke-3", "Terendah"]
    # n >= 5
    return ["Tertinggi", "Tertinggi ke-2", "Tertinggi ke-3", "Tertinggi ke-4", "Terendah"]


# ----------------------------------------------------
# Load Data Excel
# ----------------------------------------------------
file_paths = {
    2020: "2020.xlsx",
    2021: "2021.xlsx",
    2022: "2022.xlsx",
    2023: "2023.xlsx",
    2024: "2024.xlsx"
}
data = {year: pd.read_excel(path) for year, path in file_paths.items()}

# ROP Existing
rop_existing = pd.read_excel("rop existing_fix.xlsx")

# Lead time 2024 => Book1.xlsx, 2023 => Book2.xlsx
lead_time_data_2024 = pd.read_excel("Book1.xlsx")
lead_time_data_2023 = pd.read_excel("Book2.xlsx")

# Pastikan kolom lead_time numerik
for df_lead in [lead_time_data_2024, lead_time_data_2023]:
    df_lead['lead_time_minimal'] = pd.to_numeric(df_lead['lead_time_minimal'], errors='coerce')
    df_lead['lead_time_avg'] = pd.to_numeric(df_lead['lead_time_avg'], errors='coerce')
    df_lead['lead_time_maximal'] = pd.to_numeric(df_lead['lead_time_maximal'], errors='coerce')


# ----------------------------------------------------
# Set Page Config
# ----------------------------------------------------
st.set_page_config(
    page_title="Dashboard Visualisasi Evaluasi ROP Warehouse",
    page_icon="l.web.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ----------------------------------------------------
# CSS Kustom
# ----------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* Header Utama dengan Gradient */
.main-header {
    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
    padding: 30px;
    border-radius: 10px;
    text-align: center;
    color: #ffffff; /* Ubah warna teks menjadi putih untuk kontras */
    margin-bottom: 40px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

/* Container Kartu */
.card-container {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

/* DataFrame Styling */
.dataframe {
    margin: auto;
    border-collapse: collapse;
    width: 100%;
}

.dataframe th {
    background-color: #2c3e50;
    color: #ffffff;
    text-align: center;
    font-weight: 600;
    padding: 10px;
}

.dataframe tr:hover {
    background-color: #f1f1f1;
    transition: all 0.2s ease-in-out;
}

.dataframe td {
    padding: 10px;
    text-align: center;
}

/* Judul Bagian dengan Gradient */
.title-section-bg {
    background: linear-gradient(45deg, #ff7e5f, #feb47b);
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 15px;
}

.title-section-bg h2 {
    margin: 0;
    font-weight: 600;
    display: inline-block;
    padding: 5px 10px;
    color: #ffffff; /* Ubah warna teks menjadi putih untuk kontras */
}

/* Judul Bagian tanpa Background */
.title-section-no-bg {
    text-align: center;
    margin-bottom: 15px;
}

.title-section-no-bg h3, .title-section-no-bg h4 {
    margin: 0;
    font-weight: 600;
    display: inline-block;
    padding: 5px 10px;
    color: #333333;
}

.title-section-no-bg h3:hover, .title-section-no-bg h4:hover {
    color: #555555;
}

/* Note Section */
.note-section p {
    background-color: #fff3cd;
    color: #856404;
    padding: 10px;
    border-left: 5px solid #ffeeba;
    border-radius: 5px;
    font-weight: 500;
}

/* Informasi Tambahan Section */
.info-section p {
    background-color: #d4edda;
    color: #155724;
    padding: 10px;
    border-left: 5px solid #c3e6cb;
    border-radius: 5px;
    font-weight: 500;
}

/* Footer */
.footer-section {
    text-align: center;
    margin-top: 30px;
    color: #999999;
}

.footer-section hr {
    margin: 20px 0;
    border: none;
    border-top: 1px solid #ddd;
}

/* Subtitle Styling */
.subtitle {
    font-size: 14px;
    color: #666666;
    margin-bottom: 15px;
}

/* Responsive Title Sizes */
@media (max-width: 768px) {
    .title-section-bg h2 {
        font-size: 1.5em;
    }
    .title-section-no-bg h3 {
        font-size: 1.3em;
    }
    .title-section-no-bg h4 {
        font-size: 1.1em;
    }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)



# ----------------------------------------------------
# Sidebar
# ----------------------------------------------------
st.sidebar.image("654db0b264142 (1).webp", width=120)
st.sidebar.title("📊 PT Bakrie Pipe Industries")
st.sidebar.subheader("Dashboard Visualisasi Evaluasi ROP Warehouse")

# Filter Options
months = [
    "Januari", "Februari", "Maret", "April", "Mei",
    "Juni", "Juli", "Agustus", "September",
    "Oktober", "November", "Desember"
]
years = list(data.keys())

nobar_input = st.sidebar.text_input("Masukkan Nomor Barang:")
selected_months = st.sidebar.multiselect("Pilih Bulan:", ["Semua Bulan"] + months, default="Semua Bulan")
selected_years = st.sidebar.multiselect("Pilih Tahun:", years, default=years)


# ----------------------------------------------------
# Handle Search
# ----------------------------------------------------
if st.sidebar.button("Search"):
    if not nobar_input:
        st.warning("Nomor barang wajib diisi sebelum klik tombol search.")
    else:
        # Filter Data
        filtered_data = []
        for year in selected_years:
            df = data[year].copy()
            if 'tanggal' not in df.columns:
                st.error(f"Kolom 'tanggal' tidak ditemukan di data tahun {year}.")
                continue
            df['tanggal'] = pd.to_datetime(df['tanggal'], format='%d/%m/%Y', errors='coerce')
            df = df[df['nobar'].astype(str).str.contains(nobar_input, case=False, na=False)]

            if "Semua Bulan" not in selected_months:
                m_indices = [months.index(m) + 1 for m in selected_months if m in months]
                df = df[df['tanggal'].dt.month.isin(m_indices)]

            filtered_data.append(df)

        if len(filtered_data) > 0:
            filtered_data = pd.concat(filtered_data)
        else:
            filtered_data = pd.DataFrame()

        # Judul Hasil Pencarian dengan Background
        st.markdown("""
        <div class="title-section-bg">
            <h2>🎯 Berikut Hasil Data Berdasarkan Pencarian Anda!</h2>
        </div>
        """, unsafe_allow_html=True)

        if filtered_data.empty:
            st.warning("Tidak ada data untuk filter yang dipilih.")
        else:
            # Detail Barang
            first_row = filtered_data.iloc[0]
            nobar_value = first_row.get("nobar", "")
            nabar_value = first_row.get("nabar", "nabar TIDAK ADA")
            satuan_value = first_row.get("satuan", "satuan TIDAK ADA")

            st.write(f"**Nomor Barang:** {nobar_value} | **Nama Barang:** {nabar_value} | **Satuan:** {satuan_value}")

            # ------------------------------------------------
            # CARD - Data Pemakaian per Tahun
            # ------------------------------------------------
            st.markdown(f"<div style='border: 1px solid #000000; padding: 10px; margin-bottom: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
            st.markdown("""
            
                <div class="title-section-no-bg">
                    <h3>📊 Data Pemakaian per Tahun</h3>
                </div>
            """, unsafe_allow_html=True)

            # Hitung Usage
            usage_per_year = []
            for y in selected_years:
                val = filtered_data[filtered_data['tanggal'].dt.year == y]['jumlah'].sum()
                usage_per_year.append(val)

            pakai_per_bulan = [v / 12 for v in usage_per_year]
            pakai_per_minggu = [v / 4.29 for v in pakai_per_bulan]
            pakai_per_hari_avg = [v / 7 for v in pakai_per_minggu]
            pakai_per_hari_min = [v * 0.5 for v in pakai_per_hari_avg]
            pakai_per_hari_max = [v * 1.5 for v in pakai_per_hari_avg]

            # Ranking
            usage_dict = dict(zip(selected_years, usage_per_year))
            sorted_usage = sorted(usage_dict.items(), key=lambda x: x[1], reverse=True)
            rank_labels = get_rank_labels(len(sorted_usage))
            rank_dict = {}
            for i, (yr, val) in enumerate(sorted_usage):
                rank_dict[yr] = rank_labels[i] if i < len(rank_labels) else "-"

            keterangan_pemakaian = [rank_dict[y] for y in selected_years]

            usage_cols = ["Keterangan"] + [str(y) for y in selected_years]
            usage_rows = [
                ["Pemakaian Mutasi 1 th"] + usage_per_year,
                ["Pakai per bulan"] + pakai_per_bulan,
                ["Pakai per minggu"] + pakai_per_minggu,
                ["Pakai per hari (Avg)"] + pakai_per_hari_avg,
                ["Pakai per hari (Min)"] + pakai_per_hari_min,
                ["Pakai per hari (Max)"] + pakai_per_hari_max,
                ["Keterangan Pemakaian"] + keterangan_pemakaian
            ]
            df_pemakaian = pd.DataFrame(usage_rows, columns=usage_cols)

            def highlight_pemakaian(row):
                k_val = row["Keterangan"]
                if k_val == "Keterangan Pemakaian":
                    row_styles = ['background-color: #d4edda'] * len(row)
                    for i in range(1, len(row)):
                        val_text = str(row[i]).lower()
                        if val_text.startswith("tertinggi ke-4"):
                            row_styles[i] = 'background-color: #42a5f5'
                        elif val_text.startswith("tertinggi ke-3"):
                            row_styles[i] = 'background-color: #1e88e5'
                        elif val_text.startswith("tertinggi ke-2"):
                            row_styles[i] = 'background-color: #1565c0; color: #ffffff;'
                        elif val_text == "tertinggi":
                            row_styles[i] = 'background-color: #0d47a1; color: #ffffff;'
                        elif val_text == "terendah":
                            row_styles[i] = 'background-color: #bbdefb'
                        else:
                            row_styles[i] = 'background-color: #ffffff'
                    return row_styles
                else:
                    idx = row.name
                    if idx < 6:
                        return ['background-color: #fff3cd'] * len(row)
                    else:
                        return ['background-color: #d4edda'] * len(row)

            styled_pemakaian = df_pemakaian.style.apply(highlight_pemakaian, axis=1)
            st.write(styled_pemakaian)
            st.markdown('</div>', unsafe_allow_html=True)

            # ------------------------------------------------
            # CARD - Evaluasi Level Order (2024)
            #   TABEL di kiri, INFORMASI di kanan
            # ------------------------------------------------
            st.markdown(f"<div style='border: 1px solid #000000; padding: 10px; margin-bottom: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
            st.markdown("""
            
                <div class="title-section-no-bg">
                    <h3>🔍 Evaluasi Level Order (2024)</h3>
                </div>
                <div class="subtitle">Note: Menggunakan perhitungan Lead Time 2024</div>
            """, unsafe_allow_html=True)

            colEvLeft2024, colEvRight2024 = st.columns([2, 1])

            # Lead Time 2024
            lt_2024 = lead_time_data_2024[lead_time_data_2024['nobar'].astype(str).str.contains(nobar_input, case=False, na=False)]
            if not lt_2024.empty:
                lt_min_2024 = lt_2024.iloc[0]['lead_time_minimal']
                lt_avg_2024 = lt_2024.iloc[0]['lead_time_avg']
                lt_max_2024 = lt_2024.iloc[0]['lead_time_maximal']
            else:
                lt_min_2024 = lt_avg_2024 = lt_max_2024 = 0

            # ROP Existing
            rop_24 = rop_existing[rop_existing['nobar'].astype(str).str.contains(nobar_input, case=False, na=False)]
            if not rop_24.empty:
                rop_val_2024 = rop_24.iloc[0]['Rop Existing']
            else:
                rop_val_2024 = "Data tidak ditemukan"

            usage_rounded = [round(v, 2) for v in usage_per_year]
            rop_vals_2024 = [round(pakai_per_hari_max[i] * lt_max_2024) for i in range(len(selected_years))]
            min_stock_2024 = [
                rop_vals_2024[i] - round(pakai_per_hari_avg[i] * lt_avg_2024)
                for i in range(len(selected_years))
            ]
            order_qty_2024 = [
                round((rop_vals_2024[i] - round(pakai_per_hari_avg[i] * lt_avg_2024)) * 2)
                for i in range(len(selected_years))
            ]
            max_stock_2024 = []
            for i in range(len(selected_years)):
                v_24 = rop_vals_2024[i] + order_qty_2024[i] - round(pakai_per_hari_min[i] * lt_min_2024)
                max_stock_2024.append(round(v_24))

            # TABEL 2024
            with colEvLeft2024:
                eval_cols_2024 = ["Keterangan"] + [str(y) for y in selected_years]
                eval_rows_2024 = [
                    ["Pemakaian Mutasi 1 th"] + usage_rounded,
                    ["ROP"] + rop_vals_2024,
                    ["Min Stock"] + min_stock_2024,
                    ["Order Qty"] + order_qty_2024,
                    ["Max Stock"] + max_stock_2024,
                    ["Keterangan Pemakaian"] + keterangan_pemakaian
                ]
                df_eval_2024 = pd.DataFrame(eval_rows_2024, columns=eval_cols_2024)

                def highlight_eval_2024(row):
                    k_val = row["Keterangan"]
                    if k_val == "Keterangan Pemakaian":
                        row_styles = ['background-color: #d4edda'] * len(row)
                        for i in range(1, len(row)):
                            val_text = str(row[i]).lower()
                            if val_text.startswith("tertinggi ke-4"):
                                row_styles[i] = 'background-color: #42a5f5'
                            elif val_text.startswith("tertinggi ke-3"):
                                row_styles[i] = 'background-color: #1e88e5'
                            elif val_text.startswith("tertinggi ke-2"):
                                row_styles[i] = 'background-color: #1565c0; color: #ffffff;'
                            elif val_text == "tertinggi":
                                row_styles[i] = 'background-color: #0d47a1; color: #ffffff;'
                            elif val_text == "terendah":
                                row_styles[i] = 'background-color: #bbdefb'
                            else:
                                row_styles[i] = 'background-color: #ffffff'
                        return row_styles
                    elif k_val == "Pemakaian Mutasi 1 th":
                        return ['background-color: #fff3cd'] * len(row)
                    else:
                        return ['background-color: #d4edda'] * len(row)

                styled_eval_2024 = df_eval_2024.style.apply(highlight_eval_2024, axis=1)
                st.write(styled_eval_2024)

            # INFORMASI (2024) di kolom kanan
            with colEvRight2024:
                st.markdown("""
                <div class="info-section">
                    <strong>Informasi Tambahan (2024)</strong>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"**ROP Existing:** {rop_val_2024}")
                st.markdown(f"**Lead Time Minimal:** {lt_min_2024} hari")
                st.markdown(f"**Lead Time Rata-rata:** {lt_avg_2024} hari")
                st.markdown(f"**Lead Time Maksimal:** {lt_max_2024} hari")

            st.markdown('</div>', unsafe_allow_html=True)

            # ------------------------------------------------
            # CARD - Evaluasi Level Order (2023)
            #   TABEL di kiri, INFORMASI di kanan
            # ------------------------------------------------
            st.markdown(f"<div style='border: 1px solid #000000; padding: 10px; margin-bottom: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
            st.markdown("""
            
                <div class="title-section-no-bg">
                    <h3>🔍 Evaluasi Level Order (2023)</h3>
                </div>
                <div class="subtitle">Note: Menggunakan perhitungan Lead Time 2023</div>
            """, unsafe_allow_html=True)

            colEvLeft2023, colEvRight2023 = st.columns([2, 1])

            # Lead Time 2023
            lt_2023 = lead_time_data_2023[lead_time_data_2023['nobar'].astype(str).str.contains(nobar_input, case=False, na=False)]
            if not lt_2023.empty:
                lt_min_2023 = lt_2023.iloc[0]['lead_time_minimal']
                lt_avg_2023 = lt_2023.iloc[0]['lead_time_avg']
                lt_max_2023 = lt_2023.iloc[0]['lead_time_maximal']
            else:
                lt_min_2023 = lt_avg_2023 = lt_max_2023 = 0

            # Tabel Evaluasi 2023
            with colEvLeft2023:
                rop_2023 = [round(pakai_per_hari_max[i] * lt_max_2023) for i in range(len(selected_years))]
                min_stock_2023 = [
                    rop_2023[i] - round(pakai_per_hari_avg[i] * lt_avg_2023)
                    for i in range(len(selected_years))
                ]
                order_qty_2023 = [
                    round((rop_2023[i] - round(pakai_per_hari_avg[i] * lt_avg_2023)) * 2)
                    for i in range(len(selected_years))
                ]
                max_stock_2023 = []
                for i in range(len(selected_years)):
                    v_23 = rop_2023[i] + order_qty_2023[i] - round(pakai_per_hari_min[i] * lt_min_2023)
                    max_stock_2023.append(round(v_23))

                eval_cols_2023 = ["Keterangan"] + [str(y) for y in selected_years]
                eval_rows_2023 = [
                    ["Pemakaian Mutasi 1 th"] + usage_rounded,
                    ["ROP"] + rop_2023,
                    ["Min Stock"] + min_stock_2023,
                    ["Order Qty"] + order_qty_2023,
                    ["Max Stock"] + max_stock_2023,
                    ["Keterangan Pemakaian"] + keterangan_pemakaian
                ]
                df_eval_2023 = pd.DataFrame(eval_rows_2023, columns=eval_cols_2023)

                def highlight_eval_2023(row):
                    k_val = row["Keterangan"]
                    if k_val == "Keterangan Pemakaian":
                        row_styles = ['background-color: #d4edda'] * len(row)
                        for i in range(1, len(row)):
                            val_text = str(row[i]).lower()
                            if val_text.startswith("tertinggi ke-4"):
                                row_styles[i] = 'background-color: #42a5f5'
                            elif val_text.startswith("tertinggi ke-3"):
                                row_styles[i] = 'background-color: #1e88e5'
                            elif val_text.startswith("tertinggi ke-2"):
                                row_styles[i] = 'background-color: #1565c0; color: #ffffff;'
                            elif val_text == "tertinggi":
                                row_styles[i] = 'background-color: #0d47a1; color: #ffffff;'
                            elif val_text == "terendah":
                                row_styles[i] = 'background-color: #bbdefb'
                            else:
                                row_styles[i] = 'background-color: #ffffff'
                        return row_styles
                    elif k_val == "Pemakaian Mutasi 1 th":
                        return ['background-color: #fff3cd'] * len(row)
                    else:
                        return ['background-color: #d4edda'] * len(row)

                styled_eval_2023 = df_eval_2023.style.apply(highlight_eval_2023, axis=1)
                st.write(styled_eval_2023)

            # INFORMASI 2023 di kolom kanan
            with colEvRight2023:
                st.markdown("""
                <div class="info-section">
                    <strong>Informasi Tambahan (2023)</strong>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"**ROP Existing:** {rop_val_2024}")  # Asumsi ROP Existing sama untuk 2023
                st.markdown(f"**Lead Time Minimal:** {lt_min_2023} hari")
                st.markdown(f"**Lead Time Rata-rata:** {lt_avg_2023} hari")
                st.markdown(f"**Lead Time Maksimal:** {lt_max_2023} hari")

            st.markdown('</div>', unsafe_allow_html=True)

            # ------------------------------------------------
            # CARD - Visualisasi
            # ------------------------------------------------
            st.markdown(f"<div style='border: 1px solid #000000; padding: 10px; margin-bottom: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
            st.markdown("""
            <div class="card-container">
                <div class="title-section-no-bg">
                    <h3>📈 Visualisasi Data</h3>
                </div>
            <div style="text-align: center; margin-bottom: 20px;">
                <p>
                    Di bawah ini, Anda akan menemukan berbagai visualisasi yang dirancang untuk memberikan wawasan mendalam tentang tren dan pola penggunaan barang selama beberapa tahun terakhir. Visualisasi ini mencakup total barang keluar per bulan dan tren perubahan barang keluar dari waktu ke waktu. Dengan data ini, Anda dapat dengan mudah mengidentifikasi periode dengan permintaan tinggi atau rendah, serta memahami dinamika inventaris Anda secara keseluruhan.
                </p>
            </div>
            """, unsafe_allow_html=True)


            # 1) Total Barang Keluar per Bulan
            st.markdown(f"<div style='border: 1px solid #000000; padding: 10px; margin-bottom: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
            st.markdown("""
            <div class="title-section-no-bg">
                <h4>📦 Total Barang Keluar per Bulan</h4>
            </div>
            """, unsafe_allow_html=True)
            fig = make_subplots(rows=1, cols=len(selected_years),
                                subplot_titles=[str(y) for y in selected_years])
            for i, year in enumerate(selected_years):
                if year in filtered_data['tanggal'].dt.year.unique():
                    yearly_data = filtered_data[filtered_data['tanggal'].dt.year == year]
                    monthly_data = yearly_data.groupby(yearly_data['tanggal'].dt.month)['jumlah'].sum().reset_index()
                    monthly_data['tanggal'] = monthly_data['tanggal'].apply(lambda x: months[x-1] if x-1 < len(months) else x)
                    fig.add_trace(
                        go.Bar(x=monthly_data['tanggal'], y=monthly_data['jumlah'], name=str(year)),
                        row=1, col=i+1
                    )
            fig.update_layout(title_text="Total Barang Keluar per Bulan", showlegend=False, height=400)
            st.plotly_chart(fig)
            
            st.markdown(
            f"""<div style=>
            <b style='color:#000000;'>Penjelasan:</b> Grafik ini menampilkan jumlah keseluruhan barang yang dikeluarkan dari inventaris setiap bulan, memberikan wawasan mengenai fluktuasi permintaan dan membantu dalam mengidentifikasi tren permintaan sepanjang tahun. Informasi ini sangat penting untuk mengelola stok gudang secara efisien sesuai dengan kebutuhan yang diajukan oleh para pekerja produksi di PT Bakrie Pipe Industries.
            </div>""",
            unsafe_allow_html=True
            )

            # 2) Tren Barang Keluar per Bulan
            st.markdown(f"<div style='border: 1px solid #000000; padding: 10px; margin-bottom: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
            st.markdown("""
            <div class="title-section-no-bg">
                <h4>📉 Tren Barang Keluar per Bulan</h4>
            </div>
            """, unsafe_allow_html=True)
            fig2 = make_subplots(rows=1, cols=len(selected_years),
                                 subplot_titles=[str(y) for y in selected_years])
            for i, year in enumerate(selected_years):
                if year in filtered_data['tanggal'].dt.year.unique():
                    yearly_data = filtered_data[filtered_data['tanggal'].dt.year == year]
                    monthly_trend = yearly_data.groupby(yearly_data['tanggal'].dt.month)['jumlah'].sum().reset_index()
                    monthly_trend['tanggal'] = monthly_trend['tanggal'].apply(lambda x: months[x-1] if x-1 < len(months) else x)
                    fig2.add_trace(
                        go.Scatter(x=monthly_trend['tanggal'], y=monthly_trend['jumlah'],
                                   mode='lines+markers', name=str(year)),
                        row=1, col=i+1
                    )
            fig2.update_layout(title_text="Tren Barang Keluar per Bulan", showlegend=False, height=400)
            st.plotly_chart(fig2)

            st.markdown(
            f"""<div style=>
            <b style='color:#000000;'>Penjelasan:</b> Grafik ini menunjukkan pola pergerakan barang yang keluar dari inventaris seiring waktu, memungkinkan identifikasi pola musiman serta analisis perubahan dalam volume pengeluaran. Data ini krusial untuk memastikan ketersediaan stok gudang yang sesuai dengan permintaan produksi, sehingga para pekerja produksi di PT Bakrie Pipe Industries dapat bekerja dengan lancar tanpa kendala terkait ketersediaan bahan baku.
            </div>""",
            unsafe_allow_html=True
            )

            st.markdown('</div>', unsafe_allow_html=True)

else:
    # Halaman awal (belum klik search)
    st.markdown("""
    <div class="main-header">
        <h1>🌟 Selamat Datang di Smart Inventory Management (Evaluasi ROP)</h1>
        <p>Warehouse PT Bakrie Pipe Industries</p>
        <p><b>Hari ini:</b> """ + datetime.now().strftime('%A, %d %B %Y') + """</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("Gunakan filter di sebelah kiri, lalu klik tombol 'Search' untuk **mulai!**")


# (Opsional) Footer
st.markdown("""
<div class="footer-section">
    <hr>
    <p>© 2025 - PT Bakrie Pipe Industries. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)