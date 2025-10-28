import streamlit as st


# ============================================================================
# 1. 초기화 함수들
# ============================================================================

def initialize_state():
    """
    앱 실행 시 session_state 변수들을 초기화합니다.
    session_state는 페이지를 새로고침해도 값이 유지되는 저장소입니다.
    """
    # 사용자 입력값 초기화 (처음 실행할 때만)
    if 'user_height' not in st.session_state:
        st.session_state.user_height = 160
    if 'user_weight' not in st.session_state:
        st.session_state.user_weight = 60
    if 'user_age' not in st.session_state:
        st.session_state.user_age = 25
    
    # BMI 계산 결과 초기화 (처음 실행할 때만)
    if 'bmi_result' not in st.session_state:
        st.session_state.bmi_result = None
    if 'status_message' not in st.session_state:
        st.session_state.status_message = ""
    if 'recommended_weight' not in st.session_state:
        st.session_state.recommended_weight = ""
    
    # 현재 페이지 추적용 변수
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'user_info'


def clear_results():
    """
    BMI 계산 결과만 초기화합니다.
    사용자가 입력한 키, 몸무게, 나이는 그대로 유지됩니다.
    """
    st.session_state.bmi_result = None
    st.session_state.status_message = ""
    st.session_state.recommended_weight = ""


# ============================================================================
# 2. 외부에서 데이터를 가져오는 함수
# ============================================================================

def get_user_data():
    """
    다른 파일이나 함수에서 사용자 데이터를 가져올 때 사용합니다.
    
    사용 예시:
        data = get_user_data()
        print(f"키: {data['height']}cm")
    
    Returns:
        dict: 사용자의 키, 몸무게, 나이, BMI 결과가 담긴 딕셔너리
    """
    # 먼저 초기화되었는지 확인
    initialize_state()
    
    # 딕셔너리로 반환 (외부에서 사용하기 편하게)
    return {
        'height': st.session_state.user_height,
        'weight': st.session_state.user_weight,
        'age': st.session_state.user_age,
        'bmi': st.session_state.bmi_result
    }


# ============================================================================
# 3. BMI 기준 관련 함수
# ============================================================================

def get_bmi_criteria(age):
    """
    나이에 따라 다른 BMI 기준을 반환합니다.
    나이가 많을수록 정상 BMI 범위가 약간 높아집니다.
    
    Args:
        age: 사용자의 나이
    
    Returns:
        dict: BMI 기준 정보 (연령대, 저체중/정상/과체중/비만 기준값)
    """
    if 20 <= age < 40:
        return {
            'age_group': '20~40대',
            'underweight': 18.5,
            'normal_min': 18.5,
            'normal_max': 22.9,
            'overweight_max': 24.9,
            'description': '일반적인 아시아 기준'
        }
    elif 40 <= age < 60:
        return {
            'age_group': '40~60대',
            'underweight': 18.5,
            'normal_min': 18.5,
            'normal_max': 23.4,
            'overweight_max': 25.4,
            'description': '중년 이후 약간 높은 BMI 권장'
        }
    elif age >= 60:
        return {
            'age_group': '60대 이상',
            'underweight': 18.5,
            'normal_min': 18.5,
            'normal_max': 24.9,
            'overweight_max': 27.4,
            'description': '노년층은 다소 비만 허용 범위 확대'
        }
    else:  # 20세 미만
        return {
            'age_group': '20세 미만',
            'underweight': 18.5,
            'normal_min': 18.5,
            'normal_max': 22.9,
            'overweight_max': 24.9,
            'description': '일반적인 아시아 기준 적용'
        }


# ============================================================================
# 4. BMI 계산 함수
# ============================================================================

