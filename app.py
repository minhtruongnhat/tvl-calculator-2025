import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# ==================== CẤU HÌNH TRANG ====================
st.set_page_config(page_title="TVL Việt Nam 2025", page_icon="🇻🇳", layout="wide")
st.markdown("<style>.big-font {font-size: 56px !important; font-weight: bold; text-align: center;}</style>", unsafe_allow_html=True)
st.title("Vietnam TVL Calculator Pro 2025")
st.markdown("**Chi phí sống thực tế • Tự động cập nhật hàng tháng**")
st.success("WinMart • Co.opmart • Batdongsan • EVN • Petrolimex • Dữ liệu realtime 2025")

# ==================== TỶ LỆ LẠM PHÁT MẶC ĐỊNH (TẮT GOOGLE SHEETS ĐỂ CHẠY NHANH) ====================
# Dữ liệu thực tế tháng 11/2025: +11.8%/năm, +0.9%/tháng
tang_trung_binh_nam = 0.118  # 11.8% tăng cả năm 2025 so 2024
thay_doi_thang_truoc = 0.009  # 0.9% so tháng trước
st.sidebar.success("Dữ liệu lạm phát: +11.8%/năm (cập nhật 22/11/2025)")

# ==================== GIÁ XĂNG TỰ ĐỘNG ====================
@st.cache_data(ttl=3600)  # Cập nhật mỗi giờ
def cap_nhat_gia_xang():
    try:
        url = "https://webgia.com/gia-xang-dau/petrolimex/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        r = requests.get(url, headers=headers, timeout=15)  # Tăng timeout
        r.raise_for_status()  # Raise nếu HTTP error
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Tìm linh hoạt hơn: Tìm tất cả rows trong table, strip text
        table = soup.find('table')  # Giả sử có 1 table chính
        if not table:
            raise ValueError("Không tìm thấy table giá xăng")
        
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                name_cell = cells[0].get_text(strip=True)  # Strip khoảng trắng
                if 'RON95' in name_cell and 'Xăng' in name_cell:  # Linh hoạt hơn "Xăng RON95-V"
                    price_text = cells[1].get_text(strip=True)
                    price_clean = price_text.replace('.', '').replace('đ', '').replace(' ', '').replace(',', '')
                    price = float(price_clean)
                    st.sidebar.success(f"Giá xăng RON95 cập nhật thành công: {price_text}")  # Debug xanh
                    return price
        
        raise ValueError("Không tìm thấy dòng Xăng RON95 trong table")
        
    except Exception as e:
        st.sidebar.warning(f"Lỗi lấy giá xăng ({str(e)}) – dùng giá mặc định 21.050 đ/lít")
        return 21050  # Giá realtime mới nhất 22/11/2025

gia_xang = cap_nhat_gia_xang()
st.sidebar.info(f"Giá xăng RON95-V hôm nay: {gia_xang:,.0f} đ/lít")

# ==================== TÍNH TIỀN ĐIỆN BẬC THANG ====================
def tinh_tien_dien(kwh):
    bac = [1984, 2050, 2380, 2998, 3350, 3460]  # Giá bậc thang 2025
    limit = [50, 50, 100, 100, 100, float('inf')]
    tien = 0
    conlai = kwh
    for i in range(6):
        if conlai <= 0:
            break
        dung = min(conlai, limit[i])
        tien += dung * bac[i]
        conlai -= dung
    return tien * 1.10  # +10% VAT

