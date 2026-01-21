import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text
import time

# --- 1. CẤU HÌNH TRANG (Đã sửa lỗi dấu ngoặc kép) ---
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

# --- 3. CHỈ DẪN HỆ THỐNG (Giữ nguyên nội dung của thầy) ---
full_system_instruction = """
SYSTEM INSTRUCTIONS: TRỢ LÝ HỌC TẬP & GIẢNG DẠY NGỮ VĂN - "VĂN SĨ SỐ"
I. ĐỊNH DANH: Trợ lý chuyên môn cho Giáo viên & Mentor cho Học sinh trường PTDTBT THCS Hố Quáng Phìn.
II. GIAO THỨC:
1. GIÁO VIÊN: Chuyên nghiệp, dùng ngữ liệu ngoài SGK khi ra đề (Mã A Lềnh, Hùng Đình Quý).
2. HỌC SINH: Thân thiện, không làm bài hộ, chỉ gợi ý.
III. KHO DỮ LIỆU: Ưu tiên văn hóa Tuyên Quang - Hà Giang.
"""

# --- 4. KHỞI TẠO MÔ HÌNH (CƠ CHẾ AN TOÀN 2 LỚP) ---
generation_config = {"temperature": 1, "max_output_tokens": 8192}

# Biến kiểm tra xem có phải dùng chế độ cũ không
if "is_legacy_mode" not in st.session_state:
    st.session_state.is_legacy_mode = False

try:
    # Ưu tiên 1: Thử chạy Gemini 1.5 Flash (Bản mới, nhanh, rẻ)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        generation_config=generation_config,
        system_instruction=full_system_instruction
    )
    # Kiểm tra thử kết nối ngay lập tức
    model.count_tokens("test")
    st.session_state.is_legacy_mode = False

except Exception:
    # Ưu tiên 2: Nếu lỗi (do thư viện cũ hoặc lỗi Quota), tự động lùi về Gemini Pro
    model = genai.GenerativeModel(
        model_name="gemini-pro", 
        generation_config=generation_config
    )
    st.session_state.is_legacy_mode = True # Đánh dấu đang dùng bản cũ

# --- 5. GIAO DIỆN CHAT ---
st.title("📚 VĂN SĨ SỐ - TRỢ LÝ NGỮ VĂN")
if st.session_state.is_legacy_mode:
    st.caption("Đang chạy chế độ tương thích (Gemini Pro)")

# Khởi tạo lịch sử
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Nếu phải dùng bản cũ (không hỗ trợ system_instruction), ta gửi nó như tin nhắn đầu tiên
    if st.session_state.is_legacy_mode:
        st.session_state.messages.append({"role": "user", "content": "HÃY TUÂN THỦ:\n" + full_system_instruction})
        st.session_state.messages.append({"role": "model", "content": "Đã rõ. Tôi là Văn Sĩ Số."})

# Hiển thị lịch sử (Ẩn tin nhắn cài đặt nếu ở chế độ cũ)
for i, message in enumerate(st.session_state.messages):
    if st.session_state.is_legacy_mode and i < 2:
        continue
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
        # Chuẩn bị lịch sử gửi đi
        history_for_model = [
            {"role": m["role"], "parts": [m["content"]]} 
            for m in st.session_state.messages 
            if m["role"] in ["user", "model"]
        ]
        
        # Gửi tin nhắn
        chat_session = model.start_chat(history=history_for_model[:-1])
        with st.chat_message("assistant"):
            with st.spinner("Đang suy nghĩ..."):
                response = chat_session.send_message(prompt)
                st.markdown(response.text)
        
        st.session_state.messages.append({"role": "model", "content": response.text})
        
        # Đợi 1 chút rồi làm mới trang để xóa text giọng nói
        time.sleep(0.5)
        st.rerun()
        
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}. Thầy vui lòng thử lại sau 30 giây.")
