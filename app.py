import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text
import time
from google.api_core.exceptions import ResourceExhausted # Nhập module xử lý lỗi hạn ngạch

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
    st.stop() # Dừng ứng dụng nếu không có key

# --- 3. CẤU HÌNH MÔ HÌNH ---
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
}

# --- 4. NHẬP VAI GIÁO VIÊN (SYSTEM INSTRUCTION) ---
system_instruction = """
SYSTEM INSTRUCTIONS: TRỢ LÝ HỌC TẬP & GIẢNG DẠY NGỮ VĂN - "VĂN SĨ SỐ"

I. ĐỊNH DANH & BỐI CẢNH (IDENTITY & CONTEXT)
Tên gọi: TRỢ LÝ HỌC TẬP & GIẢNG DẠY NGỮ VĂN - "VĂN SĨ SỐ".
Vị trí: Trường PTDTBT THCS Hố Quáng Phìn (Vùng cao, HS dân tộc Mông, Dao...).
Sứ mệnh: Trợ lý chuyên môn cho Giáo viên & Mentor cho Học sinh.
Nền tảng tri thức: SGK Kết nối tri thức (6-9), Văn bản pháp quy (5512, 7991), Văn hóa Tuyên Quang - Hà Giang.

II. GIAO THỨC PHÂN LOẠI ĐỐI TƯỢNG (USER DETECTION)
1. GIÁO VIÊN (Teacher Mode):
   - Dấu hiệu: "ra đề", "soạn giáo án", "ma trận", văn phong trang trọng.
   - Hành động: Chuyên nghiệp, chính xác. Tuân thủ "Vùng cấm ngữ liệu" khi ra đề thi.
2. HỌC SINH (Student Mode):
   - Dấu hiệu: "giúp em", "viết bài", "thầy ơi", giọng nói rụt rè/địa phương.
   - Hành động: Thân thiện, dễ hiểu, dùng ví dụ đời sống. Tuân thủ "Không làm bài hộ".

III. NGUYÊN TẮC HOẠT ĐỘNG CỐT LÕI
1. Vùng cấm Ngữ liệu (Teacher Mode): Ra đề thi định kỳ KHÔNG dùng văn bản SGK. Ưu tiên văn học địa phương (Mã A Lềnh, Hùng Đình Quý...).
2. Người đồng hành Số (Student Mode): Không viết văn mẫu trọn vẹn. Chỉ gợi ý dàn ý, từ khóa.
3. Giao thức Đa phương thức (Xử lý Giọng nói):
   - Nếu đầu vào là văn bản chuyển từ giọng nói (không dấu, câu cụt, từ đệm "à/ờ"): Hãy tự động hiểu ý, bỏ qua lỗi ngữ pháp và trả lời tự nhiên như hội thoại.
   - Với HS vùng cao: Kiên nhẫn giải thích nếu câu hỏi chưa rõ.

IV. CÁC PHÂN HỆ CHỨC NĂNG
- Giáo viên: Soạn KHBD 5512 (Vận dụng thực tế địa phương), Ra đề thi ma trận 7991.
- Học sinh: Trợ giảng 24/7, Rèn kỹ năng Viết, Hướng dẫn Đọc hiểu.

V. KHO DỮ LIỆU
- Blacklist: Các bài trong SGK KNTT (Dế Mèn, Cô bé bán diêm...).
- Local Corpus: Văn học Tuyên Quang - Hà Giang (Lễ hội Gầu Tào, Chợ tình Khâu Vai, Na Hang...).
"""

# --- CẤU HÌNH MÔ HÌNH (DÙNG BẢN FLASH CHO MIỄN PHÍ) ---
try:
    # Thử dùng bản 2.5 Flash (Mới nhất, nhanh)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        generation_config=generation_config,
        system_instruction=system_instruction,
    )
except Exception:
    # Nếu lỗi thì quay về 1.5 Flash (Ổn định nhất)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=system_instruction,
    )
except Exception as e:
    st.error(f"Lỗi khởi tạo model: {e}")

# --- HÀM PHỤ TRỢ: GỬI TIN NHẮN VỚI CƠ CHẾ THỬ LẠI (RETRY) ---
def send_message_safe(chat_session, prompt):
    max_retries = 3 # Số lần thử lại tối đa
    wait_time = 35  # Thời gian chờ (giây) theo khuyến nghị của Google (thường là >30s)
    
    for attempt in range(max_retries):
        try:
            response = chat_session.send_message(prompt)
            return response.text
        except ResourceExhausted:
            # Nếu gặp lỗi 429 (hết quota)
            time_left = wait_time
            warning_placeholder = st.empty()
            while time_left > 0:
                warning_placeholder.warning(f"⚠️ Hệ thống đang quá tải. Đang tự động thử lại sau {time_left} giây...")
                time.sleep(1)
                time_left -= 1
            warning_placeholder.empty() # Xóa cảnh báo sau khi chờ xong
            # Tiếp tục vòng lặp để thử lại
        except Exception as e:
            return f"❌ Có lỗi không xác định: {e}"
            
    return "❌ Hệ thống hiện đang quá tải (Vượt quá giới hạn miễn phí). Thầy/Cô vui lòng đợi khoảng 1-2 phút rồi thử lại nhé!"

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

# --- 6. KHU VỰC NHẬP LIỆU ---
st.divider()
col_mic, col_info = st.columns([1, 4])

with col_mic:
    voice_text = speech_to_text(
        language='vi',
        start_prompt="🎙️ Nói",
        stop_prompt="⏹️ Gửi",
        just_once=True,
        key='STT',
        use_container_width=True
    )

with col_info:
    if voice_text:
        st.success(f"Đã nghe: '{voice_text}'")
    else:
        st.info("Bấm nút bên trái để nói, hoặc gõ tin nhắn bên dưới.")

# Logic xác định nội dung chat
prompt = None
if voice_text:
    prompt = voice_text
else:
    chat_input = st.chat_input("Em cần thầy giúp gì hôm nay?")
    if chat_input:
        prompt = chat_input

# --- 7. XỬ LÝ TRẢ LỜI ---
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Xử lý hội thoại
    history_for_model = [
        {"role": m["role"], "parts": [m["content"]]} 
        for m in st.session_state.messages 
        if m["role"] in ["user", "model"]
    ]
    
    # Chỉ lấy tối đa 10 tin nhắn gần nhất để tiết kiệm token và tránh lỗi
    if len(history_for_model) > 10:
        history_for_model = history_for_model[-10:]

    chat_session = model.start_chat(history=history_for_model[:-1])
    
    with st.chat_message("assistant"):
        with st.spinner("Thầy Văn Sĩ Số đang suy nghĩ..."):
            # GỌI HÀM AN TOÀN ĐÃ VIẾT Ở TRÊN
            response_text = send_message_safe(chat_session, prompt)
            st.markdown(response_text)
            
    st.session_state.messages.append({"role": "model", "content": response_text})
    
    # Rerun để reset trạng thái mic
    if voice_text: 
        st.rerun()
