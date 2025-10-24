import streamlit as st

from app_eda import run_eda
# from app_home import run_home
# from app_ml import run_ml

def main():
    st.title('맛춤식')

    menu = ['Home', 'EDA', 'ML']
    choice = st.sidebar.selectbox('메뉴', menu)

    if choice == menu[0] :
        pass
    elif choice == menu[1] :
        run_eda()
    elif choice == menu[2] :
        pass