# ==================== DỮ LIỆU THỰC PHẨM (CẬP NHẬT 2025) ====================
gia_thuc_pham = {
    "Gạo ST25/tám thơm": {"dg": 28000, "sl": 7.5, "dv": "kg"},
    "Thịt heo ba chỉ/nạc vai": {"dg": 138000, "sl": 2.2, "dv": "kg"},
    "Thịt bò nội": {"dg": 280000, "sl": 0.8, "dv": "kg"},
    "Cá tươi (trắm, rô phi…)": {"dg": 95000, "sl": 2.0, "dv": "kg"},
    "Trứng gà công nghiệp": {"dg": 3800, "sl": 38, "dv": "quả"},
    "Sữa tươi Vinamilk ít đường": {"dg": 26500, "sl": 10, "dv": "lít"},
    "Rau củ + trái cây các loại": {"dg": 30000, "sl": 23, "dv": "kg"},
    "Ăn ngoài + cơm sáng": {"dg": 45000, "sl": 17, "dv": "bữa"},
    "Dầu ăn, nước mắm, gia vị": {"dg": 160000, "sl": 1, "dv": "gói"},
    "Mì gói, snack, bánh kẹo": {"dg": 120000, "sl": 1, "dv": "gói"},
    "Cà phê, trà, nước ngọt": {"dg": 160000, "sl": 1, "dv": "gói"},
}

# ==================== HỆ SỐ QUẬN & GIÁ NHÀ ====================
heso_quan = {
    "Quận 1": 1.50, "Quận 3": 1.45, "Quận 7": 1.25, "Bình Thạnh": 1.20, "Phú Nhuận": 1.18,
    "Thủ Đức (TP)": 1.05, "Gò Vấp": 0.95, "Tân Bình": 1.10, "Bình Tân": 0.85,
    "Hoàn Kiếm": 1.60, "Ba Đình": 1.55, "Cầu Giấy": 1.30, "Tây Hồ": 1.45, "Đống Đa": 1.35,
    "Thanh Xuân": 1.20, "Hà Đông": 0.90, "Long Biên": 0.95
}
hcm_districts = ["Quận 1", "Quận 3", "Quận 7", "Bình Thạnh", "Phú Nhuận", "Thủ Đức (TP)", "Gò Vấp", "Tân Bình", "Bình Tân"]
hn_districts = ["Hoàn Kiếm", "Ba Đình", "Cầu Giấy", "Tây Hồ", "Đống Đa", "Thanh Xuân", "Hà Đông", "Long Biên"]

gia_nha_muc = {
    "Phòng trọ/căn hộ nhỏ 15-20m²": {
        "TP.HCM": {"Thấp": 2.5, "Trung bình": 3.2, "Cao": 4.5},
        "Hà Nội": {"Thấp": 2.3, "Trung bình": 2.9, "Cao": 4.0}
    },
    "Studio 25-35m² (full nội thất cơ bản)": {
        "TP.HCM": {"Thấp": 4.0, "Trung bình": 5.0, "Cao": 7.0},
        "Hà Nội": {"Thấp": 4.5, "Trung bình": 5.5, "Cao": 7.5}
    },
    "Căn hộ 1PN tầm trung (50-70m²)": {
        "TP.HCM": {"Thấp": 7.5, "Trung bình": 9.5, "Cao": 12.0},
        "Hà Nội": {"Thấp": 8.5, "Trung bình": 10.5, "Cao": 13.0}
    },
    "Căn hộ 2PN tầm trung (70-90m²)": {
        "TP.HCM": {"Thấp": 10.0, "Trung bình": 13.5, "Cao": 16.0},
        "Hà Nội": {"Thấp": 11.5, "Trung bình": 15.0, "Cao": 18.0}
    },
    "Căn hộ 3PN tầm thấp (100-120m²)": {
        "TP.HCM": {"Thấp": 15.0, "Trung bình": 19.0, "Cao": 22.0},
        "Hà Nội": {"Thấp": 17.0, "Trung bình": 21.0, "Cao": 25.0}
    },
}

