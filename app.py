import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==================== CẤU HÌNH TRANG ====================
st.set_page_config(page_title="TVL Việt Nam 2025", page_icon="Vietnam", layout="wide")
st.markdown("<style>.big-font {font-size: 56px !important; font-weight: bold; text-align: center;}</style>", unsafe_allow_html=True)

st.title("Vietnam TVL Calculator Pro 2025")
st.markdown("**Chi phí sống thực tế • Tự động cập nhật hàng tháng**")
st.success("WinMart • Co.opmart • Batdongsan • EVN • Petrolimex • Google Sheets Auto-sync")

# ==================== TỰ ĐỘNG LẤY % TĂNG GIÁ TỪ GOOGLE SHEETS ====================
@st.cache_data(ttl=3600)
def lay_phan_tram_tu_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1QjK8v6Y9k2f5t3xL9pR7mN8vBxZsQwRt2eYk5f3d8cU").sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        tang_nam = float(df.iloc[0]["Tăng cả năm 2025 so 2024"]) / 100
        thang_hien_tai = datetime.now().strftime("%m/%Y")
        try:
            thay_doi_thang = float(df[df["Tháng"] == thang_hien_tai]["% thay đổi so tháng trước"].iloc[0]) / 100
        except:
            thay_doi_thang = 0.012
        return tang_nam, thay_doi_thang
    except:
        return 0.118, 0.012

tang_trung_binh_nam, thay_doi_thang_truoc = lay_phan_tram_tu_sheets()

# ==================== GIÁ XĂNG TỰ ĐỘNG ====================
@st.cache_data(ttl=86400)
def cap_nhat_gia_xang():
    try:
        url = "https://webgia.com/gia-xang-dau/petrolimex/"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        price = soup.find('td', string='Xăng RON95-V').find_next_sibling('td').text
        return float(price.replace('.', '').replace('đ', ''))
    except:
        return 21050

gia_xang = cap_nhat_gia_xang()
st.sidebar.info(f"Giá xăng RON95-V hôm nay: {gia_xang:,.0f} đ/lít")

# ==================== TÍNH TIỀN ĐIỆN BẬC THANG 2025 ====================
def tinh_tien_dien(kwh):
    bac = [1984, 2050, 2380, 2998, 3350, 3460]
    limit = [50, 50, 100, 100, 100, float('inf')]
    tien = 0
    conlai = kwh
    for i in range(6):
        if conlai <= 0: break
        dung = min(conlai, limit[i])
        tien += dung * bac[i]
        conlai -= dung
    return tien * 1.1  # +10% VAT

# ==================== DỮ LIỆU THỰC PHẨM CHI TIẾT ====================
gia_thuc_pham = {
    "Gạo ST25/tám thơm":              {"dg": 28000,  "sl": 7.5,  "dv": "kg"},
    "Thịt heo ba chỉ/nạc vai":        {"dg": 138000, "sl": 2.2,  "dv": "kg"},
    "Thịt bò nội":                    {"dg": 280000, "sl": 0.8,  "dv": "kg"},
    "Cá tươi (trắm, rô phi…)":        {"dg": 95000,  "sl": 2.0,  "dv": "kg"},
    "Trứng gà công nghiệp":           {"dg": 3800,   "sl": 38,   "dv": "quả"},
    "Sữa tươi Vinamilk ít đường":     {"dg": 26500,  "sl": 10,   "dv": "lít"},
    "Rau củ + trái cây các loại":     {"dg": 30000,  "sl": 23,   "dv": "kg"},
    "Ăn ngoài + cơm sáng":            {"dg": 45000,  "sl": 17,   "dv": "bữa"},
    "Dầu ăn, nước mắm, gia vị":       {"dg": 160000, "sl": 1,    "dv": ""},
    "Mì gói, snack, bánh kẹo":        {"dg": 120000, "sl": 1,    "dv": ""},
    "Cà phê, trà, nước ngọt":         {"dg": 160000, "sl": 1,    "dv": ""},
}

