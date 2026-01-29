"""
천명 VIP - 프리미엄 사주 분석 시스템
통합 버전 v3.0 - 개인화 + 시점 반영 + PDF 저장

만세력 자동 계산 + AI 심층 통변 + 후속 질문 + PDF 다운로드
Copyright 2026 JEMINA AI
"""

import streamlit as st
from datetime import datetime, date
import anthropic
import io
import base64
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
# VIP 시스템 프롬프트 (v3.0 - 개인화 + 시점 반영)
# =====================================================
SYSTEM_PROMPT = """당신은 대한민국 상위 1%의 VIP 고객만을 위한 심층 명리 컨설턴트 **'천명 VIP'**입니다.

## 🎯 핵심 원칙

### 1. 개인화된 스토리텔링
- 매번 다른 비유와 표현 사용 (정해일주라도 "호수의 촛불", "밤바다의 등대", "겨울밤 벽난로" 등 다양하게)
- 의뢰인의 이름이 있으면 "○○○님 귀하"로 존칭
- 획일적인 템플릿 금지. 각 사주의 고유한 특성을 시적으로 표현

### 2. 현재 시점 중심 분석 (매우 중요!)
- **오늘 날짜를 반드시 확인**하고, 현재 월(月)을 기준으로 분석
- 1~3월이면 "올해 초입", 4~6월이면 "상반기 중반", 7~9월이면 "하반기 진입", 10~12월이면 "연말 마무리" 관점
- **남은 기간**에 집중: "앞으로 남은 ○개월 동안..."
- 이미 지난 달은 간략히, **앞으로 올 달은 상세히**

### 3. 월별 운세표 필수 포함 (종합운세 분석 시)
종합운세를 분석할 때는 반드시 아래 형식의 월별 표를 포함:

| 시기 | 운세 흐름 및 조언 |
|------|------------------|
| 1~3월 (봄) | [구체적 조언] |
| 4~6월 (여름) | [구체적 조언] |
| 7~9월 (가을) | [구체적 조언] |
| 10~12월 (겨울) | [구체적 조언] |

### 4. 한자 최소화, 쉬운 표현 우선
- ❌ "丁火 일간은 음화로서..."
- ✅ "정화(불꽃의 기운) 일간이신 귀하는..."
- 전문 용어는 반드시 괄호 안에 쉬운 설명 추가

### 5. VIP 톤앤매너
**오프닝 예시:**
"귀하의 사주 원국을 정밀하게 분석한 결과, [시적 비유]의 고귀한 성정이 돋보입니다. 현재 [년월] 시점에서, 귀하의 인생에 중요한 운의 변곡점에 서 계십니다."

**마무리 예시:**
- "강한 빛은 그림자를 만듭니다. 올해의 강한 기운을 지혜롭게 활용하십시오."
- "물은 낮은 곳으로 흐르듯, 겸손함이 귀하의 운을 열어줄 열쇠입니다."
- "천명 VIP는 귀하의 앞날에 늘 서광이 비치길 기원합니다."

### 6. 구체적이고 실천 가능한 개운법
- ❌ "동쪽이 길방입니다"
- ✅ "거주지나 사무실의 동쪽에 생기 있는 화분을 두시면 재물운이 살아납니다"
- ✅ "하루 20분 물소리를 들으며 명상하시면 심신의 균형에 도움이 됩니다"
- ✅ "청색 계열의 넥타이나 스카프가 귀하의 기운을 안정시켜줍니다"

### 7. 나이대별 현실적 조언
- **20대**: 취업, 진로, 연애, 자기계발
- **30대**: 결혼, 출산, 커리어 성장, 내 집 마련
- **40대**: 자녀 교육, 승진/사업, 건강 관리, 노후 준비 시작
- **50대**: 은퇴 준비, 제2의 인생, 부부관계, 건강이 최우선
- **60대 이상**: 건강 관리, 손자녀, 여가, 인생 정리

**40대 이상은 "연애운" 대신 "가정운/부부운"으로 표현** (미혼이라 밝힌 경우 제외)

### 8. 특별한 신살(神殺) 언급
천을귀인, 문창귀인, 역마살, 도화살 등 특별한 신살이 있으면 반드시 언급하고 그 의미를 설명

### 9. 분량 및 깊이
- 종합운세: 최소 2,000자 이상
- 개별 운세(직업운, 재물운 등): 최소 800자 이상
- 짧은 답변 금지. VIP 고객에게 성의없는 답변은 결례

### 10. 위험 신호 시 명확한 경고
- 충(沖), 형(刑), 파(破), 해(害) 등 흉한 기운이 있으면 구체적으로 경고
- 단, 희망적 대안과 함께 제시 (공포 조장 금지)

## 📋 응답 구조 (종합운세 분석 시)

1. **VIP 오프닝** - 시적 비유와 함께 인사
2. **타고난 기질 분석** - 일주의 특성, 성격, 재능
3. **현재 대운 분석** - 지금 어떤 흐름인지
4. **올해 세운 분석** - 현재 년도의 특징
5. **월별 운세표** - 4계절 또는 분기별
6. **분야별 운세** - 직업/재물/건강/가정
7. **VIP 개운 처방** - 구체적 실천법
8. **명언과 함께 마무리**

이제 의뢰인의 사주와 질문에 VIP 프리미엄 수준으로 답변하십시오."""


