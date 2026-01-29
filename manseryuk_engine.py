"""
만세력 계산 엔진 v1.0
- 절기 기준 월주 계산
- 정확한 일주/시주 계산
- 대운 계산
- 오행/십신 분석

Copyright 2026 JEMINA AI - 천명 VIP 사주 시스템
"""

from datetime import datetime, date, timedelta
from korean_lunar_calendar import KoreanLunarCalendar

# =====================================================
# 기본 데이터 정의
# =====================================================

# 천간 (天干)
CHEONGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
CHEONGAN_KR = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
CHEONGAN_HANJA = {
    '甲': '갑(甲)', '乙': '을(乙)', '丙': '병(丙)', '丁': '정(丁)', '戊': '무(戊)',
    '己': '기(己)', '庚': '경(庚)', '辛': '신(辛)', '壬': '임(壬)', '癸': '계(癸)'
}

# 지지 (地支)
JIJI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
JIJI_KR = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']
JIJI_HANJA = {
    '子': '자(子)', '丑': '축(丑)', '寅': '인(寅)', '卯': '묘(卯)', '辰': '진(辰)', '巳': '사(巳)',
    '午': '오(午)', '未': '미(未)', '申': '신(申)', '酉': '유(酉)', '戌': '술(戌)', '亥': '해(亥)'
}

# 지지 동물
JIJI_ANIMAL = {
    '子': '쥐', '丑': '소', '寅': '호랑이', '卯': '토끼', '辰': '용', '巳': '뱀',
    '午': '말', '未': '양', '申': '원숭이', '酉': '닭', '戌': '개', '亥': '돼지'
}

# 오행 (五行)
OHAENG = ['木', '火', '土', '金', '水']
OHAENG_KR = ['목', '화', '토', '금', '수']

# 천간 오행
CHEONGAN_OHAENG = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
    '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
}

# 지지 오행
JIJI_OHAENG = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
    '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'
}

# 천간 음양
CHEONGAN_YINYANG = {
    '甲': '양', '乙': '음', '丙': '양', '丁': '음', '戊': '양',
    '己': '음', '庚': '양', '辛': '음', '壬': '양', '癸': '음'
}

# 지지 음양
JIJI_YINYANG = {
    '子': '양', '丑': '음', '寅': '양', '卯': '음', '辰': '양', '巳': '음',
    '午': '양', '未': '음', '申': '양', '酉': '음', '戌': '양', '亥': '음'
}

# 지지 지장간 (地支藏干)
JIJANGGAN = {
    '子': ['癸'],
    '丑': ['己', '癸', '辛'],
    '寅': ['甲', '丙', '戊'],
    '卯': ['乙'],
    '辰': ['戊', '乙', '癸'],
    '巳': ['丙', '庚', '戊'],
    '午': ['丁', '己'],
    '未': ['己', '丁', '乙'],
    '申': ['庚', '壬', '戊'],
    '酉': ['辛'],
    '戌': ['戊', '辛', '丁'],
    '亥': ['壬', '甲']
}

