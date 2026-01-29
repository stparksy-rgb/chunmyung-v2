"""
천명 VIP - 프리미엄 사주 분석 시스템
통합 버전 v2.1 - UI 개선 + 음력 표시 + 나이 맞춤 통변

만세력 자동 계산 + AI 심층 통변 + 후속 질문
Copyright 2026 JEMINA AI
"""

import streamlit as st
from datetime import datetime, date
import anthropic
from manseryuk_engine import (
    calculate_saju, format_saju_display,
    CHEONGAN_OHAENG, OHAENG_KR, OHAENG,
    CHEONGAN_HANJA, JIJI_HANJA, JIJI_ANIMAL
)

# =====================================================
# 페이지 설정
# =====================================================
st.set_page_config(
    page_title="천명 VIP - 프리미엄 사주 분석",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# VIP 시스템 프롬프트 (나이 맞춤 통변 추가)
# =====================================================
SYSTEM_PROMPT = """당신은 대한민국 상위 1%의 고객만을 상대하는 심층 사주 명리학 전문가 '천명 VIP'입니다.

### [핵심 행동 지침]

1. **단답형 금지**: "재물운이 좋습니다" 같은 짧은 답변 금지. 논리적 근거와 함께 5~6문장 이상 상세히 서술.

2. **구조화된 답변**: 체계적으로 목차를 나누어 작성 (해당될 경우)
   - 타고난 기질/격국/용신 분석
   - 현재 대운/세운 분석  
   - 분야별 운세 (직업/재물/건강/인간관계)
   - 개운법 및 조언

3. **전문 용어 + 쉬운 풀이**: 격국, 용신, 충합 등 전문 용어 사용 후 반드시 쉽게 풀어 설명

4. **따뜻한 상담가 태도**: 정중하고 진지하며, 부정적 해석도 희망적 대안과 함께 제시

5. **현재 시점 기반**: 오늘 날짜를 기준으로 대운/세운 분석. 상반기면 올해 중심, 하반기면 내년 중심.

### [나이별 맞춤 통변 - 매우 중요!]

**의뢰인의 나이에 맞는 현실적인 조언을 제공하십시오:**

- **20대**: 진로, 취업, 연애, 자기계발 중심
- **30대**: 결혼, 출산, 커리어 성장, 재테크 시작 중심
- **40대**: 자녀 교육, 사업/승진, 건강 관리, 노후 준비 중심
- **50대**: 은퇴 준비, 자녀 독립, 부부 관계, 건강, 제2의 인생 중심
- **60대 이상**: 건강 관리, 손자녀, 여가 생활, 인생 정리 중심

**특히 주의사항:**
- 40대 이상이면 "연애운"이 아닌 "부부운" 또는 "가정운"으로 표현
- 이미 결혼했을 가능성이 높은 나이대에는 새로운 이성을 만난다는 표현 자제
- 의뢰인이 직접 "미혼입니다" 또는 "이혼했습니다"라고 밝힌 경우에만 연애운 언급
- 나이에 맞지 않는 비현실적인 조언 금지

### [용신 판단 원칙]
- 신강 사주: 설기(洩氣), 극(剋)하는 오행이 용신
- 신약 사주: 생(生), 부(扶)하는 오행이 용신
- 단순 공식이 아닌, 실제 오행 분포와 십신 구조 기반 판단

### [말투]
- 존칭 사용 (합쇼체)
- 따뜻하고 격려하는 어조
- "~하십시오", "~됩니다" 등 정중한 표현

### [생년월일 표기]
- 의뢰인이 음력으로 입력한 경우, 반드시 "음력 ○년 ○월 ○일생"으로 표기
- 양력으로 입력한 경우, "양력 ○년 ○월 ○일생"으로 표기
- 입력 방식을 정확히 확인하고 표기할 것

이제 사용자의 사주 정보와 질문에 VIP 프리미엄 수준으로 답변하십시오."""


# =====================================================
# 커스텀 CSS (글자색 개선)
# =====================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* 전체 텍스트 색상 밝게 */
    .stApp, .stApp p, .stApp span, .stApp div {
        color: #ffffff !important;
    }
    
    .main-title {
        text-align: center;
        color: #ffd700 !important;
        font-size: 2.5rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 10px;
    }
    
    .sub-title {
        text-align: center;
        color: #e0e0e0 !important;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    
    .saju-card {
        background: linear-gradient(145deg, #2d2d44, #1e1e2f);
        border: 2px solid #ffd700;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        margin: 5px;
    }
    
    /* 채팅 메시지 스타일 개선 */
    .chat-message {
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        color: #ffffff !important;
    }
    
    .user-message {
        background: rgba(255, 215, 0, 0.15);
        border-left: 4px solid #ffd700;
        color: #ffffff !important;
    }
    
    .assistant-message {
        background: rgba(255, 255, 255, 0.1);
        border-left: 4px solid #4CAF50;
        color: #ffffff !important;
    }
    
    /* AI 응답 텍스트 스타일 */
    .ai-response {
        color: #ffffff !important;
        font-size: 1.05rem;
        line-height: 1.8;
    }
    
    .ai-response h1, .ai-response h2, .ai-response h3 {
        color: #ffd700 !important;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    
    .ai-response strong, .ai-response b {
        color: #ffd700 !important;
    }
    
    .ai-response li {
        margin-bottom: 8px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #ffd700, #ffaa00);
        color: #000;
        font-weight: bold;
        border: none;
        border-radius: 30px;
    }
    
    .analysis-type-btn {
        margin: 5px;
    }
    
    /* 마크다운 텍스트 색상 */
    .stMarkdown {
        color: #ffffff !important;
    }
    
    .stMarkdown p {
        color: #ffffff !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #ffd700 !important;
    }
    
    /* 메트릭 스타일 */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #cccccc !important;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 세션 상태 초기화
# =====================================================
if 'saju' not in st.session_state:
    st.session_state.saju = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'saju_calculated' not in st.session_state:
    st.session_state.saju_calculated = False
if 'is_lunar' not in st.session_state:
    st.session_state.is_lunar = False
if 'birth_year' not in st.session_state:
    st.session_state.birth_year = 1985

# =====================================================
# Claude API 호출 함수
# =====================================================
def call_claude_api(messages, saju_context):
    """Claude API 호출"""
    try:
        # API 키 확인
        api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
        if not api_key:
            return "⚠️ API 키가 설정되지 않았습니다. Streamlit Cloud의 Secrets에 ANTHROPIC_API_KEY를 설정해주세요."
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # 사주 컨텍스트를 시스템 프롬프트에 추가
        full_system = SYSTEM_PROMPT + f"\n\n### [현재 분석 중인 사주]\n{saju_context}\n\n오늘 날짜: {datetime.now().strftime('%Y년 %m월 %d일')}"
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=full_system,
            messages=messages
        )
        
        return response.content[0].text
        
    except anthropic.APIError as e:
        return f"⚠️ API 오류: {str(e)}"
    except Exception as e:
        return f"⚠️ 오류 발생: {str(e)}"


def generate_saju_context(saju, is_lunar, birth_year):
    """사주 데이터를 컨텍스트 문자열로 변환 (음력/양력 구분 + 나이 포함)"""
    
    # 나이 계산
    current_year = datetime.now().year
    age = current_year - birth_year + 1  # 한국 나이
    
    # 음력/양력 표시
    if is_lunar:
        date_type = "음력"
        birth_date_display = saju['lunar_date']
    else:
        date_type = "양력"
        birth_date_display = saju['solar_date']
    
    context = f"""
【의뢰인 정보】
- 생년월일: {date_type} {birth_date_display} {saju['birth_time']}
- 나이: 만 {current_year - birth_year}세 (한국 나이 {age}세)
- 성별: {saju['gender']}
- 띠: {saju['animal']}띠
- 입력 방식: {date_type}

【사주팔자】
        시주    일주    월주    연주
천간:    {saju['hour_pillar'][0]}      {saju['day_pillar'][0]}      {saju['month_pillar'][0]}      {saju['year_pillar'][0]}
지지:    {saju['hour_pillar'][1]}      {saju['day_pillar'][1]}      {saju['month_pillar'][1]}      {saju['year_pillar'][1]}
한글:    {saju['hour_pillar_kr']}    {saju['day_pillar_kr']}    {saju['month_pillar_kr']}    {saju['year_pillar_kr']}

【일간】{saju['day_gan_kr']} / 오행: {CHEONGAN_OHAENG[saju['day_gan']]}

【오행 분포】
木: {saju['ohaeng_count']['木']} | 火: {saju['ohaeng_count']['火']} | 土: {saju['ohaeng_count']['土']} | 金: {saju['ohaeng_count']['金']} | 水: {saju['ohaeng_count']['水']}

【십신】
- 연주: {saju['sipsin'][0]['gan']}({saju['sipsin'][0]['gan_sipsin']}), {saju['sipsin'][0]['ji']}({saju['sipsin'][0]['ji_sipsin']})
- 월주: {saju['sipsin'][1]['gan']}({saju['sipsin'][1]['gan_sipsin']}), {saju['sipsin'][1]['ji']}({saju['sipsin'][1]['ji_sipsin']})
- 일주: {saju['sipsin'][2]['gan']}({saju['sipsin'][2]['gan_sipsin']}), {saju['sipsin'][2]['ji']}({saju['sipsin'][2]['ji_sipsin']})
- 시주: {saju['sipsin'][3]['gan']}({saju['sipsin'][3]['gan_sipsin']}), {saju['sipsin'][3]['ji']}({saju['sipsin'][3]['ji_sipsin']})

【대운】
{' → '.join([f"{d['pillar_kr']}({d['age']}세~)" for d in saju['daeun']])}

【분석 시 참고사항】
- 의뢰인의 나이({age}세)에 맞는 현실적인 조언을 제공할 것
- {date_type} 기준으로 생년월일을 표기할 것
"""
    return context


# =====================================================
# 헤더
# =====================================================
st.markdown('<h1 class="main-title">🔮 천명 VIP</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">대한민국 상위 1% 프리미엄 사주 분석 서비스</p>', unsafe_allow_html=True)

# =====================================================
# 사이드바 - 입력 폼
# =====================================================
with st.sidebar:
    st.markdown("### 📝 생년월일시 입력")
    
    calendar_type = st.radio("달력 유형", ["양력", "음력"], horizontal=True)
    is_lunar = (calendar_type == "음력")
    
    is_leap = False
    if is_lunar:
        is_leap = st.checkbox("윤달")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        birth_year = st.number_input("년", min_value=1900, max_value=2100, value=1985)
    with col2:
        birth_month = st.number_input("월", min_value=1, max_value=12, value=1)
    with col3:
        birth_day = st.number_input("일", min_value=1, max_value=31, value=1)
    
    col4, col5 = st.columns(2)
    with col4:
        birth_hour = st.number_input("시", min_value=0, max_value=23, value=12)
    with col5:
        birth_minute = st.number_input("분", min_value=0, max_value=59, value=0)
    
    gender = st.radio("성별", ["남", "여"], horizontal=True)
    time_unknown = st.checkbox("태어난 시간을 모릅니다")
    
    st.markdown("---")
    
    if st.button("🔮 사주 계산", use_container_width=True):
        if time_unknown:
            birth_hour = 12
            birth_minute = 0
        
        try:
            saju = calculate_saju(
                birth_year, birth_month, birth_day,
                birth_hour, birth_minute,
                is_lunar=is_lunar, is_leap=is_leap,
                gender=gender
            )
            st.session_state.saju = saju
            st.session_state.saju_calculated = True
            st.session_state.is_lunar = is_lunar
            st.session_state.birth_year = birth_year
            st.session_state.messages = []  # 새 사주면 대화 초기화
            st.success("✅ 계산 완료!")
        except Exception as e:
            st.error(f"오류: {str(e)}")
    
    # 대화 초기화 버튼
    if st.session_state.saju_calculated:
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.8rem;'>
    ⓒ 2026 JEMINA AI<br>
    천명 VIP v2.1
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# 메인 컨텐츠
# =====================================================
if st.session_state.saju_calculated and st.session_state.saju:
    saju = st.session_state.saju
    is_lunar = st.session_state.is_lunar
    birth_year = st.session_state.birth_year
    
    # 나이 계산
    current_year = datetime.now().year
    korean_age = current_year - birth_year + 1
    
    # -------------------------------------------------
    # 사주 요약 표시 (상단 고정)
    # -------------------------------------------------
    st.markdown("### 📜 사주팔자")
    
    # 음력/양력 구분 표시
    date_type = "음력" if is_lunar else "양력"
    display_date = saju['lunar_date'] if is_lunar else saju['solar_date']
    
    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
    with col_info1:
        st.metric("생년월일", f"{date_type} {display_date}")
    with col_info2:
        st.metric("양력 변환", saju['solar_date'])
    with col_info3:
        st.metric("나이", f"{korean_age}세")
    with col_info4:
        st.metric("띠", f"{saju['animal']}띠")
    
    # 사주 카드
    def get_ohaeng_color(char):
        if char in ['甲', '乙', '寅', '卯']:
            return '#4CAF50'
        elif char in ['丙', '丁', '巳', '午']:
            return '#f44336'
        elif char in ['戊', '己', '辰', '未', '戌', '丑']:
            return '#FFC107'
        elif char in ['庚', '辛', '申', '酉']:
            return '#E0E0E0'
        elif char in ['壬', '癸', '亥', '子']:
            return '#2196F3'
        return '#fff'
    
    cols = st.columns(4)
    pillars = [
        ('시주', saju['hour_pillar'], saju['hour_pillar_kr']),
        ('일주 ⭐', saju['day_pillar'], saju['day_pillar_kr']),
        ('월주', saju['month_pillar'], saju['month_pillar_kr']),
        ('연주', saju['year_pillar'], saju['year_pillar_kr']),
    ]
    
    for i, (name, pillar, pillar_kr) in enumerate(pillars):
        with cols[i]:
            gan_color = get_ohaeng_color(pillar[0])
            ji_color = get_ohaeng_color(pillar[1])
            border = "3px solid #ffd700" if "⭐" in name else "1px solid #444"
            
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.05); border: {border}; border-radius: 15px; padding: 15px; text-align: center;'>
                <div style='color: #ffd700; font-size: 0.9rem;'>{name}</div>
                <div style='color: {gan_color}; font-size: 2.5rem; font-weight: bold;'>{pillar[0]}</div>
                <div style='color: {ji_color}; font-size: 2.5rem; font-weight: bold;'>{pillar[1]}</div>
                <div style='color: #cccccc; font-size: 0.9rem;'>{pillar_kr}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 일간 & 오행
    st.markdown(f"""
    <div style='margin-top: 15px; color: #ffffff;'>
    <strong style='color: #ffd700;'>일간(나):</strong> {saju['day_gan_kr']} ({CHEONGAN_OHAENG[saju['day_gan']]}) | 
    <strong style='color: #ffd700;'>오행분포:</strong> 木 {saju['ohaeng_count']['木']} | 火 {saju['ohaeng_count']['火']} | 土 {saju['ohaeng_count']['土']} | 金 {saju['ohaeng_count']['金']} | 水 {saju['ohaeng_count']['水']}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # -------------------------------------------------
    # AI 통변 섹션
    # -------------------------------------------------
    st.markdown("### 🤖 AI 심층 통변")
    
    # 빠른 분석 버튼들 (나이에 따라 다르게)
    st.markdown("**빠른 분석:**")
    quick_cols = st.columns(6)
    
    # 40대 이상이면 "연애운" 대신 "가정운"
    if korean_age >= 40:
        relationship_label = "👨‍👩‍👧 가정운"
        relationship_question = "이 사주의 가정운과 부부운을 분석해주세요. 배우자와의 관계, 자녀운, 가정의 화목을 알려주세요."
    else:
        relationship_label = "❤️ 연애운"
        relationship_question = "이 사주의 연애운과 결혼운을 분석해주세요. 어떤 배우자가 맞고, 올해 연애운은 어떤가요?"
    
    quick_questions = [
        ("🎯 종합운세", "이 사주의 종합운세를 분석해주세요. 타고난 기질, 격국, 용신, 현재 대운, 올해 세운까지 포함해서 상세히 알려주세요."),
        ("💼 직업운", "이 사주의 직업운과 적성을 분석해주세요. 어떤 분야가 맞고, 올해 직업운은 어떤가요?"),
        ("💰 재물운", "이 사주의 재물운을 분석해주세요. 돈 버는 방식과 올해 재물운을 알려주세요."),
        (relationship_label, relationship_question),
        ("🏥 건강운", "이 사주의 건강운을 분석해주세요. 주의할 장기와 건강 관리법을 알려주세요."),
        ("🍀 개운법", "이 사주에 맞는 개운법을 알려주세요. 용신 기반으로 색상, 방향, 음식, 생활습관 등 구체적으로요."),
    ]
    
    for i, (label, question) in enumerate(quick_questions):
        with quick_cols[i]:
            if st.button(label, key=f"quick_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()
    
    st.markdown("---")
    
    # -------------------------------------------------
    # 채팅 히스토리 표시
    # -------------------------------------------------
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong style='color: #ffd700;'>🙋 질문:</strong><br>
                    <span style='color: #ffffff;'>{msg["content"]}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong style='color: #4CAF50;'>🔮 천명 VIP:</strong>
                </div>
                """, unsafe_allow_html=True)
                # AI 응답은 마크다운으로 렌더링
                st.markdown(f"<div class='ai-response'>{msg['content']}</div>", unsafe_allow_html=True)
    
    # -------------------------------------------------
    # 새 메시지가 있고 아직 응답 안 받은 경우 API 호출
    # -------------------------------------------------
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.spinner("🔮 천명 VIP가 사주를 분석하고 있습니다..."):
            saju_context = generate_saju_context(saju, is_lunar, birth_year)
            
            # API용 메시지 형식 변환
            api_messages = [
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages
            ]
            
            response = call_claude_api(api_messages, saju_context)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # -------------------------------------------------
    # 사용자 입력
    # -------------------------------------------------
    st.markdown("---")
    user_input = st.chat_input("궁금한 점을 물어보세요... (예: 올해 이직해도 될까요?)")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()
    
    # 예시 질문
    with st.expander("💡 이런 것도 물어볼 수 있어요"):
        st.markdown("""
        - 올해 상반기와 하반기 중 언제가 더 좋을까요?
        - 사업 확장 시기는 언제가 좋을까요?
        - 투자를 하려는데 올해 재물운이 어떤가요?
        - 제 사주의 용신과 기신은 무엇인가요?
        - 이직을 고려 중인데 적합한 시기가 언제일까요?
        - 건강상 특별히 주의해야 할 부분이 있나요?
        - 부모님/자녀와의 관계운은 어떤가요?
        - 내년 운세는 어떤가요?
        - 제 사주에서 가장 강한 장점은 무엇인가요?
        """)

# =====================================================
# 초기 화면 (사주 계산 전)
# =====================================================
else:
    st.markdown("""
    <div style='
        text-align: center;
        padding: 50px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        margin: 20px 0;
    '>
        <div style='font-size: 4rem;'>🔮</div>
        <h2 style='color: #ffd700; margin: 20px 0;'>프리미엄 사주 분석을 시작하세요</h2>
        <p style='color: #cccccc;'>
            왼쪽 사이드바에서 생년월일시를 입력하고<br>
            '사주 계산' 버튼을 클릭하세요.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 서비스 특징
    st.markdown("### 🌟 천명 VIP v2.1 새로운 기능")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; height: 180px;'>
            <h4 style='color: #ffd700;'>📐 정밀 만세력</h4>
            <p style='color: #cccccc;'>
            절기 기준 정확한 사주팔자 계산.
            음력/양력 자동 변환!
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; height: 180px;'>
            <h4 style='color: #ffd700;'>🤖 나이 맞춤 통변</h4>
            <p style='color: #cccccc;'>
            20대~60대 나이별 현실적 조언.
            비현실적인 통변 NO!
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; height: 180px;'>
            <h4 style='color: #ffd700;'>💬 무제한 질문</h4>
            <p style='color: #cccccc;'>
            궁금한 거 뭐든 물어보세요!
            채팅으로 후속 질문 무제한
            </p>
        </div>
        """, unsafe_allow_html=True)
