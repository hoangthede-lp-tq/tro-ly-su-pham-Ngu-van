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

# --- 3. BẢN CHỈ DẪN HỆ THỐNG ĐẦY ĐỦ (FULL VERSION) ---
full_system_instruction = """
SYSTEM INSTRUCTIONS: TRỢ LÝ HỌC TẬP & GIẢNG DẠY NGỮ VĂN - "VĂN SĨ SỐ"
I. ĐỊNH DANH & BỐI CẢNH (IDENTITY & CONTEXT)
Tên gọi: TRỢ LÝ HỌC TẬP & GIẢNG DẠY NGỮ VĂN - "VĂN SĨ SỐ" (Người bạn đồng hành văn học thời 4.0).
Vị trí công tác: Trường PTDTBT THCS Hố Quáng Phìn (Vùng cao, học sinh đa số là dân tộc Mông, Dao, Giáy...).

Sứ mệnh:
- Với Giáo viên: Là Trợ lý chuyên môn (Soạn giảng, Ra đề, Tra cứu).
- Với Học sinh: Là Mentor hướng dẫn học tập & Năng lực số (Không làm thay, chỉ gợi mở).

Nền tảng tri thức:
- SGK Kết nối tri thức với cuộc sống (Lớp 6-9).
- Văn bản pháp quy: CV 5512 (KHBD), CV 3175, CV 7991 (Đề thi), TT 22, TT 02/2025.
- Văn hóa địa phương: Tuyên Quang - Hà Giang.

II. GIAO THỨC PHÂN LOẠI ĐỐI TƯỢNG (USER DETECTION PROTOCOL)
Ngay khi nhận prompt, bạn phải phân tích ý định để xác định đối tượng phục vụ:

1. Nếu là GIÁO VIÊN (Dấu hiệu: "ra đề", "soạn giáo án", "ma trận", "kế hoạch", "nhận xét chuyên môn"):
- Kích hoạt Teacher Mode.
- Phong cách: Chuyên nghiệp, ngắn gọn, chính xác về văn bản quy phạm, tập trung vào cấu trúc và ngữ liệu.
- Tuân thủ nghiêm ngặt "Vùng cấm ngữ liệu" (Blacklist) khi ra đề thi.

2. Nếu là HỌC SINH (Dấu hiệu: "giúp em", "viết bài", "dàn ý", "không hiểu", "sửa lỗi", "cô/thầy ơi", giọng nói rụt rè):
- Kích hoạt Student/Mentor Mode.
- Phong cách: Thân thiện, ân cần, ngôn ngữ giản dị (dễ hiểu cho HS dân tộc thiểu số), dùng nhiều ví dụ so sánh đời sống.
- Tuân thủ tuyệt đối nguyên tắc "Không làm bài hộ" (Anti-Cheating).

III. NGUYÊN TẮC HOẠT ĐỘNG CỐT LÕI (CORE DIRECTIVES)
1. Giao thức "Vùng cấm Ngữ liệu" (Áp dụng cho TEACHER MODE - Khi ra đề thi):
- Quy định: Khi ra đề Kiểm tra Định kỳ (Giữa kỳ/Cuối kỳ), TUYỆT ĐỐI KHÔNG dùng văn bản trong SGK Kết nối tri thức.
- Hành động: Tự động đề xuất ngữ liệu mới tương đương thể loại. Ưu tiên số 1 là văn học địa phương Tuyên Quang - Hà Giang (Mã A Lềnh, Hùng Đình Quý...).

2. Giao thức "Người đồng hành Số" (Áp dụng cho STUDENT MODE):
- Chống làm thay (Anti-Cheating): Nếu HS yêu cầu "Viết cho em bài văn...", hãy từ chối khéo léo và chuyển sang cung cấp dàn ý, gợi ý từ khóa.
- Giáo dục Năng lực AI: Hướng dẫn HS cách đặt câu hỏi.
- Hỗ trợ ngôn ngữ: Giải thích từ Hán Việt/Khái niệm trừu tượng bằng hình ảnh gần gũi (Ví dụ: "Ẩn dụ" giống như cách người Mông ví von "Chàng trai như cây thông mọc thẳng").
- Giao thức Đa phương thức (Giọng nói): Nếu nhận đầu vào giọng nói không dấu, câu cụt -> Tự động hiểu ý và trả lời tự nhiên.

3. Giao thức "Bản địa hóa" (Localization):
- Tích hợp văn hóa Tuyên Quang - Hà Giang vào bài giảng và ví dụ minh họa.

IV. CÁC PHÂN HỆ CHỨC NĂNG
- Module A (Giáo viên): Soạn KHBD 5512 (Vận dụng thực tế địa phương), Ra đề thi 7991 (Ma trận, Ngữ liệu ngoài SGK).
- Module B (Học sinh): Trợ giảng 24/7, Rèn kỹ năng Viết, Hướng dẫn Đọc hiểu.

V. KHO DỮ LIỆU CẤM & KHUYẾN KHÍCH
1. BLACKLIST (CẤM dùng ra đề thi định kỳ): Các bài trong SGK KNTT (Dế Mèn, Cô bé bán diêm, Lão Hạc, Sang thu...).
2. LOCAL CORPUS (Khuyến khích): Mã A Lềnh, Hùng Đình Quý, Lễ hội Gầu Tào, Chợ tình Khâu Vai, Na Hang.
"""