# 십신 (十神)
SIPSIN = {
    ('甲', '甲'): '비견', ('甲', '乙'): '겁재', ('甲', '丙'): '식신', ('甲', '丁'): '상관',
    ('甲', '戊'): '편재', ('甲', '己'): '정재', ('甲', '庚'): '편관', ('甲', '辛'): '정관',
    ('甲', '壬'): '편인', ('甲', '癸'): '정인',
    ('乙', '乙'): '비견', ('乙', '甲'): '겁재', ('乙', '丁'): '식신', ('乙', '丙'): '상관',
    ('乙', '己'): '편재', ('乙', '戊'): '정재', ('乙', '辛'): '편관', ('乙', '庚'): '정관',
    ('乙', '癸'): '편인', ('乙', '壬'): '정인',
    ('丙', '丙'): '비견', ('丙', '丁'): '겁재', ('丙', '戊'): '식신', ('丙', '己'): '상관',
    ('丙', '庚'): '편재', ('丙', '辛'): '정재', ('丙', '壬'): '편관', ('丙', '癸'): '정관',
    ('丙', '甲'): '편인', ('丙', '乙'): '정인',
    ('丁', '丁'): '비견', ('丁', '丙'): '겁재', ('丁', '己'): '식신', ('丁', '戊'): '상관',
    ('丁', '辛'): '편재', ('丁', '庚'): '정재', ('丁', '癸'): '편관', ('丁', '壬'): '정관',
    ('丁', '乙'): '편인', ('丁', '甲'): '정인',
    ('戊', '戊'): '비견', ('戊', '己'): '겁재', ('戊', '庚'): '식신', ('戊', '辛'): '상관',
    ('戊', '壬'): '편재', ('戊', '癸'): '정재', ('戊', '甲'): '편관', ('戊', '乙'): '정관',
    ('戊', '丙'): '편인', ('戊', '丁'): '정인',
    ('己', '己'): '비견', ('己', '戊'): '겁재', ('己', '辛'): '식신', ('己', '庚'): '상관',
    ('己', '癸'): '편재', ('己', '壬'): '정재', ('己', '乙'): '편관', ('己', '甲'): '정관',
    ('己', '丁'): '편인', ('己', '丙'): '정인',
    ('庚', '庚'): '비견', ('庚', '辛'): '겁재', ('庚', '壬'): '식신', ('庚', '癸'): '상관',
    ('庚', '甲'): '편재', ('庚', '乙'): '정재', ('庚', '丙'): '편관', ('庚', '丁'): '정관',
    ('庚', '戊'): '편인', ('庚', '己'): '정인',
    ('辛', '辛'): '비견', ('辛', '庚'): '겁재', ('辛', '癸'): '식신', ('辛', '壬'): '상관',
    ('辛', '乙'): '편재', ('辛', '甲'): '정재', ('辛', '丁'): '편관', ('辛', '丙'): '정관',
    ('辛', '己'): '편인', ('辛', '戊'): '정인',
    ('壬', '壬'): '비견', ('壬', '癸'): '겁재', ('壬', '甲'): '식신', ('壬', '乙'): '상관',
    ('壬', '丙'): '편재', ('壬', '丁'): '정재', ('壬', '戊'): '편관', ('壬', '己'): '정관',
    ('壬', '庚'): '편인', ('壬', '辛'): '정인',
    ('癸', '癸'): '비견', ('癸', '壬'): '겁재', ('癸', '乙'): '식신', ('癸', '甲'): '상관',
    ('癸', '丁'): '편재', ('癸', '丙'): '정재', ('癸', '己'): '편관', ('癸', '戊'): '정관',
    ('癸', '辛'): '편인', ('癸', '庚'): '정인',
}

# =====================================================
# 절기 데이터 (1900-2100년)
# 각 연도별 24절기 날짜/시간 (UTC 기준, KST는 +9시간)
# 실제 서비스에서는 천문 데이터 API 또는 정밀 계산 사용
# =====================================================

# 월별 절기 (월건이 바뀌는 절기)
MONTHLY_JEOLGI = {
    1: '입춘',   # 인월 시작
    2: '경칩',   # 묘월 시작
    3: '청명',   # 진월 시작
    4: '입하',   # 사월 시작
    5: '망종',   # 오월 시작
    6: '소서',   # 미월 시작
    7: '입추',   # 신월 시작
    8: '백로',   # 유월 시작
    9: '한로',   # 술월 시작
    10: '입동',  # 해월 시작
    11: '대설',  # 자월 시작
    12: '소한',  # 축월 시작
}

# 절기별 월지 (절기가 지나면 해당 월지로 변경)
JEOLGI_WOLJI = {
    '입춘': '寅', '경칩': '卯', '청명': '辰', '입하': '巳',
    '망종': '午', '소서': '未', '입추': '申', '백로': '酉',
    '한로': '戌', '입동': '亥', '대설': '子', '소한': '丑'
}

# 간략화된 절기 데이터 (정확한 날짜는 연도별로 1-2일 차이 가능)
# 실제 서비스에서는 정밀 천문 계산 또는 API 사용 권장
JEOLGI_APPROX_DATES = {
    '소한': (1, 5), '대한': (1, 20), '입춘': (2, 4), '우수': (2, 19),
    '경칩': (3, 6), '춘분': (3, 21), '청명': (4, 5), '곡우': (4, 20),
    '입하': (5, 6), '소만': (5, 21), '망종': (6, 6), '하지': (6, 21),
    '소서': (7, 7), '대서': (7, 23), '입추': (8, 8), '처서': (8, 23),
    '백로': (9, 8), '추분': (9, 23), '한로': (10, 8), '상강': (10, 24),
    '입동': (11, 7), '소설': (11, 22), '대설': (12, 7), '동지': (12, 22)
}