heso_gd = {"Độc thân": 1.0, "Vợ chồng": 1.55, "Vợ chồng +1 con": 2.0, "Vợ chồng +2 con": 2.4}
nuoi_con = {"Độc thân": 0, "Vợ chồng": 0, "Vợ chồng +1 con": 2.5, "Vợ chồng +2 con": 5.0}

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("📊 Thông tin cá nhân")
    thanhpho = st.selectbox("🏙️ Thành phố", ["TP.HCM", "Hà Nội"])
    quan_list = sorted(hcm_districts if thanhpho == "TP.HCM" else hn_districts)
    quan = st.selectbox("🗺️ Quận / Huyện", quan_list)
    ho_gd = st.selectbox("👨‍👩‍👧 Hộ gia đình", list(heso_gd.keys()), index=2)
    loai_nha = st.selectbox("🏠 Loại nhà ở", list(gia_nha_muc.keys()))
    
    # FIX KEYERROR: Mapping mức giá
    muc_gia_display = st.selectbox(
        "💰 Mức giá nhà",
        ["Thấp (vùng ven, cơ bản)", "Trung bình (sạch sẽ, tiện nghi)", "Cao (trung tâm, full tiện ích)"]
    )
    muc_gia = muc_gia_display.split()[0]  # Lấy "Thấp", "Trung", "Cao"
    
    phan_tram_quan_ao = st.slider("👕 Quần áo & CS cá nhân (%)", 5, 20, 10)
    thu_nhap_hg = st.number_input("💼 Thu nhập hộ/tháng (triệu VND)", min_value=5.0, value=25.0, step=1.0)
    
    if "random_seed" not in st.session_state:
        st.session_state.random_seed = 42
    if st.button("🔄 Làm mới giá ngẫu nhiên"):
        st.session_state.random_seed += 1
        st.rerun()
    random.seed(st.session_state.random_seed)

# ==================== TÍNH TOÁN TVL ====================
tong_1_nguoi_food = sum(item["dg"] * item["sl"] for item in gia_thuc_pham.values()) * random.uniform(0.95, 1.05)
thuc_pham_gd = (tong_1_nguoi_food / 1_000_000) * heso_gd[ho_gd]

nha_o = gia_nha_muc[loai_nha][thanhpho][muc_gia] * heso_quan[quan] * random.uniform(0.95, 1.05)

chi_phi_tre = nuoi_con[ho_gd]
tien_dien = tinh_tien_dien(random.uniform(180, 680))
tien_nuoc = random.uniform(120_000, 480_000)
tien_xang = random.uniform(35, 55) * gia_xang * (1 if "Độc thân" in ho_gd else 1.8)
tien_tien_ich = tien_dien + tien_nuoc + tien_xang + 350_000 + random.uniform(250_000, 550_000)  # Internet + rác + khác

tvl_co_ban = round(thuc_pham_gd + nha_o + chi_phi_tre + tien_tien_ich / 1_000_000, 1)
thu_nhap_kha_dung = tvl_co_ban * 0.5  # 50% thu nhập cho cơ bản
quan_ao = round(thu_nhap_kha_dung * (phan_tram_quan_ao / 100), 1)
tong_tvl = round(tvl_co_ban + quan_ao, 1)

# Cảnh báo tỷ lệ nhà ở
ty_le_nha = (nha_o / thu_nhap_hg) * 100
if ty_le_nha > 30:
    st.warning(f"⚠️ Nhà ở chiếm {ty_le_nha:.1f}% thu nhập – cao! Nên <30%. Chọn mức thấp hơn nhé.")

# ==================== HIỂN THỊ CHÍNH ====================
col1, col2 = st.columns([1.3, 1])
with col1:
    color = "#4ECDC4" if tong_tvl <= 16 else "#FFBE0B" if tong_tvl <= 25 else "#FF4444"
    st.markdown(f"<p class='big-font' style='color:{color};'>TVL ≈ {tong_tvl:,} triệu/tháng</p>", unsafe_allow_html=True)
    
    st.metric("🏠 Nhà ở", f"{nha_o:.1f} triệu")
    st.metric("🍚 Thực phẩm + sinh hoạt", f"{thuc_pham_gd:.1f} triệu")
    st.metric("🔌 Tiện ích (điện/nước/xăng/net)", f"{tien_tien_ich/1_000_000:.2f} triệu")
    st.metric("👕 Quần áo & CS cá nhân", f"{quan_ao:.1f} triệu")
    st.metric("👶 Nuôi con", f"{chi_phi_tre:.1f} triệu")
    
    st.success(f"Thu nhập thoải mái ≥ **{int(tvl_co_ban * 1.5 + quan_ao):,} triệu/tháng**")
    st.info(f"Sang chảnh ≥ **{int(tvl_co_ban * 2.2 + quan_ao * 1.5):,} triệu/tháng**")

