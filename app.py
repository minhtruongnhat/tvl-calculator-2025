import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
import re
import io # Cần thiết để đọc CSV từ response

# ==================== CẤU HÌNH TRANG ====================
st.set_page_config(page_title="TVL Việt Nam 2025", page_icon="🇻🇳", layout="wide")
st.markdown("<style>.big-font {font-size: 56px !important; font-weight: bold; text-align: center;}</style>", unsafe_allow_html=True)
st.title("Vietnam TVL Calculator Pro 2025")
st.markdown("**Chi phí sống thực tế • Dự báo Tăng trưởng 2025**")
st.success("Dữ liệu tự động cập nhật qua CSV API (Google Sheets) và Web Scraper (Giá xăng)")

# ==================== TỰ ĐỘNG LẤY % TĂNG GIÁ TỪ URL CSV (THAY THẾ GOPY SPREADSHEET) ====================
@st.cache_data(ttl=3600)
def lay_phan_tram_tu_sheets_csv():
    """Tải dữ liệu lạm phát từ Sheets qua URL xuất CSV công khai."""
    SHEET_ID = "1QjK8v6Y9k2f5t3xL9pR7mN8vBxZsQwRt2eYk5f3d8cU"
    GID = "0" 
    CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID}"
    
    try:
        response = requests.get(CSV_URL, timeout=10)
        response.raise_for_status() 
        
        # Đọc dữ liệu trực tiếp bằng pandas
        df = pd.read_csv(io.StringIO(response.text))
        
        # Lấy Tăng cả năm
        tang_nam = float(df.iloc[0]["Tăng cả năm 2025 so 2024"]) / 100
        
        # Lấy Thay đổi tháng
        thang_hien_tai = datetime.now().strftime("%m/%Y")
        try:
            thay_doi_thang = float(df[df["Tháng"] == thang_hien_tai]["% thay đổi so tháng trước"].iloc[0]) / 100
        except:
            thay_doi_thang = 0.012 
            
        return tang_nam, thay_doi_thang, True
        
    except Exception as e:
        # st.warning/st.toast sẽ được gọi bên ngoài hàm cache
        return 0.118, 0.012, False 

tang_trung_binh_nam, thay_doi_thang_truoc, sheets_success = lay_phan_tram_tu_sheets_csv()

# Hiển thị trạng thái kết nối bên ngoài hàm cache
if sheets_success:
    st.success(f"Dữ liệu lạm phát (năm {tang_trung_binh_nam*100:.1f}%) cập nhật thành công qua CSV API.")
else:
    st.warning("Lỗi kết nối CSV API → dùng giá trị mặc định (Tăng trưởng năm 11.8%).")


# ==================== GIÁ XĂNG TỰ ĐỘNG (ĐÃ SỬA LỖI SCRAPER) ====================
@st.cache_data(ttl=86400)
def cap_nhat_gia_xang():
    GIA_XANG_MAC_DINH = 21050
    try:
        url = "https://webgia.com/gia-xang-dau/petrolimex/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        
        for row in soup.find_all('tr'):
            if 'RON95' in row.get_text():
                cells = row.find_all('td')
                if len(cells) >= 2:
                    price_raw = cells[1].get_text(strip=True)
                    price_clean = re.sub(r'[^\d]', '', price_raw) 
                    return float(price_clean), price_raw, True
        
        return GIA_XANG_MAC_DINH, f"{GIA_XANG_MAC_DINH:,.0f} đ/lít", False
    except:
        return GIA_XANG_MAC_DINH, f"{GIA_XANG_MAC_DINH:,.0f} đ/lít (Mặc định)", False

gia_xang, gia_xang_raw, is_xang_updated = cap_nhat_gia_xang()


# ==================== TÍNH TIỀN ĐIỆN BẬC THANG ====================
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