# =====================================================
# 커스텀 CSS - 전문 명리학 스타일
# =====================================================
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
    }
    
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background: #1e2329 !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #ffffff !important;
        background: rgba(255,255,255,0.1) !important;
        padding: 8px 15px !important;
        border-radius: 5px !important;
        margin: 2px !important;
    }
    
    [data-testid="stSidebar"] .stCheckbox label {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffd700 !important;
    }
    
    /* 메인 영역 텍스트 */
    .main .block-container {
        color: #e6edf3 !important;
    }
    
    .stMarkdown, .stMarkdown p, .stMarkdown span {
        color: #e6edf3 !important;
    }
    
    h1, h2, h3, h4 {
        color: #ffd700 !important;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #ffd700, #f0c000) !important;
        color: #000 !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #ffdd33, #ffd700) !important;
        transform: translateY(-1px);
    }
    
    /* 사주 카드 스타일 */
    .saju-card {
        background: linear-gradient(145deg, #21262d, #161b22);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        margin: 3px;
    }
    
    .saju-card-highlight {
        background: linear-gradient(145deg, #21262d, #161b22);
        border: 2px solid #ffd700;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        margin: 3px;
        box-shadow: 0 0 10px rgba(255,215,0,0.2);
    }
    
    /* 채팅 메시지 */
    .chat-user {
        background: rgba(255, 215, 0, 0.1);
        border-left: 3px solid #ffd700;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        color: #e6edf3 !important;
    }
    
    .chat-assistant {
        background: rgba(46, 160, 67, 0.1);
        border-left: 3px solid #2ea043;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        color: #e6edf3 !important;
    }
    
    .chat-assistant h1, .chat-assistant h2, .chat-assistant h3 {
        color: #ffd700 !important;
    }
    
    .chat-assistant strong {
        color: #ffd700 !important;
    }
    
    /* 메트릭 스타일 */
    [data-testid="stMetricValue"] {
        color: #e6edf3 !important;
        font-size: 1.1rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #8b949e !important;
    }
    
    /* 입력 필드 */
    .stNumberInput input, .stTextInput input {
        background: #21262d !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
    }
    
    /* 빠른 분석 버튼 */
    .quick-btn {
        background: linear-gradient(135deg, #238636, #2ea043) !important;
        color: white !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
        font-size: 0.85rem !important;
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
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# =====================================================
# Claude API 호출 함수
# =====================================================
def call_claude_api(messages, saju_context):
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
        if not api_key:
            return "⚠️ API 키가 설정되지 않았습니다. Streamlit Cloud의 Secrets에 ANTHROPIC_API_KEY를 설정해주세요."
        
        client = anthropic.Anthropic(api_key=api_key)
        full_system = SYSTEM_PROMPT + f"\n\n### [현재 분석 중인 사주]\n{saju_context}\n\n오늘 날짜: {datetime.now().strftime('%Y년 %m월 %d일')}"
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=full_system,
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        return f"⚠️ 오류 발생: {str(e)}"


def generate_saju_context(saju, is_lunar, birth_year, user_name=""):
    current_year = datetime.now().year
    age = current_year - birth_year + 1
    
    date_type = "음력" if is_lunar else "양력"
    birth_date_display = saju['lunar_date'] if is_lunar else saju['solar_date']
    
    # 이름 표시
    name_display = f"- 성함: {user_name}님\n" if user_name else ""
    
    context = f"""
【의뢰인 정보】
{name_display}- 생년월일: {date_type} {birth_date_display} {saju['birth_time']}
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

【참고】의뢰인 나이({age}세)에 맞는 현실적 조언, {date_type} 기준 표기"""
    return context


# =====================================================
# 사이드바
# =====================================================
with st.sidebar:
    st.markdown("## 📅 생년월일시 입력")
    st.markdown("---")
    
    # 이름 입력 (선택사항)
    st.markdown("**이름** (선택)")
    user_name = st.text_input("이름입력", placeholder="홍길동", label_visibility="collapsed")
    
    st.markdown("---")
    
    # 달력 유형
    st.markdown("**달력 유형**")
    calendar_type = st.radio("달력", ["양력", "음력"], horizontal=True, label_visibility="collapsed")
    is_lunar = (calendar_type == "음력")
    
    # 윤달
    is_leap = False
    if is_lunar:
        is_leap = st.checkbox("윤달 여부")
    
    st.markdown("---")
    
    # 생년월일
    st.markdown("**생년월일**")
    col1, col2, col3 = st.columns(3)
    with col1:
        birth_year = st.number_input("년", min_value=1900, max_value=2100, value=1985, label_visibility="collapsed")
        st.caption("년")
    with col2:
        birth_month = st.number_input("월", min_value=1, max_value=12, value=1, label_visibility="collapsed")
        st.caption("월")
    with col3:
        birth_day = st.number_input("일", min_value=1, max_value=31, value=1, label_visibility="collapsed")
        st.caption("일")
    
    # 생시
    st.markdown("**태어난 시간**")
    col4, col5 = st.columns(2)
    with col4:
        birth_hour = st.number_input("시", min_value=0, max_value=23, value=12, label_visibility="collapsed")
        st.caption("시")
    with col5:
        birth_minute = st.number_input("분", min_value=0, max_value=59, value=0, label_visibility="collapsed")
        st.caption("분")
    
    time_unknown = st.checkbox("⏰ 태어난 시간 모름")
    
    st.markdown("---")
    
    # 성별
    st.markdown("**성별**")
    gender = st.radio("성별선택", ["남", "여"], horizontal=True, label_visibility="collapsed")
    
    st.markdown("---")
    
    # 사주 계산 버튼
    if st.button("🔮 사주 계산", use_container_width=True, type="primary"):
        if time_unknown:
            birth_hour, birth_minute = 12, 0
        try:
            saju = calculate_saju(birth_year, birth_month, birth_day, birth_hour, birth_minute,
                                  is_lunar=is_lunar, is_leap=is_leap, gender=gender)
            st.session_state.saju = saju
            st.session_state.saju_calculated = True
            st.session_state.is_lunar = is_lunar
            st.session_state.birth_year = birth_year
            st.session_state.user_name = user_name if user_name else ""
            st.session_state.messages = []
            st.success("✅ 계산 완료!")
        except Exception as e:
            st.error(f"오류: {str(e)}")
    
    # 대화 초기화
    if st.session_state.saju_calculated:
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    st.markdown("---")
    st.caption("ⓒ 2026 JEMINA AI · 천명 VIP v3.0")


# =====================================================
# 메인 화면
# =====================================================

# 헤더
st.markdown("""
<div style='text-align: center; padding: 20px 0;'>
    <span style='font-size: 2.5rem;'>🔮</span>
    <h1 style='color: #ffd700; margin: 10px 0; font-size: 2rem;'>천명 VIP</h1>
    <p style='color: #8b949e; font-size: 0.95rem;'>대한민국 상위 1% 프리미엄 사주 분석 서비스</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# 사주 결과 표시
# =====================================================
if st.session_state.saju_calculated and st.session_state.saju:
    saju = st.session_state.saju
    is_lunar = st.session_state.is_lunar
    birth_year = st.session_state.birth_year
    current_year = datetime.now().year
    korean_age = current_year - birth_year + 1
    
    date_type = "음력" if is_lunar else "양력"
    display_date = saju['lunar_date'] if is_lunar else saju['solar_date']
    user_name = st.session_state.get('user_name', '')
    
    # 기본 정보
    st.markdown("### 📋 기본 정보")
    
    # 이름이 있으면 6열, 없으면 5열
    if user_name:
        info_cols = st.columns(6)
        with info_cols[0]:
            st.metric("성함", f"{user_name}님")
        with info_cols[1]:
            st.metric("입력", f"{date_type}")
        with info_cols[2]:
            st.metric("생년월일", display_date)
        with info_cols[3]:
            st.metric("양력 변환", saju['solar_date'])
        with info_cols[4]:
            st.metric("나이", f"{korean_age}세")
        with info_cols[5]:
            st.metric("띠", f"{saju['animal']}띠")
    else:
        info_cols = st.columns(5)
        with info_cols[0]:
            st.metric("입력", f"{date_type}")
        with info_cols[1]:
            st.metric("생년월일", display_date)
        with info_cols[2]:
            st.metric("양력 변환", saju['solar_date'])
        with info_cols[3]:
            st.metric("나이", f"{korean_age}세")
        with info_cols[4]:
            st.metric("띠", f"{saju['animal']}띠")
    
    # 📋 복사용 텍스트 생성
    copy_text = f"""【사주 분석 결과】
{'성함: ' + user_name + '님' if user_name else ''}
생년월일: {date_type} {display_date} ({saju['solar_date']} 양력)
나이: {korean_age}세 | 성별: {saju['gender']} | 띠: {saju['animal']}띠

【사주팔자】
시주: {saju['hour_pillar'][0]}{saju['hour_pillar'][1]} ({saju['hour_pillar_kr']})
일주: {saju['day_pillar'][0]}{saju['day_pillar'][1]} ({saju['day_pillar_kr']}) ⭐
월주: {saju['month_pillar'][0]}{saju['month_pillar'][1]} ({saju['month_pillar_kr']})
연주: {saju['year_pillar'][0]}{saju['year_pillar'][1]} ({saju['year_pillar_kr']})

【일간】{saju['day_gan_kr']} ({CHEONGAN_OHAENG[saju['day_gan']]})

【오행분포】
木: {saju['ohaeng_count']['木']} | 火: {saju['ohaeng_count']['火']} | 土: {saju['ohaeng_count']['土']} | 金: {saju['ohaeng_count']['金']} | 水: {saju['ohaeng_count']['水']}

【십신】
연주: {saju['sipsin'][0]['gan']}({saju['sipsin'][0]['gan_sipsin']}), {saju['sipsin'][0]['ji']}({saju['sipsin'][0]['ji_sipsin']})
월주: {saju['sipsin'][1]['gan']}({saju['sipsin'][1]['gan_sipsin']}), {saju['sipsin'][1]['ji']}({saju['sipsin'][1]['ji_sipsin']})
일주: {saju['sipsin'][2]['gan']}({saju['sipsin'][2]['gan_sipsin']}), {saju['sipsin'][2]['ji']}({saju['sipsin'][2]['ji_sipsin']})
시주: {saju['sipsin'][3]['gan']}({saju['sipsin'][3]['gan_sipsin']}), {saju['sipsin'][3]['ji']}({saju['sipsin'][3]['ji_sipsin']})

【대운】
{' → '.join([f"{d['pillar_kr']}({d['age']}세~)" for d in saju['daeun']])}
"""
    
    st.markdown("---")
    
    # 사주팔자
    st.markdown("### 🏛️ 사주팔자 (四柱八字)")
    
    def get_color(char):
        if char in ['甲', '乙', '寅', '卯']: return '#22c55e'  # 녹색 (목)
        elif char in ['丙', '丁', '巳', '午']: return '#ef4444'  # 빨강 (화)
        elif char in ['戊', '己', '辰', '未', '戌', '丑']: return '#eab308'  # 노랑 (토)
        elif char in ['庚', '辛', '申', '酉']: return '#e5e5e5'  # 흰색 (금)
        elif char in ['壬', '癸', '亥', '子']: return '#3b82f6'  # 파랑 (수)
        return '#e5e5e5'
    
    saju_cols = st.columns(4)
    pillars = [
        ('시주(時柱)', saju['hour_pillar'], saju['hour_pillar_kr'], False),
        ('일주(日柱)', saju['day_pillar'], saju['day_pillar_kr'], True),
        ('월주(月柱)', saju['month_pillar'], saju['month_pillar_kr'], False),
        ('연주(年柱)', saju['year_pillar'], saju['year_pillar_kr'], False),
    ]
    
    for i, (name, pillar, pillar_kr, is_main) in enumerate(pillars):
        with saju_cols[i]:
            border = "2px solid #ffd700" if is_main else "1px solid #30363d"
            shadow = "box-shadow: 0 0 15px rgba(255,215,0,0.3);" if is_main else ""
            badge = " ⭐" if is_main else ""
            
            st.markdown(f"""
            <div style='background: #21262d; border: {border}; border-radius: 10px; padding: 15px; text-align: center; {shadow}'>
                <div style='color: #8b949e; font-size: 0.8rem; margin-bottom: 8px;'>{name}{badge}</div>
                <div style='color: {get_color(pillar[0])}; font-size: 1.8rem; font-weight: bold;'>{pillar[0]}</div>
                <div style='color: {get_color(pillar[1])}; font-size: 1.8rem; font-weight: bold; margin-top: 5px;'>{pillar[1]}</div>
                <div style='color: #8b949e; font-size: 0.85rem; margin-top: 8px;'>{pillar_kr}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 일간 & 오행
    st.markdown(f"""
    <div style='margin-top: 15px; padding: 12px; background: #21262d; border-radius: 8px; border-left: 3px solid #ffd700;'>
        <span style='color: #ffd700; font-weight: bold;'>일간(나):</span> 
        <span style='color: #e6edf3;'>{saju['day_gan_kr']} ({CHEONGAN_OHAENG[saju['day_gan']]})</span>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <span style='color: #ffd700; font-weight: bold;'>오행분포:</span> 
        <span style='color: #22c55e;'>木 {saju['ohaeng_count']['木']}</span> · 
        <span style='color: #ef4444;'>火 {saju['ohaeng_count']['火']}</span> · 
        <span style='color: #eab308;'>土 {saju['ohaeng_count']['土']}</span> · 
        <span style='color: #e5e5e5;'>金 {saju['ohaeng_count']['金']}</span> · 
        <span style='color: #3b82f6;'>水 {saju['ohaeng_count']['水']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 📋 마스터용 복사 기능
    with st.expander("📋 사주 데이터 복사 (마스터용)", expanded=False):
        st.text_area("복사할 내용", copy_text, height=300, label_visibility="collapsed")
        st.caption("💡 위 텍스트를 전체 선택(Ctrl+A) 후 복사(Ctrl+C)하세요.")
    
    st.markdown("---")
    
    # AI 통변
    st.markdown("### 🤖 AI 심층 통변")
    
    # 빠른 분석 버튼
    if korean_age >= 40:
        rel_label, rel_q = "👨‍👩‍👧 가정운", "이 사주의 가정운과 부부운을 분석해주세요."
    else:
        rel_label, rel_q = "❤️ 연애운", "이 사주의 연애운과 결혼운을 분석해주세요."
    
    quick_btns = [
        ("🎯 종합운세", "이 사주의 종합운세를 분석해주세요. 타고난 기질, 격국, 용신, 현재 대운, 올해 세운까지 포함해서 상세히 알려주세요."),
        ("💼 직업운", "이 사주의 직업운과 적성을 분석해주세요."),
        ("💰 재물운", "이 사주의 재물운을 분석해주세요."),
        (rel_label, rel_q),
        ("🏥 건강운", "이 사주의 건강운을 분석해주세요."),
        ("🍀 개운법", "이 사주에 맞는 개운법을 알려주세요."),
    ]
    
    btn_cols = st.columns(6)
    for i, (label, question) in enumerate(quick_btns):
        with btn_cols[i]:
            if st.button(label, key=f"q_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()
    
    st.markdown("---")
    
    # 채팅 히스토리
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""<div class='chat-user'><strong style='color:#ffd700;'>🙋 질문:</strong> {msg["content"]}</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class='chat-assistant'><strong style='color:#2ea043;'>🔮 천명 VIP:</strong><br><br>{msg["content"]}</div>""", unsafe_allow_html=True)
    
    # PDF 다운로드 기능 (AI 응답이 있을 때만 표시)
    if st.session_state.messages and any(m["role"] == "assistant" for m in st.session_state.messages):
        st.markdown("---")
        
        # 전체 대화 내용을 텍스트로 생성
        pdf_content = f"""═══════════════════════════════════════════════════
🔮 천명 VIP - 프리미엄 사주 분석 리포트
═══════════════════════════════════════════════════

📅 분석 일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}

【의뢰인 정보】
{'• 성함: ' + user_name + '님' if user_name else ''}
• 생년월일: {date_type} {display_date}
• 양력 변환: {saju['solar_date']}
• 나이: {korean_age}세
• 성별: {saju['gender']}
• 띠: {saju['animal']}띠

【사주팔자】
┌────────┬────────┬────────┬────────┐
│  시주  │  일주⭐ │  월주  │  연주  │
├────────┼────────┼────────┼────────┤
│ {saju['hour_pillar'][0]} {saju['hour_pillar'][1]}  │ {saju['day_pillar'][0]} {saju['day_pillar'][1]}  │ {saju['month_pillar'][0]} {saju['month_pillar'][1]}  │ {saju['year_pillar'][0]} {saju['year_pillar'][1]}  │
│ {saju['hour_pillar_kr']}  │ {saju['day_pillar_kr']}  │ {saju['month_pillar_kr']}  │ {saju['year_pillar_kr']}  │
└────────┴────────┴────────┴────────┘

【일간】{saju['day_gan_kr']} ({CHEONGAN_OHAENG[saju['day_gan']]})

【오행분포】
木: {saju['ohaeng_count']['木']} | 火: {saju['ohaeng_count']['火']} | 土: {saju['ohaeng_count']['土']} | 金: {saju['ohaeng_count']['金']} | 水: {saju['ohaeng_count']['水']}

【대운 흐름】
{' → '.join([f"{d['pillar_kr']}({d['age']}세~)" for d in saju['daeun']])}

═══════════════════════════════════════════════════
📝 상담 내용
═══════════════════════════════════════════════════

"""
        # 대화 내용 추가
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                pdf_content += f"\n▶ 질문: {msg['content']}\n"
            else:
                pdf_content += f"\n🔮 천명 VIP 답변:\n{msg['content']}\n"
                pdf_content += "\n" + "─" * 50 + "\n"
        
        pdf_content += f"""
═══════════════════════════════════════════════════
ⓒ 2026 JEMINA AI · 천명 VIP v3.0
본 리포트는 참고용이며, 중요한 결정은 전문가와 상담하시기 바랍니다.
═══════════════════════════════════════════════════
"""
        
        # 다운로드 버튼들
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            # 텍스트 파일 다운로드
            file_name = f"천명VIP_사주분석_{user_name if user_name else '고객'}_{datetime.now().strftime('%Y%m%d')}.txt"
            st.download_button(
                label="📄 텍스트 파일 저장",
                data=pdf_content.encode('utf-8'),
                file_name=file_name,
                mime="text/plain",
                use_container_width=True
            )
        
        with col_dl2:
            # 마크다운/HTML 파일 다운로드 (PDF 대안)
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>천명 VIP 사주 분석 리포트</title>
    <style>
        body {{ font-family: 'Malgun Gothic', sans-serif; padding: 40px; line-height: 1.8; background: #1a1a2e; color: #e6edf3; }}
        h1 {{ color: #ffd700; text-align: center; }}
        h2 {{ color: #ffd700; border-bottom: 2px solid #ffd700; padding-bottom: 10px; }}
        .info-box {{ background: #21262d; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .saju-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .saju-table th, .saju-table td {{ border: 1px solid #30363d; padding: 15px; text-align: center; }}
        .saju-table th {{ background: #ffd700; color: #000; }}
        .question {{ background: rgba(255,215,0,0.1); padding: 15px; border-left: 4px solid #ffd700; margin: 20px 0; }}
        .answer {{ background: rgba(46,160,67,0.1); padding: 15px; border-left: 4px solid #2ea043; margin: 20px 0; }}
        .footer {{ text-align: center; color: #8b949e; margin-top: 50px; padding-top: 20px; border-top: 1px solid #30363d; }}
    </style>
</head>
<body>
    <h1>🔮 천명 VIP 사주 분석 리포트</h1>
    <p style="text-align: center; color: #8b949e;">분석 일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</p>
    
    <div class="info-box">
        <h2>📋 의뢰인 정보</h2>
        {'<p><strong>성함:</strong> ' + user_name + '님</p>' if user_name else ''}
        <p><strong>생년월일:</strong> {date_type} {display_date} (양력 {saju['solar_date']})</p>
        <p><strong>나이:</strong> {korean_age}세 | <strong>성별:</strong> {saju['gender']} | <strong>띠:</strong> {saju['animal']}띠</p>
    </div>
    
    <h2>🏛️ 사주팔자</h2>
    <table class="saju-table">
        <tr><th>시주</th><th>일주 ⭐</th><th>월주</th><th>연주</th></tr>
        <tr>
            <td>{saju['hour_pillar'][0]} {saju['hour_pillar'][1]}<br><small>{saju['hour_pillar_kr']}</small></td>
            <td style="border: 2px solid #ffd700;">{saju['day_pillar'][0]} {saju['day_pillar'][1]}<br><small>{saju['day_pillar_kr']}</small></td>
            <td>{saju['month_pillar'][0]} {saju['month_pillar'][1]}<br><small>{saju['month_pillar_kr']}</small></td>
            <td>{saju['year_pillar'][0]} {saju['year_pillar'][1]}<br><small>{saju['year_pillar_kr']}</small></td>
        </tr>
    </table>
    
    <div class="info-box">
        <p><strong>일간:</strong> {saju['day_gan_kr']} ({CHEONGAN_OHAENG[saju['day_gan']]})</p>
        <p><strong>오행분포:</strong> 木 {saju['ohaeng_count']['木']} | 火 {saju['ohaeng_count']['火']} | 土 {saju['ohaeng_count']['土']} | 金 {saju['ohaeng_count']['金']} | 水 {saju['ohaeng_count']['水']}</p>
    </div>
    
    <h2>📝 상담 내용</h2>
"""
            # 대화 내용 HTML로 추가
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    html_content += f'<div class="question"><strong>▶ 질문:</strong> {msg["content"]}</div>'
                else:
                    # 마크다운을 HTML로 변환 (간단하게)
                    answer_html = msg["content"].replace("\n", "<br>")
                    html_content += f'<div class="answer"><strong>🔮 천명 VIP:</strong><br><br>{answer_html}</div>'
            
            html_content += f"""
    <div class="footer">
        <p>ⓒ 2026 JEMINA AI · 천명 VIP v3.0</p>
        <p>본 리포트는 참고용이며, 중요한 결정은 전문가와 상담하시기 바랍니다.</p>
    </div>
</body>
</html>"""
            
            html_file_name = f"천명VIP_사주분석_{user_name if user_name else '고객'}_{datetime.now().strftime('%Y%m%d')}.html"
            st.download_button(
                label="🌐 HTML 리포트 저장",
                data=html_content.encode('utf-8'),
                file_name=html_file_name,
                mime="text/html",
                use_container_width=True
            )
        
        st.caption("💡 HTML 파일은 브라우저에서 열어 '인쇄 > PDF로 저장'하면 PDF로 변환됩니다.")
    
    # API 호출
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.spinner("🔮 천명 VIP가 사주를 분석하고 있습니다..."):
            context = generate_saju_context(saju, is_lunar, birth_year, user_name)
            api_msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            response = call_claude_api(api_msgs, context)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # 채팅 입력
    st.markdown("---")
    user_input = st.chat_input("궁금한 점을 물어보세요... (예: 올해 이직해도 될까요?)")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()

# =====================================================
# 초기 화면
# =====================================================
else:
    st.markdown("""
    <div style='text-align: center; padding: 60px 20px; background: #21262d; border-radius: 15px; margin: 20px 0;'>
        <div style='font-size: 4rem; margin-bottom: 20px;'>🔮</div>
        <h2 style='color: #ffd700; margin-bottom: 15px;'>프리미엄 사주 분석을 시작하세요</h2>
        <p style='color: #8b949e; font-size: 1rem;'>
            왼쪽 사이드바에서 생년월일시를 입력하고<br>
            '사주 계산' 버튼을 클릭하세요.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ✨ 천명 VIP v3.0 새로운 기능")
    
    feat_cols = st.columns(4)
    features = [
        ("📐 정밀 만세력", "절기 기준 정확한 사주 계산\n음력/양력 자동 변환"),
        ("🤖 개인화 통변", "월별 운세표 포함\nVIP 맞춤 스토리텔링"),
        ("💬 무제한 질문", "궁금한 거 뭐든 물어보세요\n채팅으로 후속 질문 가능"),
        ("📄 리포트 저장", "분석 결과를 파일로 저장\nHTML/텍스트 다운로드"),
    ]
    
    for i, (title, desc) in enumerate(features):
        with feat_cols[i]:
            st.markdown(f"""
            <div style='background: #21262d; padding: 25px; border-radius: 10px; text-align: center; height: 150px;'>
                <h4 style='color: #ffd700; margin-bottom: 10px;'>{title}</h4>
                <p style='color: #8b949e; font-size: 0.9rem; white-space: pre-line;'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
