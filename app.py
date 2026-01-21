import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG (Đã fix lỗi dấu ngoặc) ---
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

# --- 3. CẤU HÌNH MÔ HÌNH (Dùng bản 1.5 Flash để KHÔNG bị lỗi 429 Quota) ---
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
}

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
   - Dấu hiệu: "giúp em", "viết bài", "thầy ơi".
   - Hành động: Thân thiện, dễ hiểu, dùng ví dụ đời sống. Tuân thủ "Không làm bài hộ".

III. NGUYÊN TẮC HOẠT ĐỘNG CỐT LÕI
1. Vùng cấm Ngữ liệu (Teacher Mode): Ra đề thi định kỳ KHÔNG dùng văn bản SGK. Ưu tiên văn học địa phương (Mã A Lềnh, Hùng Đình Quý...).
2. Người đồng hành Số (Student Mode): Không viết văn mẫu trọn vẹn. Chỉ gợi ý dàn ý, từ khóa.

IV. CÁC PHÂN HỆ CHỨC NĂNG
- Giáo viên: Soạn KHBD 5512 (Vận dụng thực tế địa phương), Ra đề thi ma trận 7991.
- Học sinh: Trợ giảng 24/7, Rèn kỹ năng Viết, Hướng dẫn Đọc hiểu.

V. KHO DỮ LIỆU
- Blacklist: Các bài trong SGK KNTT (Dế Mèn, Cô bé bán diêm...).
- Local Corpus: Văn học Tuyên Quang - Hà Giang (Lễ hội Gầu Tào, Chợ tình Khâu Vai, Na Hang...).
"""

# Sử dụng gemini-1.5-flash (Ổn định, miễn phí cao)
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        generation_config=generation_config,
        system_instruction=system_instruction,
    )
except Exception as e:
    st.error(f"Lỗi khởi tạo mô hình: {e}")

# --- 4. GIAO DIỆN CHAT ---
st.title("📚 VĂN SĨ SỐ - TRỢ LÝ NGỮ VĂN")
st.caption("Trợ lý Sư phạm Ngữ Văn - Trường PTDTBT THCS Hố Quáng Phìn")

# Khởi tạo lịch sử
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 5. XỬ LÝ NHẬP LIỆU (Chỉ Text - Ổn định) ---
if prompt := st.chat_input("Em cần thầy giúp gì hôm nay?"):
    # Lưu câu hỏi
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gọi AI trả lời
    try:
        history_for_model = [
            {"role": m["role"], "parts": [m["content"]]} 
            for m in st.session_state.messages 
            if m["role"] in ["user", "model"]
        ]
        
        chat_session = model.start_chat(history=history_for_model[:-1])
        
        with st.chat_message("assistant"):
            with st.spinner("Thầy Văn Sĩ Số đang suy nghĩ..."):
                response = chat_session.send_message(prompt)
                st.markdown(response.text)
            
        st.session_state.messages.append({"role": "model", "content": response.text})
        
    except Exception as e:
        st.error(f"Có lỗi xảy ra: {e}")
