import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from datetime import datetime, timedelta
import calendar
import re

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(page_title="Moa Village", page_icon="🐿️")

# --- 세션 상태 초기화 ---
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "emotion": None,
        "emotion_intensity": 5,
        "location": None,
        "question": ""
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

# 감정 기록 저장소 (날짜별)
if "emotion_history" not in st.session_state:
    st.session_state.emotion_history = {}
    # 예시 데이터 추가 (테스트용)
    # st.session_state.emotion_history["2025-01-03"] = {
    #     "emotion": "슬픔",
    #     "score": 7,
    #     "summary": "학교를 갔는데 친구들이 너무 시끄럽다고 괴롭혀서 너무 슬펐어",
    #     "solution": "모아랑 산책 10분 완료"
    # }

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.now().strftime("%Y-%m-%d")

if "calendar_year" not in st.session_state:
    st.session_state.calendar_year = datetime.now().year

if "calendar_month" not in st.session_state:
    st.session_state.calendar_month = datetime.now().month

# 감정별 색상 매핑
EMOTION_COLORS = {
    "기쁨": "#81C784",    # 초록
    "슬픔": "#64B5F6",    # 파랑
    "분노": "#E57373",    # 빨강
    "두려움": "#8D6E63", # 갈색
    "혐오": "#BA68C8",    # 보라
    "놀람": "#FFB74D"     # 주황
}

