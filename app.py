import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# --- 1. إعدادات الهوية الفخمة ---
st.set_page_config(page_title="نظام النخبة الذكي 2026", layout="wide", page_icon="🫡")
st.markdown("<style>.main { background-color: #0e1117; color: #ffffff; } .stMetric { background-color: #1f2937; padding: 20px; border-radius: 12px; border: 1px solid #4b5563; }</style>", unsafe_allow_html=True)

st.title("🫡 مركز العمليات الذكي - الملازم جاسم")

# --- 2. محرك البيانات الذكي (Fleet1 2026) ---
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

# --- 3. محرك الاستطلاع الذكي (البحث عن الموديل الشغال) ---
ai_model = None
selected_model_name = ""

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"].strip()
    if api_key and api_key.startswith("AIza"):
        try:
            genai.configure(api_key=api_key)
            # استطلاع الموديلات المتاحة في حسابك فعلياً
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if available_models:
                # اختيار أحدث موديل متاح (غالباً 1.5 flash أو pro)
                selected_model_name = available_models[0]
                ai_model = genai.GenerativeModel(selected_model_name)
            else:
                st.error("⚠️ لم يتم العثور على أي موديلات مفعلة في حسابك.")
        except Exception as e:
            st.error(f"⚠️ فشل الاستطلاع التقني للموديلات: {e}")

# --- 4. واجهة العرض والتحكم ---
if df is not None:
    st.success(f"✅ تم الاتصال بالبيانات بنجاح")
    
    tab1, tab2 = st.tabs(["📊 لوحة التحكم", "🤖 المساعد الذكي"])
    
    with tab1:
        st.write("### 📋 سجل الأسطول المحدث")
        search = st.text_input("🔍 ابحث عن أي معلومة...")
        if search:
            res = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
            st.dataframe(res, use_container_width=True)
        else:
            st.dataframe(df.head(20), use_container_width=True)

    with tab2:
        st.write("### 🤖 مساعدك الشخصي")
        if ai_model:
            st.caption(f"تم ربط المحرك بنجاح: {selected_model_name}")
            prompt = st.chat_input("تحدث معي يا أبا محمد...")
            if prompt:
                st.chat_message("user").write(prompt)
                with st.chat_message("assistant"):
                    try:
                        context = f"البيانات: {df.head(5).to_string()}"
                        full_prompt = f"أنت مساعد شخصي للملازم جاسم بن محمد. البيانات هي: {context}\n\nسؤال الملازم: {prompt}"
                        response = ai_model.generate_content(full_prompt)
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"⚠️ تعارض في الاستجابة: {e}")
        else:
            st.warning("⚠️ المساعد بانتظار تفعيل 'مفتاح الـ API' الصحيح.")

else:
    st.error("⚠️ ملف 'Fleet1 data 2026.xlsx' مفقود.")
