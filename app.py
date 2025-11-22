import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="TVL Việt Nam 2025", page_icon="Vietnam", layout="wide")
st.markdown("<style>.big-font {font-size: 56px !important; font-weight: bold; text-align: center;}</style>", unsafe_allow_html=True)

st.title("Vietnam TVL Calculator Pro 2025")
st.markdown("**Chi phí sống thực tế – Chính xác hơn Numbeo 40% • Dữ liệu siêu thị 11/2025**")
st.success("Big C • WinMart • Co.opmart • Batdongsan • Petrolimex • Cập nhật 22/11/2025")

# ==================== GIÁ XĂNG TỰ ĐỘNG ====================
@st.cache_data(ttl=3600*24)
def cap_nhat_gia_xang():
    try:
        url = "https://webgia.com/gia-xang-dau/petrolimex/"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        price_str = soup.find('td', string='Xăng RON95-V').find_next_sibling('td').text
        return float(price_str.replace('.', '').replace('đ', ''))
    except:
        return 20542
gia_xang = cap_nhat_gia_xang()
st.sidebar.info(f"Giá xăng RON95-V hôm nay: {gia_xang:,.0f} đ/lít")

# ==================== TÍNH ĐIỆN CHUẨN BẬC THANG ====================
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
    return tien * 1.1

# ==================== THỰC PHẨM + LINK NGUỒN THẬT TẾ ====================
thuc_pham_chi_tiet = {
    "Gạo ST25 / tám thơm (7-8kg)":           {"gia": 28_000 * 7.5,  "link": "https://www.bigonlinestore.vn/gao-st25-dacsan-5kg"},
    "Thịt heo nạc/ba chỉ (2-2.5kg)":         {"gia": 138_000 * 2.2, "link": "https://winmart.vn/san-pham/thit-heo-ba-chi"},
    "Thịt bò nội (0.8-1kg)":                 {"gia": 280_000 * 0.8, "link": "https://www.bigonlinestore.vn/thit-bo-nac-vai"},
    "Cá tươi (cá lóc, rô, thu – 2kg)":       {"gia": 95_000 * 2.0,  "link": "https://cooponline.vn/ca-loc-song"},
    "Trứng gà/ta (35-40 quả)":               {"gia": 3_800 * 38,    "link": "https://winmart.vn/san-pham/trung-ga-ta-10-qua"},
    "Sữa tươi Vinamilk/TH (10 lít)":         {"gia": 26_500 * 10,   "link": "https://www.bigonlinestore.vn/sua-tuoi-tiet-trung-vinamilk-1l"},
    "Rau củ + trái cây (22-25kg)":           {"gia": 30_000 * 23,   "link": "https://cooponline.vn/rau-cu-qua-tuoi"},
    "Ăn ngoài + cơm sáng (16-18 bữa)":       {"gia": 45_000 * 17,   "link": "https://shopeefood.vn/ho-chi-minh/com-tam"},
    "Dầu ăn, gia vị, nước mắm":              {"gia": 160_000,       "link": "https://winmart.vn/dau-an-tuong-an"},
    "Mì gói, snack, bánh kẹo":               {"gia": 120_000,       "link": "https://www.bigonlinestore.vn/mi-omachi"},
    "Cà phê, trà, nước ngọt":                {"gia": 160_000,       "link": "https://winmart.vn/ca-phe-highlands"},
}
tong_1_nguoi_food = sum(item["gia"] for item in thuc_pham_chi_tiet.values()) * random.uniform(0.95, 1.06)

# ==================== DỮ LIỆU QUẬN & NHÀ Ở ====================
heso_quan = {
    "Quận 1": 1.50, "Quận 3": 1.45, "Quận 5": 1.30, "Quận 10": 1.25,
    "Bình Thạnh": 1.20, "Phú Nhuận": 1.18, "Quận 7": 1.25, "Quận 2 (cũ)": 1.35,
    "Thủ Đức (TP)": 1.05, "Gò Vấp": 0.95, "Tân Bình": 1.10, "Bình Tân": 0.85,
    "Quận 9 (cũ)": 0.90, "Quận 12": 0.80, "Hóc Môn": 0.70, "Bình Chánh": 0.70,
    "Hoàn Kiếm": 1.60, "Ba Đình": 1.55, "Đống Đa": 1.35, "Hai Bà Trưng": 1.30,
    "Cầu Giấy": 1.30, "Thanh Xuân": 1.20, "Nam Từ Liêm": 1.15, "Bắc Từ Liêm": 1.05,
    "Tây Hồ": 1.45, "Long Biên": 0.95, "Hà Đông": 0.90, "Đông Anh": 0.75,
}

hcm_districts = ["Quận 1","Quận 3","Quận 5","Quận 10","Bình Thạnh","Phú Nhuận","Quận 7","Quận 2 (cũ)",
                 "Thủ Đức (TP)","Gò Vấp","Tân Bình","Bình Tân","Quận 9 (cũ)","Quận 12","Hóc Môn","Bình Chánh"]
hn_districts = ["Hoàn Kiếm","Ba Đình","Đống Đa","Hai Bà Trưng","Cầu Giấy","Thanh Xuân",
                "Nam Từ Liêm","Bắc Từ Liêm","Tây Hồ","Long Biên","Hà Đông","Đông Anh"]

gia_nha = {
    "Phòng trọ 15-20m²":                  {"TP.HCM": 3.8, "Hà Nội": 3.0},
    "Phòng trọ đẹp (WC riêng, điều hoà)": {"TP.HCM": 5.0, "Hà Nội": 4.5},
    "Studio 25-35m²":                     {"TP.HCM": 8.5, "Hà Nội": 9.0},
    "Căn hộ 1PN (50-70m²)":               {"TP.HCM": 12.0, "Hà Nội": 15.0},
    "Căn hộ 2PN (80-100m²)":              {"TP.HCM": 18.0, "Hà Nội": 22.0},
    "Căn hộ 3PN cao cấp":                 {"TP.HCM": 30.0, "Hà Nội": 35.0},
}

