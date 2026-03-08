import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# --- 1. إعدادات الهوية ---
st.set_page_config(page_title="نظام النخبة الذكي 2026", layout="wide", page_icon="🫡")
st.markdown("<style>.main { background-color: #0e1117; color: #ffffff; } .stMetric { background-color: #1f2937; padding: 20px; border-radius: 12px; border: 1px solid #4b5563; }</style>", unsafe_allow_html=True)

st.title("🫡 مركز العمليات الذكي - الملازم جاسم")

# --- 2. محرك البيانات الذكي ---
file_name = "Fleet1 data 2026.xlsx"

@st.cache_data
def load_and_fix_data():
    if not os.path.exists(file_name): return None
    try:
        raw_df = pd.read_excel(file_name, sheet_name=0)
        target_row = 0
        for i in range(min(20, len(raw_df))):
            row_values = raw_df.iloc[i].astype(str).values
            if any("الاسم" in val or "اسم" in val for val in row_values):
                target_row = i + 1
                break
        df = pd.read_excel(file_name, sheet_name=0, skiprows=target_row)
        df.columns = [str(c).strip() for c in df.columns]
        if 'الاسم' in df.columns:
            df = df.dropna(subset=['الاسم']).reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"❌ خطأ فني في قراءة البيانات: {e}")
        return None

df = load_and_fix_data()

# --- 3. تفعيل الذكاء الاصطناعي (تعديل النيشان لتجنب خطأ 404) ---
ai_model = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"].strip()
    if api_key and api_key.startswith("AIza"):
        try:
            genai.configure(api_key=api_key)
            # استخدمنا 'gemini-1.5-flash' بدون بادئة 'models/' لتجنب خطأ 404
            ai_model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            st.error(f"⚠️ خطأ في تكوين الذكاء الاصطناعي: {e}")

# --- 4. واجهة العرض والتحكم ---
if df is not None:
    st.success(f"✅ تم سحب البيانات وتنظيفها من {file_name}")
    
    tab1, tab2 = st.tabs(["📊 لوحة التحكم", "🤖 المساعد الذكي"])
    
    with tab1:
        st.write("### 📋 سجل الحسابات والأسطول")
        search = st.text_input("🔍 ابحث عن اسم، سيارة، أو مبلغ...")
        if search:
            res = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
            st.dataframe(res, use_container_width=True)
        else:
            st.dataframe(df.head(20), use_container_width=True)

    with tab2:
        st.write("### 🤖 مساعدك الشخصي")
        prompt = st.chat_input("تحدث معي.. اسأل عن الرواتب أو تطوير النظام...")
        if prompt:
            st.chat_message("user").write(prompt)
            if ai_model:
                with st.chat_message("assistant"):
                    try:
                        context = f"الأعمدة: {df.columns.tolist()}. البيانات: {df.head(5).to_string()}"
                        full_prompt = f"أنت مساعد شخصي للملازم جاسم بن محمد. البيانات هي: {context}\n\nسؤال الملازم: {prompt}"
                        response = ai_model.generate_content(full_prompt)
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"⚠️ مشكلة في الـ API: {e}")
            else:
                st.warning("⚠️ المفتاح غير مفعل بشكل صحيح في Secrets.")
else:
    st.error(f"⚠️ الملف '{file_name}' مفقود.")
