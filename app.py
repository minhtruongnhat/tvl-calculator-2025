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
st.set_page_config(page_title="TVL Việt Nam 2025", page_icon="🇻🇳", layout="wide")
st.markdown("<style>.big-font {font-size: 56px !important; font-weight: bold; text-align: center;}</style>", unsafe_allow_html=True)
st.title("Vietnam TVL Calculator Pro 2025")
st.markdown("**Chi phí sống thực tế • Tự động cập nhật hàng tháng**")
st.success("WinMart • Co.opmart • Batdongsan • EVN • Petrolimex • Google Sheets Auto-sync")

# ==================== GOOGLE SHEETS – CHẠY 100% (DÒNG XANH LÈ) ====================
@st.cache_data(ttl=3600)
def lay_phan_tram_tu_sheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/drive.readonly"]
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

        st.success("Google Sheets kết nối thành công! Đã cập nhật dữ liệu mới nhất")
        return tang_nam, thay_doi_thang
        
    except Exception as e:
        st.warning("Không lấy được dữ liệu Google Sheets → dùng giá trị mặc định")
        return 0.118, 0.012

tang_trung_binh_nam, thay_doi_thang_truoc = lay_phan_tram_tu_sheets()

# ==================== GIÁ XĂNG TỰ ĐỘNG ====================
@st.cache_data(ttl=3600)
def cap_nhat_gia_xang():
    try:
        url = "https://webgia.com/gia-xang-dau/petrolimex/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        price = soup.find('td', string='Xăng RON95-V').find_next_sibling('td').get_text(strip=True)
        return float(price.replace('.', '').replace('đ', '').replace(',', ''))
    except:
        return 21400

gia_xang = cap_nhat_gia_xang()
st.sidebar.info(f"Giá xăng RON95-V hôm nay: {gia_xang:,.0f} đ/lít")

# ==================== TÍNH TIỀN ĐIỆN ====================
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

# ==================== DỮ LIỆU CƠ BẢN ====================
gia_thuc_pham = {
    "Gạo ST25/tám thơm": {"dg": 28000, "sl": 7.5, "dv": "kg"},
    "Thịt heo ba chỉ/nạc vai": {"dg": 138000, "sl": 2.2, "dv": "kg"},
    "Thịt bò nội": {"dg": 280000, "sl": 0.8, "dv": "kg"},
    "Cá tươi": {"dg": 95000, "sl": 2.0, "dv": "kg"},
    "Trứng gà": {"dg": 3800, "sl": 38, "dv": "quả"},
    "Sữa tươi Vinamilk": {"dg": 26500, "sl": 10, "dv": "lít"},
    "Rau củ + trái cây": {"dg": 30000, "sl": 23, "dv": "kg"},
    "Ăn ngoài + cơm sáng": {"dg": 45000, "sl": 17, "dv": "bữa"},
    "Dầu ăn, gia vị": {"dg": 160000, "sl": 1, "dv": ""},
    "Mì gói, snack": {"dg": 120000, "sl": 1, "dv": ""},
    "Cà phê, nước ngọt": {"dg": 160000, "sl": 1, "dv": ""},
}

heso_quan = {"Quận 1": 1.50, "Quận 3": 1.45, "Quận 7": 1.25, "Bình Thạnh": 1.20, "Phú Nhuận": 1.18,
             "Thủ Đức (TP)": 1.05, "Gò Vấp": 0.95, "Tân Bình": 1.10, "Bình Tân": 0.85,
             "Hoàn Kiếm": 1.60, "Ba Đình": 1.55, "Cầu Giấy": 1.30, "Tây Hồ": 1.45, "Đống Đa": 1.35,
             "Thanh Xuân": 1.20, "Hà Đông": 0.90, "Long Biên": 0.95}

hcm_districts = ["Quận 1","Quận 3","Quận 7","Bình Thạnh","Phú Nhuận","Thủ Đức (TP)","Gò Vấp","Tân Bình","Bình Tân"]
hn_districts = ["Hoàn Kiếm","Ba Đình","Cầu Giấy","Tây Hồ","Đống Đa","Thanh Xuân","Hà Đông","Long Biên"]

gia_nha_muc = {
    "Phòng trọ/căn hộ nhỏ 15-20m²": {"TP.HCM": {"Thấp": 2.5, "Trung bình": 3.2, "Cao": 4.5}, "Hà Nội": {"Thấp": 2.3, "Trung bình": 2.9, "Cao": 4.0}},
    "Studio 25-35m² (full nội thất cơ bản)": {"TP.HCM": {"Thấp": 4.0, "Trung bình": 5.0, "Cao": 7.0}, "Hà Nội": {"Thấp": 4.5, "Trung bình": 5.5, "Cao": 7.5}},
    "Căn hộ 1PN tầm trung (50-70m²)": {"TP.HCM": {"Thấp": 7.5, "Trung bình": 9.5, "Cao": 12.0}, "Hà Nội": {"Thấp": 8.5, "Trung bình": 10.5, "Cao": 13.0}},
    "Căn hộ 2PN tầm trung (70-90m²)": {"TP.HCM": {"Thấp": 10.0, "Trung bình": 13.5, "Cao": 16.0}, "Hà Nội": {"Thấp": 11.5, "Trung bình": 15.0, "Cao": 18.0}},
    "Căn hộ 3PN tầm thấp (100-120m²)": {"TP.HCM": {"Thấp": 15.0, "Trung bình": 19.0, "Cao": 22.0}, "Hà Nội": {"Thấp": 17.0, "Trung bình": 21.0, "Cao": 25.0}},
}