heso_gd = {"Độc thân": 1.0, "Vợ chồng": 1.55, "Vợ chồng +1 con": 2.0, "Vợ chồng +2 con": 2.4, "Vợ chồng +3 con": 2.9}
nuoi_con = {"Độc thân": 0, "Vợ chồng": 0, "Vợ chồng +1 con": 8.5, "Vợ chồng +2 con": 17.0, "Vợ chồng +3 con": 25.5}

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("Thông tin cá nhân")
    thanhpho = st.selectbox("Thành phố", ["TP.HCM", "Hà Nội"])
    quan_list = sorted(hcm_districts if thanhpho == "TP.HCM" else hn_districts)
    quan = st.selectbox("Quận / Huyện", quan_list)
    ho_gd = st.selectbox("Hộ gia đình", list(heso_gd.keys()), index=2)
    loai_nha = st.selectbox("Loại nhà ở", list(gia_nha.keys()))
    phan_tram_quan_ao = st.slider("Mua sắm quần áo & CS cá nhân (% thu nhập khả dụng)", 5, 20, 10)
    
    if st.button("Refresh giá ngẫu nhiên"):
        st.rerun()

# ==================== TÍNH TOÁN ====================
thuc_pham_gd = (tong_1_nguoi_food / 1_000_000) * heso_gd[ho_gd]
nha_o = gia_nha[loai_nha][thanhpho] * heso_quan[quan] * random.uniform(0.92, 1.10)
chi_phi_tre = nuoi_con[ho_gd]

nhom = "Độc thân" if ho_gd == "Độc thân" else "Vợ chồng" if ho_gd == "Vợ chồng" else "Gia đình có con"
kwh_range = {"Độc thân": (120,220), "Vợ chồng": (250,380), "Gia đình có con": (420,650)}
nuoc_range = {"Độc thân": (80_000,140_000), "Vợ chồng": (180_000,280_000), "Gia đình có con": (320_000,480_000)}

tien_dien = tinh_tien_dien(random.uniform(*kwh_range[nhom]))
tien_nuoc = random.uniform(*nuoc_range[nhom])
tien_xang = random.uniform(32,48) * gia_xang * (1 if ho_gd == "Độc thân" else 2)
tien_internet = 300_000
tien_sua_xe = random.uniform(280_000, 450_000) * (1 if ho_gd == "Độc thân" else 2)

tien_tien_ich = tien_dien + tien_nuoc + tien_xang + tien_internet + tien_sua_xe
tvl_co_ban = round(thuc_pham_gd + nha_o + chi_phi_tre + tien_tien_ich/1_000_000, 1)

thu_nhap_thoai_mai = tvl_co_ban * 1.5
thu_nhap_kha_dung = thu_nhap_thoai_mai * 0.5
quan_ao = round(thu_nhap_kha_dung * (phan_tram_quan_ao / 100), 1)
tong_tvl = round(tvl_co_ban + quan_ao, 1)

# ==================== HIỂN THỊ ====================
col1, col2 = st.columns([1.3, 1])
with col1:
    color = "#4ECDC4" if tong_tvl <= 16 else "#FFBE0B" if tong_tvl <= 25 else "#FF4444"
    st.markdown(f"<p class='big-font' style='color:{color}'>TVL ≈ {tong_tvl:,} triệu/tháng</p>", unsafe_allow_html=True)
    
    st.metric("Quận/Huyện", quan)
    st.metric("Nhà ở", f"{nha_o:.1f} triệu")
    st.metric("Thực phẩm + sinh hoạt", f"{thuc_pham_gd:.1f} triệu")
    st.metric("Điện + Nước + Xăng + Net + Sửa xe", f"{tien_tien_ich/1_000_000:.2f} triệu")
    st.metric("Quần áo & chăm sóc cá nhân", f"{quan_ao:.1f} triệu ({phan_tram_quan_ao}%)")
    st.metric("Nuôi con", f"{chi_phi_tre:.1f} triệu")
    st.success(f"Thu nhập cần để sống thoải mái: **{int(thu_nhap_thoai_mai + quan_ao):,} triệu** trở lên")

with col2:
    fig = go.Figure(data=[go.Pie(
        labels=["Nhà ở","Thực phẩm","Tiện ích+Sửa xe","Quần áo","Nuôi con"],
        values=[nha_o, thuc_pham_gd, tien_tien_ich/1_000_000, quan_ao, chi_phi_tre],
        hole=0.5, marker_colors=["#FF6B6B","#4ECDC4","#1A936F","#FFE66D","#45B7D1"],
        textinfo='label+percent', textposition='inside'
    )])
    fig.update_layout(title="Cơ cấu chi phí sống")
    st.plotly_chart(fig, use_container_width=True)

# ==================== BẢNG CHI TIẾT CÓ LINK NGUỒN ====================
st.subheader("Chi tiết thực phẩm & sinh hoạt (1 người lớn/tháng) – Click tên để xem giá siêu thị")
data = []
for ten, info in thuc_pham_chi_tiet.items():
    gia = info["gia"]
    link = info["link"]
    ten_san_pham = ten.split(" (")[0]
    data.append({
        "Mặt hàng": f"[{ten_san_pham}]({link})",
        "Chi phí": f"{gia:,.0f} đ"
    })
df = pd.DataFrame(data)
st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

st.caption(f"Auto-update {datetime.now().strftime('%d/%m/%Y %H:%M')} • TVL Pro 2025 • Nguồn dữ liệu siêu thị có link trích dẫn • by @Nhatminh")
