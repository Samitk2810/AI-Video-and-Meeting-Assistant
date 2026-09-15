import html
import os
import tempfile
from pathlib import Path

import requests

from dotenv import load_dotenv
import streamlit as st


load_dotenv()


st.set_page_config(
	page_title="Lumen | Meeting Intelligence",
	page_icon="✦",
	layout="wide",
	initial_sidebar_state="expanded",
)


st.markdown(
	"""
	<style>
	@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');

	:root {
		color-scheme: light dark;
		--ink: #17211f;
		--muted: #64716c;
		--paper: #f4f5ef;
		--panel: #fbfcf8;
		--panel-alt: #e8eee7;
		--line: #d4ddd5;
		--mint: #b9e9d0;
		--mint-deep: #21845f;
		--coral: #f28d72;
		--navy: #233b55;
	}
	[data-theme="dark"] {
		--ink: #f2f5ef;
		--muted: #aebbb3;
		--paper: #111817;
		--panel: #192321;
		--panel-alt: #202e29;
		--line: #34443d;
		--mint: #9de0bd;
		--mint-deep: #6fd0a0;
		--coral: #ff9d80;
		--navy: #142735;
	}
	@media (prefers-color-scheme: dark) {
		:root:not([data-theme="light"]) {
			--ink: #f2f5ef;
			--muted: #aebbb3;
			--paper: #111817;
			--panel: #192321;
			--panel-alt: #202e29;
			--line: #34443d;
			--mint: #9de0bd;
			--mint-deep: #6fd0a0;
			--coral: #ff9d80;
			--navy: #142735;
		}
	}

	* { font-family: 'Space Grotesk', sans-serif; }
	.stApp { background: radial-gradient(circle at 88% 4%, color-mix(in srgb, var(--mint) 14%, transparent), transparent 24rem), var(--paper); color: var(--ink); }
	[data-testid="stHeader"] { background: transparent; }
	[data-testid="stSidebar"] { background: var(--panel-alt); border-right: 1px solid var(--line); }
	[data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }
	.block-container { max-width: 1440px; padding: 2.5rem 4rem 4rem; }
	h1, h2, h3, h4 { color: var(--ink); letter-spacing: -0.045em; }
	h1 { font-size: clamp(2.5rem, 5.5vw, 6.4rem); line-height: .91; margin: 0; max-width: 900px; }
	h2 { font-size: 1.45rem; margin: 0; }
	h3 { font-size: 1rem; letter-spacing: -0.02em; }
	p, label, .stMarkdown, [data-testid="stCaptionContainer"] { color: var(--muted); }
	.brand { font-family: 'DM Mono', monospace; font-size: .78rem; letter-spacing: .12em; text-transform: uppercase; color: var(--mint-deep); }
	.eyebrow { color: var(--coral); font: 500 .72rem 'DM Mono', monospace; letter-spacing: .14em; text-transform: uppercase; margin-bottom: 1rem; }
	.hero-copy { max-width: 760px; margin: 1.4rem 0 2.2rem; font-size: 1.05rem; line-height: 1.7; }
	.hero-mark { color: var(--coral); }
	.section-rule { border-top: 1px solid var(--line); margin: 2.4rem 0 1.5rem; }
	.metric { background: var(--panel); border: 1px solid var(--line); border-top: 3px solid var(--mint-deep); padding: 1.1rem 1.25rem; min-height: 100px; }
	.metric-label { color: var(--muted); font: 500 .68rem 'DM Mono', monospace; letter-spacing: .08em; text-transform: uppercase; }
	.metric-value { color: var(--ink); font-size: 1.7rem; font-weight: 800; margin-top: .45rem; }
	.result-panel { background: var(--panel); border: 1px solid var(--line); padding: 1.5rem 1.7rem; min-height: 190px; }
	.panel-kicker { color: var(--mint-deep); font: 500 .68rem 'DM Mono', monospace; letter-spacing: .1em; text-transform: uppercase; margin-bottom: .9rem; }
	.quote-panel { background: var(--navy); color: #eff8f2; padding: 1.7rem; font-size: 1.08rem; line-height: 1.7; min-height: 190px; }
	.quote-panel .panel-kicker { color: var(--mint); }
	.empty-state { border: 1px dashed var(--line); padding: 3rem; text-align: center; color: var(--muted); background: color-mix(in srgb, var(--panel) 55%, transparent); }
	.stButton > button { border-radius: 2px; border: 1px solid var(--ink); background: var(--ink); color: var(--paper); font-weight: 700; padding: .65rem 1rem; }
	.stButton > button:hover { border-color: var(--mint-deep); background: var(--mint-deep); color: white; }
	.stDownloadButton > button { border-radius: 0; }
	.stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div, [data-testid="stFileUploaderDropzone"] { border-radius: 2px; border-color: var(--line); background: var(--panel); color: var(--ink); }
	.stTabs [data-baseweb="tab-list"] { gap: 1.4rem; border-bottom: 1px solid var(--line); }
	.stTabs [data-baseweb="tab"] { padding: .8rem 0; color: var(--muted); }
	.stTabs [aria-selected="true"] { color: var(--ink); }
	.stChatMessage { background: var(--panel); border: 1px solid var(--line); border-radius: 2px; }
	[data-testid="stChatInput"] textarea { background: var(--panel); color: var(--ink); }
	.mono { font-family: 'DM Mono', monospace; }
	@media (max-width: 800px) { .block-container { padding: 1.5rem 1.1rem 3rem; } h1 { font-size: 3.1rem; } }
	</style>
	""",
	unsafe_allow_html=True,
)


