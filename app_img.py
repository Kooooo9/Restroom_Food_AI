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
    st.title("AI 음식 분석기")
    st.caption("AI가 음식 이미지를 분석해 영양정보를 예측해줍니다.")

    try:
        regressor = train_regression_model()
    except Exception as e:
        st.error(f"food1.csv 불러오기 실패: {e}")
        return
    
    file = st.file_uploader("사진을 업로드하세요", type=['jpg', 'jpeg', 'png'])
    if not file:
        st.info("이미지를 업로드하면 AI가 분석을 시작합니다.")
        return
        
    image = Image.open(file)
    st.image(image, caption="AI가 분석할 이미지")

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

        st.subheader("AI 분석 결과")
        st.markdown(f"> {finish}")

        kcal = extract_number(finish, "열량")
        carbo = extract_number(finish, "탄수화물")
        protein = extract_number(finish, "단백질")
        fat = extract_number(finish, "지방")
        sugar = extract_number(finish, "당류")
        sodium = extract_number(finish, "나트륨")

        data = pd.DataFrame({
            "영양성분": ["열량(kcal)", "탄수화물(g)", "단백질(g)", "지방(g)", "당류(g)", "나트륨(mg)"],
            "예상값": [kcal, carbo, protein, fat, sugar, sodium]})
        
        st.markdown("### 📊 영양정보 요약")
        st.dataframe(data, width='stretch')

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