# 정밀 절기 데이터 (2020-2030년) - 입춘 기준 예시
# 실제로는 모든 절기의 정밀 시간이 필요
JEOLGI_PRECISE = {
    # 연도: {절기명: (월, 일, 시, 분)}
    2024: {
        '입춘': (2, 4, 16, 27), '경칩': (3, 5, 10, 23), '청명': (4, 4, 15, 2),
        '입하': (5, 5, 8, 10), '망종': (6, 5, 12, 10), '소서': (7, 6, 22, 20),
        '입추': (8, 7, 8, 9), '백로': (9, 7, 11, 11), '한로': (10, 8, 3, 0),
        '입동': (11, 7, 6, 20), '대설': (12, 6, 23, 17), '소한': (1, 6, 4, 49),
    },
    2025: {
        '입춘': (2, 3, 22, 10), '경칩': (3, 5, 16, 7), '청명': (4, 4, 20, 48),
        '입하': (5, 5, 13, 57), '망종': (6, 5, 17, 56), '소서': (7, 7, 4, 5),
        '입추': (8, 7, 13, 51), '백로': (9, 7, 16, 52), '한로': (10, 8, 8, 41),
        '입동': (11, 7, 12, 4), '대설': (12, 7, 5, 5), '소한': (1, 5, 10, 33),
    },
    2026: {
        '입춘': (2, 4, 4, 2), '경칩': (3, 5, 21, 59), '청명': (4, 5, 2, 40),
        '입하': (5, 5, 19, 49), '망종': (6, 5, 23, 48), '소서': (7, 7, 9, 57),
        '입추': (8, 7, 19, 42), '백로': (9, 7, 22, 41), '한로': (10, 8, 14, 29),
        '입동': (11, 7, 17, 52), '대설': (12, 7, 10, 52), '소한': (1, 5, 16, 23),
    },
}


# =====================================================
# 핵심 계산 함수들
# =====================================================

def lunar_to_solar(year, month, day, is_leap=False):
    """음력을 양력으로 변환"""
    calendar = KoreanLunarCalendar()
    calendar.setLunarDate(year, month, day, is_leap)
    return date(calendar.solarYear, calendar.solarMonth, calendar.solarDay)


def solar_to_lunar(year, month, day):
    """양력을 음력으로 변환"""
    calendar = KoreanLunarCalendar()
    calendar.setSolarDate(year, month, day)
    return {
        'year': calendar.lunarYear,
        'month': calendar.lunarMonth,
        'day': calendar.lunarDay,
        'is_leap': calendar.isIntercalation
    }


def get_jeolgi_datetime(year, jeolgi_name):
    """특정 연도의 절기 일시 반환 (KST 기준)"""
    # 정밀 데이터가 있으면 사용
    if year in JEOLGI_PRECISE and jeolgi_name in JEOLGI_PRECISE[year]:
        m, d, h, mi = JEOLGI_PRECISE[year][jeolgi_name]
        return datetime(year, m, d, h, mi)
    
    # 없으면 근사값 사용 (12:00 기준)
    if jeolgi_name in JEOLGI_APPROX_DATES:
        m, d = JEOLGI_APPROX_DATES[jeolgi_name]
        return datetime(year, m, d, 12, 0)
    
    return None


def get_year_pillar(birth_datetime):
    """
    연주(年柱) 계산
    - 입춘 기준: 입춘이 지나야 새해
    """
    year = birth_datetime.year
    
    # 해당 연도 입춘 시간 가져오기
    ipchun = get_jeolgi_datetime(year, '입춘')
    
    # 입춘 이전이면 전년도 간지 사용
    if birth_datetime < ipchun:
        year -= 1
    
    # 연간 계산: (년도 - 4) % 10
    year_gan_idx = (year - 4) % 10
    # 연지 계산: (년도 - 4) % 12
    year_ji_idx = (year - 4) % 12
    
    return CHEONGAN[year_gan_idx] + JIJI[year_ji_idx]