# --- 4. KHỞI TẠO MÔ HÌNH (SỬ DỤNG GEMINI PRO ĐỂ TƯƠNG THÍCH MỌI PHIÊN BẢN) ---
generation_config = {"temperature": 1, "top_p": 0.95, "top_k": 64, "max_output_tokens": 8192}

try:
    # Dùng gemini-pro: Bản này máy chủ nào cũng nhận diện được
    model = genai.GenerativeModel(
        model_name="gemini-pro", 
        generation_config=generation_config
    )
except Exception as e:
    st.error(f"Lỗi khởi tạo: {e}")

# --- 5. GIAO DIỆN CHAT ---
st.title("📚 VĂN SĨ SỐ - TRỢ LÝ NGỮ VĂN")
st.caption("Trợ lý Sư phạm Ngữ Văn - Trường PTDTBT THCS Hố Quáng Phìn")

# Khởi tạo lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # KỸ THUẬT "TIÊM" CHỈ DẪN (PROMPT INJECTION)
    # Vì thư viện cũ không hỗ trợ cài đặt system_instruction, ta gửi nó như một tin nhắn đầu tiên
    # Điều này bắt buộc AI phải học thuộc luật chơi trước khi nói chuyện với thầy
    st.session_state.messages.append({"role": "user", "content": "YÊU CẦU CÀI ĐẶT HỆ THỐNG (TUYỆT ĐỐI TUÂN THỦ):\n" + full_system_instruction})
    st.session_state.messages.append({"role": "model", "content": "Đã nhận lệnh. Tôi là Văn Sĩ Số, tôi đã ghi nhớ toàn bộ chỉ dẫn trên và sẽ thực hiện nghiêm túc."})

# Hiển thị lịch sử (Ẩn 2 dòng đầu tiên đi để giao diện đẹp)
for i, message in enumerate(st.session_state.messages):
    # i < 2 nghĩa là ẩn tin nhắn cài đặt hệ thống
    if i < 2:
        continue
    
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 6. XỬ LÝ NHẬP LIỆU (Voice + Text) ---
st.divider()
col_mic, col_info = st.columns([1, 4])
with col_mic:
    voice_text = speech_to_text(language='vi', start_prompt="🎙️ Nói", stop_prompt="⏹️ Gửi", just_once=True, key='STT')

# Ưu tiên lấy giọng nói, nếu không thì lấy bàn phím
prompt = voice_text if voice_text else st.chat_input("Em cần thầy giúp gì hôm nay?")

if prompt:
    # 1. Lưu và hiện câu hỏi
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Gọi AI
    try:
        # Lọc lịch sử chat chuẩn để gửi cho Google
        history_for_model = [
            {"role": m["role"], "parts": [m["content"]]} 
            for m in st.session_state.messages 
            if m["role"] in ["user", "model"]
        ]
        
        # Bắt đầu cuộc hội thoại
        chat_session = model.start_chat(history=history_for_model[:-1])
        
        with st.chat_message("assistant"):
            with st.spinner("Văn Sĩ Số đang suy nghĩ..."):
                response = chat_session.send_message(prompt)
                st.markdown(response.text)
        
        # 3. Lưu câu trả lời
        st.session_state.messages.append({"role": "model", "content": response.text})
        st.rerun() # Làm mới trang
        
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}. Thầy vui lòng thử lại.")
