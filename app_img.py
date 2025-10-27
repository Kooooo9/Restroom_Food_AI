import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from PIL import Image


api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = st.secrets["API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

def run_img():
    st.title("AI 음식 분석기")
    st.caption("AI가 음식 이미지를 분석해 영양정보를 예측해줍니다.")
    file = st.file_uploader("사진을 업로드하세요", type=['jpg', 'jpeg', 'png'])

    if file is not None:
        image = Image.open(file)
        st.image(image, caption="AI가 분석할 이미지")

        with st.spinner("🤖 AI가 이미지를 분석 중입니다..."):
            ex = model.generate_content([
                """
                당신은 헬스 트레이너이자 영양 코치입니다.
                음식 사진을 보고 아래 형식으로 한국어로 분석하세요.

                🍽 음식 이름:  
                🔥 영양정보 (1인분 기준)
                - 열량(kcal):  
                - 탄수화물(g):  
                - 단백질(g):  
                - 지방(g):  
                💡 운동 후 섭취 시 장점:  
                ⚠️ 주의사항:

                출력은 줄마다 구분된 명확한 텍스트로 작성하세요.
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

        data = pd.DataFrame({
            "영양성분": ["열량(kcal)", "탄수화물(g)", "단백질(g)", "지방(g)"],
            "예상값": [kcal, carbo, protein, fat]
        })
        st.markdown("### 📊 영양정보 요약")
        st.dataframe(data, use_container_width=True)

        st.markdown("### 💪 운동 후 섭취 시 장점")
        st.write(extract_section(finish, "💡 운동 후 섭취 시 장점", "⚠️ 주의사항"))

        st.markdown("### ⚠️ 주의사항")
        st.write(extract_section(finish, "⚠️ 주의사항"))

    else:
        st.info("음식 사진을 업로드해주세요.")

import re

def extract_number(text, keyword):
    pattern = rf"{keyword}.*?(\d+)"
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None

def extract_section(text, start, end_marker=None):
    start_idx = text.find(start)
    if start_idx == -1:
        return
    if end_marker:
        end_idx = text.find(end_marker, start_idx)
        section = text[start_idx + len(start):end_idx].strip()
    else:
        section = text[start_idx + len(start):].strip()
    return section if section else ""