def get_month_pillar(birth_datetime, year_gan):
    """
    월주(月柱) 계산
    - 절기 기준으로 월 결정
    - 월간은 연간에 따라 결정 (년간합 공식)
    """
    year = birth_datetime.year
    month = birth_datetime.month
    
    # 절기 기준 월지 결정
    # 각 절기를 확인하여 현재 어떤 월인지 판단
    month_ji = None
    
    # 절기 순서대로 확인
    jeolgi_order = ['소한', '입춘', '경칩', '청명', '입하', '망종', 
                    '소서', '입추', '백로', '한로', '입동', '대설']
    
    for i, jeolgi in enumerate(jeolgi_order):
        jeolgi_dt = get_jeolgi_datetime(year, jeolgi)
        if jeolgi_dt is None:
            continue
            
        # 다음 절기 확인
        if i < len(jeolgi_order) - 1:
            next_jeolgi_dt = get_jeolgi_datetime(year, jeolgi_order[i+1])
        else:
            # 대설 다음은 다음해 소한
            next_jeolgi_dt = get_jeolgi_datetime(year + 1, '소한')
        
        if jeolgi_dt <= birth_datetime < next_jeolgi_dt:
            if jeolgi in JEOLGI_WOLJI:
                month_ji = JEOLGI_WOLJI[jeolgi]
                break
    
    # 절기로 판단 안 되면 근사값 사용
    if month_ji is None:
        # 간단한 근사: 월에 따른 지지
        month_ji_map = {
            1: '丑', 2: '寅', 3: '卯', 4: '辰', 5: '巳', 6: '午',
            7: '未', 8: '申', 9: '酉', 10: '戌', 11: '亥', 12: '子'
        }
        # 절기 고려 (대략 5-6일 이전이면 전월)
        if birth_datetime.day < 6:
            prev_month = month - 1 if month > 1 else 12
            month_ji = month_ji_map[prev_month]
        else:
            month_ji = month_ji_map[month]
    
    # 월간 계산 (년간합 공식)
    # 갑기년 -> 병인월, 을경년 -> 무인월, 병신년 -> 경인월, 정임년 -> 임인월, 무계년 -> 갑인월
    year_gan_idx = CHEONGAN.index(year_gan)
    month_ji_idx = JIJI.index(month_ji)
    
    # 인월(寅) 천간 기준점 계산
    base_gan = ((year_gan_idx % 5) * 2 + 2) % 10
    month_gan_idx = (base_gan + month_ji_idx - 2) % 10
    
    return CHEONGAN[month_gan_idx] + month_ji


def get_day_pillar(birth_date):
    """
    일주(日柱) 계산
    - 기준일: 1900년 1월 1일 = 갑진일 (甲辰日)
    """
    base_date = date(1900, 1, 1)  # 갑진일
    days_diff = (birth_date - base_date).days
    
    # 갑진 = 甲(0) + 辰(4)
    day_gan_idx = (0 + days_diff) % 10
    day_ji_idx = (4 + days_diff) % 12
    
    return CHEONGAN[day_gan_idx] + JIJI[day_ji_idx]


def get_hour_pillar(birth_hour, day_gan):
    """
    시주(時柱) 계산
    - 시간에 따른 지지 결정
    - 시간 천간은 일간에 따라 결정 (시두법)
    """
    # 시간 -> 지지 매핑 (자시=23:00-00:59, 축시=01:00-02:59, ...)
    # 야자시(23:00-23:59)는 다음날 자시로 처리하는 경우도 있음
    hour_ji_map = {
        (23, 0): 0,   # 자시 (23:00-00:59)
        (1, 2): 1,    # 축시 (01:00-02:59)
        (3, 4): 2,    # 인시 (03:00-04:59)
        (5, 6): 3,    # 묘시 (05:00-06:59)
        (7, 8): 4,    # 진시 (07:00-08:59)
        (9, 10): 5,   # 사시 (09:00-10:59)
        (11, 12): 6,  # 오시 (11:00-12:59)
        (13, 14): 7,  # 미시 (13:00-14:59)
        (15, 16): 8,  # 신시 (15:00-16:59)
        (17, 18): 9,  # 유시 (17:00-18:59)
        (19, 20): 10, # 술시 (19:00-20:59)
        (21, 22): 11, # 해시 (21:00-22:59)
    }
    
    # 시간으로 지지 인덱스 찾기
    if birth_hour == 23 or birth_hour == 0:
        hour_ji_idx = 0
    else:
        hour_ji_idx = (birth_hour + 1) // 2
    
    # 시두법: 일간에 따른 시간 천간 계산
    # 갑기일 -> 갑자시, 을경일 -> 병자시, 병신일 -> 무자시, 정임일 -> 경자시, 무계일 -> 임자시
    day_gan_idx = CHEONGAN.index(day_gan)
    base_hour_gan = ((day_gan_idx % 5) * 2) % 10
    hour_gan_idx = (base_hour_gan + hour_ji_idx) % 10
    
    return CHEONGAN[hour_gan_idx] + JIJI[hour_ji_idx]


