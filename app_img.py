import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from PIL import Image
# GradientBoostingRegressor를 사용하도록 import
from sklearn.ensemble import GradientBoostingRegressor 
import re

# =========================================================================
# 1. 환경 설정 및 헬퍼 함수
# =========================================================================



def load_model():
    """Gemini AI 모델을 로드합니다."""
    # API 키 로딩 로직 유지
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Streamlit Secrets에서 로드 시도
        if "GEMINI_API_KEY" in st.secrets:
             api_key = st.secrets["GEMINI_API_KEY"]
        else:
             st.error("⚠️ GEMINI_API_KEY 환경 변수 또는 Streamlit Secrets를 설정해주세요.")
             return None
             
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")

def extract_number(text, keyword):
    """AI 응답 텍스트에서 특정 키워드의 숫자 값을 추출합니다."""
    # 숫자 앞에 공백이 없는 경우를 위해 정규식 수정
    pattern = rf"{keyword}.*?(\d+)"
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None

def extract_section(text, start, end_marker=None):
    """AI 응답 텍스트에서 특정 섹션의 내용을 추출합니다."""
    start_idx = text.find(start)
    if start_idx == -1:
        return ""
    start_idx += len(start)
    if end_marker:
        end_idx = text.find(end_marker, start_idx)
        if end_idx == -1:
            end_idx = len(text)
    else:
        end_idx = len(text)
    return text[start_idx:end_idx].strip()

def train_regression_model():
    """Gradient Boosting Regressor 모델을 학습시킵니다."""
    try:
        # food1.csv 파일 경로가 현재 디렉토리에 있다고 가정
        df = pd.read_csv("./food1.csv")
    except FileNotFoundError:
        st.error("❌ food1.csv 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
        return None
        
    X = df[["탄수화물(g)", "단백질(g)", "지방(g)", "당류(g)", "나트륨(mg)"]]
    y = df["에너지(kcal)"]
    
    # GradientBoostingRegressor 사용 및 학습
    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3).fit(X, y)
    return model

# =========================================================================
# 2. 메인 실행 함수
# =========================================================================

