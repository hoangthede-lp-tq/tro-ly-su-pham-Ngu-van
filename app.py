import streamlit as st
import google.generativeai as genai
import importlib.metadata

st.title("🛠 Trạm Khám Bệnh Kỹ Thuật")

# 1. Kiểm tra xem Streamlit đã cài bản mới nhất chưa
try:
    version = importlib.metadata.version("google-generativeai")
    st.info(f"Phiên bản thư viện Google đang chạy: {version}")
    # Nếu version nhỏ hơn 0.7.0 thì đây chính là nguyên nhân lỗi
except:
    st.error("Không kiểm tra được phiên bản thư viện.")

# 2. Kiểm tra xem Chìa khóa của thầy "nhìn thấy" được những model nào
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    st.success("✅ Đã nhận được API Key")
    
    st.write("---")
    st.write("**Danh sách các Model (Bộ não) thực tế đang có sẵn:**")
    
    try:
        models_found = False
        for m in genai.list_models():
            # Chỉ liệt kê các model biết tạo văn bản (loại bỏ model nhúng, âm thanh...)
            if 'generateContent' in m.supported_generation_methods:
                st.code(f"{m.name}") # Đây là tên chính xác chúng ta cần copy
                models_found = True
        
        if not models_found:
            st.warning("Kết nối được nhưng không tìm thấy model nào. Có thể API Key này chưa được kích hoạt quyền.")
            
    except Exception as e:
        st.error(f"❌ Lỗi kết nối: {e}")
        st.write("Gợi ý: Thầy kiểm tra lại API Key xem có bị copy thừa dấu cách không?")

else:
    st.error("⚠️ Chưa tìm thấy API Key trong Secrets.")