# ==================== DỮ LIỆU CƠ SỞ ====================
gia_thuc_pham = {
    "Gạo ST25/tám thơm": {"dg": 28000, "sl": 7.5, "dv": "kg"}, "Thịt heo ba chỉ/nạc vai": {"dg": 138000, "sl": 2.2, "dv": "kg"},
    "Thịt bò nội": {"dg": 280000, "sl": 0.8, "dv": "kg"}, "Cá tươi (trắm, rô phi…)": {"dg": 95000, "sl": 2.0, "dv": "kg"},
    "Trứng gà công nghiệp": {"dg": 3800, "sl": 38, "dv": "quả"}, "Sữa tươi Vinamilk ít đường": {"dg": 26500, "sl": 10, "dv": "lít"},
    "Rau củ + trái cây các loại": {"dg": 30000, "sl": 23, "dv": "kg"}, "Ăn ngoài + cơm sáng": {"dg": 45000, "sl": 17, "dv": "bữa"},
    "Dầu ăn, nước mắm, gia vị": {"dg": 160000, "sl": 1, "dv": ""}, "Mì gói, snack, bánh kẹo": {"dg": 120000, "sl": 1, "dv": ""},
    "Cà phê, trà, nước ngọt": {"dg": 160000, "sl": 1, "dv": ""},
}

heso_quan = {"Quận 1": 1.50, "Quận 3": 1.45, "Quận 7": 1.25, "Bình Thạnh": 1.20, "Phú Nhuận": 1.18,
             "Thủ Đức (TP)": 1.05, "Gò Vấp": 0.95, "Tân Bình": 1.10, "Bình Tân": 0.85,
             "Hoàn Kiếm": 1.60, "Ba Đình": 1.55, "Cầu Giấy": 1.30, "Tây Hồ": 1.45, "Đống Đa": 1.35,
             "Thanh Xuân": 1.20, "Hà Đông": 0.90, "Long Biên": 0.95}

hcm_districts = ["Quận 1","Quận 3","Quận 7","Bình Thạnh","Phú Nhuận","Thủ Đức (TP)","Gò Vấp","Tân Bình","Bình Tân"]
hn_districts = ["Hoàn Kiếm","Ba Đình","Cầu Giấy","Tây Hồ","Đống Đa","Thanh Xuân","Hà Đông","Long Biên"]

