import streamlit as st

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb

def run_eda():
    df = pd.read_excel('./data/20250408_음식DB.xlsx')

    st.text('이 데이터는 음식DB.xlsx 데이터입니다.')

    radio_menu = ['데이터프레임', '성분별 통계']
    radio_choice = st.radio('선택하세요', radio_menu)
    if radio_choice == radio_menu[0] :
        st.dataframe(df)
    elif radio_choice == radio_menu[1] :
        st.dataframe(df.describe())

        st.subheader('최대 / 최소값 확인')

        min_max_menu = df.columns[ 1 :  ]
        select_choice = st.selectbox('컬럼을 선택하세요', min_max_menu)

        print(select_choice)
    
        st.info(f'{select_choice}는 {(df[select_choice].min())} 부터 {(df[select_choice].max())} 까지 있습니다.')