def calculate_bmi():
    """
    사용자가 입력한 값으로 BMI를 계산합니다.
    버튼을 클릭하면 이 함수가 실행됩니다.
    
    계산 과정:
    1. 입력값 유효성 검사
    2. BMI 계산 (체중 / 키^2)
    3. 나이대별 BMI 기준으로 상태 판단
    4. 적정 체중 범위 계산
    5. 결과를 session_state에 저장
    """
    # session_state에서 값 가져오기
    height = st.session_state.user_height
    weight = st.session_state.user_weight
    age = st.session_state.user_age
    
    # --- 1단계: 입력값 유효성 검사 ---
    if not height or height < 140 or height > 250:
        st.error("키는 140cm ~ 250cm 사이로 입력해주세요.")
        clear_results()
        return
    
    if not weight or weight < 40 or weight > 200:
        st.error("몸무게는 40kg ~ 200kg 사이로 입력해주세요.")
        clear_results()
        return
    
    if not age or age < 1 or age > 100:
        st.error("나이는 1세 ~ 100세 사이로 입력해주세요.")
        clear_results()
        return
    
    # --- 2단계: BMI 계산 ---
    # BMI 공식: 체중(kg) ÷ (키(m))^2
    height_m = height / 100.0  # cm를 m로 변환
    bmi = weight / (height_m ** 2)
    
    # 결과를 session_state에 저장
    st.session_state.bmi_result = bmi
    
    # --- 3단계: 나이대별 BMI 기준 가져오기 ---
    criteria = get_bmi_criteria(age)
    
    # --- 4단계: BMI 상태 판단 ---
    if bmi < criteria['underweight']:
        status = "저체중입니다."
    elif bmi < criteria['normal_max']:
        status = "정상 체중입니다."
    elif bmi <= criteria['overweight_max']:
        status = "과체중입니다."
    else:
        status = "비만입니다."
    
    # --- 5단계: 적정 체중 범위 계산 ---
    ideal_weight_min = criteria['normal_min'] * (height_m ** 2)
    ideal_weight_max = criteria['normal_max'] * (height_m ** 2)
    
    # --- 6단계: 결과 메시지 생성 및 저장 ---
    # 상태 메시지
    status_msg = f"현재 사용자의 BMI는 {bmi:.2f}이며, {status}"
    
    # 적정 체중 정보 메시지
    recommended_msg = f"""
    **{age}세 ({criteria['age_group']})** 사용자님의 적정 체중 정보:
    
    - 키: **{height:.0f}cm**
    - 정상 BMI 범위: **{criteria['normal_min']} ~ {criteria['normal_max']}**
    - 적정 체중 범위: **{ideal_weight_min:.1f}kg ~ {ideal_weight_max:.1f}kg**
    """
    
    # session_state에 저장
    st.session_state.status_message = status_msg
    st.session_state.recommended_weight = recommended_msg


# ============================================================================
# 5. 화면 구성 함수 (메인 UI)
# ============================================================================

def run_user_info():
    """
    BMI 계산기의 메인 화면을 구성합니다.
    이 함수를 호출하면 화면이 표시됩니다.
    """
    # 앱 실행 시 초기화 (처음 한 번만)
    initialize_state()
    
    # 다른 페이지에서 돌아왔을 때 결과 초기화
    if st.session_state.current_page != 'user_info':
        clear_results()
        st.session_state.current_page = 'user_info'
    
    # --- 화면 제목 ---
    st.markdown("---")
    st.subheader('사용자의 정보를 입력 받아 BMI를 계산 해드립니다.')
    
    # --- 입력 필드 (3개를 가로로 배치) ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 키 입력 필드
        # 주의: value 대신 session_state 키만 사용 (경고 해결)
        st.number_input(
            '키(cm)', 
            min_value=140,
            max_value=250,
            step=1,
            key='user_height',  # session_state에 자동 저장
            on_change=clear_results  # 값이 변경되면 결과 초기화
        )
    
    with col2:
        # 몸무게 입력 필드
        st.number_input(
            '몸무게(kg)', 
            min_value=40,
            max_value=200,
            step=1,
            key='user_weight',  # session_state에 자동 저장
            on_change=clear_results  # 값이 변경되면 결과 초기화
        )
    
    with col3:
        # 나이 입력 필드
        st.number_input(
            '나이', 
            min_value=1,
            max_value=100,
            step=1,
            key='user_age',  # session_state에 자동 저장
            on_change=clear_results  # 값이 변경되면 결과 초기화
        )
    
    # --- BMI 계산 버튼 ---
    st.button('BMI 계산 및 결과 확인', on_click=calculate_bmi)
    
    st.markdown("---")
    
    # --- 결과 표시 (BMI가 계산된 경우에만) ---
    if st.session_state.bmi_result is not None:
        # BMI 결과 출력
        st.info(f"BMI 계산 결과: {st.session_state.status_message}", icon="💡")
        
        st.markdown("---")
        
        # 적정 체중 정보 출력
        st.write("### 적정 체중 정보")
        st.markdown(st.session_state.recommended_weight)