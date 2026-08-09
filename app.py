import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from PIL import Image
import re

# --- 🗝️ كلمة السر الخاصة بالأدمن ---
ADMIN_PASSWORD = "mohamed_kouirs_2026"

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="ملخص دروس المغرب - بالدارجة",
    page_icon="🇲🇦",
    layout="wide"
)

# --- 2. إدارة الجلسة ---
if "visitor_count" not in st.session_state:
    st.session_state.visitor_count = 125
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "videos_list" not in st.session_state:
    st.session_state.videos_list = []

st.session_state.visitor_count += 1

# --- 3. تصميم CSS ---
st.markdown("""
    <style>
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 15px;
        background-color: #FFFFFF;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 15px;
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

# --- 4. الهيدر العلوي ---
st.markdown("""
    <div class="top-header">
        <div style="font-size: 20px;">🔔</div>
        <div><img src="https://upload.wikimedia.org/wikipedia/commons/d/d1/Coat_of_arms_of_Morocco.svg" class="header-logo"></div>
    </div>
""", unsafe_allow_html=True)

# --- 5. القائمة الجانبية ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    
    admin_input = st.text_input("🔑 دخول الأدمن (كلمة السر):", type="password")
    if admin_input == ADMIN_PASSWORD:
        st.session_state.is_admin = True
        st.success("👑 مرحباً بك يا محمد (وضع المدير مفعل)")
    else:
        st.session_state.is_admin = False

    st.markdown("---")
    api_key = st.text_input("أدخل GEMINI API KEY (تأكد أن يبدأ بـ AIzaSy):", type="password")
    st.markdown("[كيف تحصل على مفتاح API؟](https://aistudio.google.com/app/apikey)")
    
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

# --- 6. لوحة التحكم للأدمن ---
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

# --- 7. الإعلانات للزوار ---
if not st.session_state.is_admin:
    st.markdown('<div class="ad-box">📢 مساحة إعلانية (Google AdSense) - تظهر للزوار العاديين فقط</div>', unsafe_allow_html=True)

# --- 8. الواجهة الرئيسية ---
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
        # البحث عن النص بأي لغة متاحة (العربية، التلقائية، الفرنسية، الإنجليزية)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['ar', 'ar-MA', 'en', 'fr'])
        data = transcript.fetch()
        return " ".join([i['text'] for i in data])
    except Exception:
        try:
            # محاولة احتياطية لجلب أي نص مترجم إلكترونياً
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
            if not api_key:
                st.error("⚠️ يرجى إدخال Gemini API Key في القائمة الجانبية أولاً.")
            elif not video_url:
                st.warning("⚠️ يرجى إدخال رابط الفيديو.")
            else:
                v_id = extract_video_id(video_url)
                if v_id:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')

                    prompt_lang = "الدارجة المغربية المبسطة والشريحة" if "الدارجة" in language else language

                    with st.spinner("جاري استخراج تفاصيل الدرس وتلخيصه..."):
                        text = get_transcript(v_id)
                        
                        if text:
                            try:
                                prompt = f"قم بتلخيص هذا الدرس الشامل بالكامل وبطريقة مبسطة يفهمها التلميذ بـ ({prompt_lang}) وبأسلوب ({summary_type}):\n\n{text}"
                                response = model.generate_content(prompt)
                                st.success("✅ تم التلخيص بنجاح!")
                                st.markdown(response.text)
                            except Exception as e:
                                st.error(f"حدث خطأ أثناء التلخيص: {e}")
                        else:
                            st.warning("⚠️ هذا الفيديو المحدد لا يحتوي على نص ترجمة تلقائي من يوتيوب. يُفضل تجربة فيديو آخر يحتوي على شرح أو نصوص توضيحية مفعلة.")
                else:
                    st.error("رابط اليوتيوب غير صحيح.")

    with col_btn2:
        if st.button("➕ حفظ الفيديو للتحليل مع الصورة", use_container_width=True):
            v_id = extract_video_id(video_url)
            if v_id:
                text = get_transcript(v_id)
                if text:
                    st.session_state.videos_list.append(text)
                    st.success(f"تمت إضافة الفيديو! الإجمالي: {len(st.session_state.videos_list)} فيديو.")
                else:
                    st.warning("تم حفظ الرابط لاستخدامه أثناء تحليل الصورة.")
                    st.session_state.videos_list.append(f"رابط فيديو مرفق: {video_url}")
            else:
                st.error("يرجى إدخال رابط فيديو صحيح أولاً.")

    if st.session_state.videos_list:
        st.caption(f"📌 الفيديوهات المخزنة في الجلسة: {len(st.session_state.videos_list)}")

with col_vid2:
    st.info("💡 **مميزات المنصة:**\n1. **دعم كامل للدارجة المغربية** لتبسيط الشرح والدروس.\n2. **تحليل واستخراج الدروس** بنقرة واحدة.\n3. رفع صور الفروض والتمارين لحلها بالكامل.")

# --- 9. تحليل صورة الفرض ---
if btn_analyze:
    if not api_key:
        st.error("⚠️ يرجى أدخال API Key في القائمة الجانبية أولاً.")
    elif not uploaded_image:
        st.warning("⚠️ يرجى رفع صورة الفرض التجريبي من القائمة الجانبية.")
    else:
        with st.spinner("جاري قراءة الفرض واستخراج جميع الأسئلة وحلها..."):
            try:
                genai.configure(api_key=api_key)
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
            except Exception as e:
                st.error(f"حدث خطأ: {e}")

# --- 10. الحقوق ---
st.markdown("""
    <div class="footer">
        <div class="footer-title">صنع من طرف محمد كويرس</div>
        <div class="footer-sub">© 2026 جميع الحقوق محفوظة لملخص دروس المغرب</div>
    </div>
""", unsafe_allow_html=True)