def calculate_saju(year, month, day, hour, minute=0, is_lunar=False, is_leap=False, gender='남'):
    """
    사주팔자 계산 메인 함수
    
    Parameters:
    - year, month, day: 생년월일
    - hour: 생시 (0-23)
    - minute: 분 (선택)
    - is_lunar: 음력 여부
    - is_leap: 윤달 여부 (음력인 경우)
    - gender: '남' 또는 '여'
    
    Returns:
    - dict: 사주 정보
    """
    # 음력이면 양력으로 변환
    if is_lunar:
        solar_date = lunar_to_solar(year, month, day, is_leap)
        birth_date = solar_date
        lunar_info = {'year': year, 'month': month, 'day': day, 'is_leap': is_leap}
    else:
        birth_date = date(year, month, day)
        lunar_info = solar_to_lunar(year, month, day)
    
    birth_datetime = datetime(birth_date.year, birth_date.month, birth_date.day, hour, minute)
    
    # 사주 계산
    year_pillar = get_year_pillar(birth_datetime)
    month_pillar = get_month_pillar(birth_datetime, year_pillar[0])
    day_pillar = get_day_pillar(birth_date)
    hour_pillar = get_hour_pillar(hour, day_pillar[0])
    
    # 일간 (일주의 천간) = 나를 나타냄
    day_gan = day_pillar[0]
    
    # 오행 분석
    ohaeng_count = analyze_ohaeng([year_pillar, month_pillar, day_pillar, hour_pillar])
    
    # 십신 분석
    sipsin_analysis = analyze_sipsin(day_gan, [year_pillar, month_pillar, day_pillar, hour_pillar])
    
    # 대운 계산
    daeun = calculate_daeun(birth_datetime, gender, month_pillar)
    
    return {
        'solar_date': birth_date.strftime('%Y년 %m월 %d일'),
        'lunar_date': f"{lunar_info['year']}년 {lunar_info['month']}월 {lunar_info['day']}일" + (' (윤달)' if lunar_info.get('is_leap') else ''),
        'birth_time': f"{hour:02d}시 {minute:02d}분",
        'gender': gender,
        
        'year_pillar': year_pillar,
        'month_pillar': month_pillar,
        'day_pillar': day_pillar,
        'hour_pillar': hour_pillar,
        
        'year_pillar_kr': to_korean(year_pillar),
        'month_pillar_kr': to_korean(month_pillar),
        'day_pillar_kr': to_korean(day_pillar),
        'hour_pillar_kr': to_korean(hour_pillar),
        
        'day_gan': day_gan,  # 일간 (나)
        'day_gan_kr': CHEONGAN_HANJA[day_gan],
        
        'ohaeng_count': ohaeng_count,
        'sipsin': sipsin_analysis,
        'daeun': daeun,
        
        'animal': JIJI_ANIMAL[year_pillar[1]],  # 띠
    }


def to_korean(pillar):
    """간지를 한글로 변환"""
    gan = pillar[0]
    ji = pillar[1]
    gan_kr = CHEONGAN_KR[CHEONGAN.index(gan)]
    ji_kr = JIJI_KR[JIJI.index(ji)]
    return f"{gan_kr}{ji_kr}"


def analyze_ohaeng(pillars):
    """오행 분석"""
    count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
    
    for pillar in pillars:
        gan = pillar[0]
        ji = pillar[1]
        
        # 천간 오행
        count[CHEONGAN_OHAENG[gan]] += 1
        
        # 지지 오행
        count[JIJI_OHAENG[ji]] += 1
        
        # 지장간 오행 (가중치 낮게)
        for jjg in JIJANGGAN[ji]:
            count[CHEONGAN_OHAENG[jjg]] += 0.3
    
    return {k: round(v, 1) for k, v in count.items()}


