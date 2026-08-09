import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from PIL import Image
import re
from datetime import datetime

# --- 🗝️ كلمة السر للأدمن ---
ADMIN_PASSWORD = "mohamed_kouirs_2026"

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="ملخص دروس المغرب - بالدارجة",
    page_icon="🇲🇦",
    layout="wide"
)

# --- 2. الإعدادات السريّة للمفتاح تلقائياً ---
api_key_secret = st.secrets.get("GEMINI_API_KEY", "")

# --- 3. إدارة الجلسة والبيانات الحافظة ---
if "visitor_count" not in st.session_state:
    st.session_state.visitor_count = 125
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "videos_list" not in st.session_state:
    st.session_state.videos_list = []
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# قاعدة بيانات مؤقتة لحفظ ملخصات الحساب ومنع ضياعها بالخطأ
if "user_history" not in st.session_state:
    st.session_state.user_history = []

st.session_state.visitor_count += 1

# --- 4. تصميم الصفحة CSS ---
st.markdown("""
    <style>
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 20px;
        background-color: #FFFFFF;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 20px;
    }
    .header-logo {
        width: 45px;
    }
    .main-title {
        text-align: center;
        color: #000000;
        font-weight: bold;
        font-size: 1.8rem;
        margin-bottom: 15px;
    }
    .admin-dashboard {
        background-color: #EBF8FF;
        border: 2px solid #3182CE;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .ad-box {
        background-color: #FFFBEB;
        border: 1px dashed #D97706;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
        font-size: 14px;
        color: #92400E;
    }
    .login-container {
        max-width: 450px;
        margin: 20px auto;
        padding: 25px;
        border-radius: 12px;
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .history-card {
        background-color: #F3F4F6;
        border-right: 4px solid #10B981;
        padding: 10px 15px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    .footer {
        width: 100%;
        background-color: #FAFAFA;
        text-align: center;
        padding: 20px 0;
        margin-top: 40px;
        border-top: 1px solid #EEEEEE;
    }
    .footer-title {
        font-size: 22px;
        font-weight: bold;
        color: #000000;
        margin-bottom: 5px;
    }
    .footer-sub {
        font-size: 12px;
        color: #6B7280;
    }
    </style>
""", unsafe_allow_html=True)

# --- 5. الهيدر العلوي ---
st.markdown("""
    <div class="top-header">
        <div style="font-size: 20px;">🔔</div>
        <div><img src="https://upload.wikimedia.org/wikipedia/commons/d/d1/Coat_of_arms_of_Morocco.svg" class="header-logo"></div>
    </div>
""", unsafe_allow_html=True)

