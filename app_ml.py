import streamlit as st
import pandas as pd
import numpy as np

def meal_plan(df, kcal, carb, protein, fat, meal_count):
    carb = (kcal * (carb / 100)) / 4
    protein = (kcal * (protein / 100)) / 4
    fat = (kcal * (fat / 100)) / 9
# 영양소가 1g당 제공하는 칼로리가 달라 g을 계산하는 공식 추가해뒀습니다.
# 탄수화물, 단백질 = 1g 당 4kcal, 지방 = 1g당 9kcal
        

  
def run_ml():
    df = pd.read_csv('./food1.csv')

    st.subheader('AI 식단 생성')
    
    kcal = st.number_input('목표 칼로리 (kcal)', 1000, 6000, 2500, step=50)
    col0, col1, col2, col3 = st.columns(4)
    with col0 : meal_count = st.slider("끼니 수", 1, 5, 3)
    with col1 : carb = st.slider('탄수화물 (%)', 10, 80, 50)
    with col2 : protein = st.slider('단백질 (%)', 10, 50, 30)
    with col3 : fat = st.slider('지방 (%)', 10, 50, 20)

    input = st.text_input("피해야 할 음식", "우유, 땅콩", key="피해야 할 음식")

    if st.button("식단 생성"):
        avoid_foods = [x.strip() for x in input.split(',') if x.strip()]
        df_filtered = df[~df['식품명'].str.contains('|'.join(avoid_foods), na=False)]
        
if __name__ == "__main__":
    run_ml()