gia_nha = {
    "Phòng trọ/căn hộ nhỏ 15-20m²": {"TP.HCM": 3.8, "Hà Nội": 3.3},
    "Studio 25-35m² (full nội thất cơ bản)": {"TP.HCM": 7.2, "Hà Nội": 8.0},
    "Căn hộ 1PN tầm trung (50-70m²)": {"TP.HCM": 13.5, "Hà Nội": 16.5},
    "Căn hộ 2PN tầm trung (70-90m²)": {"TP.HCM": 18.0, "Hà Nội": 22.0},
    "Căn hộ 3PN tầm thấp (100-120m²)": {"TP.HCM": 24.0, "Hà Nội": 28.0},
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
    
    # Hiển thị trạng thái giá xăng
    if is_xang_updated:
        st.sidebar.success(f"Giá xăng RON95-V cập nhật: {gia_xang_raw}")
    else:
        st.sidebar.warning(f"Giá xăng RON95-V: {gia_xang_raw} (Sử dụng giá mặc định)")
        
    if st.button("Làm mới giá ngẫu nhiên"): st.rerun()

# ==================== TÍNH TOÁN TVL (ĐÃ SỬA LỖI LẠM PHÁT VÀ LOGIC) ====================

# 1. Chi phí Thực phẩm (Biến động + Lạm phát)
tong_1_nguoi_food_base = sum(item["dg"] * item["sl"] for item in gia_thuc_pham.values())
# ÁP DỤNG LẠM PHÁT
tong_1_nguoi_food_final = (tong_1_nguoi_food_base * random.uniform(0.95, 1.06)) * (1 + tang_trung_binh_nam)
thuc_pham_gd = round((tong_1_nguoi_food_final / 1_000_000) * heso_gd[ho_gd], 2)

# 2. Chi phí Nhà ở (Biến động + Lạm phát)
nha_o_base = gia_nha[loai_nha][thanhpho] * heso_quan[quan]
# ÁP DỤNG LẠM PHÁT
nha_o = (nha_o_base * random.uniform(0.93, 1.09)) * (1 + tang_trung_binh_nam)
nha_o = round(nha_o, 2)

# 3. Chi phí Trẻ em (ÁP DỤNG LẠM PHÁT)
chi_phi_tre = nuoi_con[ho_gd] * (1 + tang_trung_binh_nam)
chi_phi_tre = round(chi_phi_tre, 2)

# 4. Chi phí Tiện ích (Điện/Xăng Realtime + Nước/Cố định có Lạm phát)
kwh_tieu_thu = random.uniform(150, 650)
tien_dien = tinh_tien_dien(kwh_tieu_thu) # Không lạm phát vì tính theo bậc thang EVN
tien_nuoc_final = random.uniform(100_000, 500_000) * (1 + tang_trung_binh_nam)
tien_xang_base = random.uniform(35, 50) * gia_xang * (1 if "Độc thân" in ho_gd else 2)
tien_co_dinh_final = (300_000 + random.uniform(300_000, 500_000)) * (1 + tang_trung_binh_nam)

tien_tien_ich = tien_dien + tien_nuoc_final + tien_xang_base + tien_co_dinh_final

# 5. Tổng hợp TVL cơ bản
tvl_co_ban = thuc_pham_gd + nha_o + chi_phi_tre + tien_tien_ich/1_000_000

# 6. Chi phí Quần áo (SỬA LỖI LOGIC: Tính theo % Chi phí Cơ bản Tùy nghi)
chi_phi_phu = thuc_pham_gd + tien_tien_ich/1_000_000 
quan_ao = round(chi_phi_phu * (phan_tram_quan_ao / 100), 2)
tong_tvl = round(tvl_co_ban + quan_ao, 2)

# ==================== HIỂN THỊ CHÍNH ====================
col1, col2 = st.columns([1.3, 1])
with col1:
    color = "#4ECDC4" if tong_tvl <= 16 else "#FFBE0B" if tong_tvl <= 25 else "#FF4444"
    st.markdown(f"<p class='big-font' style='color:{color}'>TVL ≈ {tong_tvl:,.2f} triệu/tháng</p>", unsafe_allow_html=True)
    st.caption(f"Dự báo TVL 2025 (Áp dụng tăng trưởng {tang_trung_binh_nam*100:.1f}% năm)")
    
    st.metric("Nhà ở", f"{nha_o:.2f} triệu")
    st.metric("Thực phẩm + sinh hoạt", f"{thuc_pham_gd:.2f} triệu")
    st.metric("Tiện ích & Vận chuyển", f"{tien_tien_ich/1_000_000:.2f} triệu")
    st.metric("Quần áo & CS cá nhân", f"{quan_ao:.2f} triệu")
    st.metric("Nuôi con", f"{chi_phi_tre:.2f} triệu")
    st.success(f"Thu nhập tối thiểu để sống thoải mái ≥ **{int(tvl_co_ban*1.5 + quan_ao):,} triệu/tháng**")

with col2:
    fig = go.Figure(data=[go.Pie(
        labels=["Nhà ở","Thực phẩm","Tiện ích","Quần áo","Nuôi con"],
        values=[nha_o, thuc_pham_gd, tien_tien_ich/1e6, quan_ao, chi_phi_tre],
        hole=0.5,
        marker_colors=["#FF6B6B","#4ECDC4","#1A936F","#FFE66D","#45B7D1"],
        textinfo='label+percent'
    )])
    fig.update_layout(title="Cơ cấu chi phí sống")
    st.plotly_chart(fig, use_container_width=True)

# ==================== BẢNG CHI TIẾT THỰC PHẨM ====================
st.markdown("---")
st.subheader("Chi tiết giá thực phẩm & sinh hoạt (1 người lớn/tháng)")

data = []
for ten, info in gia_thuc_pham.items():
    thanh_tien = info["dg"] * info["sl"]
    so_luong = f"{info['sl']} {info['dv']}" if info['dv'] else ""
    data.append({"Mặt hàng": ten, "Đơn giá": f"{info['dg']:,.0f} đ", "Số lượng": so_luong, "Thành tiền": f"{thanh_tien:,.0f} đ"})
st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

# ==================== SO SÁNH NĂM & THÁNG ====================
st.markdown("---")
st.subheader("So sánh TVL theo Thời gian")

c1, c2 = st.columns(2)
with c1:
    tvl_2024 = round(tong_tvl / (1 + tang_trung_binh_nam), 2)
    st.metric("TVL Năm 2024 (Ước tính)", f"{tvl_2024:,.2f} triệu/tháng", f"+{tang_trung_binh_nam*100:.1f}%")
with c2:
    tvl_thang_truoc = round(tong_tvl / (1 + thay_doi_thang_truoc), 2)
    st.metric("TVL Tháng trước (Ước tính)", f"{tvl_thang_truoc:,.2f} triệu/tháng", f"+{thay_doi_thang_truoc*100:.1f}%")

st.caption(f"Auto-update {datetime.now().strftime('%d/%m/%Y %H:%M')} • TVL Pro 2025 • by @Nhatminh")
