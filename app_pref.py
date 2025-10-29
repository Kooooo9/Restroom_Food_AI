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
    # 데이터프레임 스타일을 위한 CSS 추가
    st.markdown("""
    <style>
        /* 데이터프레임이 컨테이너를 벗어나지 않도록 */
        div[data-testid="column"] > div {
            overflow-x: hidden;
        }
        
        /* 데이터프레임 자체 스타일 */
        div[data-testid="stDataFrame"] {
            width: 100% !important;
        }
        
        div[data-testid="stDataFrame"] > div {
            width: 100% !important;
            overflow-x: auto;
        }
    </style>
    """, unsafe_allow_html=True)
    
    df = pd.read_csv('./food1.csv')
    
    # 페이지 헤더
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: var(--primary-color);">맛 선호도 분석</h1>
            <p style="color: var(--text-color); font-size: 1.2rem;">
                나트륨과 당류 기준으로 선호하는 맛을 분석하고 비슷한 음식을 찾아보세요
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 입력 섹션
    st.markdown("""
        <div class="custom-card">
            <h2>🎯 선호도 입력</h2>
            <p>원하는 나트륨과 당류 수치를 입력해주세요.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        natrium = st.number_input('나트륨(mg)', 
                                min_value=0, 
                                max_value=10000, 
                                step=10,
                                help="나트륨 함량을 입력하세요 (0~10000mg)")
    with col2:
        sugar = st.number_input('당류(g)', 
                              min_value=0.0, 
                              max_value=100.0, 
                              step=0.1,
                              help="당류 함량을 입력하세요 (0~100g)")

    if natrium > 0 or sugar > 0:
        salt_result = salty(natrium)
        sweet_result = sweet(sugar)

        # 분석 결과 카드
        st.markdown("""
        <div class="custom-card">
            <h2 style="color: var(--primary-color);">분석 결과</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # 짠맛과 단맛 결과를 열로 분리
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="custom-card" style="height: 100%;">
                <div style="text-align: center;">
                    <h3 style="color: var(--accent-color); margin-bottom: 1rem;">🧂 짠맛 단계</h3>
                    <div style="font-size: 1.5rem; font-weight: bold; margin: 1rem 0;">{salt_result}</div>
                    <div style="color: var(--text-color);">{int(natrium)}mg</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="custom-card" style="height: 100%;">
                <div style="text-align: center;">
                    <h3 style="color: var(--secondary-color); margin-bottom: 1rem;">🍯 단맛 단계</h3>
                    <div style="font-size: 1.5rem; font-weight: bold; margin: 1rem 0;">{sweet_result}</div>
                    <div style="color: var(--text-color);">{sugar:.1f}g</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        df["나트륨차이"] = abs(df["나트륨(mg)"] - natrium)
        df["당류차이"] = abs(df["당류(g)"] - sugar)

        # 추천 음식 섹션
        st.markdown("""
        <div class="custom-card">
            <h2 style="color: var(--primary-color); margin-bottom: 1.5rem;">추천 음식</h2>
        </div>
        """, unsafe_allow_html=True)

        # 각각의 테이블을 독립적인 카드에 배치
        col1, col2 = st.columns(2)
        
        with col1:
            # 나트륨 데이터
            similar_salty = df.sort_values("나트륨차이").head(10)[["식품명", "나트륨(mg)"]]
            similar_salty["나트륨(mg)"] = similar_salty["나트륨(mg)"].astype(int)
            
            with st.container():
                st.markdown("""
                <div class="custom-card">
                    <h3 style="color: var(--accent-color); margin-bottom: 1rem;">🧂 비슷한 짠맛의 음식</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.dataframe(
                    similar_salty,
                    use_container_width=True,
                    height=300,
                    hide_index=True
                )

        with col2:
            # 당류 데이터
            similar_sweet = df.sort_values("당류차이").head(10)[["식품명", "당류(g)"]]
            similar_sweet["당류(g)"] = similar_sweet["당류(g)"].round(1)
            
            with st.container():
                st.markdown("""
                <div class="custom-card">
                    <h3 style="color: var(--secondary-color); margin-bottom: 1rem;">🍯 비슷한 단맛의 음식</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.dataframe(
                    similar_sweet,
                    use_container_width=True,
                    height=300,
                    hide_index=True
                )

    else:
        st.markdown("""
        <div class="custom-card" style="text-align: center;">
            <h3 style="color: var(--primary-color);">👆 나트륨 또는 당류 값을 입력해주세요</h3>
            <p>원하는 맛의 수치를 입력하면 비슷한 음식을 찾아드립니다.</p>
        </div>
        """, unsafe_allow_html=True)