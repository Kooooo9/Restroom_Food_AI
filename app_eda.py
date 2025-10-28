import streamlit as st

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb

def run_eda():
    df = pd.read_csv('./food1.csv')

    # 음식별 영양정보 탐색 
    st.markdown("---")
    st.subheader("음식별 탄단지 정보")

    choice = st.selectbox("음식을 선택하세요", df["식품명"].unique())
    info = df[df["식품명"] == choice].iloc[0]

    st.markdown(f"""
    ### {choice}의 영양정보  
    - **칼로리:** {int(info['에너지(kcal)'])} kcal  
    - **탄수화물:** {float(info['탄수화물(g)'])} g  
    - **단백질:** {float(info['단백질(g)'])} g  
    - **지방:** {float(info['지방(g)'])} g  
    """)



