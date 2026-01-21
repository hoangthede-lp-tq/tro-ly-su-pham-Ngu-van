import streamlit as st
import google.generativeai as genai
import sys

# 1. Cấu hình trang
st.set_page_config(page_title="Kiểm tra Hệ thống", page_icon="🔧")
st.title("🔧 TRANG CHẨN ĐOÁN LỖI")

# 2. Kiểm tra Thư viện
try:
    version = genai.__version__
    st.success(f"✅ Đã cài thư viện google-generativeai phiên bản: {version}")
    
    # Kiểm tra xem phiên bản có đủ mới không (cần >= 0.8.3)
    # Đây là cách so sánh đơn giản, thầy chỉ cần nhìn số là được
    if version < "0.8.3":
        st.error("❌ Phiên bản quá cũ! Lỗi do file 'requirements.txt' chưa được nhận.")
        st.info("👉 Thầy hãy kiểm tra lại tên file 'requirements.txt' trên GitHub xem có viết sai chính tả không.")
    else:
        st.info("✅ Phiên bản thư viện đã ổn.")
        
except Exception as e:
    st.error("❌ Chưa cài được thư viện google-generativeai.")

# 3. Kiểm tra API Key & Liệt kê Mô hình
st.write("---")
st.write("📡 Đang kết nối thử đến Google...")

if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    try:
        # Thử lấy danh sách mô hình
        models = list(genai.list_models())
        found_models = [m.name for m in models if 'gemini' in m.name]
        
        if found_models:
            st.success(f"✅ Kết nối thành công! Tìm thấy {len(found_models)} mô hình Gemini.")
            st.json(found_models) # Hiện danh sách để thầy xem
            
            # Nếu kết nối OK, hiện khung chat thử
            st.write("---")
            st.header("💬 Chat Test")
            model = genai.GenerativeModel("gemini-1.5-flash") 
            if prompt := st.chat_input("Gõ thử gì đó..."):
                st.write(f"User: {prompt}")
                response = model.generate_content(prompt)
                st.write(f"AI: {response.text}")
        else:
            st.warning("⚠️ Kết nối được nhưng không thấy mô hình Gemini nào. Có thể Key này bị hạn chế.")
            
    except Exception as e:
        st.error(f"❌ Lỗi kết nối API: {e}")
        st.error("👉 Khả năng cao API Key bị sai hoặc lấy nhầm chỗ. Hãy lấy lại Key tại aistudio.google.com")
else:
    st.error("❌ Chưa nhập API Key trong Secrets.")
