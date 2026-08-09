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

# --- 3. إدارة الجلسة وقاعدة البيانات البسيطة ---
if "visitor_count" not in st.session_state:
    st.session_state.visitor_count = 125
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

# --- 4. دالة الاستدعاء الذكية لمعالجة خطأ 404 وتجربة النماذج المتاحة تلقائياً ---
def generate_with_fallback(client, contents_payload):
    candidate_models = [
        'gemini-2.5-flash',
        'gemini-2.0-flash',
        'gemini-1.5-flash',
        'gemini-1.5-pro'
    ]
    last_error = None
    
    # تجربة أسماء النماذج الأكثر انتشاراً أولاً
    for m in candidate_models:
        try:
            return client.models.generate_content(model=m, contents=contents_payload)
        except Exception as e:
            last_error = e
            if "404" in str(e) or "NOT_FOUND" in str(e):
                continue
            else:
                raise e
                
    # إذا لم تنجح الأسماء الثابتة، نبحث ديناميكياً داخل قائمة النماذج المتاحة لمفتاحك
    try:
        models_list = list(client.models.list())
        for m in models_list:
            m_name = getattr(m, 'name', '')
            if 'flash' in m_name or 'pro' in m_name:
                try:
                    return client.models.generate_content(model=m_name, contents=contents_payload)
                except Exception:
                    continue
    except Exception:
        pass
        
    raise last_error

# --- 5. تصميم ألوان حديث وجذاب ---
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
        width: 50px;
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

# --- 6. الهيدر العلوي ---
st.markdown("""
    <div class="top-header">
        <div style="font-size: 24px;">🔔</div>
        <div><img src="https://upload.wikimedia.org/wikipedia/commons/d/d1/Coat_of_arms_of_Morocco.svg" class="header-logo"></div>
    </div>
""", unsafe_allow_html=True)

# --- 7. نظام تسجيل الحسابات ---
if not st.session_state.user_authenticated:
    st.markdown('<h1 class="main-title">📚 منصة ملخص دروس المغرب الذكية 🇲🇦</h1>', unsafe_allow_html=True)
    
    col_acc1, col_acc2, col_acc3 = st.columns([1, 2, 1])
    with col_acc2:
        tab_login, tab_signup = st.tabs(["🔐 تسجيل الدخول", "✨ إنشاء حساب جديد"])
        
        with tab_login:
            st.markdown("<h4 style='text-align: center; color: #38bdf8;'>تسجيل الدخول لحسابك</h4>", unsafe_allow_html=True)
            user_in = st.text_input("اسم المستخدم / البريد الإلكتروني:", key="login_user")
            pass_in = st.text_input("كلمة السر:", type="password", key="login_pass")
            
            if st.button("دخول", type="primary", use_container_width=True):
                user_clean = user_in.strip().lower()
                if user_clean in st.session_state.users_db:
                    if st.session_state.users_db[user_clean]["pass"] == pass_in:
                        st.session_state.user_authenticated = True
                        st.session_state.current_user = user_clean
                        st.success("تم تسجيل الدخول بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ كلمة السر غير صحيحة! يرجى التأكد وإعادة المحاولة.")
                else:
                    st.error("❌ هذا الحساب غير موجود! يمكنك إنشاء حساب جديد من التبويب المجاور.")

        with tab_signup:
            st.markdown("<h4 style='text-align: center; color: #38bdf8;'>إنشاء حساب جديد</h4>", unsafe_allow_html=True)
            new_user = st.text_input("اختر اسم المستخدم / البريد:", key="new_user")
            new_pass = st.text_input("اختر كلمة السر:", type="password", key="new_pass")
            confirm_pass = st.text_input("تأكيد كلمة السر:", type="password", key="conf_pass")
            
            if st.button("إنشاء الحساب 🚀", use_container_width=True):
                user_clean = new_user.strip().lower()
                if not user_clean or not new_pass:
                    st.warning("⚠️ يرجى ملء كافة البيانات.")
                elif len(new_pass) < 4:
                    st.warning("⚠️ كلمة السر يجب أن تتكون من 4 رموز على الأقل.")
                elif new_pass != confirm_pass:
                    st.error("❌ كلمتا السر غير متطابقتين.")
                elif user_clean in st.session_state.users_db:
                    st.error("❌ اسم المستخدم هذا مستعمل من قبل، اختر اسماً آخر.")
                else:
                    st.session_state.users_db[user_clean] = {
                        "pass": new_pass,
                        "history": []
                    }
                    st.session_state.user_authenticated = True
                    st.session_state.current_user = user_clean
                    st.success("✅ تم إنشاء الحساب بنجاح ودخولك للمنصة!")
                    st.rerun()

