import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from PIL import Image
from sklearn.linear_model import LinearRegression

def load_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = st.secrets["API"]["API_KEY"]
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")

import re

def extract_number(text, keyword):
    pattern = rf"{keyword}.*?(\d+)"
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None

def extract_section(text, start, end_marker=None):
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
    df = pd.read_csv("./food1.csv")
    X = df[["탄수화물(g)", "단백질(g)", "지방(g)", "당류(g)", "나트륨(mg)"]]
    y = df["에너지(kcal)"]
    model = LinearRegression().fit(X,y)
    return model

def run_img():
    # 페이지 헤더
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: var(--primary-color);">AI 음식 영양 분석기</h1>
            <p style="color: var(--text-color); font-size: 1.2rem;">
                음식 사진을 업로드하면 AI가 자동으로 영양 정보를 분석해드립니다
            </p>
        </div>
    """, unsafe_allow_html=True)

    try:
        regressor = train_regression_model()
    except Exception as e:
        st.markdown("""
            <div class="custom-card" style="text-align: center;">
                <h3 style="color: var(--accent-color);">⚠️ 데이터 로드 오류</h3>
                <p>영양 정보 데이터베이스를 불러오는데 실패했습니다.</p>
            </div>
        """, unsafe_allow_html=True)
        return
    
    # 파일 업로드 섹션
    st.markdown("""
        <div class="custom-card">
            <h2>📸 음식 사진 업로드</h2>
            <p>분석하고 싶은 음식의 사진을 업로드해주세요.</p>
        </div>
    """, unsafe_allow_html=True)
    
    file = st.file_uploader("", type=['jpg', 'jpeg', 'png'])
    
    if not file:
        st.markdown("""
            <div class="custom-card" style="text-align: center;">
                <h3 style="color: var(--primary-color);">👆 사진을 업로드해주세요</h3>
                <p>지원 형식: JPG, JPEG, PNG</p>
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
    st.image(image, use_column_width=True)

    model = load_model()
    with st.spinner("🤖 AI가 이미지를 분석 중입니다..."):
        ex = model.generate_content([
                """
                당신은 한국 음식 영양분석에 전문적인 헬스 트레이너이자 영양 코치입니다.
                음식 사진을 보고 영양 성분을 1인분 기준으로 추정하세요.

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
                """,
                image
            ])
        finish = ex.text.strip()

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

        if all(v is not None for v in [carbo, protein, fat, sugar, sodium]):
            new_data = pd.DataFrame([[carbo, protein, fat, sugar, sodium]], 
                                    columns=["탄수화물(g)", "단백질(g)", "지방(g)", "당류(g)", "나트륨(mg)"])
            corrected_kcal = regressor.predict(new_data)[0]
            st.success(f"🎯 보정된 예측 kcal: **{corrected_kcal:.2f} kcal**")
        else:
            st.warning("⚠️ 일부 영양성분이 누락되어 kcal 보정이 불가능합니다.")

        st.markdown("### 💪 운동 후 섭취 시 장점")
        st.write(extract_section(finish, "💡 운동 후 섭취 시 장점", "⚠️ 주의사항"))

        st.markdown("### ⚠️ 주의사항")
        st.write(extract_section(finish, "⚠️ 주의사항"))