def _reset_results() -> None:
	st.session_state.pop("meeting", None)
	st.session_state.pop("chat_history", None)


def _save_upload(uploaded_file) -> str:
	suffix = Path(uploaded_file.name).suffix or ".tmp"
	with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
		temp_file.write(uploaded_file.getbuffer())
		return temp_file.name


def _as_text(value) -> str:
	if isinstance(value, (list, tuple, set)):
		return "\n".join(f"• {item}" for item in value)
	if isinstance(value, dict):
		return "\n".join(f"**{key}:** {item}" for key, item in value.items())
	return str(value or "No information extracted.")


def _meeting_export(meeting: dict) -> str:
	sections = [
		meeting.get("title", "Meeting brief"),
		"SUMMARY\n" + _as_text(meeting.get("summary")),
	]
	if meeting.get("full_brief"):
		sections.extend(
			[
				"ACTION ITEMS\n" + _as_text(meeting.get("action_items")),
				"DECISIONS\n" + _as_text(meeting.get("decisions")),
				"OPEN QUESTIONS\n" + _as_text(meeting.get("questions")),
			]
		)
	return "\n\n".join(sections)


FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")


def _analyze_with_api(source: str, language: str) -> dict:
	response = requests.post(
		f"{FASTAPI_URL}/analyze",
		json={"source": source, "language": language},
		timeout=1800,
	)
	if not response.ok:
		try:
			detail = response.json().get("detail", response.text)
		except Exception:
			detail = response.text
		raise RuntimeError(str(detail))
	return response.json()


def _ask_with_api(analysis_id: str, question: str) -> str:
	response = requests.post(
		f"{FASTAPI_URL}/analyses/{analysis_id}/ask",
		json={"question": question},
		timeout=300,
	)
	if not response.ok:
		try:
			detail = response.json().get("detail", response.text)
		except Exception:
			detail = response.text
		raise RuntimeError(str(detail))
	return str(response.json().get("answer", ""))


def _format_analysis_error(error: Exception) -> str:
	message = str(error)
	if "503" in message or "upstream" in message or "overflow" in message:
		return "Mistral temporarily reset the analysis request. No RAG database was involved. Please click Analyze again in a moment; if it repeats, try a shorter recording or check Mistral service status."
	if "401" in message or "Invalid API Key" in message:
		return "Mistral rejected the API key. Update MISTRAL_API_KEY in the project .env file with a current key, then restart FastAPI."
	if "MISTRAL_API_KEY" in message or "API key" in message:
		return "MISTRAL_API_KEY is missing. Add it to the project .env file, then restart FastAPI."
	if "Connection refused" in message or "Failed to establish a new connection" in message:
		return f"Could not connect to FastAPI at {FASTAPI_URL}. Start the FastAPI server and try again."
	return f"Analysis could not be completed: {message}"


def _format_chat_error(error: Exception) -> str:
	message = str(error)
	if "503" in message or "upstream" in message or "overflow" in message:
		return "Mistral is temporarily unavailable for this request. Please try the question again in a moment. If it keeps happening, ask a shorter question."
	if "401" in message or "Invalid API Key" in message:
		return "Mistral rejected the API key. Update MISTRAL_API_KEY in .env and restart FastAPI."
	if "Connection refused" in message or "Failed to establish a new connection" in message:
		return f"Could not connect to FastAPI at {FASTAPI_URL}. Start the FastAPI server and try again."
	return f"I could not answer that right now: {message}"


