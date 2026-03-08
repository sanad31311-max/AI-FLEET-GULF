import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from datetime import datetime
import os

# --- 1. إعدادات الهوية والواجهة الاحترافية ---
st.set_page_config(page_title="نظام النخبة 2026", layout="wide", page_icon="🫡")

# تصميم فخم (Dark Mode)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1f2937; padding: 20px; border-radius: 12px; border: 1px solid #4b5563; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #374151; }
    .stDataFrame { border: 1px solid #374151; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات المعتمد (Fleet1 data 2026) ---
file_name = "Fleet1 data 2026.xlsx"

@st.cache_data
def load_data():
    if os.path.exists(file_name):
        try:
            # يقرأ أول ورقة في الإكسل ويتجاوز أول سطرين حسب تنسيق ملفك
            df = pd.read_excel(file_name, sheet_name=0, skiprows=2)
            df = df.dropna(subset=['الاسم']).reset_index(drop=True)
            return df
        except Exception as e:
            st.error(f"❌ خطأ فني في قراءة البيانات: {e}")
            return None
    return None

df = load_data()

# --- 3. إعداد الذكاء الاصطناعي (Gemini) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    ai_model = genai.GenerativeModel('gemini-pro')
else:
    ai_model = None

# --- 4. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=70)
    st.title("غرفة العمليات")
    st.subheader(f"الملازم جاسم بن محمد 🫡")
    st.markdown("---")
    menu = st.radio("انتقل إلى:", 
                    ["📊 لوحة التحكم", "📋 سجل الأسطول والعمالة", "💸 الديتور المالي", "🤖 المساعد الشخصي"])
    st.markdown("---")
    st.caption(f"آخر تحديث للنظام: {datetime.now().strftime('%Y-%m-%d')}")

# --- 5. منطق الصفحات ---
if df is not None:
    # --- لوحة التحكم ---
    if menu == "📊 لوحة التحكم":
        st.title("📊 مركز التحكم والسيطرة - 2026")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي القوة البشرية", len(df))
        with col2:
            debt_val = df['مدين مستحقات'].sum() if 'مدين مستحقات' in df.columns else 0
            st.metric("إجمالي المديونيات", f"{debt_val:,.0f} ريال", delta_color="inverse")
        with col3:
            st.metric("حالة الربط التقني", "متصل ✅")
        
        st.markdown("---")
        # رسم بياني للمستحقات
        if 'رصيد مستحقات' in df.columns:
            fig = px.bar(df.head(10), x='الاسم', y='رصيد مستحقات', color='رصيد مستحقات',
                         title="أعلى 10 مستحقات مالية", color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)

    # --- سجل الأسطول ---
    elif menu == "📋 سجل الأسطول والعمالة":
        st.title("📋 سجل العمالة والسيارات المعتمد")
        search = st.text_input("🔍 ابحث عن اسم الموظف أو رقم الإقامة...")
        if search:
            filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
            st.dataframe(filtered, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

    # --- الديتور المالي ---
    elif menu == "💸 الديتور المالي":
        st.title("💸 كشف الحسابات (مدين / دائن)")
        st.info("هذا الجدول يوضح ميزانية الخدمات والمستحقات بناءً على ملف Fleet1 data 2026.")
        # عرض أعمدة الديتور الأساسية
        cols_to_show = [c for c in df.columns if any(x in c for x in ['الاسم', 'مدين', 'دائن', 'رصيد'])]
        st.table(df[cols_to_show].head(20))

    # --- المساعد الشخصي (الذكاء الاصطناعي) ---
    elif menu == "🤖 المساعد الشخصي":
        st.title("🤖 مساعدك الذكي (صلاحيات مفتوحة)")
        st.markdown("> **أبشر طال عمرك يا أبا محمد، أنا متصل بالبيانات وجاهز لخدمتك.**")
        
        user_input = st.chat_input("تحدث معي عن أي رصيد أو معلومة...")
        if user_input:
            st.chat_message("user").write(user_input)
            with st.chat_message("assistant"):
                if ai_model:
                    # إرسال سياق البيانات للـ AI
                    context = f"بياناتك الحالية: {df.head(10).to_string()}"
                    response = ai_model.generate_content(f"{context}\n\nسؤال المستخدم: {user_input}")
                    st.write(response.text)
                else:
                    st.write("أبشر طال عمرك، جاري تحليل البيانات.. (يرجى تفعيل API Key لتفعيل الردود الذكية).")

else:
    st.error(f"⚠️ تنبيه: الملف '{file_name}' لم يتم العثور عليه في المستودع.")
    st.info(f"يرجى التأكد من رفع ملف الإكسل باسم: {file_name}")
    st.write("الملفات الحالية في GitHub:", os.listdir())
