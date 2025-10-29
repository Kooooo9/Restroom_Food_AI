import streamlit as st
from koreanize_matplotlib import koreanize
koreanize()
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb

def run_eda():
    df = pd.read_csv('./food1.csv')

    # 페이지 헤더
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: var(--primary-color);">음식 영양 정보 분석</h1>
            <p style="color: var(--text-color); font-size: 1.2rem;">
                다양한 음식의 영양 정보를 확인하고 분석해보세요
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 음식 선택 섹션
    st.markdown("""
        <div class="custom-card">
            <h2>🔍 음식 검색</h2>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        choice = st.selectbox("분석할 음식을 선택하세요", df["식품명"].unique())
    with col2:
        st.write("")  # 간격 유지용

    # 선택된 음식 정보
    info = df[df["식품명"] == choice].iloc[0]
    
    # 영양 정보 카드
    st.markdown(f"""
        <div class="custom-card">
            <h2 style="color: var(--primary-color); margin-bottom: 1.5rem;">{choice}의 영양 분석</h2>
        </div>
    """, unsafe_allow_html=True)

    # 영양소 정보를 가로 막대 차트로 표시
    st.markdown("""
    <div class="custom-card">
        <h3>📊 영양소 함량</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 영양소 정보를 선호도 바 형태로 표시
    nutrients_info = [
        {"name": "에너지 (kcal)", "value": info['에너지(kcal)'], "max": 1000, "color": "#ff4b4b"},
        {"name": "탄수화물 (g)", "value": info['탄수화물(g)'], "max": 100, "color": "#4bb543"},
        {"name": "단백질 (g)", "value": info['단백질(g)'], "max": 50, "color": "#3498db"},
        {"name": "지방 (g)", "value": info['지방(g)'], "max": 50, "color": "#9b59b6"}
    ]

    for nutrient in nutrients_info:
        col1, col2 = st.columns([1, 5])
        with col1:
            st.write(f"{nutrient['name']}")
        with col2:
            # 진행바의 색상과 배경색을 커스텀
            progress_html = f"""
            <div style="width: 100%; background-color: rgba(0,0,0,0.1); border-radius: 10px; margin: 5px 0;">
                <div style="width: {min(100, (nutrient['value']/nutrient['max'])*100)}%; 
                            background-color: {nutrient['color']}; 
                            height: 20px; 
                            border-radius: 10px; 
                            text-align: right; 
                            padding-right: 10px;
                            color: white;
                            line-height: 20px;
                            font-size: 14px;">
                    {nutrient['value']:.1f}
                </div>
            </div>
            """
            st.markdown(progress_html, unsafe_allow_html=True)

    # 영양 밸런스 시각화
    st.markdown("""
    <div class="custom-card">
        <h2>📊 영양소 비율</h2>
    </div>
    """, unsafe_allow_html=True)

    # 원형 차트 생성
    col1, col2 = st.columns([2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(5, 5))
        nutrients = ['탄수화물', '단백질', '지방']
        values = [info['탄수화물(g)'], info['단백질(g)'], info['지방(g)']]
        colors = ['#2ECC71', '#3498DB', '#E74C3C']
        
        # 도넛 차트 생성 (텍스트 없이)
        plt.pie(values, colors=colors, startangle=90, 
                wedgeprops=dict(width=0.7))
        
        # 범례 설정
        plt.legend(nutrients,
                  title="영양소",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.title(f'{choice}의 영양소 비율', pad=20, size=12)
        st.pyplot(fig)
    
    # 추천 식단 조합
    st.markdown("""
    <div class="custom-card">
        <h2>💡 영양 분석 결과</h2>
        <p style="margin-top: 1rem;">이 음식의 영양 특성을 고려한 균형잡힌 식단 구성을 위한 조언입니다.</p>
    </div>
    """, unsafe_allow_html=True)

    # 영양소 비율에 따른 추천 메시지
    carb_ratio = info['탄수화물(g)'] * 4 / info['에너지(kcal)'] * 100 if info['에너지(kcal)'] > 0 else 0
    protein_ratio = info['단백질(g)'] * 4 / info['에너지(kcal)'] * 100 if info['에너지(kcal)'] > 0 else 0
    fat_ratio = info['지방(g)'] * 9 / info['에너지(kcal)'] * 100 if info['에너지(kcal)'] > 0 else 0

    st.info(f"""
    - 탄수화물 비율: {carb_ratio:.1f}% (권장: 50-60%)
    - 단백질 비율: {protein_ratio:.1f}% (권장: 15-20%)
    - 지방 비율: {fat_ratio:.1f}% (권장: 20-25%)
    """)



