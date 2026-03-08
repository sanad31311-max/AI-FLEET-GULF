import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. إعدادات الهوية والواجهة الاحترافية ---
st.set_page_config(page_title="نظام النخبة الذكي 2026", layout="wide", page_icon="🫡")

# تصميم فخم (Dark Mode) وتنسيقات CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1f2937; padding: 20px; border-radius: 12px; border: 1px solid #4b5563; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #374151; }
    h1, h2, h3 { color: #f3f4f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات (Data Engine) ---
@st.cache_data
def load_data():
    file_name = "Fleet data 2026.xlsx"
    try:
        # قراءة البيانات مع تجاوز أول سطرين (بناءً على ملفك)
        df = pd.read_excel(file_name, sheet_name="كشف", skiprows=2)
        # تنظيف البيانات البسيطة
        df = df.dropna(subset=['الاسم']) 
        return df
    except Exception as e:
        st.error(f"⚠️ خطأ في قراءة ملف الإكسل: {e}")
        return None

df = load_data()

# --- 3. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=80)
    st.title("غرفة العمليات")
    st.write(f"الملازم: جاسم بن محمد 🫡")
    st.markdown("---")
    menu = st.radio("القوائم الرئيسية:", 
                    ["📊 لوحة التحكم", "📋 سجل الأسطول والعمالة", "💸 الديتور المالي", "🤖 المساعد الشخصي (AI)"])
    st.markdown("---")
    st.caption(f"التاريخ الحالي: {datetime.now().strftime('%Y-%m-%d')}")

# التحقق من وجود البيانات
if df is not None:
    # --- 4. لوحة التحكم (Dashboard) ---
    if menu == "📊 لوحة التحكم":
        st.title("📊 مركز التحكم والسيطرة - 2026")
        
        # مؤشرات الأداء الحية (Metrics)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي القوة البشرية", len(df))
        with col2:
            # افتراض أسماء الأعمدة من ملفك
            total_debt = df['مدين مستحقات'].sum() if 'مدين مستحقات' in df.columns else 0
            st.metric("إجمالي المستحقات (مدين)", f"{total_debt:,.0f} ريال", delta_color="inverse")
        with col3:
            total_credit = df['دائن مستحقات'].sum() if 'دائن مستحقات' in df.columns else 0
            st.metric("إجمالي المدفوعات (دائن)", f"{total_credit:,.0f} ريال")

        st.markdown("---")
        
        # رسومات بيانية
        col_left, col_right = st.columns(2)
        with col_left:
            if 'رصيد مستحقات' in df.columns:
                fig = px.pie(df.head(10), values='رصيد مستحقات', names='الاسم', 
                             title="توزيع المستحقات لأعلى 10 أفراد", hole=0.4,
                             color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.write("### 📝 آخر العمليات")
            st.dataframe(df[['الاسم', 'رصيد مستحقات', 'السيارة']].head(8), use_container_width=True)

    # --- 5. سجل الأسطول ---
    elif menu == "📋 سجل الأسطول والعمالة":
        st.title("📋 سجل العمالة والسيارات")
        search = st.text_input("🔍 ابحث عن اسم الموظف أو رقم الإقامة...")
        if search:
            filtered = df[df['الاسم'].str.contains(search, na=False) | df['الاقامه'].astype(str).str.contains(search, na=False)]
        else:
            filtered = df
        st.dataframe(filtered, use_container_width=True)

    # --- 6. الديتور المالي ---
    elif menu == "💸 الديتور المالي":
        st.title("💸 كشف الحسابات (مدين / دائن)")
        st.info("هذا القسم مخصص لمتابعة 'قيمة الشهر' والخدمات والمستحقات.")
        st.table(df[['الاسم', 'مدين خدمات', 'دائن خدمات', 'مدين مستحقات', 'دائن مستحقات', 'رصيد مستحقات']].head(20))

    # --- 7. المساعد الشخصي (AI Assistant) ---
    elif menu == "🤖 المساعد الشخصي (AI)":
        st.title("🤖 المساعد الشخصي الذكي")
        st.markdown("> **أبشر طال عمرك يا أبا محمد، أنا متصل بملف Fleet data 2026 وجاهز لخدمتك.**")
        
        prompt = st.chat_input("اسألني عن رصيد أي موظف أو معلومات السيارة...")
        if prompt:
            with st.chat_message("user"): st.write(prompt)
            with st.chat_message("assistant"):
                # محرك بحث ذكي بسيط
                found = df[df['الاسم'].apply(lambda x: any(p in str(x) for p in prompt.split()))]
                if not found.empty:
                    res = found.iloc[0]
                    st.write(f"أبشر طال عمرك، الموظف **{res['الاسم']}** رصيده الحالي **{res['رصيد مستحقات']} ريال**. والسيارة المسجلة له هي **{res['السيارة']}**.")
                else:
                    st.write("أبشر طال عمرك، جاري البحث والتحليل بناءً على الصلاحيات المفتوحة التي منحتني إياها.")

else:
    st.warning("⚠️ لم يتم العثور على ملف 'Fleet data 2026.xlsx'. يرجى رفعه على GitHub.")
