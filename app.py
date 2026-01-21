import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text
import time

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title='TRỢ LÝ HỌC TẬP & GIẢNG DẠY NGỮ VĂN - "VĂN SĨ SỐ"',
    page_icon="📚",
    layout="centered"
)

# --- 2. CẤU HÌNH API KEY ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Chưa tìm thấy API Key. Vui lòng kiểm tra lại Secrets.")
    st.stop()

# --- 3. CHỈ DẪN HỆ THỐNG ---
system_instruction = """
SYSTEM INSTRUCTIONS: TRỢ LÝ HỌC TẬP & GIẢNG DẠY NGỮ VĂN - "VĂN SĨ SỐ"
I. ĐỊNH DANH: Trợ lý chuyên môn cho Giáo viên & Mentor cho Học sinh trường PTDTBT THCS Hố Quáng Phìn.
II. GIAO THỨC:
1. GIÁO VIÊN: Chuyên nghiệp, dùng ngữ liệu ngoài SGK khi ra đề (Mã A Lềnh, Hùng Đình Quý).
2. HỌC SINH: Thân thiện, không làm bài hộ, chỉ gợi ý.
III. KHO DỮ LIỆU: Ưu tiên văn hóa Tuyên Quang - Hà Giang.
"""

# --- 4. KHỞI TẠO MÔ HÌNH (SỬ DỤNG BẢN FLASH LATEST - ỔN ĐỊNH NHẤT) ---
generation_config = {"temperature": 1, "max_output_tokens": 8192}

try:
    # Dùng alias "gemini-flash-latest" để tự động chọn bản Flash ổn định nhất của Google
    # Bản này có hạn mức miễn phí cao, tránh lỗi 429
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest", 
        generation_config=generation_config,
        system_instruction=system_instruction
    )
except Exception:
    # Dự phòng cuối cùng
    model = genai.GenerativeModel("gemini-pro")

# --- 5. GIAO DIỆN CHAT ---
st.title("📚 VĂN SĨ SỐ - TRỢ LÝ NGỮ VĂN")
st.caption("Trợ lý Sư phạm Ngữ Văn - Trường PTDTBT THCS Hố Quáng Phìn")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 6. XỬ LÝ NHẬP LIỆU (Voice + Text) ---
st.divider()
col_mic, col_info = st.columns([1, 4])
with col_mic:
    voice_text = speech_to_text(language='vi', start_prompt="🎙️ Nói", stop_prompt="⏹️ Gửi", just_once=True, key='STT')

prompt = voice_text if voice_text else st.chat_input("Em cần thầy giúp gì hôm nay?")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        history_for_model = [
            {"role": m["role"], "parts": [m["content"]]} 
            for m in st.session_state.messages 
            if m["role"] in ["user", "model"]
        ]
        
        chat_session = model.start_chat(history=history_for_model[:-1])
        
        with st.chat_message("assistant"):
            with st.spinner("Đang suy nghĩ..."):
                response = chat_session.send_message(prompt)
                st.markdown(response.text)
        
        st.session_state.messages.append({"role": "model", "content": response.text})
        time.sleep(0.5)
        st.rerun()
        
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}. Thầy vui lòng thử lại sau 30 giây.")