with st.sidebar:
	st.markdown('<div class="brand">✦ LUMEN / 01</div>', unsafe_allow_html=True)
	st.markdown("## New analysis")
	st.caption("Turn any recording into a clear, searchable brief.")

	input_mode = st.radio(
		"Source",
		["YouTube / local path", "Meeting audio", "Simple upload"],
		format_func=lambda item: {"YouTube / local path": "01  YouTube / local path", "Meeting audio": "02  Meeting audio · full brief", "Simple upload": "03  Simple upload"}[item],
		label_visibility="collapsed",
	)
	source = ""
	uploaded_file = None
	if input_mode == "YouTube / local path":
		st.caption("Title, summary, and chat")
		source = st.text_input("Source", placeholder="https://youtube.com/... or C:\\recording.mp4", label_visibility="collapsed")
	elif input_mode == "Meeting audio":
		st.caption("Full extraction: actions, decisions, and questions")
		uploaded_file = st.file_uploader("Drop meeting audio", type=["mp3", "wav", "m4a", "ogg", "flac"], label_visibility="collapsed")
	else:
		st.caption("Title, summary, and chat")
		uploaded_file = st.file_uploader("Drop a file", type=["mp4", "mp3", "wav", "m4a", "webm", "mov", "ogg", "flac"], label_visibility="collapsed")

	language = st.selectbox("Transcript language", ["english", "hinglish"], format_func=lambda item: item.title())
	analyze = st.button("Analyze →", use_container_width=True, type="primary")
	if st.session_state.get("meeting") and st.button("Start a new analysis", use_container_width=True):
		_reset_results()
		st.rerun()
	st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
	st.caption("Local transcription · Mistral intelligence · Chroma memory")


if analyze:
	temporary_path = None
	if uploaded_file is not None:
		temporary_path = _save_upload(uploaded_file)
		source = temporary_path
	if not source.strip():
		st.sidebar.error("Add a URL, file path, or upload a recording first.")
	else:
		try:
			with st.status("Building your brief", expanded=True) as status:
				st.write("Extracting audio…")
				meeting = _analyze_with_api(source.strip(), language)
				meeting["full_brief"] = input_mode == "Meeting audio"
				status.update(label="Brief ready", state="complete", expanded=False)
			st.session_state.meeting = meeting
			st.session_state.chat_history = []
		except Exception as error:
			st.error(_format_analysis_error(error))
		finally:
			if temporary_path and os.path.exists(temporary_path):
				os.unlink(temporary_path)


st.markdown('<div class="eyebrow">Conversation intelligence workspace</div>', unsafe_allow_html=True)
st.markdown('<h1>Make every conversation<br><span class="hero-mark">move forward.</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-copy">From a YouTube lesson to a team recording, Lumen turns spoken ideas into a clear, searchable point of view.</p>', unsafe_allow_html=True)

meeting = st.session_state.get("meeting")
if not meeting:
	st.markdown('<div class="empty-state"><strong>Your next brief starts here.</strong><br>Choose a source in the left panel to transcribe, summarize, and query any conversation.</div>', unsafe_allow_html=True)
else:
	title = html.escape(str(meeting.get("title", "Untitled meeting")))
	st.markdown(f'<div class="section-rule"></div><div class="brand">CURRENT BRIEF</div><h2 style="margin-top:.45rem">{title}</h2>', unsafe_allow_html=True)
	if meeting.get("full_brief"):
		metrics = st.columns(3)
		for column, label, key in zip(metrics, ["Action items", "Decisions", "Open questions"], ["action_items", "decisions", "questions"]):
			value = meeting.get(key, [])
			count = len(value) if isinstance(value, (list, tuple, set, dict)) else (0 if not value else 1)
			column.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{count:02d}</div></div>', unsafe_allow_html=True)

	st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
	summary_col, decisions_col = st.columns([1.35, 1])
	with summary_col:
		st.markdown('<div class="result-panel"><div class="panel-kicker">Executive readout</div>', unsafe_allow_html=True)
		st.markdown(_as_text(meeting.get("summary")))
		st.markdown('</div>', unsafe_allow_html=True)
	with decisions_col:
		st.markdown('<div class="quote-panel"><div class="panel-kicker">Decisions captured</div>', unsafe_allow_html=True)
		st.markdown(_as_text(meeting.get("decisions")) if meeting.get("full_brief") else "Use the chat to explore the source in context.")
		st.markdown('</div>', unsafe_allow_html=True)

	if meeting.get("full_brief"):
		tab_items, tab_actions, tab_chat = st.tabs(["Meeting map", "Action desk", "Ask the meeting"])
		with tab_items:
			left, right = st.columns(2)
			with left:
				st.markdown("### Open questions")
				st.markdown(_as_text(meeting.get("questions")))
			with right:
				st.markdown("### Decisions")
				st.markdown(_as_text(meeting.get("decisions")))
		with tab_actions:
			st.markdown("### What happens next")
			st.markdown(_as_text(meeting.get("action_items")))
	else:
		tab_chat = st.container()
	with tab_chat:
		history = st.session_state.setdefault("chat_history", [])
		for message in history:
			with st.chat_message(message["role"]):
				st.markdown(message["content"])
		question = st.chat_input("Ask about the content…")
		if question:
			history.append({"role": "user", "content": question})
			with st.chat_message("user"):
				st.markdown(question)
			with st.chat_message("assistant"):
				with st.spinner("Searching the conversation"):
					try:
						answer = _ask_with_api(meeting["analysis_id"], question)
					except Exception as error:
						answer = _format_chat_error(error)
				st.markdown(answer)
			history.append({"role": "assistant", "content": answer})

	st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
	st.download_button("Download brief", _meeting_export(meeting), file_name="meeting-brief.txt", mime="text/plain")