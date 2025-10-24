import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from PIL import Image

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key="AIzaSyA6kFiZlrVEeq4fPwf1kw7NeHCGKYtBNYM")
model = genai.GenerativeModel("gemini-2.5-flash")

def main():
    df = pd.read_csv("./data/20250408_음식DB.csv")
    st.title("이미지 분석")
    file = st.file_uploader("사진을 업로드하세요.", type=['jpg','jpeg','png'])
    finish = ""

    if file is not None:
        image = Image.open(file)
        st.image(file)

        with st.spinner("AI가 이미지를 분석 중입니다..."):
            ex = model.generate_content([
                "업로드한 사진 속의 음식 이름을 알려줘."
                "가능한 구체적으로 한국어로 답해줘", image
            ])
            finish = ex.text.strip()

    st.write(finish)

if __name__ == "__main__":
    main()