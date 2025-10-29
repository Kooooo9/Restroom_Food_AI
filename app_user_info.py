import streamlit as st


# ============================================================================
# 1. 초기화 함수
# ============================================================================

def initialize_state():
    """
    앱이 처음 실행될 때 필요한 변수들을 준비합니다.
    이미 값이 있으면 건드리지 않고, 없을 때만 기본값을 설정합니다.
    
    예시:
    - 처음 실행: user_height = 160 (기본값)
    - 사용자가 170으로 변경
    - 페이지 이동 후 복귀: user_height = 170 (유지됨)
    
    중요: number_input의 key와 연결된 값은 여기서 초기화해야 합니다!
    """
    # 사용자 입력값 (없을 때만 기본값 설정)
    if 'user_height' not in st.session_state:
        st.session_state.user_height = 160
    
    if 'user_weight' not in st.session_state:
        st.session_state.user_weight = 60
    
    if 'user_age' not in st.session_state:
        st.session_state.user_age = 25
    
    # BMI 계산 결과 (없을 때만 초기화)
    if 'bmi_result' not in st.session_state:
        st.session_state.bmi_result = None
    
    if 'status_message' not in st.session_state:
        st.session_state.status_message = ""
    
    if 'recommended_weight' not in st.session_state:
        st.session_state.recommended_weight = ""
    
    # 현재 어느 페이지인지 추적
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'user_info'


def clear_results():
    """
    BMI 계산 결과만 지웁니다.
    사용자가 입력한 키, 몸무게, 나이는 그대로 유지됩니다.
    
    언제 사용되나요?
    - 사용자가 키/몸무게/나이를 변경했을 때
    - 다른 페이지에서 돌아왔을 때
    """
    st.session_state.bmi_result = None
    st.session_state.status_message = ""
    st.session_state.recommended_weight = ""


# ============================================================================
# 2. 데이터 가져오기 함수
# ============================================================================

def get_user_data():
    """
    현재 저장된 사용자 데이터를 가져옵니다.
    다른 파일이나 함수에서 사용자 정보가 필요할 때 사용합니다.
    
    사용 예시:
        data = get_user_data()
        if data['height'] is not None:
            print(f"키: {data['height']}cm, 몸무게: {data['weight']}kg")
    
    Returns:
        dict: 사용자의 키, 몸무게, 나이, BMI 결과. 초기화되지 않은 경우 None 반환
    """
    try:
        # 세션 상태가 초기화되어 있는지 확인
        if not all(key in st.session_state for key in ['user_height', 'user_weight', 'user_age', 'bmi_result']):
            # 세션 상태가 초기화되지 않은 경우
            initialize_state()
            return {
                'height': None,
                'weight': None,
                'age': None,
                'bmi': None
            }
        
        # 세션 상태가 초기화된 경우
        return {
            'height': st.session_state.user_height,
            'weight': st.session_state.user_weight,
            'age': st.session_state.user_age,
            'bmi': st.session_state.bmi_result
        }
    except Exception:
        # 예기치 않은 오류 발생 시
        return {
            'height': None,
            'weight': None,
            'age': None,
            'bmi': None
        }


# ============================================================================
# 3. BMI 기준표
# ============================================================================

def get_bmi_criteria(age):
    """
    나이에 따라 다른 BMI 기준을 알려줍니다.
    
    왜 나이별로 다른가요?
    - 나이가 많을수록 건강한 BMI 범위가 약간 높아집니다
    - 노년층은 약간의 체중이 건강에 더 유리할 수 있습니다
    
    Args:
        age (int): 사용자의 나이
    
    Returns:
        dict: BMI 기준 정보
            - age_group: 연령대
            - underweight: 저체중 기준
            - normal_min: 정상 체중 최소값
            - normal_max: 정상 체중 최대값
            - overweight_max: 과체중 최대값
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
    사용자가 입력한 정보로 BMI를 계산합니다.
    'BMI 계산 및 결과 확인' 버튼을 누르면 이 함수가 실행됩니다.
    
    계산 순서:
    1. 입력값이 올바른지 확인 (유효성 검사)
    2. BMI 계산 (공식: 체중 ÷ 키² )
    3. 나이에 맞는 BMI 기준 가져오기
    4. 저체중/정상/과체중/비만 판단
    5. 적정 체중 범위 계산
    6. 결과를 session_state에 저장
    """
    # 사용자가 입력한 값 가져오기
    height = st.session_state.user_height
    weight = st.session_state.user_weight
    age = st.session_state.user_age
    
    # --- 1단계: 입력값 검사 ---
    # 키가 너무 작거나 크면 에러
    if not height or height < 140 or height > 250:
        st.error("키는 140cm ~ 250cm 사이로 입력해주세요.")
        clear_results()
        return
    
    # 몸무게가 너무 작거나 크면 에러
    if not weight or weight < 40 or weight > 200:
        st.error("몸무게는 40kg ~ 200kg 사이로 입력해주세요.")
        clear_results()
        return
    
    # 나이가 범위를 벗어나면 에러
    if not age or age < 1 or age > 100:
        st.error("나이는 1세 ~ 100세 사이로 입력해주세요.")
        clear_results()
        return
    
    # --- 2단계: BMI 계산 ---
    # BMI 공식: 체중(kg) ÷ (키(m))²
    # 예: 70kg, 170cm → 70 ÷ (1.7)² = 24.22
    height_m = height / 100.0  # cm를 m로 변환 (170cm → 1.7m)
    bmi = weight / (height_m ** 2)  # ** 2는 제곱을 의미
    
    # 계산된 BMI 저장
    st.session_state.bmi_result = bmi
    
    # --- 3단계: 나이에 맞는 BMI 기준 가져오기 ---
    criteria = get_bmi_criteria(age)
    
    # --- 4단계: BMI로 상태 판단하기 ---
    if bmi < criteria['underweight']:
        status = "저체중입니다."
    elif bmi < criteria['normal_max']:
        status = "정상 체중입니다."
    elif bmi <= criteria['overweight_max']:
        status = "과체중입니다."
    else:
        status = "비만입니다."
    
    # --- 5단계: 적정 체중 범위 계산 ---
    # 정상 BMI 범위로 역계산
    # 예: BMI 18.5~22.9, 키 170cm → 53.5~66.2kg
    ideal_weight_min = criteria['normal_min'] * (height_m ** 2)
    ideal_weight_max = criteria['normal_max'] * (height_m ** 2)
    
    # --- 6단계: 결과 메시지 만들기 ---
    # 상태 메시지 (예: "현재 사용자의 BMI는 24.22이며, 과체중입니다.")
    status_msg = f"현재 사용자의 BMI는 {bmi:.2f}이며, {status}"
    
    # 적정 체중 정보 메시지
    recommended_msg = f"""

    - 키: **{height:.0f}cm**
    - 정상 BMI 범위: **{criteria['normal_min']} ~ {criteria['normal_max']}**
    - 적정 체중 범위: **{ideal_weight_min:.1f}kg ~ {ideal_weight_max:.1f}kg**
    """
    
    # 결과를 session_state에 저장 (화면에 표시하기 위해)
    st.session_state.status_message = status_msg
    st.session_state.recommended_weight = recommended_msg