# --- 공통 스타일 ---
def apply_common_style():
    st.markdown("""
        <style>
        .stApp {
            background-color: #1e1e1e;
            display: flex;
            justify-content: center;
        }
        header { visibility: hidden; }
        
        .block-container {
            width: 430px !important;
            max-width: 430px !important;
            min-height: 850px !important;
            margin: auto !important;
            padding-top: 0 !important;
            padding-bottom: 50px !important;
            border-radius: 40px;
            box-shadow: 0 0 50px rgba(0,0,0,0.5);
            background: linear-gradient(180deg, #87CEEB 0%, #90EE90 50%, #98FB98 100%);
            overflow-y: auto !important;
        }
        
        .stButton > button {
            background-color: #E8A87C !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 15px 60px !important;
            font-size: 1.2rem !important;
            font-weight: bold !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
        }
        .stButton > button:hover {
            background-color: #D4956A !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 페이지 1: 랜딩 ---
def page_landing():
    st.markdown("""
        <style>
        .block-container {
            background: linear-gradient(180deg, #87CEEB 0%, #7EC87E 40%, #5A9A5A 100%) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="
            background-color: #C4A574;
            border: 5px solid #8B7355;
            border-radius: 10px;
            padding: 20px 40px;
            margin: 60px auto 30px auto;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        ">
            <h1 style="color: #4A3728; font-size: 2rem; margin: 0;">MOA VILLAGE</h1>
        </div>
    """, unsafe_allow_html=True)
    
    if os.path.exists("./모아_stand.png"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("./모아_stand.png", width=250)
    else:
        st.markdown("<div style='text-align:center; font-size:8rem;'>🐿️</div>", unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start", use_container_width=True):
            st.session_state.page = "intro"
            st.rerun()
    
    st.write("")
    
    # 달력 보기 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📅 감정 달력 보기", use_container_width=True):
            st.session_state.page = "calendar"
            st.rerun()

# --- 페이지 2: 인트로 ---
def page_intro():
    st.markdown("""
        <style>
        .block-container {
            background: linear-gradient(180deg, #FFF8DC 0%, #7EC87E 30%, #5A9A5A 100%) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="
            background-color: white;
            border-radius: 20px;
            padding: 25px;
            margin: 40px 20px 30px 20px;
            text-align: center;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        ">
            <p style="color: #4A3728; font-size: 1.1rem; line-height: 1.8; margin: 0; font-weight: 500;">
                안녕 난 모아야!<br>
                네 마음속의 퀘스트 가이드야.<br>
                나와 재미있는 퀘스트를 하면서<br>
                오늘 하루의 일과를 남겨보자!<br>
                준비됐어?
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if os.path.exists("./모아_stand.png"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("./모아_stand.png", width=220)
    
    st.write("")
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("준비 완료", use_container_width=True):
            st.session_state.page = "emotion"
            st.rerun()

# --- 페이지 3: 감정 선택 ---
def page_emotion():
    st.markdown("""
        <style>
        .block-container {
            background-color: #FFF8DC !important;
            padding-top: 20px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="
            border: 2px solid #C4A574;
            border-radius: 20px;
            padding: 12px 20px;
            margin: 20px auto;
            text-align: center;
        ">
            <span style="color: #4A3728; font-size: 1rem;">지금 너의 기분은 어때?</span>
        </div>
    """, unsafe_allow_html=True)
    
    if os.path.exists("./모아_다람쥐.png"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image("./모아_다람쥐.png", width=80)
    
    st.write("")
    
    emotions = ["기쁨", "두려움", "놀람", "슬픔", "혐오", "분노"]
    
    col1, col2 = st.columns(2)
    for i, emotion in enumerate(emotions):
        with col1 if i % 2 == 0 else col2:
            if st.button(emotion, key=f"emotion_{emotion}", use_container_width=True):
                st.session_state.user_data["emotion"] = emotion
                st.rerun()
    
    if st.session_state.user_data["emotion"]:
        st.success(f"선택된 감정: {st.session_state.user_data['emotion']}")
    
    st.write("")
    
    st.markdown("<p style='text-align:center; color:#666;'>감정의 세기는 어느정도야?</p>", unsafe_allow_html=True)
    intensity = st.slider("", 0, 10, st.session_state.user_data["emotion_intensity"], label_visibility="collapsed")
    st.session_state.user_data["emotion_intensity"] = intensity
    
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("선택 완료", key="emotion_done", use_container_width=True):
            if st.session_state.user_data["emotion"]:
                st.session_state.page = "location"
                st.rerun()
            else:
                st.warning("감정을 선택해주세요!")

# --- 페이지 4: 장소 선택 ---
def page_location():
    st.markdown("""
        <style>
        .block-container {
            background-color: #FFF8DC !important;
            padding-top: 20px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="
            border: 2px solid #C4A574;
            border-radius: 20px;
            padding: 12px 20px;
            margin: 20px auto;
            text-align: center;
        ">
            <span style="color: #4A3728;">오늘 가장 기억이 나는 장소가 어디야?</span>
        </div>
    """, unsafe_allow_html=True)
    
    if os.path.exists("./모아_다람쥐.png"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image("./모아_다람쥐.png", width=80)
    
    st.write("")
    
    locations = ["직장", "학교", "집", "알바", "학원"]
    
    col1, col2, col3 = st.columns(3)
    for i, loc in enumerate(locations[:3]):
        with [col1, col2, col3][i]:
            if st.button(f"📍\n{loc}", key=f"loc_{loc}", use_container_width=True):
                st.session_state.user_data["location"] = loc
                st.rerun()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    for i, loc in enumerate(locations[3:]):
        with [col1, col2][i]:
            if st.button(f"📍\n{loc}", key=f"loc_{loc}", use_container_width=True):
                st.session_state.user_data["location"] = loc
                st.rerun()
    
    if st.session_state.user_data["location"]:
        st.success(f"선택된 장소: {st.session_state.user_data['location']}")
    
    st.write("")
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("선택 완료", key="location_done", use_container_width=True):
            if st.session_state.user_data["location"]:
                st.session_state.page = "input"
                st.rerun()
            else:
                st.warning("장소를 선택해주세요!")

# --- 페이지 5: 텍스트 입력 ---
def page_input():
    st.markdown("""
        <style>
        .block-container {
            background: linear-gradient(180deg, #87CEEB 0%, #7EC87E 40%, #5A9A5A 100%) !important;
            padding-top: 20px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="
            background-color: #C4A574;
            border: 4px solid #8B7355;
            border-radius: 8px;
            padding: 10px 25px;
            margin: 20px auto;
            text-align: center;
            width: fit-content;
        ">
            <span style="color: #4A3728; font-weight: bold; font-size: 1.2rem;">MOA VILLAGE</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="
            background-color: white;
            border-radius: 15px;
            padding: 15px 20px;
            margin: 20px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        ">
            <p style="color: #8B4513; font-size: 0.95rem; margin: 0; line-height: 1.6;">
                오늘 하루를 떠올려봐!<br>
                가장 기억에 남는 에피소드를<br>
                영화의 한 장면처럼 써줄래?
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='color: white; margin-left: 20px; font-weight: bold;'>입력:</p>", unsafe_allow_html=True)
    user_input = st.text_area("", placeholder="오늘 있었던 일을 자유롭게 적어주세요...", height=150, label_visibility="collapsed")
    
    if os.path.exists("./모아_stand.png"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col3:
            st.image("./모아_stand.png", width=100)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("분석 시작! 🐿️", use_container_width=True):
            if user_input.strip():
                st.session_state.user_data["question"] = user_input
                st.session_state.page = "chat"
                st.rerun()
            else:
                st.warning("오늘 있었던 일을 적어주세요!")

# --- 페이지 6: 챗봇 ---
def page_chat():
    st.markdown("""
        <style>
        .block-container {
            background-color: #FFF8DC !important;
            padding-top: 20px !important;
            padding-bottom: 30px !important;
        }
        /* 챗봇 페이지 버튼 크기 줄이기 */
        .block-container .stButton > button {
            padding: 10px 20px !important;
            font-size: 0.9rem !important;
            min-height: 0 !important;
            border-radius: 20px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <h2 style='text-align: center; color: #4A3728; margin-bottom: 5px;'>
            🐿️ Moa's 분석 결과
        </h2>
    """, unsafe_allow_html=True)
    
    data = st.session_state.user_data
    st.markdown(f"""
        <div style="
            background-color: #ffffff;
            border: 2px solid #C4A574;
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0 20px 0;
        ">
            <p style="margin: 5px 0; color: #4A3728; text-align: center;">
                📍 {data['location']} &nbsp;&nbsp;
                💭 {data['emotion']} ({data['emotion_intensity']}/10)
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.messages:
        initial_query = f"""
        [사용자 정보]
        - 사용자가 선택한 감정: {data['emotion']} (강도: {data['emotion_intensity']}/10)
        - 주요 장소: {data['location']}
        
        [사용자가 작성한 오늘의 에피소드]
        {data['question']}
        """
        st.session_state.messages.append({"role": "user", "content": data['question']})
        
        chain = get_chain()
        if chain:
            with st.spinner("모아가 분석 중이에요... 🐿️"):
                try:
                    response = chain.invoke(initial_query)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # 감정 기록 저장
                    save_emotion_record(response, data)
                    
                except Exception as e:
                    st.error(f"오류: {e}")
    
    chat_container = st.container()
    with chat_container:
        avatar_icon = "./모아_다람쥐.png" if os.path.exists("./모아_다람쥐.png") else "🐿️"
        for message in st.session_state.messages:
            role = message["role"]
            avatar = avatar_icon if role == "assistant" else None
            with st.chat_message(role, avatar=avatar):
                st.markdown(message["content"])
    
    st.write("")
    
    st.markdown("<p style='color:#4A3728; font-weight:bold;'>💬 추가 질문</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("", placeholder="추가로 궁금한 점...", label_visibility="collapsed", key="chat_input")
    with col2:
        send_clicked = st.button("➤", key="send_btn")
    
    if send_clicked and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        chain = get_chain()
        if chain:
            try:
                response = chain.invoke(user_input)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                st.error(f"오류: {e}")
    
    st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 처음으로", use_container_width=True):
            st.session_state.page = "landing"
            st.session_state.messages = []
            st.session_state.user_data = {"emotion": None, "emotion_intensity": 5, "location": None, "question": ""}
            st.rerun()
    with col2:
        if st.button("📅 달력 보기", use_container_width=True):
            st.session_state.page = "calendar"
            st.rerun()

# --- 감정 기록 저장 함수 ---
def save_emotion_record(response, data):
    today = datetime.now().strftime("%Y-%m-%d")
    
    # GPT 응답에서 감정과 점수 추출 시도
    emotion_match = re.search(r'감정:\s*(기쁨|슬픔|분노|두려움|혐오|놀람)', response)
    score_match = re.search(r'점수:\s*(\d+)', response)
    
    final_emotion = emotion_match.group(1) if emotion_match else data['emotion']
    final_score = int(score_match.group(1)) if score_match else data['emotion_intensity']
    
    st.session_state.emotion_history[today] = {
        "emotion": final_emotion,
        "score": final_score,
        "summary": data['question'][:50] + "..." if len(data['question']) > 50 else data['question'],
        "full_summary": data['question'],
        "location": data['location'],
        "solution": "모아와 대화 완료! 🐿️"
    }

# --- 페이지 7: 감정 달력 ---
def page_calendar():
    st.markdown("""
        <style>
        .block-container {
            background-color: #FFF8DC !important;
            padding: 20px !important;
        }
        /* 달력 페이지 버튼 크기 줄이기 */
        .block-container .stButton > button {
            padding: 8px 20px !important;
            font-size: 0.9rem !important;
            min-height: 0 !important;
            border-radius: 15px !important;
        }
        .calendar-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            background-color: rgba(255,255,255,0.5);
            border-radius: 15px;
        }
        .calendar-table th {
            color: #888;
            font-size: 0.8rem;
            padding: 10px 5px;
            text-align: center;
        }
        .calendar-table td {
            text-align: center;
            padding: 8px 5px;
            color: #4A3728;
            font-size: 0.9rem;
        }
        .calendar-day {
            width: 35px;
            height: 35px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 월 네비게이션 (한 줄에 버튼과 제목 배치)
    year = st.session_state.calendar_year
    month = st.session_state.calendar_month
    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("◀", key="prev_month"):
            if st.session_state.calendar_month == 1:
                st.session_state.calendar_month = 12
                st.session_state.calendar_year -= 1
            else:
                st.session_state.calendar_month -= 1
            st.rerun()
    with col2:
        st.markdown(f"<h3 style='text-align:center; color:#4A3728; margin:0;'>{month_names[month-1]} {year}</h3>", unsafe_allow_html=True)
    with col3:
        if st.button("▶", key="next_month"):
            if st.session_state.calendar_month == 12:
                st.session_state.calendar_month = 1
                st.session_state.calendar_year += 1
            else:
                st.session_state.calendar_month += 1
            st.rerun()
    
    st.write("")
    
    # 달력을 HTML 테이블로 생성
    cal = calendar.monthcalendar(year, month)
    
    # 기록 있는 날짜 목록
    recorded_days = []
    for day_list in cal:
        for day in day_list:
            if day != 0:
                date_str = f"{year}-{month:02d}-{day:02d}"
                if date_str in st.session_state.emotion_history:
                    recorded_days.append(day)
    
    # HTML 테이블 생성
    html = """
    <table class="calendar-table">
        <thead>
            <tr>
                <th>Sun</th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for week in cal:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += "<td></td>"
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                if date_str in st.session_state.emotion_history:
                    record = st.session_state.emotion_history[date_str]
                    color = EMOTION_COLORS.get(record["emotion"], "#E8A87C")
                    html += f'<td><div class="calendar-day" style="background-color: {color}; color: white;">🐿️<br>{day}</div></td>'
                else:
                    html += f'<td><div class="calendar-day">{day}</div></td>'
        html += "</tr>"
    
    html += "</tbody></table>"
    
    st.markdown(html, unsafe_allow_html=True)
    
    st.write("")
    
    # 날짜 선택 (기록 있는 날짜만)
    if recorded_days:
        st.markdown("<p style='color:#4A3728; font-weight:bold;'>📅 기록된 날짜 선택:</p>", unsafe_allow_html=True)
        
        # 기록된 날짜들을 버튼으로 표시
        cols = st.columns(min(len(recorded_days), 5))
        for i, day in enumerate(recorded_days[:5]):  # 최대 5개까지 표시
            date_str = f"{year}-{month:02d}-{day:02d}"
            with cols[i]:
                if st.button(f"{day}일", key=f"select_{date_str}"):
                    st.session_state.selected_date = date_str
                    st.session_state.page = "care_journal"
                    st.rerun()
    
    # 선택된 날짜 정보 표시
    st.write("")
    selected = st.session_state.selected_date
    record = st.session_state.emotion_history.get(selected)
    
    st.markdown(f"""
        <div style="
            background-color: white;
            border: 2px solid #C4A574;
            border-radius: 15px;
            padding: 20px;
            margin-top: 10px;
        ">
            <h3 style="color: #C4A574; text-align: center; margin-bottom: 10px;">{selected}</h3>
    """, unsafe_allow_html=True)
    
    if record:
        color = EMOTION_COLORS.get(record["emotion"], "#888")
        st.markdown(f"""
            <p style="color: {color}; font-size: 1.1rem; font-weight: bold; text-align: center;">
                {record['emotion']} ({record['score']}/10)
            </p>
            <p style="color: #666; font-size: 0.9rem; text-align: center;">{record['summary']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("케어 일지 보러가기", use_container_width=True, key="view_journal"):
                st.session_state.page = "care_journal"
                st.rerun()
    else:
        st.markdown("""
            <p style='color: #888; text-align: center;'>기록이 없습니다</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 홈으로", use_container_width=True, key="cal_home"):
            st.session_state.page = "landing"
            st.rerun()

# --- 페이지 8: 케어 일지 ---
def page_care_journal():
    st.markdown("""
        <style>
        .block-container {
            background-color: #FFF8DC !important;
            padding: 20px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    selected = st.session_state.selected_date
    record = st.session_state.emotion_history.get(selected)
    
    # 헤더
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #4A3728;">🐿️ 마인드 케어 일지 🐿️</h2>
            <p style="color: #C4A574; font-size: 1.2rem; font-weight: bold;">{selected}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if record:
        # 오늘의 하루 요약
        st.markdown(f"""
            <div style="text-align: center; margin: 10px 0;">
                <p style="color: #4A3728;">🐿️ 오늘의 하루 요약 🐿️</p>
            </div>
            <div style="
                background-color: #E8F5E9;
                border: 2px solid #81C784;
                border-radius: 15px;
                padding: 15px;
                margin: 10px 0;
                text-align: center;
            ">
                <p style="color: #4A3728; margin: 0;">{record.get('full_summary', record['summary'])}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # 오늘의 케어
        st.markdown(f"""
            <div style="text-align: center; margin: 20px 0 10px 0;">
                <p style="color: #4A3728;">🐿️ 오늘의 케어 🐿️</p>
            </div>
            <div style="
                background-color: white;
                border: 2px solid #C4A574;
                border-radius: 15px;
                padding: 15px;
                margin: 10px 0;
                text-align: center;
            ">
                <p style="color: #4A3728; margin: 0;">{record['solution']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # 다람쥐 이미지
        if os.path.exists("./모아_다람쥐.png"):
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.image("./모아_다람쥐.png", width=80)
        
        # 이번 주 기분 변화
        st.markdown("""
            <div style="
                background-color: white;
                border: 2px solid #C4A574;
                border-radius: 15px;
                padding: 15px;
                margin: 20px 0;
                text-align: center;
            ">
                <p style="color: #4A3728; font-weight: bold; margin-bottom: 15px;">이번 주 나의 기분 변화</p>
        """, unsafe_allow_html=True)
        
        # 주간 감정 바 그래프
        selected_date = datetime.strptime(selected, "%Y-%m-%d")
        start_of_week = selected_date - timedelta(days=selected_date.weekday() + 1)  # Sunday
        
        days_kr = ["월", "화", "수", "목", "금", "토", "일"]
        cols = st.columns(7)
        
        for i in range(7):
            day_date = start_of_week + timedelta(days=i+1)
            day_str = day_date.strftime("%Y-%m-%d")
            day_record = st.session_state.emotion_history.get(day_str)
            
            with cols[i]:
                if day_record:
                    color = EMOTION_COLORS.get(day_record["emotion"], "#888")
                    st.markdown(f"""
                        <div style="
                            background-color: {color};
                            height: 40px;
                            border-radius: 5px;
                            margin-bottom: 5px;
                        "></div>
                        <p style="text-align:center; font-size:0.8rem; color:#4A3728;">{days_kr[i]}</p>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="
                            background-color: #eee;
                            height: 40px;
                            border-radius: 5px;
                            margin-bottom: 5px;
                        "></div>
                        <p style="text-align:center; font-size:0.8rem; color:#4A3728;">{days_kr[i]}</p>
                    """, unsafe_allow_html=True)
        
        # 감정 범례
        st.markdown("<div style='margin-top: 15px;'>", unsafe_allow_html=True)
        legend_cols = st.columns(3)
        emotions_list = list(EMOTION_COLORS.items())
        for i, (emotion, color) in enumerate(emotions_list):
            with legend_cols[i % 3]:
                st.markdown(f"""
                    <div style="display: flex; align-items: center; margin: 3px 0;">
                        <div style="width: 15px; height: 15px; background-color: {color}; border-radius: 3px; margin-right: 5px;"></div>
                        <span style="font-size: 0.75rem; color: #4A3728;">{emotion}</span>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        st.info("해당 날짜의 기록이 없습니다.")
    
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📅 캘린더 보러가기", use_container_width=True):
            st.session_state.page = "calendar"
            st.rerun()

# --- LLM 체인 ---
def get_chain():
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ .env 파일에 OPENAI_API_KEY가 설정되지 않았습니다.")
        return None
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    template = """당신의 이름은 "Moa(모아)"입니다. 귀여운 다람쥐 캐릭터이자 심리 상담가입니다.
    
    [당신의 역할]
    1. 사용자가 제공한 '선택한 감정', '장소', '에피소드'를 종합적으로 분석합니다.
    2. 에피소드 내용을 바탕으로 **최종 감정**을 6가지(기쁨, 슬픔, 분노, 두려움, 혐오, 놀람) 중 **반드시 1개만** 선택하세요.
    3. **최종 감정 점수**를 1~10점 사이로 매기세요. (1: 매우 약함, 10: 매우 강함)
    4. 사용자가 왜 그런 감정을 느꼈는지 공감하며 따뜻하게 설명해주세요.
    5. 마지막으로 그 감정에 도움이 되는 따뜻한 솔루션을 제공하세요.
    
    [응답 형식]
    반드시 아래 형식을 따라 응답하세요:
    
    🎯 **최종 감정 분석**
    - 감정: [6가지 중 1개]
    - 점수: [1~10]/10
    
    💭 **감정 분석**
    (공감하며 설명)
    
    🌱 **오늘의 솔루션**
    (따뜻한 조언)
    
    말투는 다정한 다람쥐체("~했어요", "~인 것 같아요 🐿️")를 사용하세요.
    
    Question:
    {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = (
        {"question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain

# --- 메인 ---
apply_common_style()

if st.session_state.page == "landing":
    page_landing()
elif st.session_state.page == "intro":
    page_intro()
elif st.session_state.page == "emotion":
    page_emotion()
elif st.session_state.page == "location":
    page_location()
elif st.session_state.page == "input":
    page_input()
elif st.session_state.page == "chat":
    page_chat()
elif st.session_state.page == "calendar":
    page_calendar()
elif st.session_state.page == "care_journal":
    page_care_journal()
