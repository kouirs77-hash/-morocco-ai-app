import streamlit as st
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
from PIL import Image
import pypdf
import re
import json
from datetime import datetime

# --- 🗝️ كلمة السر للمالك ---
ADMIN_PASSWORD = "mohamed_kouirs_2026"

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="منصة ملخص الدروس المغربية 🇲🇦",
    page_icon="📚",
    layout="wide"
)

# --- 2. إدارة الجلسات وقاعدة البيانات ---
if "visitor_count" not in st.session_state:
    st.session_state.visitor_count = 150
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "mohamed": {"pass": "123456", "history": []}
    }

st.session_state.visitor_count += 1

# --- 3. بنية البرمجة الكائنية OOP لمعالجة الخدمات وتفادي الأخطاء ---
class GeminiServiceManager:
    """كلاس مخصص لإدارة طلبات النموذج وتفادي الأخطاء تلقائياً"""
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.candidate_models = [
            'gemini-2.0-flash',
            'gemini-1.5-flash'
        ]

    def generate_safe_content(self, contents_payload):
        last_error = None
        for model_name in self.candidate_models:
            try:
                return self.client.models.generate_content(
                    model=model_name, 
                    contents=contents_payload
                )
            except Exception as e:
                last_error = e
                err_str = str(e)
                # تخطي أخطاء الضغط والنموذج غير الموجود
                if any(err in err_str for err in ["404", "NOT_FOUND", "429", "RESOURCE_EXHAUSTED"]):
                    continue
                else:
                    raise e
        raise last_error

# --- 4. تصميم الألوان والواجهة الحديثة ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 25px;
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 25px;
    }
    .header-logo {
        width: 45px;
        filter: drop-shadow(0px 0px 8px rgba(255, 215, 0, 0.5));
    }
    .main-title {
        text-align: center;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 2.2rem;
        margin-bottom: 20px;
    }
    .admin-card {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.2) 0%, rgba(99, 102, 241, 0.2) 100%);
        border: 1px solid #38bdf8;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .stButton>button {
        border-radius: 12px !important;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        box-shadow: 0 4px 14px 0 rgba(168, 85, 247, 0.39) !important;
        transition: all 0.3s ease !important;
    }
    .footer {
        text-align: center;
        padding: 25px 0;
        margin-top: 50px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        color: #94a3b8;
    }
    </style>
""", unsafe_allow_html=True)

# --- 5. الهيدر ---
st.markdown("""
    <div class="top-header">
        <div style="font-size: 24px;">🔔</div>
        <div><img src="https://upload.wikimedia.org/wikipedia/commons/d/d1/Coat_of_arms_of_Morocco.svg" class="header-logo"></div>
    </div>
