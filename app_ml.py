import streamlit as st
import os
import google.generativeai as genai

# Gemini API 설정
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # 실제 API 키로 교체 필요
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def get_ai_diet_recommendation(bmi: float, preferences: list, avoid_foods: list) -> str:
    """AI를 통한 맞춤형 식단 추천"""
    
    # BMI 카테고리 결정
    bmi_category = "저체중" if bmi < 18.5 else "정상" if bmi < 25 else "과체중" if bmi < 30 else "비만"
    
    prompt = f"""
    다음 조건에 맞는 하루 식단을 추천해주세요:
    
    - BMI: {bmi:.1f} ({bmi_category})
    - 선호하는 음식: {', '.join(preferences) if preferences else '없음'}
    - 피해야 할 음식: {', '.join(avoid_foods) if avoid_foods else '없음'}
    
    다음 형식으로 자세히 응답해주세요:
    
    ### 🌅 아침
    - 추천 식단:
    - 예상 칼로리:
    - 추천 이유:
    
    ### 🌞 점심
    - 추천 식단:
    - 예상 칼로리:
    - 추천 이유:
    
    ### 🌙 저녁
    - 추천 식단:
    - 예상 칼로리:
    - 추천 이유:
    
    ### 💡 전체적인 식단 구성 이유:
    
    ### ⚠️ 주의사항:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"식단 생성 중 오류가 발생했습니다: {str(e)}"

def run_ml():
    st.set_page_config(page_title="AI 맞춤 식단 생성기", layout="wide")
    
    # 헤더
    st.title('🍽️ AI 맞춤 식단 생성기')
    st.markdown('### 당신의 BMI와 식품 선호도에 맞는 맞춤형 식단을 추천해드립니다.')
    
    # 사용자 정보 입력
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 BMI 정보")
        bmi = st.number_input(
            "BMI 수치를 입력해주세요",
            min_value=10.0,
            max_value=50.0,
            value=22.0,
            step=0.1,
            help="BMI = 체중(kg) / (신장(m))²"
        )
        
        # BMI 상태 표시
        bmi_status = "저체중" if bmi < 18.5 else "정상" if bmi < 25 else "과체중" if bmi < 30 else "비만"
        status_color = {
            "저체중": "blue",
            "정상": "green",
            "과체중": "orange",
            "비만": "red"
        }
        st.markdown(f"**BMI 상태:** {bmi_status}")
        st.progress(min(bmi/40, 1.0))  # BMI 시각화
        
        # BMI 설명
        st.info("""
        💡 **BMI 범위 안내**
        - 저체중: 18.5 미만
        - 정상: 18.5 ~ 24.9
        - 과체중: 25 ~ 29.9
        - 비만: 30 이상
        """)
    
    with col2:
        st.markdown("### 🍳 식단 선호도")
        preferences = st.text_area(
            "선호하는 음식을 입력해주세요 (쉼표로 구분)",
            placeholder="예: 연어, 닭가슴살, 브로콜리",
            help="좋아하는 음식이나 자주 먹고 싶은 음식을 입력하세요."
        )
        
        avoid_foods = st.text_area(
            "피해야 할 음식을 입력해주세요 (쉼표로 구분)",
            placeholder="예: 땅콩, 우유, 새우",
            help="알레르기가 있거나 건강상 피해야 하는 음식을 입력하세요."
        )
        
        # 입력값 처리
        pref_list = [food.strip() for food in preferences.split(',') if food.strip()]
        avoid_list = [food.strip() for food in avoid_foods.split(',') if food.strip()]
    
    # 구분선
    st.divider()
    
    # 식단 생성 버튼
    if st.button("🤖 AI 맞춤 식단 생성하기", type="primary"):
        with st.spinner("AI가 맞춤형 식단을 생성하고 있습니다..."):
            recommendation = get_ai_diet_recommendation(bmi, pref_list, avoid_list)
            
            # 결과 표시
            st.markdown(recommendation)
            
            # 주의사항
            st.info("""
            💡 **참고사항**
            - 이 식단은 참고용이며, 실제 섭취 시에는 개인의 건강 상태를 고려해주세요.
            - 특별한 건강 상태나 질환이 있다면 반드시 의사와 상담 후 섭취하세요.
            - 식단은 매일 다양하게 구성하는 것이 좋습니다.
            """)

if __name__ == "__main__":
    run_ml()