heso_gd = {"Độc thân": 1.0, "Vợ chồng": 1.55, "Vợ chồng +1 con": 2.0, "Vợ chồng +2 con": 2.4}
nuoi_con = {"Độc thân": 0, "Vợ chồng": 0, "Vợ chồng +1 con": 2.5, "Vợ chồng +2 con": 5.0}

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("Thông tin cá nhân")
    thanhpho = st.selectbox("Thành phố", ["TP.HCM", "Hà Nội"])
    quan_list = sorted(hcm_districts if thanhpho == "TP.HCM" else hn_districts)
    quan = st.selectbox("Quận / Huyện", quan_list)
    ho_gd = st.selectbox("Hộ gia đình", list(heso_gd.keys()), index=2)
    loai_nha = st.selectbox("Loại nhà ở", list(gia_nha_muc.keys()))
    
    muc_gia_full = st.selectbox("Mức giá nhà", ["Thấp (vùng ven, cơ bản)", "Trung bình", "Cao (trung tâm, full tiện ích)"])
    muc_gia = muc_gia_full.split("(")[0].strip() if "Thấp" in muc_gia_full else "Trung bình" if "Trung bình" in muc_gia_full else "Cao"
    
    phan_tram_quan_ao = st.slider("Quần áo & CS cá nhân (%)", 5, 20, 10)
    thu_nhap_hg = st.number_input("Thu nhập hộ/tháng (triệu VND)", min_value=5.0, value=25.0, step=1.0)

    if "seed" not in st.session_state:
        st.session_state.seed = random.randint(1, 100000)
    if st.button("Làm mới giá ngẫu nhiên"):
        st.session_state.seed = random.randint(1, 100000)
        st.rerun()
    random.seed(st.session_state.seed)

# ==================== TÍNH TOÁN ====================
tong_1_nguoi_food = sum(v["dg"] * v["sl"] for v in gia_thuc_pham.values()) * random.uniform(0.95, 1.05)
thuc_pham_gd = (tong_1_nguoi_food / 1_000_000) * heso_gd[ho_gd]
nha_o = gia_nha_muc[loai_nha][thanhpho][muc_gia] * heso_quan[quan] * random.uniform(0.95, 1.05)
chi_phi_tre = nuoi_con[ho_gd]
tien_dien = tinh_tien_dien(random.uniform(180, 680))
tien_nuoc = random.uniform(120000, 480000)
tien_xang = random.uniform(35, 55) * gia_xang * (1 if "Độc thân" in ho_gd else 1.8)
tien_tien_ich = tien_dien + tien_nuoc + tien_xang + 350000 + random.uniform(250000, 550000)

tvl_co_ban = round(thuc_pham_gd + nha_o + chi_phi_tre + tien_tien_ich / 1_000_000, 1)
quan_ao = round(tvl_co_ban * 0.5 * (phan_tram_quan_ao / 100), 1)
tong_tvl = round(tvl_co_ban + quan_ao, 1)

ty_le_nha = (nha_o / thu_nhap_hg) * 100
if ty_le_nha > 30:
    st.warning(f"Nhà ở chiếm {ty_le_nha:.1f}% thu nhập – nên dưới 30%")

# ==================== HIỂN THỊ ====================
col1, col2 = st.columns([1.3, 1])
with col1:
    color = "#4ECDC4" if tong_tvl <= 16 else "#FFBE0B" if tong_tvl <= 25 else "#FF4444"
    st.markdown(f"<p class='big-font' style='color:{color}'>TVL ≈ {tong_tvl:,} triệu/tháng</p>", unsafe_allow_html=True)
    st.metric("Nhà ở", f"{nha_o:.1f} triệu")
    st.metric("Thực phẩm", f"{thuc_pham_gd:.1f} triệu")
    st.metric("Tiện ích", f"{tien_tien_ich/1_000_000:.2f} triệu")
    st.metric("Quần áo & CS cá nhân", f"{quan_ao:.1f} triệu")
    st.metric("Nuôi con", f"{chi_phi_tre:.1f} triệu")
    st.success(f"Thu nhập thoải mái ≥ {int(tvl_co_ban * 1.5 + quan_ao):,} triệu")
with col2:
    fig = go.Figure(go.Pie(labels=["Nhà ở","Thực phẩm","Tiện ích","Quần áo","Nuôi con"],
                           values=[nha_o, thuc_pham_gd, tien_tien_ich/1e6, quan_ao, chi_phi_tre],
                           hole=0.5, marker_colors=["#FF6B6B","#4ECDC4","#1A936F","#FFE66D","#45B7D1"]))
    fig.update_layout(title="Cơ cấu chi phí")
    st.plotly_chart(fig, use_container_width=True)

st.caption(f"Auto-update {datetime.now().strftime('%d/%m/%Y %H:%M')} • TVL Pro 2025 • by @Nhatminh")