# ============================================================================
# 5. 화면 구성 (메인 UI)
# ============================================================================

def run_user_info():
    """
    BMI 계산기 화면을 만듭니다.
    이 함수를 호출하면 전체 화면이 나타납니다.
    """
    # 앱 시작 시 필요한 변수들 준비 (없으면 생성, 있으면 유지)
    initialize_state()
    
    # 다른 페이지에서 돌아왔을 때만 결과 초기화
    if st.session_state.current_page != 'user_info':
        clear_results()
        st.session_state.current_page = 'user_info'
    
    # --- 화면 제목 ---
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: var(--primary-color);">BMI 계산기</h1>
            <p style="color: var(--text-color); font-size: 1.2rem;">
                사용자의 정보를 입력받아 BMI를 계산하여 식단을 추천하는 데 활용됩니다.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- 입력 섹션 ---
    st.markdown("""
        <div class="custom-card">
            <h2>👤 사용자 정보 입력</h2>
            <p>키, 몸무게, 나이를 입력해주세요.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- 입력 필드 (가로로 3개 배치) ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 키 입력 필드
        # on_change로 직접 session_state 업데이트
        height = st.number_input(
            '키(cm)', 
            min_value=140,
            max_value=250,
            step=1,
            value=st.session_state.user_height,
            help="키는 140cm ~ 250cm 사이로 입력해주세요"
        )
        # 값이 변경되면 session_state 업데이트
        if height != st.session_state.user_height:
            st.session_state.user_height = height
            clear_results()
    
    with col2:
        # 몸무게 입력 필드
        weight = st.number_input(
            '몸무게(kg)', 
            min_value=40,
            max_value=200,
            step=1,
            value=st.session_state.user_weight
        )
        if weight != st.session_state.user_weight:
            st.session_state.user_weight = weight
            clear_results()
    
    with col3:
        # 나이 입력 필드
        age = st.number_input(
            '나이', 
            min_value=1,
            max_value=100,
            step=1,
            value=st.session_state.user_age
        )
        if age != st.session_state.user_age:
            st.session_state.user_age = age
            clear_results()
    
    # --- BMI 계산 버튼 ---
    # 버튼을 누르면 calculate_bmi() 함수가 실행됨
    st.button('BMI 계산 및 결과 확인', on_click=calculate_bmi, use_container_width=True)
    
    # --- 결과 표시 ---
    # BMI가 계산되었을 때만 결과를 보여줌
    if st.session_state.bmi_result is not None:
        # BMI 결과 출력
        st.markdown("""
            <div class="custom-card">
                <h2 style="color: var(--primary-color);">BMI 계산 결과</h2>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="custom-card" style="height: 240px;">
                <div style="text-align: center;">
                    <h3 style="color: var(--accent-color); margin-bottom: 1rem;">📊 BMI 수치</h3>
                    <div style="font-size: 1.5rem; font-weight: bold; margin: 1rem 0;">{st.session_state.bmi_result:.1f}</div>
                    <div style="color: var(--text-color);">{st.session_state.status_message}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="custom-card" style="height: 100%;">
                <div style="text-align: center;">
                    <h3 style="color: var(--secondary-color); margin-bottom: 1rem;">⚖️ 적정 체중 정보</h3>
                    <div style="text-align: left;">{st.session_state.recommended_weight}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)