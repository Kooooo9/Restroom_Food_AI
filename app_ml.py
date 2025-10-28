import streamlit as st
import pandas as pd



def run_ml():
    df = pd.read_csv('./food1.csv')

    st.subheader('AI 식단 생성')
    
    st.number_input('목표 칼로리 (kcal)', 1000, 6000, 2500, step=50)
    col0, col1, col2, col3 = st.columns(4)
    with col0 : meal_count = st.slider("끼니 수", 1, 5, 3)
    with col1 : carb = st.slider('탄수화물 (%)', 10, 80, 50)
    with col2 : protein = st.slider('단백질 (%)', 10, 50, 30)
    with col3 : fat = st.slider('지방 (%)', 10, 50, 20)

    input = st.text_input("피해야 할 음식", "우유, 땅콩", key="피해야 할 음식")

    if st.button("식단 생성"):
        avoid_foods = [x.strip() for x in input.split(',')]
        st.write("피해야 할 음식", avoid_foods)