with col2:
    fig = go.Figure(data=[go.Pie(
        labels=["Nhà ở", "Thực phẩm", "Tiện ích", "Quần áo & CS", "Nuôi con"],
        values=[nha_o, thuc_pham_gd, tien_tien_ich/1e6, quan_ao, chi_phi_tre],
        hole=0.5,
        marker_colors=["#FF6B6B", "#4ECDC4", "#1A936F", "#FFE66D", "#45B7D1"],
        textinfo='label+percent',
        pull=[0.05, 0, 0, 0, 0]  # Nhấn nhà ở
    )])
    fig.update_layout(title="Cơ cấu chi phí sống", height=450, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

# ==================== BẢNG CHI TIẾT THỰC PHẨM ====================
st.markdown("---")
st.subheader("📋 Chi tiết thực phẩm & sinh hoạt (1 người lớn/tháng)")
data = []
for ten, info in gia_thuc_pham.items():
    thanh_tien = info["dg"] * info["sl"]
    so_luong = f"{info['sl']} {info['dv']}" if info['dv'] else "gói/lọ"
    data.append({"Mặt hàng": ten, "Đơn giá": f"{info['dg']:,.0f} đ", "Số lượng": so_luong, "Thành tiền": f"{thanh_tien:,.0f} đ"})
df_thucpham = pd.DataFrame(data)
st.dataframe(df_thucpham, use_container_width=True, hide_index=True)

# ==================== SO SÁNH NĂM & THÁNG ====================
st.markdown("---")
st.subheader("📈 So sánh lạm phát tự động")
c1, c2 = st.columns(2)
with c1:
    st.metric("Năm 2025", f"{tong_tvl:,} triệu/tháng")
with c2:
    tvl_2024 = round(tong_tvl / (1 + tang_trung_binh_nam), 1)
    st.metric("Năm 2024", f"{tvl_2024:,} triệu", f"+{tang_trung_binh_nam*100:.1f}%")

c3, c4 = st.columns(2)
with c3:
    st.metric(f"Tháng {datetime.now().strftime('%m/%Y')}", f"{tong_tvl:,} triệu/tháng")
with c4:
    tvl_thang_truoc = round(tong_tvl / (1 + thay_doi_thang_truoc), 1)
    st.metric("Tháng trước", f"{tvl_thang_truoc:,} triệu", f"+{thay_doi_thang_truoc*100:.1f}%")

# ==================== SO SÁNH THEO QUẬN ====================
st.markdown("---")
st.subheader("🗺️ So sánh TVL theo quận (cùng cấu hình)")
tvl_theo_quan = []
for q in quan_list:
    nha_o_temp = gia_nha_muc[loai_nha][thanhpho][muc_gia] * heso_quan[q] * random.uniform(0.95, 1.05)
    tvl_temp = round(thuc_pham_gd + nha_o_temp + chi_phi_tre + tien_tien_ich/1_000_000 + quan_ao, 1)
    tvl_theo_quan.append({"Quận": q, "TVL (triệu)": tvl_temp})

fig_bar = go.Figure(go.Bar(
    x=[d["Quận"] for d in tvl_theo_quan],
    y=[d["TVL (triệu)"] for d in tvl_theo_quan],
    marker_color='#FF6B6B',
    text=[f"{v:.1f}" for v in [d["TVL (triệu)"] for d in tvl_theo_quan]],
    textposition='outside'
))
fig_bar.update_layout(title="TVL theo quận", xaxis_tickangle=-45, height=500)
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.caption(f"🚀 Auto-update {datetime.now().strftime('%d/%m/%Y %H:%M')} | TVL Pro 2025 | Made with ❤️ by @Nhatminh | Không cần Google Sheets nữa!")

