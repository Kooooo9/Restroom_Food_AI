from app_eda import run_eda
from app_pref import run_pref
from app_img import run_img
from app_ml import run_ml
import streamlit as st

from app_user_info import run_user_info


def main():
    
    st.title('맛춤식')

    menu = ['Home', '사용자 정보', 'Pref', 'EDA', 'ML', 'Image']
    choice = st.sidebar.selectbox('메뉴', menu)

    if choice == menu[0]:
        st.write("이 앱은 식단 데이터를 분석하고 AI로 추천합니다.")
    elif choice == menu[1]:
        run_user_info()
    elif choice == menu[2]:
        run_pref()
    elif choice == menu[3]:
        run_eda()
    elif choice == menu[4]:
        run_ml()
    elif choice == menu[5]:
        run_img()

if __name__ == '__main__':
    main()

