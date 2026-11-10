import os
from dotenv import load_dotenv
import streamlit as st
import google.genai as genai
from streamlit_webrtc import webrtc_streamer, WebRtcMode
av = __import__('av')
import random
import uuid

# --- 🔑 .env 파일에서 Gemini API 안전하게 불러오기 ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(
    page_title="SpeakFlow AI",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.set_page_config(
    page_title="SpeakFlow AI",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# CSS 스타일링 (기존 디자인 유지)
st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 680px; }
    .profile-badge { background-color: #EFF6FF; color: #2563EB; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; float: right; }
    .header-title { font-size: 1.4rem; font-weight: 800; color: #1E293B; }
    .header-sub { font-size: 0.85rem; color: #64748B; margin-bottom: 1.2rem; }
    .ai-card { padding: 1.2rem; background: linear-gradient(135deg, #FFFFFF 0%, #EFF6FF 100%); border-radius: 16px; border: 1px solid #BFDBFE; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08); margin-bottom: 1.2rem; }
    .stButton>button { border-radius: 10px !important; font-weight: 600 !important; font-size: 0.88rem !important; width: 100%; }
    div.stButton > button:first-child { background-color: #2563EB !important; color: white !important; border: none !important; }
    div.stButton > button:first-child:hover { background-color: #1D4ED8 !important; }
</style>
""", unsafe_allow_html=True)

AI_RECOMMENDED_TOPICS = [
    {"title": "☕ 카페에서 취향대로 커스텀 주문하기", "desc": "원두 선택부터 옵션 변경까지 영어로 주문해 보세요."},
    {"title": "🎬 최근에 본 재미있는 영화 추천하기", "desc": "줄거리와 느낀 감정을 자연스럽게 공유해 보세요."},
    {"title": "✈️ 공항 입국 심사관의 질문에 답하기", "desc": "체류 목적과 기간을 명확하게 답변하는 연습입니다."},
]

if "screen" not in st.session_state:
    st.session_state.screen = "dashboard"
if "current_ai_pick" not in st.session_state:
    st.session_state.current_ai_pick = AI_RECOMMENDED_TOPICS[0]
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = st.session_state.current_ai_pick["title"]
if "saved_notes" not in st.session_state:
    st.session_state.saved_notes = []

# --- 🎙️ 실시간 오디오 스트림 처리 콜백 함수 ---
def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
    # 실시간으로 들어오는 오디오 프레임 처리 영역
    # WebRTC를 통해 마이크 오디오가 실시간으로 수신됩니다.
    return frame

# --- [화면 1] 메인 대시보드 ---
if st.session_state.screen == "dashboard":
    st.markdown("""
    <div class="profile-badge">ME</div>
    <div class="header-title">SpeakFlow AI ✨</div>
    <div class="header-sub">버튼 누름 없는 실시간 음성 통화로 영어 회화를 시작하세요.</div>
    """, unsafe_allow_html=True)

    if st.button("🔖 내 오답노트 보관함"):
        st.session_state.screen = "notes"
        st.rerun()

    st.divider()

    pick = st.session_state.current_ai_pick
    st.markdown(f"""
    <div class="ai-card">
        <span style="font-size: 11px; color: #2563EB; font-weight: bold; background: white; padding: 3px 8px; border-radius: 6px;">✨ TODAY'S AI PICK</span>
        <div style="font-size: 1.15rem; font-weight: bold; color: #1E293B; margin-top: 8px;">{pick['title']}</div>
        <div style="font-size: 0.82rem; color: #64748B; margin-top: 4px;">{pick['desc']}</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("📞 실시간 통화 시작하기"):
            st.session_state.selected_topic = pick['title']
            st.session_state.screen = "practice"
            st.rerun()
    with col2:
        if st.button("🎲 다른 추천 받기"):
            st.session_state.current_ai_pick = random.choice(AI_RECOMMENDED_TOPICS)
            st.rerun()

# --- [화면 2] 실시간 라이브 통화 화면 ---
elif st.session_state.screen == "practice":
    st.markdown(f"### 📞 Live Call: {st.session_state.selected_topic}")
    st.caption("진짜 전화 통화처럼 마이크가 켜져 있습니다. 편하게 말씀하세요!")

    if st.button("⏹️ 통화 종료 & 피드백 받기"):
        st.session_state.screen = "feedback"
        st.rerun()

    st.divider()

    # WebRTC 실시간 양방향 오디오 스트리밍 컴포넌트
    webrtc_streamer(
        key="speakflow-live",
        mode=WebRtcMode.SENDRECV,
        audio_frame_callback=audio_frame_callback,
        media_stream_constraints={"video": False, "audio": True},
        async_processing=True,
    )

    st.info("💡 통화 연결 버튼(Start)을 누르고 마이크 권한을 허용하면 실시간으로 AI 튜터와 음성 연결이 유지됩니다.")

# --- [화면 3] 피드백 리포트 ---
elif st.session_state.screen == "feedback":
    st.markdown("### Today's AI Feedback Report ✨")
    if st.button("🏠 대시보드로 돌아가기"):
        st.session_state.screen = "dashboard"
        st.rerun()
    st.divider()
    st.info("실시간 통화 세션이 종료되었습니다. 오늘도 수고하셨습니다!")

# --- [화면 4] 오답노트 ---
elif st.session_state.screen == "notes":
    st.markdown("### 🔖 내 오답노트 보관함")
    if st.button("← 대시보드로 돌아가기"):
        st.session_state.screen = "dashboard"
        st.rerun()
    st.divider()
    st.write("저장된 오답이 없습니다.")