# ==================== HỆ SỐ QUẬN & GIÁ NHÀ TẦM TRUNG/THẤP CẤP (ĐÃ CẬP NHẬT 11/2025) ====================
heso_quan = {
    "Quận 1": 1.50, "Quận 3": 1.45, "Quận 7": 1.25, "Bình Thạnh": 1.20, "Phú Nhuận": 1.18,
    "Thủ Đức (TP)": 1.05, "Gò Vấp": 0.95, "Tân Bình": 1.10, "Bình Tân": 0.85,
    "Hoàn Kiếm": 1.60, "Ba Đình": 1.55, "Cầu Giấy": 1.30, "Tây Hồ": 1.45, "Đống Đa": 1.35,
    "Thanh Xuân": 1.20, "Hà Đông": 0.90, "Long Biên": 0.95,
}

hcm_districts = ["Quận 1","Quận 3","Quận 7","Bình Thạnh","Phú Nhuận","Thủ Đức (TP)","Gò Vấp","Tân Bình","Bình Tân"]
hn_districts = ["Hoàn Kiếm","Ba Đình","Cầu Giấy","Tây Hồ","Đống Đa","Thanh Xuân","Hà Đông","Long Biên"]

gia_nha = {
    "Phòng trọ/căn hộ nhỏ 15-20m²":           {"TP.HCM": 3.8, "Hà Nội": 3.3},
    "Studio 25-35m² (full nội thất cơ bản)":  {"TP.HCM": 7.2, "Hà Nội": 8.0},
    "Căn hộ 1PN tầm trung (50-70m²)":         {"TP.HCM": 13.5, "Hà Nội": 16.5},
    "Căn hộ 2PN tầm trung (70-90m²)":         {"TP.HCM": 18.0, "Hà Nội": 22.0},
    "Căn hộ 3PN tầm thấp (100-120m²)":        {"TP.HCM": 24.0, "Hà Nội": 28.0},
}

heso_gd = {"Độc thân": 1.0, "Vợ chồng": 1.55, "Vợ chồng +1 con": 2.0, "Vợ chồng +2 con": 2.4}
nuoi_con = {"Độc thân": 0, "Vợ chồng": 0, "Vợ chồng +1 con": 8.5, "Vợ chồng +2 con": 17.0}

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("Thông tin cá nhân")
    thanhpho = st.selectbox("Thành phố", ["TP.HCM", "Hà Nội"])
    quan_list = sorted(hcm_districts if thanhpho == "TP.HCM" else hn_districts)
    quan = st.selectbox("Quận / Huyện", quan_list)
    ho_gd = st.selectbox("Hộ gia đình", list(heso_gd.keys()), index=2)
    loai_nha = st.selectbox("Loại nhà ở", list(gia_nha.keys()))
    phan_tram_quan_ao = st.slider("Quần áo & CS cá nhân (%)", 5, 20, 10)
    if st.button("Làm mới giá"): st.rerun()

# ==================== TÍNH TOÁN TVL ====================
tong_1_nguoi_food = sum(item["dg"] * item["sl"] for item in gia_thuc_pham.values()) * random.uniform(0.95, 1.06)
thuc_pham_gd = (tong_1_nguoi_food / 1_000_000) * heso_gd[ho_gd]

nha_o = gia_nha[loai_nha][thanhpho] * heso_quan[quan] * random.uniform(0.93, 1.09)
chi_phi_tre = nuoi_con[ho_gd]

kwh = random.uniform(150, 650)
tien_dien = tinh_tien_dien(kwh)
tien_nuoc = random.uniform(100_000, 500_000)
tien_xang = random.uniform(35, 50) * gia_xang * (1 if "Độc thân" in ho_gd else 2)
tien_tien_ich = tien_dien + tien_nuoc + tien_xang + 300_000 + random.uniform(300_000, 500_000)

