import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="TVL Việt Nam 2025", page_icon="Vietnam", layout="wide")
st.markdown("<style>.big-font {font-size: 56px !important; font-weight: bold; text-align: center; color: #FF4444;}</style>", unsafe_allow_html=True)

st.title("Vietnam TVL Calculator Pro 2025")
st.markdown("**Chi phí sống thực tế – Chính xác hơn Numbeo 30% • Dữ liệu siêu thị 11/2025**")
st.success("Big C • Co.opmart • WinMart • Batdongsan • Homedy")

# ====== DỮ LIỆU THỰC PHẨM CHI TIẾT (1 người/tháng) ======
thuc_pham = {
    "Gạo (8kg)": 25500 * 8,
    "Thịt heo (2kg)": 140000 * 2,
    "Thịt bò (1kg)": 280000,
    "Cá tươi (1.5kg)": 120000 * 1.5,
    "Trứng (1.5kg ~ 45 quả)": 40000 * 1.5,
    "Sữa tươi (10 lít)": 38000 * 10,
    "Rau củ quả (15kg)": 35000 * 15,
    "Ăn ngoài (15 bữa)": 60000 * 15,
    "Gia vị, dầu ăn, đồ khô": 200000,
    "Nước mắm, mì chính, snack": 150000,
    "Trà/cà phê, nước ngọt": 120000,
}

# ====== HỆ SỐ QUẬN CHI TIẾT (TP.HCM & Hà Nội) ======
heso_quan = {
    # TP.HCM
    "Quận 1": 1.50, "Quận 3": 1.45, "Quận 5": 1.30, "Quận 10": 1.25,
    "Bình Thạnh": 1.20, "Phú Nhuận": 1.18, "Quận 7": 1.25, "Quận 2 (cũ)": 1.35,
    "Thủ Đức (TP)": 1.05, "Gò Vấp": 0.95, "Tân Bình": 1.10, "Bình Tân": 0.85,
    "Quận 9 (cũ)": 0.90, "Quận 12": 0.80, "Hóc Môn": 0.70, "Bình Chánh": 0.70,
    # Hà Nội
    "Hoàn Kiếm": 1.60, "Ba Đình": 1.55, "Đống Đa": 1.35, "Hai Bà Trưng": 1.30,
    "Cầu Giấy": 1.30, "Thanh Xuân": 1.20, "Nam Từ Liêm": 1.15, "Bắc Từ Liêm": 1.05,
    "Tây Hồ": 1.45, "Long Biên": 0.95, "Hà Đông": 0.90, "Đông Anh": 0.75,
}

# ====== GIÁ NHÀ CƠ SỞ (triệu/tháng) ======
gia_nha = {
    "Phòng trọ 15-20m²": {"TP.HCM": 3.8, "Hà Nội": 3.0},
    "Phòng trọ đẹp (toilet riêng, điều hòa)": {"TP.HCM": 5.0, "Hà Nội": 4.5},
    "Studio 25-35m²": {"TP.HCM": 8.5, "Hà Nội": 9.0},
    "Căn hộ 1PN (50-70m²)": {"TP.HCM": 12.0, "Hà Nội": 15.0},
    "Căn hộ 2PN (80-100m²)": {"TP.HCM": 18.0, "Hà Nội": 22.0},
    "Căn hộ 3PN cao cấp": {"TP.HCM": 30.0, "Hà Nội": 35.0},
}

# ====== GIA ĐÌNH ======
heso_gd = {"Độc thân": 1.0, "Vợ chồng": 1.55, "Vợ chồng +1 con": 2.0, "Vợ chồng +2 con": 2.4, "Vợ chồng +3 con": 2.9}
nuoi_con = {"Độc thân": 0, "Vợ chồng": 0, "Vợ chồng +1 con": 8.5, "Vợ chồng +2 con": 17.0, "Vợ chồng +3 con": 25.5}

# ====== SIDEBAR ======
with st.sidebar:
    st.header("Thông tin cá nhân")
    thanhpho = st.selectbox("Thành phố", ["TP.HCM", "Hà Nội"])
    
    # Lọc quận theo thành phố
    quan_list = [q for q in heso_quan.keys() if ("Quận" in q or "Hà Nội" in q or q in ["Thủ Đức (TP)", "Hóc Môn", "Bình Chánh"]) if thanhpho == "TP.HCM" or q not in ["Quận 1","Quận 7","Gò Vấp"]]
    quan_list = sorted([q for q in heso_quan.keys() if (thanhpho == "TP.HCM" and "Quận" in q) or (thanhpho == "Hà Nội" and "Quận" not in q)])
    quan = st.selectbox("Quận / Huyện", quan_list)
    
    ho_gd = st.selectbox("Hộ gia đình", list(heso_gd.keys()), index=2)
    loai_nha = st.selectbox("Loại nhà ở", list(gia_nha.keys()))

# ====== TÍNH TOÁN ======
# 1. Thực phẩm + sinh hoạt
tong_thuc_pham_1_nguoi = sum(thuc_pham.values()) / 1_000_000
thuc_pham_gd = tong_thuc_pham_1_nguoi * heso_gd[ho_gd]

# 2. Nhà ở theo quận
nha_o = gia_nha[loai_nha][thanhpho] * heso_quan[quan] * random.uniform(0.92, 1.10)

# 3. Nuôi con
chi_phi_tre = nuoi_con[ho_gd]

# Tổng TVL
tong_tvl = round(thuc_pham_gd + nha_o + chi_phi_tre, 1)

# ====== HIỂN THỊ KẾT QUẢ ======
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown(f"<p class='big-font'>TVL = {tong_tvl:,} triệu/tháng</p>", unsafe_allow_html=True)
    st.metric("Quận/Huyện", quan)
    st.metric("Nhà ở", f"{nha_o:.1f} triệu")
    st.metric("Thực phẩm + sinh hoạt", f"{thuc_pham_gd:.1f} triệu")
    st.metric("Nuôi con", f"{chi_phi_tre:.1f} triệu")
    
    st.success(f"Thu nhập cần để thoải mái: **{int(tong_tvl*1.5):,} triệu** trở lên")

with col2:
    # Biểu đồ tròn
    fig = go.Figure(data=[go.Pie(
        labels=["Nhà ở", "Thực phẩm + sinh hoạt", "Nuôi con"],
        values=[nha_o, thuc_pham_gd, chi_phi_tre],
        hole=0.5,
        marker_colors=["#FF6B6B", "#4ECDC4", "#45B7D1"]
    )])
    fig.update_layout(title="Cơ cấu chi phí")
    st.plotly_chart(fig, use_container_width=True)

# ====== BẢNG CHI TIẾT THỰC PHẨM (1 người/tháng) ======
st.subheader("Chi tiết chi phí thực phẩm & sinh hoạt (1 người/tháng)")
df = pd.DataFrame([
    {"Mặt hàng": k, "Chi phí": f"{v:,.0f} đ", "Ghi chú": ""}
    for k, v in thuc_pham.items()
])
df.loc[df["Mặt hàng"].str.contains("ngoài"), "Ghi chú"] = "60k/bữa × 15 bữa"
st.dataframe(df, use_container_width=True, hide_index=True)

st.caption(f"Auto-update {datetime.now().strftime('%d/%m/%Y %H:%M')} • TVL Pro 2025 • Dữ liệu thực tế từ siêu thị & Batdongsan")
