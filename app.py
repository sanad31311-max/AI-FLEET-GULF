import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# --- 1. إعداد الهوية الفخمة ---
st.set_page_config(page_title="نظام النخبة الذكي 2026", layout="wide", page_icon="🫡")
st.markdown("<style>.main { background-color: #0e1117; color: #ffffff; }</style>", unsafe_allow_html=True)

st.title("🫡 مركز العمليات الذكي - الملازم جاسم")

# --- 2. محرك البحث الذاتي عن البيانات (Auto-Correction) ---
file_name = "Fleet1 data 2026.xlsx"

@st.cache_data
def load_and_fix_data():
    if not os.path.exists(file_name): return None
    try:
        # قراءة الملف كاملاً
        raw_df = pd.read_excel(file_name, sheet_name=0)
        
        # الذكاء الاصطناعي: البحث عن سطر البداية الحقيقي
        # سنبحث عن السطر الذي يحتوي على كلمات (الاسم، الإقامة، رصيد)
        target_row = 0
        for i in range(len(raw_df.head(20))):
            row_values = raw_df.iloc[i].astype(str).values
            if any("الاسم" in val or "اسم" in val for val in row_values):
                target_row = i + 1
                break
        
        # إعادة تحميل الملف من نقطة البداية الصحيحة
        df = pd.read_excel(file_name, sheet_name=0, skiprows=target_row)
        
        # تنظيف أسماء الأعمدة من المسافات
        df.columns = [str(c).strip() for c in df.columns]
        
        # البحث عن عمود الأسماء وربطه بالنظام
        name_cols = [c for c in df.columns if "الاسم" in c or "اسم" in c]
        if name_cols:
            df = df.rename(columns={name_cols[0]: 'الاسم'})
            
        return df.dropna(subset=['الاسم']).reset_index(drop=True)
    except Exception as e:
        st.error(f"❌ عذراً طال عمرك، حدث خطأ في تحليل 'الديتور': {e}")
        return None

df = load_and_fix_data()

# --- 3. تفعيل الذكاء الاصطناعي (Gemini) ---
# المساعد سيعمل فور وضعك للمفتاح في Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
    ai_active = True
else:
    ai_active = False

# --- 4. واجهة العرض والتحكم ---
if df is not None:
    st.success(f"✅ تم سحب البيانات وتنظيفها تلقائياً من {file_name}")
    
    tab1, tab2 = st.tabs(["📊 لوحة التحكم الحية", "🤖 المساعد الشخصي المفتوح"])
    
    with tab1:
        st.write("### 📋 سجل الحسابات والأسطول المحدث")
        search = st.text_input("🔍 ابحث عن أي معلومة (اسم، سيارة، مبلغ)...")
        if search:
            res = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
            st.dataframe(res, use_container_width=True)
        else:
            st.dataframe(df.head(20), use_container_width=True)

    with tab2:
        if ai_active:
            st.write("### 🤖 مساعدك الشخصي الآن بصلاحيات مفتوحة")
            prompt = st.chat_input("تحدث معي.. اسأل عن الرواتب، المستحقات، أو تطوير النظام...")
            if prompt:
                st.chat_message("user").write(prompt)
                with st.chat_message("assistant"):
                    # إرسال سياق الملف للذكاء الاصطناعي
                    context = f"البيانات المكتشفة: {df.columns.tolist()}. ملخص البيانات: {df.head(5).to_string()}"
                    response = model.generate_content(f"{context}\n\nسؤال الملازم جاسم: {prompt}")
                    st.write(response.text)
        else:
            st.warning("⚠️ طال عمرك، المساعد جاهز ولكن يحتاج 'مفتاح الـ API' ليتحدث معك.")
            st.info("طريقة التفعيل: اذهب لإعدادات Streamlit -> Secrets وضف المفتاح هناك.")

else:
    st.error("⚠️ لم نجد الملف أو أن التنسيق يختلف تماماً. يرجى التأكد من رفع 'Fleet1 data 2026.xlsx'")
