import streamlit as st
import google.generativeai as genai

# 1. Cấu hình trang (Đã sửa lỗi dấu ngoặc kép gây SyntaxError)
st.set_page_config(
    page_title='TRỢ LÝ HỌC TẬP & GIẢNG DẠY NGỮ VĂN - "VĂN SĨ SỐ"',
    page_icon="📚",
    layout="centered"
)

st.title("📚 VĂN SĨ SỐ - TRỢ LÝ NGỮ VĂN")
st.caption("Trợ lý Sư phạm Ngữ Văn - Trường PTDTBT THCS Hố Quáng Phìn")

# 2. Kiểm tra và Cấu hình API Key (Khắc phục lỗi "Chưa tìm thấy API Key")
if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception as e:
        st.error(f"Lỗi cấu hình API: {e}")
else:
    st.error("Chưa tìm thấy API Key. Thầy vui lòng vào Settings -> Secrets để nhập key.")
    st.stop() # Dừng chương trình nếu không có key

# 3. Khởi tạo mô hình (Ưu tiên 1.5 Flash, tự động lùi về Pro nếu lỗi)
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
    # Test thử
    model.count_tokens("test")
except Exception:
    model = genai.GenerativeModel("gemini-pro")

# 4. Giao diện Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Em cần thầy giúp gì hôm nay?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    try:
        response = model.generate_content(prompt)
        st.session_state.messages.append({"role": "model", "content": response.text})
        st.chat_message("assistant").write(response.text)
    except Exception as e:
        st.error(f"Có lỗi khi gọi AI: {e}")
