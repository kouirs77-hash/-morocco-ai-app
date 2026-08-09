import streamlit as st
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
from PIL import Image
import pypdf
import re
from datetime import datetime

# --- 🗝️ كلمة السر للأدمن ---
ADMIN_PASSWORD = "mohamed_kouirs_2026"

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="منصة ملخص الدروس المغربية 🇲🇦",
    page_icon="📚",
    layout="wide"
)

# --- 2. الإعدادات السريّة للمفتاح تلقائياً ---
api_key_secret = st.secrets.get("GEMINI_API_KEY", "")

# --- 3. إدارة الجلسة والبيانات ---
if "visitor_count" not in st.session_state:
    st.session_state.visitor_count = 125
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "user_history" not in st.session_state:
    st.session_state.user_history = []
if "gallery_permission" not in st.session_state:
    st.session_state.gallery_permission = False

st.session_state.visitor_count += 1

# --- 4. تصميم ألوان حديث وجذاب (Modern Dynamic UI) ---
st.markdown("""
    <style>
    /* خلفية متناسقة وألوان جذابة */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* الهيدر العلوي */
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
        width: 50px;
        filter: drop-shadow(0px 0px 8px rgba(255, 215, 0, 0.5));
    }
    
    /* العناوين والبطاقات */
    .main-title {
        text-align: center;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 2.2rem;
        margin-bottom: 20px;
    }
    
    .custom-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    
    .admin-dashboard {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.2) 0%, rgba(99, 102, 241, 0.2) 100%);
        border: 1px solid #38bdf8;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* الأزرار المصممة بألوان جذابة */
    .stButton>button {
        border-radius: 12px !important;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        box-shadow: 0 4px 14px 0 rgba(168, 85, 247, 0.39) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(168, 85, 247, 0.6) !important;
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

# --- 5. الهيدر العلوي ---
st.markdown("""
    <div class="top-header">
        <div style="font-size: 24px;">🔔</div>
        <div><img src="https://upload.wikimedia.org/wikipedia/commons/d/d1/Coat_of_arms_of_Morocco.svg" class="header-logo"></div>
    </div>
""", unsafe_allow_html=True)

# --- 6. شاشة تسجيل الدخول ---
if not st.session_state.user_authenticated:
    st.markdown('<h1 class="main-title">📚 منصة ملخص دروس المغرب الذكية 🇲🇦</h1>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="custom-card" style="max-width: 480px; margin: 0 auto; text-align: center;">
            <h3 style="color: #38bdf8;">🔐 تسجيل الدخول للحساب</h3>
            <p style="color: #94a3b8; font-size: 14px;">أدخل معلومات حسابك للوصول للملخصات وحفظ الملفات تلقائياً.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_acc1, col_acc2, col_acc3 = st.columns([1, 2, 1])
    with col_acc2:
        tab_google, tab_apple = st.tabs(["🌐 حساب Google", "🍏 حساب iCloud / Apple"])
        
        with tab_google:
            username = st.text_input("اسم الحساب / البريد الإلكتروني:", key="g_user")
            password = st.text_input("كلمة السر:", type="password", key="g_pass")
            if st.button("دخول للحساب", type="primary", use_container_width=True):
                if username and len(password) >= 4:
                    st.session_state.user_authenticated = True
                    st.session_state.user_info = {"type": "Google", "username": username}
                    st.rerun()
                else:
                    st.error("يرجى إدخال اسم الحساب وكلمة سر مكونة من 4 أحرف/أرقام على الأقل.")
                    
        with tab_apple:
            apple_id = st.text_input("اسم حساب Apple ID / iCloud:", key="a_user")
            apple_pass = st.text_input("كلمة السر:", type="password", key="a_pass")
            if st.button("دخول بـ Apple ID", use_container_width=True):
                if apple_id and len(apple_pass) >= 4:
                    st.session_state.user_authenticated = True
                    st.session_state.user_info = {"type": "iCloud", "username": apple_id}
                    st.rerun()
                else:
                    st.error("يرجى إدخال البيانات بالشكل الصحيح.")

# --- 7. التطبيق الرئيسي بعد الدخول ---
else:
    # --- القائمة الجانبية (3 أشرطة / Sidebar) ---
    with st.sidebar:
        st.write(f"👤 مرحباً: **{st.session_state.user_info['username']}**")
        st.caption(f"نوع الحساب: {st.session_state.user_info['type']}")
        
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state.user_authenticated = False
            st.session_state.user_info = None
            st.rerun()

        st.markdown("---")
        
        # --- 📁 أرشيف الملخصات المحفوظة ---
        st.header("📜 الملخصات المحفوظة")
        if st.session_state.user_history:
            st.success(f"لديك {len(st.session_state.user_history)} ملخصات محفوظة.")
            for idx, item in enumerate(reversed(st.session_state.user_history)):
                with st.expander(f"📌 {item['title']} ({item['time']})"):
                    st.markdown(item['content'])
        else:
            st.info("لا توجد ملخصات محفوظة بعد. كل عمل تقوم به سيحفظ هنا لمنع ضياعه!")

        st.markdown("---")
        st.header("⚙️ إعدادات المفتاح والمدير")
        
        admin_input = st.text_input("🔑 دخول الأدمن:", type="password")
        if admin_input == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.success("👑 وضع الأدمن مفعل (محمد كويرس)")
        else:
            st.session_state.is_admin = False

        st.markdown("---")
        
        input_key = st.text_input("Gemini API Key:", value=api_key_secret, type="password")
        final_api_key = input_key if input_key else api_key_secret
        
        language = st.selectbox("🎯 لغة الشرح والرد:", ["الدارجة المغربية 🇲🇦", "العربية الفصحى 🇲🇦", "الفرنسية 🇫🇷", "الإنجليزية 🇬🇧"])

    # --- لوحة الأدمن ---
    if st.session_state.is_admin:
        st.markdown("""
        <div class="admin-dashboard">
            <h3 style="margin:0; color:#38bdf8;">👑 لوحة تحكم المالك: محمد كويرس</h3>
            <p style="margin:5px 0 15px 0; font-size:14px; color:#cbd5e1;">✨ التصفح المباشر وتتبع الأرباح وإحصائيات الزوار.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_adm1, col_adm2, col_adm3 = st.columns(3)
        with col_adm1:
            st.metric(label="👥 الزوار", value=f"{st.session_state.visitor_count}")
        with col_adm2:
            estimated_earnings = round(st.session_state.visitor_count * 0.008, 2)
            st.metric(label="💰 الأرباح المتوقعة", value=f"${estimated_earnings} USD")
        with col_adm3:
            st.metric(label="🏦 حالة الحساب البنكي", value="جاهز 🟢")
        st.markdown("---")

    # --- الواجهة الرئيسية ---
    st.markdown('<h1 class="main-title">📚 منصة التلخيص وطرح الأسئلة الذكية 🇲🇦</h1>', unsafe_allow_html=True)

    # دالة استخراج النص من PDF
    def extract_pdf_text(uploaded_file):
        pdf_reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text

    # تقسيم الصفحة إلى تبويبات احترافية
    tab_media, tab_yt = st.tabs(["📄 رفع صور / ملفات PDF / صور المعرض", "🎥 تلخيص فيديوهات اليوتيوب"])

    # === التبويب الأول: رفع الصور والملفات والأسئلة ===
    with tab_media:
        st.subheader("📸 رفع الدرس (صور أو PDF) وطرح الأسئلة")
        
        # طلب الإذن للوصول لصور الهاتف
        st.markdown("##### 📱 إذن المعرض والكتالوج:")
        col_perm1, col_perm2 = st.columns([3, 1])
        with col_perm1:
            st.caption("يتطلب اختيار الصور المباشرة منح الإذن للوصول لمكتبة الصور داخل هاتفك.")
        with col_perm2:
            if st.button("🔓 منح إذن الوصول للصور"):
                st.session_state.gallery_permission = True
                st.success("تم إعطاء الإذن بنجاح! يمكنك الآن اختيار الصور.")

        st.markdown("---")

        col_up1, col_up2 = st.columns(2)
        
        uploaded_images = []
        uploaded_pdf_text = ""

        with col_up1:
            st.markdown("🖼️ **رفع صور الدرس / الفرض:**")
            files_img = st.file_uploader("اختر صورة أو مجموعة صور من هاتفك:", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            if files_img:
                for f in files_img:
                    uploaded_images.append(Image.open(f))
                st.success(f"تم تحميل {len(uploaded_images)} صورة بنجاح!")

        with col_up2:
            st.markdown("📄 **رفع ملف الدرس (PDF):**")
            file_pdf = st.file_uploader("اختر ملف PDF للدرس:", type=["pdf"])
            if file_pdf:
                uploaded_pdf_text = extract_pdf_text(file_pdf)
                st.success("تم قراءة واستخراج نص ملف الـ PDF بنجاح!")

        st.markdown("---")

        # خيار العمل: تلخيص أم سؤال؟
        action_type = st.radio("🎯 ماذا تريد أن تفعل بالملفات والصور المرفقة؟", ["🚀 تلخيص شامل للمحتوى بالكامل", "❓ طرح سؤال محدد وحله من الصور/الملف"])

        user_query = ""
        if action_type == "❓ طرح سؤال محدد وحله من الصور/الملف":
            user_query = st.text_area("✍️ اكتب سؤالك هنا بالتفصيل ليتم إجابته واستخراجه من المرفقات:")

        if st.button("✨ تنفيذ العملية الآن", type="primary", use_container_width=True):
            if not final_api_key:
                st.error("⚠️ يرجى إدخال API Key في القائمة الجانبية أولاً.")
            elif not uploaded_images and not uploaded_pdf_text:
                st.warning("⚠️ يرجى رفع صورة واحدة على الأقل أو ملف PDF للبدء.")
            else:
                with st.spinner("جاري التحليل واستخراج الإجابات..."):
                    try:
                        client = genai.Client(api_key=final_api_key)
                        prompt_lang = "الدارجة المغربية المبسطة" if "الدارجة" in language else language

                        if action_type == "🚀 تلخيص شامل للمحتوى بالكامل":
                            prompt = f"قم بقراءة وتلخيص وشرح محتوى الصور والملفات المرفقة بالكامل بطريقة منظمة ومبسطة يفهمها التلميذ بـ ({prompt_lang})."
                        else:
                            prompt = f"بناءً على المرفقات، أجب على السؤال التالي بالتفصيل والشرح المبسط بـ ({prompt_lang}):\n\nالسؤال: {user_query}"

                        if uploaded_pdf_text:
                            prompt += f"\n\nمحتوى ملف الـ PDF المرفق:\n{uploaded_pdf_text[:10000]}"

                        contents_payload = [prompt]
                        if uploaded_images:
                            contents_payload.extend(uploaded_images)

                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=contents_payload
                        )

                        st.success("✅ تم إنجاز العملية بنجاح!")
                        st.markdown(response.text)

                        # حفظ في السجل
                        current_time = datetime.now().strftime("%H:%M - %Y/%m/%d")
                        st.session_state.user_history.append({
                            "title": "تحليل صور / PDF / أسئلة",
                            "time": current_time,
                            "content": response.text
                        })

                    except Exception as e:
                        st.error(f"حدث خطأ أثناء المعالجة: {e}")

    # === التبويب الثاني: اليوتيوب ===
    with tab_yt:
        st.subheader("🎥 تلخيص فيديوهات اليوتيوب")
        video_url = st.text_input("🔗 أدخل رابط فيديو اليوتيوب:", placeholder="https://www.youtube.com/watch?v=...")
        
        if st.button("🚀 تلخيص فيديو اليوتيوب", type="primary", use_container_width=True):
            if not final_api_key:
                st.error("⚠️ يرجى إدخال Gemini API Key في القائمة الجانبية أولاً.")
            elif not video_url:
                st.warning("⚠️ يرجى إدخال رابط الفيديو.")
            else:
                v_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', video_url)
                if v_match:
                    v_id = v_match.group(1)
                    client = genai.Client(api_key=final_api_key)
                    prompt_lang = "الدارجة المغربية المبسطة" if "الدارجة" in language else language

                    with st.spinner("جاري تحليل وفهم الفيديو..."):
                        try:
                            # محاولة جلب النص
                            try:
                                transcript_list = YouTubeTranscriptApi.get_transcript(v_id)
                                text = " ".join([i['text'] for i in transcript_list])
                            except Exception:
                                text = None

                            if text:
                                prompt = f"قم بتلخيص هذا الدرس بـ ({prompt_lang}):\n\n{text}"
                            else:
                                prompt = f"أنا أعطيك رابط درس يوتيوب: {video_url}\nقم بتلخيص وشرح هذا الدرس بـ ({prompt_lang})."

                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=prompt
                            )

                            st.success("✅ تم تلخيص الفيديو بنجاح!")
                            st.markdown(response.text)

                            current_time = datetime.now().strftime("%H:%M - %Y/%m/%d")
                            st.session_state.user_history.append({
                                "title": f"فيديو يوتيوب ({v_id})",
                                "time": current_time,
                                "content": response.text
                            })
                        except Exception as e:
                            st.error(f"حدث خطأ: {e}")

# --- 8. الحقوق والذيل ---
st.markdown("""
    <div class="footer">
        <div>صنع بكل حب من طرف <b>محمد كويرس</b></div>
        <div style="font-size: 12px; margin-top: 5px;">© 2026 جميع الحقوق محفوظة لملخص دروس المغرب</div>
    </div>
""", unsafe_allow_html=True)
