import streamlit as st
import google.generativeai as genai
import tempfile
import os

st.set_page_config(page_title="المساعد الدراسي الذكي", page_icon="🎓", layout="centered")

st.title("🎓 المساعد الدراسي المغربي")
st.caption("رفع الفيديوهات + تلخيص + حل التمارين بالذكاء الاصطناعي")

api_key = st.text_input("🔑 أدخل مفتاح Gemini API:", type="password")

if api_key:
    genai.configure(api_key=api_key)

subjects = [
    "الرياضيات", "الفيزياء والكيمياء", "علوم الحياة والأرض",
    "اللغة العربية", "اللغة الفرنسية", "اللغة الإنجليزية",
    "الفلسفة", "التاريخ والجغرافيا", "التربية الإسلامية"
]
selected_subject = st.selectbox("📚 اختر المادة الدراسية:", subjects)

uploaded_files = st.file_uploader(
    "🎥 اختر فيديوهات الدرس من هاتفك:", 
    type=["mp4", "mov", "mkv"], 
    accept_multiple_files=True
)

if "videos_ref" not in st.session_state:
    st.session_state.videos_ref = []

if uploaded_files and api_key:
    if st.button("⚡ تحليل الفيديوهات"):
        with st.spinner("جاري رفع وتحليل الفيديو... قد يستغرق ذلك لحظات"):
            st.session_state.videos_ref = []
            for file in uploaded_files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                    tmp.write(file.read())
                    tmp_path = tmp.name
                
                video_data = genai.upload_file(path=tmp_path)
                st.session_state.videos_ref.append(video_data)
                os.remove(tmp_path)
                
            st.success("✅ تم تحليل الفيديوهات بنجاح!")

if st.session_state.videos_ref:
    st.markdown("---")
    action = st.radio("ماذا تريد أن تفعل؟", ["📝 تلخيص الدرس", "❓ حل تمارين وأسئلة"])
    
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    if action == "📝 تلخيص الدرس":
        if st.button("إنشاء التلخيص"):
            with st.spinner("جاري كتابة الملخص..."):
                prompt = f"قم بتلخيص جميع الدروس الموجودة في هذه الفيديوهات لمادة {selected_subject} بأسلوب محدد ومنظم باللغة العربية."
                res = model.generate_content([prompt, *st.session_state.videos_ref])
                st.markdown("### 📄 الملخص:")
                st.write(res.text)

    elif action == "❓ حل تمارين وأسئلة":
        user_q = st.text_area("أكتب التمرين هنا (أو صورته ونصه):")
        if st.button("إرسال الحل"):
            if user_q:
                with st.spinner("جاري استخراج الحل من الفيديوهات..."):
                    prompt = f"أنت أستاذ مادة {selected_subject}. أجب على التمرين التالي اعتماداً فقط على الشرح الموجود بالفيديوهات المرفقة:\n{user_q}"
                    res = model.generate_content([prompt, *st.session_state.videos_ref])
                    st.markdown("### 🎯 الحل:")
                    st.write(res.text)