# --- 8. التطبيق الرئيسي ---
else:
    current_u = st.session_state.current_user
    user_data = st.session_state.users_db[current_u]

    with st.sidebar:
        st.write(f"👤 مرحباً: **{current_u}**")
        
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state.user_authenticated = False
            st.session_state.current_user = None
            st.rerun()

        st.markdown("---")
        
        st.header("📜 الملخصات والحلول المحفوظة")
        if user_data["history"]:
            st.success(f"لديك {len(user_data['history'])} عمليات محفوظة.")
            for idx, item in enumerate(reversed(user_data["history"])):
                with st.expander(f"📌 {item['title']} ({item['time']})"):
                    st.markdown(item['content'])
        else:
            st.info("لا توجد عمليات محفوظة بعد.")

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

    st.markdown('<h1 class="main-title">📚 منصة التلخيص وحل الفروض الذكية 🇲🇦</h1>', unsafe_allow_html=True)

    def extract_pdf_text(uploaded_file):
        pdf_reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text

    tab_media, tab_yt = st.tabs(["📄 رفع صور الدرس أو الفروض / ملفات PDF", "🎥 تلخيص فيديوهات اليوتيوب"])

    with tab_media:
        st.subheader("📸 اختيار العملية ورفع المرفقات")

        action_type = st.radio(
            "🎯 ماذا تريد أن تفعل؟ (اختر نوع العملية أولاً):",
            [
                "🚀 تلخيص شامل للمحتوى بالكامل",
                "❓ طرح سؤال محدد وحله من الصور/الملف",
                "📝 حل الفرض/التمرين المرفق بالكامل مع الشرح"
            ]
        )

        user_query = ""
        if action_type == "❓ طرح سؤال محدد وحله من الصور/الملف":
            user_query = st.text_area("✍️ اكتب سؤالك هنا بالتفصيل ليتم إجابته واستخراجه من المرفقات:")

        st.markdown("---")

        col_up1, col_up2 = st.columns(2)
        
        uploaded_images = []
        uploaded_pdf_text = ""

        with col_up1:
            st.markdown("🖼️ **رفع صور (الدرس / الفرض / التمارين):**")
            files_img = st.file_uploader("اختر صور الفرض أو الدرس من هاتفك:", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            if files_img:
                for f in files_img:
                    uploaded_images.append(Image.open(f))
                st.success(f"تم تحميل {len(uploaded_images)} صورة بنجاح!")

        with col_up2:
            st.markdown("📄 **رفع ملف (PDF):**")
            file_pdf = st.file_uploader("اختر ملف PDF للدرس أو الفرض:", type=["pdf"])
            if file_pdf:
                uploaded_pdf_text = extract_pdf_text(file_pdf)
                st.success("تم قراءة واستخراج نص ملف الـ PDF بنجاح!")

        st.markdown("---")

        if st.button("✨ تنفيذ العملية الآن", type="primary", use_container_width=True):
            if not final_api_key:
                st.error("⚠️ يرجى إدخال API Key في القائمة الجانبية أولاً.")
            elif not uploaded_images and not uploaded_pdf_text:
                st.warning("⚠️ يرجى رفع صورة واحدة على الأقل أو ملف PDF للبدء.")
            else:
                with st.spinner("جاري التحليل والحل بكفاءة عالية..."):
                    try:
                        client = genai.Client(api_key=final_api_key)
                        prompt_lang = "الدارجة المغربية المبسطة" if "الدارجة" in language else language

                        if action_type == "🚀 تلخيص شامل للمحتوى بالكامل":
                            prompt = f"قم بقراءة وتلخيص وشرح محتوى الصور والملفات المرفقة بالكامل بطريقة منظمة ومبسطة يفهمها التلميذ بـ ({prompt_lang})."
                        elif action_type == "❓ طرح سؤال محدد وحله من الصور/الملف":
                            prompt = f"بناءً على المرفقات، أجب على السؤال التالي بالتفصيل والشرح المبسط بـ ({prompt_lang}):\n\nالسؤال: {user_query}"
                        else:
                            prompt = f"قم بقراءة وحل جميع أسئلة الفرض/التمرين الموجود في الصور والملفات المرفقة بالكامل خطوة بخطوة مع تقديم شرح ودليل مبسط لكل إجابة بـ ({prompt_lang})."

                        if uploaded_pdf_text:
                            prompt += f"\n\nمحتوى ملف الـ PDF المرفق:\n{uploaded_pdf_text[:10000]}"

                        contents_payload = [prompt]
                        if uploaded_images:
                            contents_payload.extend(uploaded_images)

                        # تنفيذ الطلب باستخدام نظام التجربة الذكي المانع لأخطاء 404
                        response = generate_with_fallback(client, contents_payload)

                        st.success("✅ تم إنجاز العملية بنجاح!")
                        st.markdown(response.text)

                        current_time = datetime.now().strftime("%H:%M - %Y/%m/%d")
                        user_data["history"].append({
                            "title": action_type,
                            "time": current_time,
                            "content": response.text
                        })

                    except Exception as e:
                        st.error(f"حدث خطأ أثناء المعالجة: {e}")

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
                            try:
                                transcript_list = YouTubeTranscriptApi.get_transcript(v_id)
                                text = " ".join([i['text'] for i in transcript_list])
                            except Exception:
                                text = None

                            if text:
                                prompt = f"قم بتلخيص هذا الدرس بـ ({prompt_lang}):\n\n{text}"
                            else:
                                prompt = f"أنا أعطيك رابط درس يوتيوب: {video_url}\nقم بتلخيص وشرح هذا الدرس بـ ({prompt_lang})."

                            response = generate_with_fallback(client, prompt)

                            st.success("✅ تم تلخيص الفيديو بنجاح!")
                            st.markdown(response.text)

                            current_time = datetime.now().strftime("%H:%M - %Y/%m/%d")
                            user_data["history"].append({
                                "title": f"فيديو يوتيوب ({v_id})",
                                "time": current_time,
                                "content": response.text
                            })
                        except Exception as e:
                            st.error(f"حدث خطأ: {e}")

st.markdown("""
    <div class="footer">
        <div>صنع بكل حب من طرف <b>محمد كويرس</b></div>
        <div style="font-size: 12px; margin-top: 5px;">© 2026 جميع الحقوق محفوظة لملخص دروس المغرب</div>
    </div>
""", unsafe_allow_html=True)
