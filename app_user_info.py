import streamlit as st


# ============================================================================
# 1. 초기화 함수
# ============================================================================

def initialize_state():
    """
    앱이 처음 실행될 때 필요한 변수들을 준비합니다.
    이미 값이 있으면 건드리지 않고, 없을 때만 기본값을 설정합니다.
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
    ideal_weight_min = criteria['normal_min'] * (height_m ** 2)
    ideal_weight_max = criteria['normal_max'] * (height_m ** 2)
    
    # --- 6단계: 결과 메시지 만들기 ---
    # 상태 메시지
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
    
    # 출력 카드와 유사한 디자인을 위해 number_input의 스타일을 변경합니다.
    custom_css = """
    <style>
    /* 1. 입력 필드 컨테이너 스타일 (배경, 테두리, 둥근 모서리) */
    /* stNumberInput 위젯의 베이스 입력 영역 타겟팅 */
    div[data-testid*="stNumberInput"] > div[data-baseweb="base-input"] {
        background: var(--card-bg); 
        border-radius: 8px;
        border: 1px solid var(--border-color);
        padding: 0.5rem 0.5rem; /* 내부 패딩 조절 */
    }

    /* 2. 실제 숫자 입력 요소 폰트 크기 및 정렬 */
    div[data-testid*="stNumberInput"] input {
        font-size: 1.5rem !important; /* 출력 값 폰트 크기(1.5rem)와 통일 */
        text-align: center; /* 텍스트 중앙 정렬 */
        margin: 0.5rem 0; /* 상하 여백 추가 */
        padding: 0 !important; /* 내부 패딩 제거 (컨테이너에서 처리) */
    }

    /* 3. 라벨 (키, 몸무게, 나이) 스타일: 출력 카드의 제목(h3)과 유사하게 */
    div[data-testid*="stNumberInput"] > label {
        text-align: center; /* 라벨 중앙 정렬 */
        padding-bottom: 0.5rem; /* 아래쪽 여백 추가 */
    }
    div[data-testid*="stNumberInput"] label p {
        color: var(--primary-color) !important; /* 라벨 색상 변경 (예: primary-color) */
        font-size: 1rem !important; /* 라벨 폰트 크기 */
        font-weight: bold;
        margin: 0 !important;
    }
    
    /* 4. 스크롤 버튼 영역 배경색 (선택 사항) */
    div[data-baseweb="base-input"] > div:nth-child(2) {
        background: var(--card-bg);
    }
    </style>
    """

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
    
    st.markdown(custom_css, unsafe_allow_html=True)
    # --- 입력 필드 (가로로 3개 배치) ---
    col1, col2, col3 = st.columns(3)

    with col1:
        # 키 입력 필드 (label_visibility="hidden" 적용)
        height = st.number_input(
            '키(cm)', 
            min_value=140,
            max_value=250,
            step=1,
            value=st.session_state.user_height,
            help="키는 140cm ~ 250cm 사이로 입력해주세요",
            label_visibility="visible" # CSS로 라벨을 재정의하기 위해 visible 유지
        )
        # 값이 변경되면 session_state 업데이트
        if height != st.session_state.user_height:
            st.session_state.user_height = height
            clear_results()
    
    with col2:
        # 몸무게 입력 필드 (label_visibility="hidden" 적용)
        weight = st.number_input(
            '몸무게(kg)', 
            min_value=40,
            max_value=200,
            step=1,
            value=st.session_state.user_weight,
            label_visibility="visible"
        )
        if weight != st.session_state.user_weight:
            st.session_state.user_weight = weight
            clear_results()
    
    with col3:
        # 나이 입력 필드 (label_visibility="hidden" 적용)
        age = st.number_input(
            '나이', 
            min_value=1,
            max_value=100,
            step=1,
            value=st.session_state.user_age,
            label_visibility="visible"
        )
        if age != st.session_state.user_age:
            st.session_state.user_age = age
            clear_results()
    
    # --- BMI 계산 버튼 ---
    st.button('BMI 계산 및 결과 확인', on_click=calculate_bmi, use_container_width=True)
    
    # --- 결과 표시 ---
    if st.session_state.bmi_result is not None:
        # BMI 결과 출력
        st.markdown("""
            <div class="custom-card">
                <h2 style="color: var(--primary-color);">BMI 계산 결과</h2>
            </div>
        """, unsafe_allow_html=True)
        
        col3, col4 = st.columns(2)
        with col3:
            st.markdown(f"""
            <div class="custom-card" style="height: 240px;">
                <div style="text-align: center;">
                    <h3 style="color: var(--accent-color); margin-bottom: 1rem;">📊 BMI 수치</h3>
                    <div style="font-size: 1.5rem; font-weight: bold; margin: 1rem 0;">{st.session_state.bmi_result:.1f}</div>
                    <div style="color: var(--text-color);">{st.session_state.status_message}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="custom-card" style="height: 100%;">
                <div style="text-align: center;">
                    <h3 style="color: var(--secondary-color); margin-bottom: 1rem;">⚖️ 적정 체중 정보</h3>
                    <div style="text-align: left;">{st.session_state.recommended_weight}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