def run_img():
    # 페이지 헤더
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: var(--primary-color);">AI 음식 영양 분석기</h1>
            <p style="color: var(--text-color); font-size: 1.2rem;">
                음식 사진을 업로드하고 (필요시 음식 이름을 입력하여) 영양 정보를 분석해드립니다
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 1. 모델 및 데이터 로드
    regressor = train_regression_model()
    if regressor is None:
        # 데이터 로드 오류는 train_regression_model 내부에서 이미 출력됨
        return

    # 2. 파일 업로드 및 사용자 입력
    st.markdown("""
        <div class="custom-card">
            <h2>📸 음식 사진 업로드</h2>
            <p>분석하고 싶은 음식의 사진을 업로드해주세요.</p>
        </div>
    """, unsafe_allow_html=True)
    
    file = st.file_uploader("", type=['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'])
    
    user_food_name = st.text_input(
        "음식 이름 (선택 사항)",
        placeholder="예: 닭가슴살 샐러드, 참치 김치찌개",
        help="사진 인식의 정확도를 높이기 위해 음식 이름을 직접 입력할 수 있습니다."
    )
    
    if not file:
        st.markdown("""
            <div class="custom-card" style="text-align: center;">
                <h3 style="color: var(--primary-color);">👆 사진을 업로드해주세요</h3>
                <p>지원 형식: JPG, JPEG, PNG, gif, webp, bmp</p>
            </div>
        """, unsafe_allow_html=True)
        return
        
    # 이미지 표시
    image = Image.open(file)
    st.markdown("""
        <div class="custom-card">
            <h2>🖼️ 분석할 이미지</h2>
        </div>
    """, unsafe_allow_html=True)
    st.image(image, width=800)

    # ⭐ 3. '분석 시작' 버튼과 AI 분석 로직
    if st.button("🚀 AI 영양 분석 시작", type="primary"):
        
        model = load_model()
        if model is None:
             # API 키 로드 오류 시 중단
             return

        with st.spinner("🤖 AI가 이미지를 분석 중입니다..."):
            
            food_clarification = ""
            if user_food_name:
                food_clarification = f"사용자가 입력한 음식 이름은 **'{user_food_name}'**입니다. AI는 이 정보를 최우선으로 고려하여 분석해야 합니다."
            
            # 개선된 AI 프롬프트
            prompt = f"""
            당신은 한국 음식 영양분석에 전문적인 헬스 트레이너이자 영양 코치입니다.
            음식 사진을 보고 영양 성분을 1인분 기준으로 추정하세요.
            
            {food_clarification}
            
            **[중요]**
            1. 사진에 보이는 음식의 종류(예: 밥, 닭가슴살, 김치)와 양(예: 밥 200g, 닭가슴살 100g)을 최대한 구체적으로 고려하여 분석을 수행해야 합니다.
            2. 음식의 일반적인 레시피를 바탕으로 현실적이고 정량적인 수치만 추정하세요.
            3. 추정된 영양소 값이 비현실적(예: 탄수화물 0g, 단백질 1000g)이지 않도록 주의하세요.

            반드시 아래 형식을 그대로 유지하고 한국어로 작성하세요.
            (모든 수치는 단위 포함 : kcal, g, mg)

            🍽 음식 이름:  
            🔥 영양정보 (1인분 기준)
            - 열량(kcal):  
            - 탄수화물(g):  
            - 단백질(g):  
            - 지방(g):  
            - 당류(g):
            - 나트륨(mg):

            💡 운동 후 섭취 시 장점:  
            ⚠️ 주의사항:

            출력은 위 형식 그대로, 문장과 숫자만 포함된 깔끔한 텍스트로 작성하세요.
            """
            
            ex = model.generate_content([
                    prompt, 
                    image
                ])
            finish = ex.text.strip()

            # 4. 결과 출력
            st.markdown("""
                <div class="custom-card">
                    <h2>🤖 AI 분석 결과</h2>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="custom-card" style="background-color: var(--card-bg); padding: 1rem;">
                    {finish}
                </div>
            """, unsafe_allow_html=True)

            # 영양소 값 추출
            kcal = extract_number(finish, "열량")
            carbo = extract_number(finish, "탄수화물")
            protein = extract_number(finish, "단백질")
            fat = extract_number(finish, "지방")
            sugar = extract_number(finish, "당류")
            sodium = extract_number(finish, "나트륨")

            # 영양소 카드 표시
            st.markdown("""
                <div class="custom-card">
                    <h2>📊 영양소 분석</h2>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;">
            """, unsafe_allow_html=True)

            cols = st.columns(3)
            
            nutrient_data = [
                {"name": "열량", "value": kcal, "unit": "kcal", "icon": "🔥", "color": "primary"},
                {"name": "탄수화물", "value": carbo, "unit": "g", "icon": "🌾", "color": "secondary"},
                {"name": "단백질", "value": protein, "unit": "g", "icon": "🥩", "color": "accent"},
                {"name": "지방", "value": fat, "unit": "g", "icon": "🥑", "color": "primary"},
                {"name": "당류", "value": sugar, "unit": "g", "icon": "🍯", "color": "secondary"},
                {"name": "나트륨", "value": sodium, "unit": "mg", "icon": "🧂", "color": "accent"}
            ]

            for i, nutrient in enumerate(nutrient_data):
                with cols[i % 3]:
                    st.markdown(f"""
                        <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px; border: 1px solid var(--border-color); text-align: center;">
                            <h3 style="color: var(--{nutrient['color']}-color); margin: 0;">{nutrient['icon']} {nutrient['name']}</h3>
                            <p style="font-size: 1.5rem; margin: 0.5rem 0;">{nutrient['value']} {nutrient['unit']}</p>
                        </div>
                    """, unsafe_allow_html=True)

            # Gradient Boosting Model을 사용한 칼로리 보정
            if all(v is not None for v in [carbo, protein, fat, sugar, sodium]):
                new_data = pd.DataFrame([[carbo, protein, fat, sugar, sodium]], 
                                        columns=["탄수화물(g)", "단백질(g)", "지방(g)", "당류(g)", "나트륨(mg)"])
                corrected_kcal = regressor.predict(new_data)[0]
                st.success(f"🎯 예상 칼로리 kcal: **{corrected_kcal:.2f} kcal**")
            else:
                st.warning("⚠️ 일부 영양성분이 누락되어 kcal 보정이 불가능합니다.")

            # 피드백 출력
            st.markdown("### 💪 운동 후 섭취 시 장점")
            st.write(extract_section(finish, "💡 운동 후 섭취 시 장점", "⚠️ 주의사항"))

            st.markdown("### ⚠️ 주의사항")
            st.write(extract_section(finish, "⚠️ 주의사항"))