import streamlit as st
import pandas as pd
import numpy as np

from app_user_info import get_user_data

def meal_plan(df, kcal, carb, protein, fat, meal_count):
    carb = (kcal * (carb / 100)) / 4
    protein = (kcal * (protein / 100)) / 4
    fat = (kcal * (fat / 100)) / 9
# 영양소가 1g당 제공하는 칼로리가 달라 g을 계산하는 공식 추가해뒀습니다.
# 탄수화물, 단백질 = 1g 당 4kcal, 지방 = 1g당 9kcal
        
def run_ml():
    df = pd.read_csv('./food1.csv')
    
    # 페이지 헤더
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: var(--primary-color);">AI 맞춤 식단 생성</h1>
            <p style="color: var(--text-color); font-size: 1.2rem;">
                AI가 당신의 건강 정보와 선호도를 기반으로 최적의 식단을 구성해드립니다
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 사용자 정보 섹션
    user_data = get_user_data()
    height = user_data.get('height')
    weight = user_data.get('weight')
    age = user_data.get('age')
    bmi = user_data.get('bmi')

    if height is None or weight is None or age is None or bmi is None:
        st.warning("⚠️ 사용자 정보가 필요합니다. 상단 메뉴의 '사용자 정보 입력'에서 정보를 입력해주세요.")
        st.stop()  # 여기서 실행을 중단합니다.

    st.markdown("""
        <div class="custom-card">
            <h2>👤 사용자 정보</h2>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px; border: 1px solid var(--border-color); text-align: center;">
            <h3 style="color: var(--primary-color); margin: 0;">키</h3>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">{height} cm</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px; border: 1px solid var(--border-color); text-align: center;">
            <h3 style="color: var(--secondary-color); margin: 0;">체중</h3>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">{weight} kg</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px; border: 1px solid var(--border-color); text-align: center;">
            <h3 style="color: var(--accent-color); margin: 0;">나이</h3>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">{age} 세</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px; border: 1px solid var(--border-color); text-align: center;">
            <h3 style="color: var(--primary-color); margin: 0;">BMI</h3>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">{bmi:.1f}</p>
        </div>
        """, unsafe_allow_html=True)

    # 식단 설정 섹션
    st.markdown("""
        <div class="custom-card">
            <h2>🎯 목표 설정</h2>
            <p>원하는 영양소 비율과 끼니 수를 설정하세요.</p>
        </div>
    """, unsafe_allow_html=True)

    kcal = st.number_input('목표 칼로리 (kcal)', 1000, 6000, 2500, step=50,
                          help="하루 목표 칼로리를 입력하세요")

    col0, col1, col2, col3 = st.columns(4)
    with col0:
        meal_count = st.slider("끼니 수", 1, 5, 3,
                             help="하루 몇 끼로 나눌지 선택하세요")
    with col1:
        carb = st.slider('탄수화물 (%)', 10, 80, 50,
                        help="탄수화물 비율을 선택하세요")
    with col2:
        protein = st.slider('단백질 (%)', 10, 50, 30,
                          help="단백질 비율을 선택하세요")
    with col3:
        fat = st.slider('지방 (%)', 10, 50, 20,
                       help="지방 비율을 선택하세요")

    # 제외 식품 설정
    st.markdown("""
        <div class="custom-card">
            <h2>⚠️ 제외할 음식</h2>
            <p>알레르기나 선호하지 않는 음식을 입력하세요.</p>
        </div>
    """, unsafe_allow_html=True)

    input = st.text_input("피해야 할 음식 (쉼표로 구분)", 
                         "우유, 땅콩",
                         key="피해야 할 음식",
                         help="피하고 싶은 음식을 쉼표(,)로 구분하여 입력하세요")

    # 실행 버튼
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <button class="stButton">
                <span>🤖 AI 식단 생성하기</span>
            </button>
        </div>
    """, unsafe_allow_html=True)

    if st.button("식단 생성", key="generate_diet"):
        avoid_foods = [x.strip() for x in input.split(',') if x.strip()]
        df_filtered = df[~df['식품명'].str.contains('|'.join(avoid_foods), na=False)]
        
        st.markdown("""
            <div class="custom-card">
                <h2>🍽️ AI 추천 식단</h2>
                <p>당신의 건강 정보와 선호도를 반영한 맞춤형 식단입니다.</p>
            </div>
        """, unsafe_allow_html=True)
        
if __name__ == "__main__":
    run_ml()