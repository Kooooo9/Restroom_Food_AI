import streamlit as st


# --- 0. 결과 초기화 함수 (Input 변경 시 호출) ---
def clear_results():
    """BMI 계산 결과를 세션 상태에서 지웁니다."""
    # 사용자의 요청에 따라 계산 결과만 초기화합니다.
    st.session_state.bmi_result = None
    st.session_state.status_message = ""
    st.session_state.recommended_weight = ""
    # 입력 정보(키, 몸무게, 나이)는 유지됩니다.


# --- 1. 세션 상태 초기화 함수 (가장 먼저, 외부로 분리) ---
def initialize_state():
    """st.session_state 변수들을 초기화합니다."""
    if 'user_height' not in st.session_state:
        st.session_state.user_height = 160
    if 'user_weight' not in st.session_state:
        st.session_state.user_weight = 60
    if 'user_age' not in st.session_state:
        st.session_state.user_age = 25
    
    if 'bmi_result' not in st.session_state:
        st.session_state.bmi_result = None
    if 'status_message' not in st.session_state:
        st.session_state.status_message = ""
    if 'recommended_weight' not in st.session_state:
        st.session_state.recommended_weight = ""
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'user_info'


# --- 2. 외부에서 값만 가져오는 함수 ---
def get_user_data():
    """
    외부에서 사용자 입력 값을 가져오는 함수
    
    Returns:
        dict: {
            'height': 키(cm),
            'weight': 몸무게(kg),
            'age': 나이,
            'bmi': BMI 계산 결과 (계산 전이면 None)
        }
    """
    # 세션 상태 초기화 확인
    initialize_state()
    
    return {
        'height': st.session_state.user_height,
        'weight': st.session_state.user_weight,
        'age': st.session_state.user_age,
        'bmi': st.session_state.bmi_result
    }


# --- 결과 초기화 함수 ---
def clear_results():
    """BMI 계산 결과를 세션 상태에서 지웁니다."""
    st.session_state.bmi_result = None
    st.session_state.status_message = ""
    st.session_state.recommended_weight = ""

# --- 1-1. 나이대별 BMI 기준 반환 함수 ---
def get_bmi_criteria(age):
    """
    나이에 따른 BMI 기준을 반환합니다.
    
    Returns:
        dict: {
            'age_group': 연령대 설명,
            'underweight': 저체중 상한값,
            'normal_min': 정상 하한값,
            'normal_max': 정상 상한값,
            'overweight_max': 과체중 상한값,
            'description': 기준 설명
        }
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


# --- 2. BMI 계산 및 상태 업데이트 함수 (버튼 클릭 시 실행) ---
def calculate_bmi():
    """
    세션 상태에 저장된 값을 바탕으로 BMI를 계산하고, 
    유효성 검사를 수행하며 결과를 세션 상태에 저장합니다.
    """
    h = st.session_state.user_height
    w = st.session_state.user_weight
    a = st.session_state.user_age


    # 유효성 검사: 입력값이 None이거나 0 이하인 경우
    if not h or h <= 0 or h < 140 or h > 250:
        st.error("키(140cm ~ 250cm)를 올바르게 입력해주세요.")
        # 오류 발생 시 결과 초기화
        clear_results()
        return


    if not w or w <= 0 or w < 40 or w > 200:
        st.error("몸무게(40kg ~ 200kg)를 올바르게 입력해주세요.")
        # 오류 발생 시 결과 초기화
        clear_results()
        return


    if not a or a < 1 or a > 100:
        st.error("나이(1세 ~ 100세)를 올바르게 입력해주세요.")
        # 오류 발생 시 결과 초기화
        clear_results()
        return


    # 2. BMI 계산: BMI = 체중(kg) / (키(m))^2
    height_m = h / 100.0 # 계산을 위해 실수형 변환
    bmi = w / (height_m ** 2)
    st.session_state.bmi_result = bmi

    # 2-1. 나이대별 BMI 기준 가져오기
    criteria = get_bmi_criteria(a)

    # 3. BMI 상태 분류 (나이대별 기준 적용)
    if bmi < criteria['underweight']:
        status = "저체중입니다."
        status_category = "저체중"
    elif bmi < criteria['normal_max']:
        status = "정상 체중입니다."
        status_category = "정상"
    elif bmi <= criteria['overweight_max']:
        status = "과체중입니다."
        status_category = "과체중"
    else:
        status = "비만입니다."
        status_category = "비만"


    # 4. 적정 체중 범위 계산 (나이대별 정상 BMI 기준)
    ideal_weight_min = criteria['normal_min'] * (height_m ** 2)
    ideal_weight_max = criteria['normal_max'] * (height_m ** 2)


    # 5. 결과 메시지 생성
    
    # st.info에 들어갈 메시지 형식
    status_msg = f"현재 사용자의 BMI는 {bmi:.2f}이며, {status}"
    
    # st.write에 들어갈 메시지 형식
    recommended_msg = f"""
    **{a}세 ({criteria['age_group']})** 사용자님의 적정 체중 정보:
    
    - 키: **{h:.0f}cm**
    - 정상 BMI 범위: **{criteria['normal_min']} ~ {criteria['normal_max']}**
    - 적정 체중 범위: **{ideal_weight_min:.1f}kg ~ {ideal_weight_max:.1f}kg**
    """
    
    st.session_state.status_message = status_msg
    st.session_state.recommended_weight = recommended_msg


# --- 3. Streamlit UI 구성 ---


def run_user_info():
    # 상태 초기화 함수 호출
    

    # 페이지 재진입 감지: 다른 페이지에서 돌아온 경우 결과 초기화
    if st.session_state.current_page != 'user_info':
        clear_results()
        st.session_state.current_page = 'user_info'
    st.markdown("---")
    st.subheader('사용자의 정보를 입력 받아 BMI를 계산 해드립니다.')
    
    # 입력 필드를 가로로 배열 (3개 컬럼)
    col1, col2, col3 = st.columns(3)
    
    # IMPORTANT: Add on_change=clear_results to inputs
    with col1:
        st.number_input(
            '키(cm)', 
            min_value=140, # 정수형 최소값
            max_value=250, # 정수형 최대값
            value=st.session_state.user_height,
            step=1,        # 1 단위로 입력 (정수형 의도)
            key='user_height',
            on_change=clear_results # 값이 변경될 때마다 결과 초기화
        )
    
    with col2:
        st.number_input(
            '몸무게(kg)', 
            min_value=40,  # 정수형 최소값
            max_value=200, # 정수형 최대값
            value=st.session_state.user_weight,
            step=1,        # 1 단위로 입력 (정수형 의도)
            key='user_weight',
            on_change=clear_results # 값이 변경될 때마다 결과 초기화
        )
    
    with col3:
        st.number_input(
            '나이', 
            min_value=1, 
            max_value=100, 
            value=st.session_state.user_age,
            key='user_age',
            on_change=clear_results # 값이 변경될 때마다 결과 초기화
        )


    # 버튼: on_click을 사용하여 calculate_bmi 함수 연결
    st.button('BMI 계산 및 결과 확인', on_click=calculate_bmi)
    
    st.markdown("---")


    # 결과 출력
    if st.session_state.bmi_result is not None:
        # BMI 계산 결과 출력: st.info 사용
        st.info(f"BMI 계산 결과: {st.session_state.status_message}", icon="💡")
        
        st.markdown("---")


        # 적정 체중 정보 출력
        st.write("### 적정 체중 정보")
        st.markdown(st.session_state.recommended_weight)