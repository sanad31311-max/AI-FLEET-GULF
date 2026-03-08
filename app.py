import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="نظام النخبة 2026", layout="wide", page_icon="🫡")
st.title("🫡 نظام الملازم جاسم بن محمد - مركز العمليات")

file_name = "Fleet1 data 2026.xlsx"

@st.cache_data
def load_data():
    if os.path.exists(file_name):
        try:
            # سنقرأ الملف بدون تجاوز أسطر أولاً لنعرف مكانه
            df = pd.read_excel(file_name, sheet_name=0)
            
            # إذا كان أول سطر فيه بيانات فارغة، سنحاول تنظيفه تلقائياً
            df.columns = [str(c).strip() for c in df.columns]
            
            # محرك البحث عن عمود الأسماء (سواء كان اسمه الاسم أو نيم أو غيره)
            possible_names = ['الاسم', 'اسم الموظف', 'Name', 'الأسم']
            found_col = [c for c in df.columns if any(p in c for p in possible_names)]
            
            if found_col:
                df = df.rename(columns={found_col[0]: 'الاسم'})
                return df
            else:
                st.warning(f"⚠️ لم أجد عموداً باسم 'الاسم'. الأعمدة المكتشفة هي: {list(df.columns)}")
                return df
        except Exception as e:
            st.error(f"❌ خطأ في تحليل محتوى الملف: {e}")
            return None
    return None

df = load_data()

if df is not None:
    st.success(f"✅ تم الاتصال بملف {file_name} بنجاح")
    
    # محرك بحث بسيط
    search = st.text_input("🔍 ابحث في السجل الحية...")
    if search:
        filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        st.dataframe(filtered)
    else:
        st.write("### 📊 معاينة البيانات:")
        st.dataframe(df.head(20))
else:
    st.error(f"⚠️ الملف '{file_name}' مفقود من الميدان.")
