from app_eda import run_eda
from app_pref import run_pref
from app_img import run_img
from app_ml import run_ml
import streamlit as st


def main():
    
    st.title('맛춤식')

    menu = ['Home', 'Pref', 'EDA', 'ML', 'Image']
    choice = st.sidebar.selectbox('메뉴', menu)

    if choice == 'Home':
        st.write("이 앱은 식단 데이터를 분석하고 AI로 추천합니다.")
    elif choice == 'Pref':
        run_pref()
    elif choice == 'EDA':
        run_eda()
    elif choice == 'ML':
        run_ml()
    elif choice == 'Image':
        run_img()

if __name__ == '__main__':
    main()

