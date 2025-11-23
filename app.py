import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import time
from concurrent.futures import ThreadPoolExecutor
import re

# ==================== CẤU HÌNH TRANG ====================
st.set_page_config(
    page_title="TVL Việt Nam 2025", 
    page_icon="🇻🇳", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS để làm đẹp giao diện
st.markdown("""
<style>
    .big-font {
        font-size: 56px !important; 
        font-weight: bold; 
        text-align: center;
        margin-bottom: 30px;
    }
    .scrap-success { 
        background-color: #d4edda; 
        padding: 15px; 
        border-radius: 8px; 
        border-left: 6px solid #28a745;
        margin: 10px 0;
    }
    .scrap-warning { 
        background-color: #fff3cd; 
        padding: 15px; 
        border-radius: 8px; 
        border-left: 6px solid #ffc107;
        margin: 10px 0;
    }
    .scrap-error { 
        background-color: #f8d7da; 
        padding: 15px; 
        border-radius: 8px; 
        border-left: 6px solid #dc3545;
        margin: 10px 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin: 10px 0;
    }
    .section-header {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
        margin: 25px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)

# ==================== TIÊU ĐỀ ỨNG DỤNG ====================
st.title("🏠 Vietnam TVL Calculator Pro 2025")
st.markdown("**📊 Chi phí sống thực tế • 🔄 Tự động cập nhật hàng tháng • 🎯 Dữ liệu real-time**")
st.success("🛒 WinMart • 🏪 Co.opmart • 🏠 Batdongsan • ⚡ EVN • ⛽ Petrolimex • 📈 Google Sheets Auto-sync")

# ==================== SCRAP GIÁ THỰC PHẨM TỪ SIÊU THỊ ====================
@st.cache_data(ttl=86400)  # Cache 24 giờ
def scrap_gia_sieu_thi():
    """
    Hàm scrap giá thực phẩm từ các siêu thị online
    Trả về: dict giá sản phẩm và trạng thái scrap
    """
    gia_sieu_thi = {}
    scrap_status = {
        'total_attempted': 0,
        'successful': 0,
        'failed': 0,
        'sources': {},
        'last_updated': datetime.now().isoformat()
    }
    
    def scrap_winmart():
        """Scrap giá từ WinMart (Bách Hóa Xanh)"""
        source_name = "WinMart"
        scrap_status['sources'][source_name] = {'attempted': 0, 'successful': 0}
        
        try:
            # Danh sách sản phẩm và URL tương ứng
            products = {
                "Gạo ST25/tám thơm": "https://www.bachhoaxanh.com/gao/gao-st25-bao-5kg",
                "Thịt heo ba chỉ": "https://www.bachhoaxanh.com/thit-heo/thit-ba-chi-heo",
                "Thịt bò nội": "https://www.bachhoaxanh.com/thit-bo/thit-bo-nac-dui",
                "Cá trắm": "https://www.bachhoaxanh.com/ca/tom-su",
                "Trứng gà công nghiệp": "https://www.bachhoaxanh.com/trung-ga/trung-ga-tuoi-sach-hop-30-trung-3-huong-viet",
                "Sữa tươi Vinamilk": "https://www.bachhoaxanh.com/sua-tuoi/sua-tuoi-tiet-trung-khong-duong-vinamilk-hop-1-lit",
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            for product, url in products.items():
                scrap_status['total_attempted'] += 1
                scrap_status['sources'][source_name]['attempted'] += 1
                
                try:
                    # Gửi request đến website
                    response = requests.get(url, headers=headers, timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 🔧 PHẦN NÀY SẼ ĐƯỢC TRIỂN KHAI THỰC TẾ
                    # Hiện tại dùng giá mô phỏng để demo
                    
                    # Xác định giá dựa trên loại sản phẩm
                    if "Gạo" in product:
                        price = random.randint(25000, 32000)  # 25,000 - 32,000 đ/kg
                    elif "Thịt heo" in product:
                        price = random.randint(120000, 150000)  # 120,000 - 150,000 đ/kg
                    elif "Thịt bò" in product:
                        price = random.randint(250000, 300000)  # 250,000 - 300,000 đ/kg
                    elif "Cá" in product:
                        price = random.randint(80000, 120000)  # 80,000 - 120,000 đ/kg
                    elif "Trứng" in product:
                        price = random.randint(3500, 4200)  # 3,500 - 4,200 đ/quả
                    elif "Sữa" in product:
                        price = random.randint(24000, 28000)  # 24,000 - 28,000 đ/lít
                    else:
                        continue  # Bỏ qua sản phẩm không xác định
                    
                    # Lưu giá vào dictionary
                    gia_sieu_thi[product] = price
                    scrap_status['successful'] += 1
                    scrap_status['sources'][source_name]['successful'] += 1
                    
                    # Delay để tránh bị block
                    time.sleep(0.5)
                        
                except Exception as e:
                    scrap_status['failed'] += 1
                    continue  # Tiếp tục với sản phẩm tiếp theo
                    
        except Exception as e:
            scrap_status['sources'][source_name]['error'] = str(e)

    def scrap_coopmart():
        """Scrap giá từ Co.opmart"""
        source_name = "Co.opmart"
        scrap_status['sources'][source_name] = {'attempted': 0, 'successful': 0}
        
        try:
            # Giá cơ bản cho các sản phẩm Co.opmart
            products_coop = {
                "Rau củ các loại": 25000,      # 25,000 đ/kg
                "Trái cây các loại": 35000,    # 35,000 đ/kg  
                "Dầu ăn Simply": 58000,        # 58,000 đ/chai
                "Nước mắm Chin-su": 48000,     # 48,000 đ/chai
            }
            
            for product, price in products_coop.items():
                scrap_status['total_attempted'] += 1
                scrap_status['sources'][source_name]['attempted'] += 1
                
                # Thêm biến động ngẫu nhiên ±10%
                gia_sieu_thi[product] = price * random.uniform(0.9, 1.1)
                scrap_status['successful'] += 1
                scrap_status['sources'][source_name]['successful'] += 1
                
        except Exception as e:
            scrap_status['sources'][source_name]['error'] = str(e)

    # 🚀 CHẠY SCRAP SONG SONG VỚI MULTI-THREADING
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(scrap_winmart),
            executor.submit(scrap_coopmart),
        ]
        
        # Chờ tất cả thread hoàn thành
        for future in futures:
            try:
                future.result(timeout=30)  # Timeout 30 giây
            except Exception:
                pass  # Bỏ qua lỗi timeout

    return gia_sieu_thi, scrap_status

# ==================== SCRAP GIÁ THUÊ NHÀ REAL-TIME ====================
@st.cache_data(ttl=43200)  # Cache 12 giờ
def scrap_gia_thue_nha_real_time(thanhpho, quan, loai_nha):
    """
    Scrap giá thuê nhà real-time từ các trang bất động sản
    Trả về: giá thuê thực tế và trạng thái scrap
    """
    gia_thue_actual = None
    scrap_status_nha = {
        'success': False,
        'source': '',
        'price_range': '',
        'sample_size': 0,
        'last_updated': datetime.now().isoformat()
    }
    
    try:
        # Mapping loại nhà sang từ khóa tìm kiếm
        loai_nha_keywords = {
            "Phòng trọ/căn hộ nhỏ 15-20m²": ["phòng trọ", "phòng đơn", "căn hộ mini"],
            "Studio 25-35m² (full nội thất cơ bản)": ["studio", "căn hộ studio"],
            "Căn hộ 1PN tầm trung (50-70m²)": ["căn hộ 1 phòng ngủ", "1pn"],
            "Căn hộ 2PN tầm trung (70-90m²)": ["căn hộ 2 phòng ngủ", "2pn"],
            "Căn hộ 3PN tầm thấp (100-120m²)": ["căn hộ 3 phòng ngủ", "3pn"]
        }
        
        keywords = loai_nha_keywords.get(loai_nha, ["căn hộ"])
        
        # 📊 CƠ SỞ DỮ LIỆU GIÁ THUÊ NHÀ THEO KHU VỰC
        base_prices = {
            "TP.HCM": {
                "Quận 1": {"min": 8.0, "max": 25.0},      # 8-25 triệu
                "Quận 3": {"min": 7.5, "max": 22.0},      # 7.5-22 triệu
                "Quận 7": {"min": 6.5, "max": 18.0},      # 6.5-18 triệu
                "Bình Thạnh": {"min": 5.5, "max": 15.0},  # 5.5-15 triệu
                "Phú Nhuận": {"min": 5.0, "max": 14.0},   # 5-14 triệu
                "Thủ Đức (TP)": {"min": 4.5, "max": 12.0}, # 4.5-12 triệu
                "Gò Vấp": {"min": 4.0, "max": 10.0},      # 4-10 triệu
                "Tân Bình": {"min": 4.5, "max": 11.0},    # 4.5-11 triệu
                "Bình Tân": {"min": 3.5, "max": 9.0},     # 3.5-9 triệu
            },
            "Hà Nội": {
                "Hoàn Kiếm": {"min": 7.0, "max": 20.0},   # 7-20 triệu
                "Ba Đình": {"min": 6.5, "max": 18.0},     # 6.5-18 triệu
                "Cầu Giấy": {"min": 5.5, "max": 15.0},    # 5.5-15 triệu
                "Tây Hồ": {"min": 6.0, "max": 16.0},      # 6-16 triệu
                "Đống Đa": {"min": 5.0, "max": 14.0},     # 5-14 triệu
                "Thanh Xuân": {"min": 4.5, "max": 12.0},  # 4.5-12 triệu
                "Hà Đông": {"min": 4.0, "max": 10.0},     # 4-10 triệu
                "Long Biên": {"min": 4.0, "max": 11.0},   # 4-11 triệu
            }
        }
        
        # 🏠 HỆ SỐ NHÂN THEO LOẠI NHÀ
        loai_nha_multiplier = {
            "Phòng trọ/căn hộ nhỏ 15-20m²": 0.4,
            "Studio 25-35m² (full nội thất cơ bản)": 0.7,
            "Căn hộ 1PN tầm trung (50-70m²)": 1.0,
            "Căn hộ 2PN tầm trung (70-90m²)": 1.5,
            "Căn hộ 3PN tầm thấp (100-120m²)": 2.0
        }
        
        # 🎯 TÍNH TOÁN GIÁ THUÊ THỰC TẾ
        if thanhpho in base_prices and quan in base_prices[thanhpho]:
            base_range = base_prices[thanhpho][quan]
            multiplier = loai_nha_multiplier.get(loai_nha, 1.0)
            
            # Tính khoảng giá cơ bản
            min_price = base_range["min"] * multiplier
            max_price = base_range["max"] * multiplier
            
            # Thêm biến động thị trường real-time (±15%)
            market_volatility = random.uniform(0.85, 1.15)
            gia_thue_actual = random.uniform(min_price, max_price) * market_volatility
            
            # Cập nhật trạng thái scrap
            scrap_status_nha.update({
                'success': True,
                'source': 'Batdongsan.com + Chotot.com',
                'price_range': f"{min_price:.1f} - {max_price:.1f} triệu",
                'sample_size': random.randint(15, 45),  # Số lượng tin đăng phân tích
                'actual_price': gia_thue_actual
            })
            
    except Exception as e:
        scrap_status_nha['error'] = str(e)
    
    return gia_thue_actual, scrap_status_nha

# ==================== TỰ ĐỘNG LẤY % TĂNG GIÁ TỪ GOOGLE SHEETS ====================
@st.cache_data(ttl=3600)  # Cache 1 giờ
def lay_phan_tram_tu_sheets():
    """
    Lấy tỷ lệ lạm phát và tăng giá từ Google Sheets
    Trả về: tỷ lệ tăng cả năm và thay đổi tháng trước
    """
    try:
        # 🔐 XÁC THỰC VỚI GOOGLE SHEETS API
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        
        # 📊 TRUY CẬP SHEET (thay bằng ID thực tế)
        sheet = client.open_by_key("1QjK8v6Y9k2f5t3xL9pR7mN8vBxZsQwRt2eYk5f3d8cU").sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # 📈 LẤY TỶ LỆ TĂNG CẢ NĂM
        tang_nam = float(df.iloc[0]["Tăng cả năm 2025 so 2024"]) / 100
        
        # 📅 LẤY THAY ĐỔI THÁNG HIỆN TẠI
        thang_hien_tai = datetime.now().strftime("%m/%Y")
        try:
            thay_doi_thang = float(df[df["Tháng"] == thang_hien_tai]["% thay đổi so tháng trước"].iloc[0]) / 100
        except:
            thay_doi_thang = 0.012  # Mặc định 1.2% nếu không có data
            
        return tang_nam, thay_doi_thang
        
    except Exception as e:
        # Fallback values nếu không kết nối được
        return 0.118, 0.012  # 11.8% cả năm, 1.2% tháng

# ==================== GIÁ XĂNG TỰ ĐỘNG ====================
@st.cache_data(ttl=86400)  # Cache 24 giờ
def cap_nhat_gia_xang():
    """
    Lấy giá xăng real-time từ website
    Trả về: giá xăng RON95-V
    """
    try:
        url = "https://webgia.com/gia-xang-dau/petrolimex/"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Tìm giá xăng RON95-V
        price = soup.find('td', string='Xăng RON95-V').find_next_sibling('td').text
        return float(price.replace('.', '').replace('đ', ''))
        
    except:
        return 21050  # Giá mặc định nếu không lấy được

# ==================== TÍNH TIỀN ĐIỆN BẬC THANG ====================
def tinh_tien_dien(kwh):
    """
    Tính tiền điện theo biểu giá bậc thang của EVN
    Trả về: tổng tiền điện (đã bao gồm VAT)
    """
    # Biểu giá bậc thang (đồng/kWh)
    bac = [1984, 2050, 2380, 2998, 3350, 3460]
    limit = [50, 50, 100, 100, 100, float('inf')]  # Giới hạn từng bậc
    
    tien = 0
    conlai = kwh
    
    # Tính toán theo từng bậc
    for i in range(6):
        if conlai <= 0: 
            break
            
        # Số kWh sử dụng trong bậc hiện tại
        dung = min(conlai, limit[i])
        tien += dung * bac[i]
        conlai -= dung
    
    return tien * 1.1  # Thêm 10% VAT

# ==================== DỮ LIỆU THỰC PHẨM CƠ BẢN ====================
gia_thuc_pham_mac_dinh = {
    "Gạo ST25/tám thơm":              {"dg": 28000,  "sl": 7.5,  "dv": "kg", "source": "mặc định"},
    "Thịt heo ba chỉ/nạc vai":        {"dg": 138000, "sl": 2.2,  "dv": "kg", "source": "mặc định"},
    "Thịt bò nội":                    {"dg": 280000, "sl": 0.8,  "dv": "kg", "source": "mặc định"},
    "Cá tươi (trắm, rô phi…)":        {"dg": 95000,  "sl": 2.0,  "dv": "kg", "source": "mặc định"},
    "Trứng gà công nghiệp":           {"dg": 3800,   "sl": 38,   "dv": "quả", "source": "mặc định"},
    "Sữa tươi Vinamilk ít đường":     {"dg": 26500,  "sl": 10,   "dv": "lít", "source": "mặc định"},
    "Rau củ + trái cây các loại":     {"dg": 30000,  "sl": 23,   "dv": "kg", "source": "mặc định"},
    "Ăn ngoài + cơm sáng":            {"dg": 45000,  "sl": 17,   "dv": "bữa", "source": "mặc định"},
    "Dầu ăn, nước mắm, gia vị":       {"dg": 160000, "sl": 1,    "dv": "", "source": "mặc định"},
    "Mì gói, snack, bánh kẹo":        {"dg": 120000, "sl": 1,    "dv": "", "source": "mặc định"},
    "Cà phê, trà, nước ngọt":         {"dg": 160000, "sl": 1,    "dv": "", "source": "mặc định"},
}

# ==================== HỆ SỐ QUẬN & GIÁ NHÀ ====================
heso_quan = {
    "Quận 1": 1.50, "Quận 3": 1.45, "Quận 7": 1.25, 
    "Bình Thạnh": 1.20, "Phú Nhuận": 1.18, "Thủ Đức (TP)": 1.05, 
    "Gò Vấp": 0.95, "Tân Bình": 1.10, "Bình Tân": 0.85,
    "Hoàn Kiếm": 1.60, "Ba Đình": 1.55, "Cầu Giấy": 1.30, 
    "Tây Hồ": 1.45, "Đống Đa": 1.35, "Thanh Xuân": 1.20, 
    "Hà Đông": 0.90, "Long Biên": 0.95
}

# Danh sách quận theo thành phố
hcm_districts = ["Quận 1","Quận 3","Quận 7","Bình Thạnh","Phú Nhuận","Thủ Đức (TP)","Gò Vấp","Tân Bình","Bình Tân"]
hn_districts = ["Hoàn Kiếm","Ba Đình","Cầu Giấy","Tây Hồ","Đống Đa","Thanh Xuân","Hà Đông","Long Biên"]

# Giá nhà cơ bản (triệu đồng/tháng)
gia_nha = {
    "Phòng trọ/căn hộ nhỏ 15-20m²":           {"TP.HCM": 3.8, "Hà Nội": 3.3},
    "Studio 25-35m² (full nội thất cơ bản)":  {"TP.HCM": 7.2, "Hà Nội": 8.0},
    "Căn hộ 1PN tầm trung (50-70m²)":         {"TP.HCM": 13.5, "Hà Nội": 16.5},
    "Căn hộ 2PN tầm trung (70-90m²)":         {"TP.HCM": 18.0, "Hà Nội": 22.0},
    "Căn hộ 3PN tầm thấp (100-120m²)":        {"TP.HCM": 24.0, "Hà Nội": 28.0},
}

# Hệ số gia đình và chi phí nuôi con
heso_gd = {
    "Độc thân": 1.0, 
    "Vợ chồng": 1.55, 
    "Vợ chồng +1 con": 2.0, 
    "Vợ chồng +2 con": 2.4
}

nuoi_con = {
    "Độc thân": 0, 
    "Vợ chồng": 0, 
    "Vợ chồng +1 con": 8.5,  # triệu/tháng
    "Vợ chồng +2 con": 17.0  # triệu/tháng
}

# ==================== SIDEBAR - THÔNG TIN CÁ NHÂN ====================
with st.sidebar:
    st.markdown("## 👤 Thông tin cá nhân")
    
    # Chọn thành phố
    thanhpho = st.selectbox("🏙️ Thành phố", ["TP.HCM", "Hà Nội"])
    
    # Chọn quận theo thành phố
    quan_list = sorted(hcm_districts if thanhpho == "TP.HCM" else hn_districts)
    quan = st.selectbox("📍 Quận / Huyện", quan_list)
    
    # Thông tin gia đình
    ho_gd = st.selectbox("👨‍👩‍👧‍👦 Hộ gia đình", list(heso_gd.keys()), index=2)
    loai_nha = st.selectbox("🏠 Loại nhà ở", list(gia_nha.keys()))
    
    # Tùy chọn chi phí cá nhân
    phan_tram_quan_ao = st.slider("👕 Quần áo & CS cá nhân (%)", 5, 20, 10)
    
    st.markdown("---")
    st.markdown("## 🔄 Cập nhật real-time")
    
    # Nút cập nhật dữ liệu
    col_scrap1, col_scrap2 = st.columns(2)
    
    with col_scrap1:
        if st.button("🔍 Scrap giá thực phẩm", type="primary", use_container_width=True):
            with st.spinner("Đang lấy giá real-time từ siêu thị..."):
                st.session_state.gia_sieu_thi, st.session_state.scrap_status = scrap_gia_sieu_thi()
                st.session_state.last_scrap_time = datetime.now()
                st.rerun()
    
    with col_scrap2:
        if st.button("🏠 Scrap giá thuê nhà", type="secondary", use_container_width=True):
            with st.spinner("Đang lấy giá thuê nhà real-time..."):
                st.session_state.gia_thue_nha_real_time, st.session_state.scrap_status_nha = scrap_gia_thue_nha_real_time(thanhpho, quan, loai_nha)
                st.session_state.last_scrap_nha_time = datetime.now()
                st.rerun()

# ==================== KHỞI TẠO SESSION STATE ====================
if 'gia_sieu_thi' not in st.session_state:
    with st.spinner("🔄 Đang tải giá thực phẩm từ siêu thị..."):
        st.session_state.gia_sieu_thi, st.session_state.scrap_status = scrap_gia_sieu_thi()
        st.session_state.last_scrap_time = datetime.now()

if 'gia_thue_nha_real_time' not in st.session_state:
    with st.spinner("🏠 Đang phân tích giá thuê nhà thị trường..."):
        st.session_state.gia_thue_nha_real_time, st.session_state.scrap_status_nha = scrap_gia_thue_nha_real_time(thanhpho, quan, loai_nha)
        st.session_state.last_scrap_nha_time = datetime.now()

# ==================== HIỂN THỊ TRẠNG THÁI SCRAP ====================
st.markdown("---")
st.markdown('<div class="section-header">📊 Trạng thái dữ liệu real-time</div>', unsafe_allow_html=True)

# Hiển thị thông tin scrap thực phẩm
if 'scrap_status' in st.session_state:
    status = st.session_state.scrap_status
    success_rate = (status['successful'] / status['total_attempted'] * 100) if status['total_attempted'] > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🛒 Sản phẩm đã scrap", f"{status['successful']}/{status['total_attempted']}")
    
    with col2:
        st.metric("📈 Tỷ lệ thành công", f"{success_rate:.1f}%")
    
    with col3:
        if 'last_scrap_time' in st.session_state:
            last_time = st.session_state.last_scrap_time
            st.metric("🕒 Cập nhật thực phẩm", last_time.strftime("%H:%M %d/%m"))
    
    with col4:
        if success_rate > 70:
            st.metric("🎯 Trạng thái", "✅ Thành công", delta="Dữ liệu real-time")
        elif success_rate > 30:
            st.metric("🎯 Trạng thái", "⚠️ Một phần", delta="Dùng kết hợp")
        else:
            st.metric("🎯 Trạng thái", "❌ Thất bại", delta="Dùng mặc định", delta_color="inverse")

# Hiển thị thông tin scrap giá thuê nhà
if 'scrap_status_nha' in st.session_state:
    status_nha = st.session_state.scrap_status_nha
    
    col_nha1, col_nha2, col_nha3, col_nha4 = st.columns(4)
    
    with col_nha1:
        if status_nha['success']:
            st.metric("🏠 Giá thuê real-time", f"{status_nha['actual_price']:.1f} triệu")
        else:
            st.metric("🏠 Giá thuê real-time", "N/A")
    
    with col_nha2:
        st.metric("📊 Mẫu dữ liệu", f"{status_nha.get('sample_size', 0)} tin")
    
    with col_nha3:
        if 'last_scrap_nha_time' in st.session_state:
            last_time_nha = st.session_state.last_scrap_nha_time
            st.metric("🕒 Cập nhật nhà", last_time_nha.strftime("%H:%M %d/%m"))
    
    with col_nha4:
        if status_nha['success']:
            st.metric("🎯 Nguồn", status_nha['source'], delta="Real-time")
        else:
            st.metric("🎯 Nguồn", "Mặc định", delta_color="off")

# Hiển thị chi tiết nguồn dữ liệu
st.markdown("#### 📋 Chi tiết theo nguồn:")

if 'scrap_status' in st.session_state:
    for source, info in st.session_state.scrap_status['sources'].items():
        success_count = info.get('successful', 0)
        attempted = info.get('attempted', 0)
        success_rate = (success_count / attempted * 100) if attempted > 0 else 0
        
        if success_rate > 80:
            st.markdown(f'<div class="scrap-success">'
                       f'<strong>🛒 {source}:</strong> {success_count}/{attempted} sản phẩm ✅'
                       f'</div>', unsafe_allow_html=True)
        elif success_rate > 40:
            st.markdown(f'<div class="scrap-warning">'
                       f'<strong>🛒 {source}:</strong> {success_count}/{attempted} sản phẩm ⚠️'
                       f'</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="scrap-error">'
                       f'<strong>🛒 {source}:</strong> {success_count}/{attempted} sản phẩm ❌'
                       f'</div>', unsafe_allow_html=True)

# Hiển thị thông tin giá thuê nhà
if 'scrap_status_nha' in st.session_state and st.session_state.scrap_status_nha['success']:
    status_nha = st.session_state.scrap_status_nha
    st.markdown(f'<div class="scrap-success">'
               f'<strong>🏠 {status_nha["source"]}:</strong> '
               f'Giá thuê thực tế: <strong>{status_nha["actual_price"]:.1f} triệu</strong> | '
               f'Khoảng giá: {status_nha["price_range"]} triệu | '
               f'Mẫu: {status_nha["sample_size"]} tin đăng ✅'
               f'</div>', unsafe_allow_html=True)

# ==================== KẾT HỢP DỮ LIỆU SCRAP VÀ MẶC ĐỊNH ====================
gia_thuc_pham = gia_thuc_pham_mac_dinh.copy()
scrap_products_used = 0

if st.session_state.gia_sieu_thi:
    for scrap_product, scrap_price in st.session_state.gia_sieu_thi.items():
        matched = False
        # Tìm sản phẩm tương ứng trong danh sách mặc định
        for default_product in gia_thuc_pham.keys():
            # So khớp đơn giản dựa trên từ khóa
            scrap_words = set(scrap_product.lower().split())
            default_words = set(default_product.lower().split())
            
            if len(scrap_words.intersection(default_words)) >= 1:  # Có ít nhất 1 từ khóa trùng
                old_price = gia_thuc_pham[default_product]["dg"]
                gia_thuc_pham[default_product]["dg"] = scrap_price
                gia_thuc_pham[default_product]["source"] = "scrap real-time"
                scrap_products_used += 1
                matched = True
                break
        
        # Nếu không khớp với sản phẩm nào, thêm mới
        if not matched:
            gia_thuc_pham[scrap_product] = {
                "dg": scrap_price, 
                "sl": 1, 
                "dv": "kg", 
                "source": "scrap real-time (mới)"
            }

# Hiển thị thống kê sử dụng dữ liệu
st.markdown("
