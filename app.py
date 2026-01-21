import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text

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

# --- 3. NỘI DUNG NHẬP VAI (SYSTEM INSTRUCTION) ---
sys_prompt = """
SYSTEM INSTRUCTIONS: TRỢ LÝ HỌC TẬP & GIẢNG DẠY NGỮ VĂN - "VĂN SĨ SỐ"
I. ĐỊNH DANH: Trợ lý chuyên môn cho Giáo viên & Mentor cho Học sinh trường PTDTBT THCS Hố Quáng Phìn.
II. GIAO THỨC:
1. GIÁO VIÊN: Chuyên nghiệp, dùng ngữ liệu ngoài SGK khi ra đề (Mã A Lềnh, Hùng Đình Quý).
2. HỌC SINH: Thân thiện, không làm bài hộ, chỉ gợi ý.
III. KHO DỮ LIỆU: Ưu tiên văn hóa Tuyên Quang - Hà Giang.
"""

# --- 4. KHỞI TẠO MÔ HÌNH (CƠ CHẾ AN TOÀN CAO NHẤT) ---
generation_config = {"temperature": 1, "max_output_tokens": 8192}

# Thử khởi tạo mô hình tốt nhất (1.5 Flash)
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        generation_config=generation_config,
        system_instruction=sys_prompt
    )
    # Nếu thành công, in log nhỏ để biết (chỉ hiện khi chạy local)
    print("Đang chạy: Gemini 1.5 Flash")

except Exception as e:
    # Nếu lỗi (do thư viện cũ hoặc quota), chuyển sang chế độ "Sinh tồn" (Gemini Pro)
    # Lưu ý: Gemini Pro cũ không hỗ trợ tham số 'system_instruction' trong hàm khởi tạo
    # nên ta phải bỏ nó đi và "tiêm" nó vào lịch sử chat sau.
    model = genai.GenerativeModel(
        model_name="gemini-pro", 
        generation_config=generation_config
    )
    # Đánh dấu là đang dùng bản cũ để xử lý logic chèn prompt
    st.session_state.use_legacy_prompting = True
    print(f"Đang chạy: Gemini Pro (Backup mode). Lỗi trước đó: {e}")

# --- 5. GIAO DIỆN CHAT ---
st.title("📚 VĂN SĨ SỐ - TRỢ LÝ NGỮ VĂN")
st.caption("Trợ lý Sư phạm Ngữ Văn - Trường PTDTBT THCS Hố Quáng Phìn")

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Nếu phải dùng chế độ cũ, ta chèn câu nhập vai vào dòng đầu tiên của lịch sử
    if "use_legacy_prompting" in st.session_state:
        st.session_state.messages.append({"role": "user", "content": sys_prompt})
        st.session_state.messages.append({"role": "model", "content": "Tôi đã hiểu nhiệm vụ. Tôi là Văn Sĩ Số."})

# Hiển thị lịch sử (Bỏ qua câu lệnh hệ thống nếu đang dùng chế độ cũ để giao diện đẹp)
for i, message in enumerate(st.session_state.messages):
    # Nếu đang dùng chế độ cũ, ẩn 2 dòng đầu (là dòng nhập vai) đi
    if "use_legacy_prompting" in st.session_state and i < 2:
        continue
    
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 6. NHẬP LIỆU & XỬ LÝ ---
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
        # Chuẩn bị lịch sử chat để gửi
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
        st.rerun() # Làm mới để xóa text voice
        
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}. Thầy hãy thử 'Reboot App' hoặc chờ 1 phút.")
