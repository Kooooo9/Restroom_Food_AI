import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from PIL import Image

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key="AIzaSyA6kFiZlrVEeq4fPwf1kw7NeHCGKYtBNYM")
model = genai.GenerativeModel("gemini-2.5-flash")

def main():
    st.title("AI 음식 분석")
    st.caption("이미지 기반 음식 이름 + 영양 성분 추정 시스템")
    file = st.file_uploader("사진을 업로드하세요.", type=['jpg','jpeg','png'])
    finish = ""

    if file is not None:
        image = Image.open(file)
        st.image(file, caption="AI가 분석할 이미지", width=500)

        with st.spinner("AI가 이미지를 분석 중입니다..."):   
            ex = model.generate_content([
                """
                당신은 음식 전문가입니다.
                이 음식 사진을 보고 다음을 한국어로 자세히 알려주세요:
                1. 음식 이름
                2. 대표 재료 3~5가지
                3. 예상되는 열량(kcal)과 주요 영양성분(탄수화물, 단백질, 지방) 수치 추정
                4. 간단한 맛 설명 한 줄
                """, image
                ])
            finish = ex.text.strip()

            st.write(finish)
    else:
        st.info("이미지를 업로드하면 AI가 자동으로 분석해줍니다.")


if __name__ == "__main__":
    main()