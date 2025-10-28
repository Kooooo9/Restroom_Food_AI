import streamlit as st
from app_pref import run_pref
from app_eda import run_eda
from app_ml import run_ml
from app_img import run_img

def main():
    st.title("맛춤식 - AI 맞춤형 식단 관리 앱")

    menu = [
        "홈",
        "내 맛 선호도 입력",
        "음식 영양 정보 보기",
        "맞춤 식단 설정",
        "AI 음식 분석기"
    ]
    choice = st.sidebar.selectbox("메뉴를 선택하세요", menu)

    if "홈" in choice:
        st.write("이 앱은 사용자의 맛 선호도와 AI 분석을 기반으로 맞춤 식단을 추천합니다.")
    elif "맛 선호도" in choice:
        run_pref()
    elif "영양 정보" in choice:
        run_eda()
    elif "식단 설정" in choice:
        run_ml()
    elif "분석기" in choice:
        run_img()

if __name__ == "__main__":
    main()