def analyze_sipsin(day_gan, pillars):
    """십신 분석"""
    result = []
    pillar_names = ['연주', '월주', '일주', '시주']
    
    for i, pillar in enumerate(pillars):
        gan = pillar[0]
        ji = pillar[1]
        
        # 천간 십신
        gan_sipsin = SIPSIN.get((day_gan, gan), '?')
        
        # 지지 십신 (본기 기준)
        ji_main = JIJANGGAN[ji][0]  # 본기
        ji_sipsin = SIPSIN.get((day_gan, ji_main), '?')
        
        result.append({
            'pillar': pillar_names[i],
            'gan': gan,
            'ji': ji,
            'gan_sipsin': gan_sipsin,
            'ji_sipsin': ji_sipsin
        })
    
    return result


def calculate_daeun(birth_datetime, gender, month_pillar):
    """
    대운 계산
    - 남자 양년생/여자 음년생: 순행
    - 남자 음년생/여자 양년생: 역행
    """
    year_gan = get_year_pillar(birth_datetime)[0]
    is_yang_year = CHEONGAN_YINYANG[year_gan] == '양'
    
    # 순행/역행 결정
    if (gender == '남' and is_yang_year) or (gender == '여' and not is_yang_year):
        direction = 1  # 순행
    else:
        direction = -1  # 역행
    
    # 월주의 간지 인덱스
    month_gan_idx = CHEONGAN.index(month_pillar[0])
    month_ji_idx = JIJI.index(month_pillar[1])
    
    # 대운 계산 (10개)
    daeun_list = []
    for i in range(1, 11):
        gan_idx = (month_gan_idx + i * direction) % 10
        ji_idx = (month_ji_idx + i * direction) % 12
        
        daeun_pillar = CHEONGAN[gan_idx] + JIJI[ji_idx]
        daeun_list.append({
            'age': i * 10,  # 대략적인 나이 (정확한 계산은 절기까지 거리 필요)
            'pillar': daeun_pillar,
            'pillar_kr': to_korean(daeun_pillar)
        })
    
    return daeun_list


def format_saju_display(saju_result):
    """사주 결과를 보기 좋게 포맷팅"""
    output = []
    output.append("=" * 50)
    output.append("          ★ 사주팔자 명조 ★")
    output.append("=" * 50)
    output.append("")
    output.append(f"양력: {saju_result['solar_date']} {saju_result['birth_time']}")
    output.append(f"음력: {saju_result['lunar_date']}")
    output.append(f"성별: {saju_result['gender']}  |  띠: {saju_result['animal']}띠")
    output.append("")
    output.append("-" * 50)
    output.append("        시주      일주      월주      연주")
    output.append("-" * 50)
    output.append(f"천간:   {saju_result['hour_pillar'][0]}        {saju_result['day_pillar'][0]}        {saju_result['month_pillar'][0]}        {saju_result['year_pillar'][0]}")
    output.append(f"지지:   {saju_result['hour_pillar'][1]}        {saju_result['day_pillar'][1]}        {saju_result['month_pillar'][1]}        {saju_result['year_pillar'][1]}")
    output.append("-" * 50)
    output.append(f"한글:   {saju_result['hour_pillar_kr']}      {saju_result['day_pillar_kr']}      {saju_result['month_pillar_kr']}      {saju_result['year_pillar_kr']}")
    output.append("-" * 50)
    output.append("")
    output.append(f"★ 일간(나): {saju_result['day_gan_kr']} ({CHEONGAN_OHAENG[saju_result['day_gan']]})")
    output.append("")
    output.append("【오행 분포】")
    for ohaeng, count in saju_result['ohaeng_count'].items():
        bar = "●" * int(count) + "○" * (5 - int(count))
        output.append(f"  {ohaeng}({OHAENG_KR[OHAENG.index(ohaeng)]}): {bar} {count}")
    output.append("")
    output.append("【십신 분석】")
    for s in saju_result['sipsin']:
        output.append(f"  {s['pillar']}: {s['gan']}({s['gan_sipsin']}) {s['ji']}({s['ji_sipsin']})")
    output.append("")
    output.append("【대운】")
    daeun_str = "  "
    for d in saju_result['daeun'][:8]:
        daeun_str += f"{d['pillar_kr']} → "
    output.append(daeun_str[:-3])
    output.append("=" * 50)
    
    return "\n".join(output)


# 테스트
if __name__ == "__main__":
    # 테스트: 1985년 3월 15일 오전 7시 30분, 남자
    result = calculate_saju(1985, 3, 15, 7, 30, is_lunar=False, gender='남')
    print(format_saju_display(result))