""", unsafe_allow_html=True)

# --- 6. نظام الدخول والحسابات ---
if not st.session_state.user_authenticated:
    st.markdown('<h1 class="main-title">📚 منصة ملخص دروس المغرب الذكية 🇲🇦</h1>', unsafe_allow_html=True)
    
    _, col_acc, _ = st.columns([1, 2, 1])
    with col_acc:
        tab_login, tab_signup = st.tabs(["🔐 تسجيل الدخول", "✨ إنشاء حساب جديد"])
        
        with tab_login:
            st.markdown("<h4 style='text-align: center; color: #38bdf8;'>تسجيل الدخول</h4>", unsafe_allow_html=True)
            user_in = st.text_input("اسم المستخدم:", key="login_user")
            pass_in = st.text_input("كلمة السر:", type="password", key="login_pass")
            
            if st.button("دخول 🚀", type="primary", use_container_width=True):
                user_clean = user_in.strip().lower()
                if user_clean in st.session_state.users_db and st.session_state.users_db[user_clean]["pass"] == pass_in:
                    st.session_state.user_authenticated = True
                    st.session_state.current_user = user_clean
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ بيانات الدخول غير صحيحة!")

        with tab_signup:
            st.markdown("<h4 style='text-align: center; color: #38bdf8;'>إنشاء حساب جديد</h4>", unsafe_allow_html=True)
            new_user = st.text_input("اسم المستخدم الجديد:", key="new_user")
            new_pass = st.text_input("كلمة السر:", type="password", key="new_pass")
            confirm_pass = st.text_input("تأكيد كلمة السر:", type="password", key="conf_pass")
            
            if st.button("إنشاء الحساب ✨", use_container_width=True):
                user_clean = new_user.strip().lower()
                if not user_clean or not new_pass:
                    st.warning("⚠️ يرجى إدخال كافة البيانات.")
                elif new_pass != confirm_pass:
                    st.error("❌ كلمتا السر غير متطابقتين.")
                elif user_clean in st.session_state.users_db:
                    st.error("❌ اسم المستخدم مستعمل سابقاً.")
                else:
                    st.session_state.users_db[user_clean] = {"pass": new_pass, "history": []}
                    st.session_state.user_authenticated = True
                    st.session_state.current_user = user_clean
                    st.success("✅ تم إنشاء الحساب بنجاح!")
                    st.rerun()

# --- 7. التطبيق الرئيسي ---
else:
    current_u = st.session_state.current_user
    user_data = st.session_state.users_db[current_u]

    api_key_secret = st.secrets.get("GEMINI_API_KEY", "")

    with st.sidebar:
        st.write(f"👤 مرحباً بك: **{current_u}**")
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state.user_authenticated = False
            st.session_state.current_user = None
            st.rerun()

        st.markdown("---")
        st.header("📜 السجل المحفوظ")
        if user_data["history"]:
            for item in reversed(user_data["history"]):
                with st.expander(f"📌 {item['title']} ({item['time']})"):
                    st.markdown(item['content'])
        else:
            st.info("لا توجد عمليات محفوظة.")

        st.markdown("---")
        st.header("⚙️ الإعدادات والمدير")
        admin_input = st.text_input("🔑 كلمة سر الأدمن:", type="password")
        st.session_state.is_admin = (admin_input == ADMIN_PASSWORD)

        input_key = st.text_input("Gemini API Key الخاص بك:", value=api_key_secret, type="password")
        final_api_key = input_key if input_key else api_key_secret

        language = st.selectbox("🎯 لغة الشرح:", ["الدارجة المغربية 🇲🇦", "العربية الفصحى 🇲🇦", "الفرنسية 🇫🇷", "الإنجليزية 🇬🇧"])

    if st.session_state.is_admin:
        st.markdown("""
        <div class="admin-card">
            <h3 style="margin:0; color:#38bdf8;">👑 لوحة مالك المنصة: محمد كويرس</h3>
            <p style="margin:5px 0 0 0; color:#cbd5e1;">متابعة الأداء وإحصائيات الاستخدام المباشرة.</p>
        </div>
        """, unsafe_allow_html=True)
        col_a1, col_a2, col_a3 = st.columns(3)
        col_a1.metric("👥 عدد الزيارات", f"{st.session_state.visitor_count}")
        col_a2.metric("💰 الأرباح التقديرية", f"${round(st.session_state.visitor_count * 0.01, 2)} USD")
        col_a3.metric("🟢 حالة السيرفر", "متصل ومستقر")
        st.markdown("---")

    st.markdown('<h1 class="main-title">📚 منصة التلخيص وحل التمارين الذكية 🇲🇦</h1>', unsafe_allow_html=True)

    def extract_pdf_text(uploaded_file):
        try:
            pdf_reader = pypdf.PdfReader(uploaded_file)
            return "".join([page.extract_text() or "" for page in pdf_reader.pages])
        except Exception:
            return ""

    tab_media, tab_quiz, tab_yt = st.tabs(["📄 رفع الدرس / التمارين", "🧩 اختبر فهمك (Quiz)", "🎥 تلخيص يوتيوب"])

    with tab_media:
        st.subheader("📸 رفع الملفات والصور")
        action_type = st.radio(
            "🎯 ماذا تريد أن تفعل؟",
            ["🚀 تلخيص شامل للمحتوى", "❓ طرح سؤال محدد وحله", "📝 حل الفرض/التمرين بالكامل مع الشرح"]
        )

        user_query = ""
        if action_type == "❓ طرح سؤال محدد وحله":
            user_query = st.text_area("✍️ اكتب سؤالك بالتفصيل هنا:")

        col_u1, col_u2 = st.columns(2)
        uploaded_images, uploaded_pdf_text = [], ""

        with col_u1:
            files_img = st.file_uploader("اختر صور الدرس/الفرض:", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            if files_img:
                uploaded_images = [Image.open(f) for f in files_img]
                st.success(f"تم تحميل {len(uploaded_images)} صورة!")

        with col_u2:
            file_pdf = st.file_uploader("اختر ملف PDF:", type=["pdf"])
            if file_pdf:
                uploaded_pdf_text = extract_pdf_text(file_pdf)
                st.success("تم استخراج النص من PDF بنجاح!")

        if st.button("✨ بدء المعالجة والتحليل", type="primary", use_container_width=True):
            if not final_api_key:
                st.error("⚠️ يرجى إضافة API Key في الشريط الجانبي.")
            elif not uploaded_images and not uploaded_pdf_text:
                st.warning("⚠️ يرجى رفع صور أو ملف PDF أولاً.")
            else:
                with st.spinner("جاري المعالجة بذكاء وسرعة..."):
                    try:
                        gemini_mgr = GeminiServiceManager(final_api_key)
                        prompt_lang = "الدارجة المغربية المبسطة" if "الدارجة" in language else language

                        if action_type == "🚀 تلخيص شامل للمحتوى":
                            prompt = f"قم بتلخيص وشرح محتوى الدرس بأسلوب منظم وسهل الفهم بـ ({prompt_lang})."
                        elif action_type == "❓ طرح سؤال محدد وحله":
                            prompt = f"أجب على السؤال التالي بناءً على المرفقات بـ ({prompt_lang}):\n{user_query}"
                        else:
                            prompt = f"قم بحل جميع تمارين الفرض المرفق خطوة بخطوة مع الشرح المبسط بـ ({prompt_lang})."

                        if uploaded_pdf_text:
                            prompt += f"\n\nنص PDF المرفق:\n{uploaded_pdf_text[:10000]}"

                        payload = [prompt] + uploaded_images
                        response = gemini_mgr.generate_safe_content(payload)

                        st.success("✅ تم التلخيص والحل بنجاح!")
                        st.markdown(response.text)

                        # حفظ في السجل
                        user_data["history"].append({
                            "title": action_type,
                            "time": datetime.now().strftime("%H:%M - %Y/%m/%d"),
                            "content": response.text
                        })
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء المعالجة: {e}")

    # --- تبويب جديد: مولد الاختبارات التفاعلية ---
    with tab_quiz:
        st.subheader("🧩 إنشاء اختبار تفاعلي لتقييم فهمك للدرس")
        st.write("قم بوضع نص الدرس أو الاعتماد على آخر ملف قمت برفعه لتوليد أسئلة اختيار من متعدد!")
        
        quiz_text_input = st.text_area("أدخل نص الدرس هنا (أو اتركه فارغاً لاستعمال نص PDF المرفق):")

        if st.button("🚀 توليد أسئلة الاختبار الآن", type="primary", use_container_width=True):
            target_text = quiz_text_input if quiz_text_input else uploaded_pdf_text
            if not final_api_key:
                st.error("⚠️ يرجى إدخال API Key أولاً.")
            elif not target_text:
                st.warning("⚠️ يرجى إدخال نص الدرس أو رفع ملف PDF أولاً لتوليد الأسئلة.")
            else:
                with st.spinner("جاري إعداد أسئلة الاختبار التفاعلي..."):
                    try:
                        gemini_mgr = GeminiServiceManager(final_api_key)
                        quiz_prompt = f"""
                        قم بتوليد 3 أسئلة اختيار من متعدد (MCQ) بناءً على هذا النص:
                        {target_text[:4000]}
                        
                        اكتب الرد بصيغة قائمة بسيطة واضحة تحتوي على:
                        السؤال، 4 خيارات، والإجابة الصحيحة مع الشرح بـ ({language}).
                        """
                        res = gemini_mgr.generate_safe_content([quiz_prompt])
                        st.markdown(res.text)
                    except Exception as e:
                        st.error(f"خطأ في توليد الأسئلة: {e}")

    with tab_yt:
        st.subheader("🎥 تلخيص فيديو يوتيوب")
        video_url = st.text_input("🔗 ضع رابط يوتيوب هنا:")
        
        if st.button("🚀 تلخيص الفيديو", type="primary", use_container_width=True):
            if not final_api_key or not video_url:
                st.warning("⚠️ يرجى التأكد من إدخال API Key ورابط الفيديو.")
            else:
                v_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', video_url)
                if v_match:
                    v_id = v_match.group(1)
                    gemini_mgr = GeminiServiceManager(final_api_key)
                    prompt_lang = "الدارجة المغربية المبسطة" if "الدارجة" in language else language

                    with st.spinner("جاري تحليل الفيديو..."):
                        try:
                            try:
                                t_list = YouTubeTranscriptApi.get_transcript(v_id)
                                text = " ".join([i['text'] for i in t_list])
                            except Exception:
                                text = None

                            prompt = f"ملخص الدرس من هذا النص بـ ({prompt_lang}):\n{text}" if text else f"قم بتلخيص وشرح محتوى الفيديو المتاح في الرابط: {video_url} بـ ({prompt_lang})."
                            res = gemini_mgr.generate_safe_content([prompt])

                            st.success("✅ تم تلخيص الفيديو!")
                            st.markdown(res.text)
                        except Exception as e:
                            st.error(f"حدث خطأ: {e}")

st.markdown("""
    <div class="footer">
        <div>صنع بكل حب من طرف <b>محمد كويرس</b></div>
        <div style="font-size: 12px; margin-top: 5px;">© 2026 جميع الحقوق محفوظة لـ منصة ملخص دروس المغرب</div>
    </div>
""", unsafe_allow_html=True)
