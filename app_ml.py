import streamlit as st

<<<<<<< Updated upstream:app.py
def main():
=======

def run_ml():
>>>>>>> Stashed changes:app_ml.py
    st.subheader('AI 식단 생성')
    
    st.number_input('목표 칼로리 (kcal)', 1000, 6000, 2500, step=50)

    st.slider('탄수화물 (%)', 10, 80, 50)
    st.slider('단백질 (%)', 10, 50, 30)
    st.slider('지방 (%)', 10, 50, 20)


<<<<<<< Updated upstream:app.py




if __name__ == '__main__':
    main()
=======
>>>>>>> Stashed changes:app_ml.py