# --- 6. شاشة تسجيل الدخول بالتفصيل (اسم الحساب + كلمة السر) ---
if not st.session_state.user_authenticated:
    st.markdown('<h1 class="main-title">📚 مرحبا بك في منصة ملخص دروس المغرب 🇲🇦</h1>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="login-container">
            <h3>🔐 تسجيل الدخول بالحساب</h3>
            <p style="color: #6B7280; font-size: 14px;">أدخل اسم حسابك وكلمة السر لحفظ ملخصاتك تلقائياً.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_acc1, col_acc2, col_acc3 = st.columns([1, 2, 1])
    with col_acc2:
        tab_google, tab_apple = st.tabs(["🌐 حساب Google / عادي", "🍏 حساب iCloud / Apple"])
        
        with tab_google:
            username = st.text_input("اسم الحساب / البريد (Google):", key="g_user")
            password = st.text_input("كلمة السر:", type="password", key="g_pass")
            if st.button("دخول للحساب", type="primary", use_container_width=True):
                if username and len(password) >= 4:
                    st.session_state.user_authenticated = True
                    st.session_state.user_info = {"type": "Google", "username": username}
                    st.rerun()
                else:
                    st.error("يرجى إدخال اسم الحساب وكلمة سر من 4 أحرف/أرقام على الأقل.")
                    
        with tab_apple:
            apple_id = st.text_input("اسم حساب Apple ID / iCloud:", key="a_user")
            apple_pass = st.text_input("كلمة السر:", type="password", key="a_pass")
            if st.button("دخول بـ Apple ID", use_container_width=True):
                if apple_id and len(apple_pass) >= 4:
                    st.session_state.user_authenticated = True
                    st.session_state.user_info = {"type": "iCloud", "username": apple_id}
                    st.rerun()
                else:
                    st.error("يرجى إدخال اسم الحساب وكلمة السر بشكل صحيح.")

# --- 7. التطبيق الرئيسي بعد الدخول ---
else:

    # --- القائمة الجانبية الجانبية والعلوية ---
    with st.sidebar:
        st.write(f"👤 الحساب الحالي: **{st.session_state.user_info['username']}**")
        st.caption(f"النوع: {st.session_state.user_info['type']}")
        
        if st.button("تسجيل الخروج 🚪"):
            st.session_state.user_authenticated = False
            st.session_state.user_info = None
            st.rerun()

        st.markdown("---")
        
        # --- 📁 أرشيف وملخصات المحفوظة (حفظ التلخيصات السابقة) ---
        st.header("📜 الملخصات المحفوظة בחسابك")
        if st.session_state.user_history:
            st.success(f"لديك {len(st.session_state.user_history)} ملخصات محفوظة.")
            for idx, item in enumerate(reversed(st.session_state.user_history)):
                with st.expander(f"📌 {item['title']} - ({item['time']})"):
                    st.markdown(item['content'])
        else:
            st.info("لا توجد ملخصات محفوظة بعد. أي تلخيص تقوم به سيحفظ هنا تلقائياً!")

        st.markdown("---")
        st.header("⚙️ الإعدادات العامة")
        
        admin_input = st.text_input("🔑 دخول الأدمن (كلمة السر):", type="password")
        if admin_input == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.success("👑 مرحباً بك يا محمد (وضع المدير مفعل)")
        else:
            st.session_state.is_admin = False

        st.markdown("---")
        
        input_key = st.text_input("أدخل GEMINI API KEY:", value=api_key_secret, type="password")
        final_api_key = input_key if input_key else api_key_secret
        
        language = st.selectbox("🎯 لغة التلخيص والرد:", ["الدارجة المغربية 🇲🇦", "العربية الفصحى 🇲🇦", "الفرنسية 🇫🇷", "الإنجليزية 🇬🇧"])
        summary_type = st.selectbox("📝 نوع التلخيص:", ["ملخص شامل وتفصيلي", "نقاط رئيسية وسريعة", "أسئلة وإجابات وشرح مبسط"])

        st.markdown("---")
        st.header("🖼️ تحليل الصور والفروض")
        uploaded_image = st.file_uploader("قم برفع صورة الفرض أو التمرين:", type=["png", "jpg", "jpeg"])
        image_prompt = st.text_area(
            "التعليمات:",
            value="استخرج جميع الأسئلة والتمارين المكتوبة في الصورة وأجب عليها بالكامل إجابة نموذجية وبشرح واضح يفهمه الطالب المغربي."
        )
        btn_analyze = st.button("🔍 تحليل الصورة وحل الفرض كامل", use_container_width=True)

    # --- لوحة التحكم للأدمن ---
    if st.session_state.is_admin:
        st.markdown("""
        <div class="admin-dashboard">
            <h3 style="margin:0; color:#2B6CB0;">👑 لوحة تحكم المالك: محمد كويرس</h3>
            <p style="margin:5px 0 15px 0; font-size:14px; color:#4A5568;">✨ أنت تتصفح الموقع حالياً بوضع الأدمن (بدون إعلانات).</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_adm1, col_adm2, col_adm3 = st.columns(3)
        with col_adm1:
            st.metric(label="👥 عدد زوار الموقع", value=f"{st.session_state.visitor_count} زائر")
        with col_adm2:
            estimated_earnings = round(st.session_state.visitor_count * 0.008, 2)
            st.metric(label="💰 أرباح مشاهدة الإعلانات", value=f"${estimated_earnings} USD")
        with col_adm3:
            st.metric(label="🏦 نقل الأموال للحساب البنكي", value="جاهز للسحب 🟢")
        st.markdown("---")

    # --- الإعلانات للزوار ---
    if not st.session_state.is_admin:
        st.markdown('<div class="ad-box">📢 مساحة إعلانية (Google AdSense) - تظهر للزوار العاديين فقط</div>', unsafe_allow_html=True)

    # --- الواجهة الرئيسية ---
    st.markdown('<h1 class="main-title">📚 تلخيص دروس وفيديوهات المغرب 🇲🇦</h1>', unsafe_allow_html=True)

    def extract_video_id(url):
        if not url:
            return None
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be\/([0-9A-Za-z_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_transcript(video_id):
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['ar', 'ar-MA', 'en', 'fr'])
            data = transcript.fetch()
            return " ".join([i['text'] for i in data])
        except Exception:
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                return " ".join([i['text'] for i in transcript_list])
            except Exception:
                return None

    col_vid1, col_vid2 = st.columns([2, 1])

    with col_vid1:
        video_url = st.text_input("🔗 أدخل رابط فيديو اليوتيوب (دروس مغربية، شرح بالدارجة...):", placeholder="https://www.youtube.com/watch?v=...")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 ملخص الدرس", type="primary", use_container_width=True):
                if not final_api_key:
                    st.error("⚠️ يرجى إدخال Gemini API Key في القائمة الجانبية أولاً.")
                elif not video_url:
                    st.warning("⚠️ يرجى إدخال رابط الفيديو.")
                else:
                    v_id = extract_video_id(video_url)
                    if v_id:
                        genai.configure(api_key=final_api_key)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        prompt_lang = "الدارجة المغربية المبسطة والتفصيلية" if "الدارجة" in language else language

                        with st.spinner("جاري تحليل وفهم محتوى الدرس..."):
                            text = get_transcript(v_id)
                            res_text = ""
                            
                            if text:
                                prompt = f"قم بتلخيص هذا الدرس الشامل بالكامل وبطريقة مبسطة يفهمها التلميذ بـ ({prompt_lang}) وبأسلوب ({summary_type}):\n\n{text}"
                                response = model.generate_content(prompt)
                                res_text = response.text
                            else:
                                prompt = f"أنا أعطيك رابط درس من يوتيوب: {video_url}\nقم بتلخيص وشرح موضوع هذا الدرس بالتفصيل وبأسلوب مبسط جداً بـ ({prompt_lang})، محدداً النقاط الأساسية والشرح المطلوب للتمارين والدروس المغربية."
                                try:
                                    response = model.generate_content(prompt)
                                    res_text = response.text
                                except Exception as e:
                                    st.error(f"حدث خطأ أثناء المعالجة: {e}")

                            if res_text:
                                st.success("✅ تم التلخيص بنجاح وحفظه في حسابك!")
                                st.markdown(res_text)
                                
                                # حفظ التلخيص تلقائياً في حساب المستخدم
                                current_time = datetime.now().strftime("%H:%M - %Y/%m/%d")
                                st.session_state.user_history.append({
                                    "title": f"درس يوتيوب ({v_id})",
                                    "time": current_time,
                                    "content": res_text
                                })
                    else:
                        st.error("رابط اليوتيوب غير صحيح.")

        with col_btn2:
            if st.button("➕ حفظ الفيديو للتحليل مع الصورة", use_container_width=True):
                v_id = extract_video_id(video_url)
                if v_id:
                    text = get_transcript(v_id)
                    if text:
                        st.session_state.videos_list.append(text)
                    else:
                        st.session_state.videos_list.append(f"رابط فيديو مرفق: {video_url}")
                    st.success(f"تمت إضافة الفيديو! الإجمالي: {len(st.session_state.videos_list)} فيديو.")
                else:
                    st.error("يرجى إدخال رابط فيديو صحيح أولاً.")

    with col_vid2:
        st.info("💡 **مميزات المنصة:**\n1. **حفظ محلي فوري** لجميع ملخصاتك في القائمة الجانبية (3 أشرطة بالاكود).\n2. **دعم كامل للدارجة المغربية** لتبسيط الشرح والدروس.\n3. رفع صور الفروض والتمارين لحلها بالكامل.")

    # --- تحليل صورة الفرض ---
    if btn_analyze:
        if not final_api_key:
            st.error("⚠️ يرجى إدخال API Key في القائمة الجانبية أولاً.")
        elif not uploaded_image:
            st.warning("⚠️ يرجى رفع صورة الفرض من القائمة الجانبية.")
        else:
            with st.spinner("جاري قراءة الفرض واستخراج جميع الأسئلة وحلها..."):
                try:
                    genai.configure(api_key=final_api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    img = Image.open(uploaded_image)

                    context = ""
                    if st.session_state.videos_list:
                        context = "\n\nالمعطيات المأخوذة من فيديوهات الدروس المرفقة:\n" + "\n--- فيديو جديد ---\n".join([v[:3000] for v in st.session_state.videos_list])

                    prompt_lang = "الدارجة المغربية" if "الدارجة" in language else language
                    full_prompt = f"{image_prompt}\nقم بالشرح والحل بـ ({prompt_lang}).\n{context}"
                    response = model.generate_content([full_prompt, img])

                    st.markdown("---")
                    st.subheader("📝 نتائج تحليل الفرض وإجابة جميع الأسئلة")
                    col_res1, col_res2 = st.columns([1, 2])
                    with col_res1:
                        st.image(img, caption="صورة الفرض المرفوع", use_column_width=True)
                    with col_res2:
                        st.markdown(response.text)
                    
                    # حفظ التحلل في تاريخ الحساب
                    current_time = datetime.now().strftime("%H:%M - %Y/%m/%d")
                    st.session_state.user_history.append({
                        "title": f"حل فرض/صورة",
                        "time": current_time,
                        "content": response.text
                    })

                except Exception as e:
                    st.error(f"حدث خطأ: {e}")

# --- 8. الحقوق ---
st.markdown("""
    <div class="footer">
        <div class="footer-title">صنع من طرف محمد كويرس</div>
        <div class="footer-sub">© 2026 جميع الحقوق محفوظة لملخص دروس المغرب</div>
    </div>
""", unsafe_allow_html=True)