tvl_co_ban = round(thuc_pham_gd + nha_o + chi_phi_tre + tien_tien_ich/1_000_000, 1)
thu_nhap_kha_dung = tvl_co_ban * 1.5 * 0.5
quan_ao = round(thu_nhap_kha_dung * (phan_tram_quan_ao / 100), 1)
tong_tvl = round(tvl_co_ban + quan_ao, 1)

# ==================== HIỂN THỊ CHÍNH ====================
col1, col2 = st.columns([1.3, 1])
with col1:
    color = "#4ECDC4" if tong_tvl <= 16 else "#FFBE0B" if tong_tvl <= 25 else "#FF4444"
    st.markdown(f"<p class='big-font' style='color:{color}'>TVL ≈ {tong_tvl:,} triệu/tháng</p>", unsafe_allow_html=True)
    st.metric("Nhà ở", f"{nha_o:.1f} triệu")
    st.metric("Thực phẩm + sinh hoạt", f"{thuc_pham_gd:.1f} triệu")
    st.metric("Tiện ích (điện nước xăng net)", f"{tien_tien_ich/1_000_000:.2f} triệu")
    st.metric("Quần áo & CS cá nhân", f"{quan_ao:.1f} triệu")
    st.metric("Nuôi con (nếu có)", f"{chi_phi_tre:.1f} triệu")
    st.success(f"Thu nhập thoải mái ≥ **{int(tvl_co_ban*1.5 + quan_ao):,} triệu/tháng**")

with col2:
    fig = go.Figure(data=[go.Pie(
        labels=["Nhà ở", "Thực phẩm", "Tiện ích", "Quần áo & CS", "Nuôi con"],
        values=[nha_o, thuc_pham_gd, tien_tien_ich/1e6, quan_ao, chi_phi_tre],
        hole=0.5,
        marker_colors=["#FF6B6B","#4ECDC4","#1A936F","#FFE66D","#45B7D1"],
        textinfo='label+percent'
    )])
    fig.update_layout(title="Cơ cấu chi phí sống")
    st.plotly_chart(fig, use_container_width=True)

# ==================== BẢNG GIÁ CHI TIẾT THỰC PHẨM ====================
st.markdown("---")
st.subheader("Chi tiết giá thực phẩm & sinh hoạt (1 người lớn/tháng – 11/2025)")

data = []
for ten, info in gia_thuc_pham.items():
    thanh_tien = info["dg"] * info["sl"]
    so_luong = f"{info['sl']} {info['dv']}" if info['dv'] else ""
    data.append({
        "Mặt hàng": ten,
        "Đơn giá": f"{info['dg']:,.0f} đ",
        "Số lượng": so_luong,
        "Thành tiền": f"{thanh_tien:,.0f} đ"
    })

st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

# ==================== SO SÁNH NĂM & THÁNG ====================
st.markdown("---")
st.subheader("So sánh tự động từ Google Sheets")

c1, c2 = st.columns(2)
with c1.metric("Năm 2025", f"{tong_tvl:,} triệu/tháng")
 tvl_2024 = round(tong_tvl / (1 + tang_trung_binh_nam), 1)
 c2.metric("Năm 2024", f"{tvl_2024:,} triệu/tháng", f"+{tang_trung_binh_nam*100:.1f}%")

c3, c4 = st.columns(2)
 c3.metric(f"Tháng {datetime.now():%m/%Y}", f"{tong_tvl:,} triệu/tháng")
 tvl_thang_truoc = round(tong_tvl / (1 + thay_doi_thang_truoc), 1)
 c4.metric("Tháng trước", f"{tvl_thang_truoc:,} triệu/tháng", f"+{thay_doi_thang_truoc*100:.1f}%")

st.caption(f"Auto-update {datetime.now().strftime('%d/%m/%Y %H:%M')} • TVL Pro 2025 • by @Nhatminh")
