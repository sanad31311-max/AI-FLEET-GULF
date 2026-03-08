import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# --- 1. إعدادات الهوية الفخمة ---
st.set_page_config(page_title="نظام النخبة الذكي 2026", layout="wide", page_icon="🫡")
st.markdown("<style>.main { background-color: #0e1117; color: #ffffff; } .stMetric { background-color: #1f2937; padding: 20px; border-radius: 12px; border: 1px solid #4b5563; }</style>", unsafe_allow_html=True)

st.title("🫡 مركز العمليات الذكي - الملازم جاسم")

# --- 2. محرك البيانات الذكي (Auto-Discovery) ---
file_name = "Fleet1 data 2026.xlsx"

@st.cache_data
def load_and_fix_data():
    if not os.path.exists(file_name): return None
    try:
        # قراءة الملف ومحاولة إيجاد سطر البداية
        raw_df = pd.read_excel(file_name, sheet_name=0)
        target_row = 0
        for i in range(min(20, len(raw_df))):
            row_values = raw_df.iloc[i].astype(str).values
            if any("الاسم" in val or "اسم" in val for val in row_values):
                target_row = i + 1
                break
        df = pd.read_excel(file_name, sheet_name=0, skiprows=target_row)
        df.columns = [str(c).strip() for c in df.columns]
        # تنظيف البيانات
        if 'الاسم' in df.columns:
            df = df.dropna(subset=['الاسم']).reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"❌ خطأ فني في قراءة البيانات: {e}")
        return None

df = load_and_fix_data()

# --- 3. تفعيل الذكاء الاصطناعي (Gemini 1.5) ---
ai_active = False
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"] != "ضع_مفتاحك_هنا":
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        ai_active = True
    except:
        ai_active = False

# --- 4. واجهة العرض والتحكم ---
if df is not None:
    st.success(f"✅ تم سحب البيانات وتنظيفها تلقائياً من {file_name}")
    
    tab1, tab2 = st.tabs(["📊 لوحة التحكم الحية", "🤖 المساعد الشخصي المفتوح"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write("### 📋 سجل الحسابات المحدث")
            search = st.text_input("🔍 ابحث عن أي معلومة (اسم، سيارة، مبلغ)...")
            if search:
                res = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
                st.dataframe(res, use_container_width=True)
            else:
                st.dataframe(df.head(20), use_container_width=True)
        with col2:
            st.write("### 📈 ملخص سريع")
            st.metric("إجمالي السجلات", len(df))
            st.info("النظام يقوم بتحديث نفسه آلياً بمجرد رفع أي ملف جديد.")

    with tab2:
        st.write("### 🤖 مساعدك الشخصي الآن بصلاحيات مفتوحة")
        if ai_active:
            prompt = st.chat_input("تحدث معي.. اسأل عن الرواتب، المستحقات، أو تطوير النظام...")
            if prompt:
                st.chat_message("user").write(prompt)
                with st.chat_message("assistant"):
                    try:
                        # إرسال سياق الملف للذكاء الاصطناعي
                        context = f"الأعمدة المتاحة: {df.columns.tolist()}. لمحة عن البيانات: {df.head(5).to_string()}"
                        response = model.generate_content(f"أنت مساعد شخصي للملازم جاسم بن محمد. البيانات المتاحة هي: {context}\n\nسؤال الملازم جاسم: {prompt}")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"⚠️ عذراً طال عمرك، هناك مشكلة في الاتصال بالـ API. تأكد من صحة المفتاح في Secrets. (Error: {e})")
        else:
            st.warning("⚠️ المساعد يحتاج 'مفتاح الـ API' ليعمل.")
            st.info("طريقة التفعيل: Streamlit Settings -> Secrets -> GEMINI_API_KEY = 'مفتاحك_هنا'")

else:
    st.error("⚠️ لم نجد الملف أو أن التنسيق يختلف. تأكد من رفع 'Fleet1 data 2026.xlsx'")
