import pandas as pd
import streamlit as st

# 짠맛 단계
def salty(natrium):
    if natrium < 100:
        return '싱거움'
    elif natrium < 400:
        return '조금 짠'
    elif natrium < 800:
        return '보통 짠맛'
    elif natrium < 1200:
        return '짠맛'
    else:
        return '매우 짠맛'
# 단맛 단계 
def sweet(sugar):
    if sugar < 5:
        return '거의 안 달음'
    elif sugar < 10:
        return '살짝 단맛'
    elif sugar < 20:
        return '적당히 단맛'
    elif sugar < 30:
        return '꽤 단맛'
    else:
        return '엄청 단맛'

# streamlit
def run_pref():
    st.markdown("---")
    
    df = pd.read_csv('./food1.csv')
    # 사용자 입력
    st.subheader('수치를 입력하세요')
    col1, col2 = st.columns(2)
    with col1:
        natrium = st.number_input('나트륨(mg)', min_value=0, max_value=10000, step=10)
    with col2:
        sugar = st.number_input('당류(g)', min_value=0.0, max_value=100.0, step=0.1)

    if natrium > 0 or sugar > 0:
        salt_result = salty(natrium)
        sweet_result = sweet(sugar)

        st.success(f"입력 결과: 짠맛 '{salt_result}', 단맛 '{sweet_result}' " )
        
        df["나트륨차이"] = abs(df["나트륨(mg)"] - natrium)
        df["당류차이"] = abs(df["당류(g)"] - sugar)

        # 비슷한 짠맛 음식
        st.subheader("비슷한 짠맛의 음식")
        st.dataframe(df.sort_values("나트륨차이").head(10)[["식품명", "나트륨(mg)"]])

        # 비슷한 단맛 음식
        st.subheader("비슷한 단맛의 음식")
        st.dataframe(df.sort_values("당류차이").head(10)[["식품명", "당류(g)"]])
    else:
        st.info("나트륨 또는 당류 값을 입력해 주세요")