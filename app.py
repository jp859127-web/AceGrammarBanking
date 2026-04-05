import streamlit as st
import google.generativeai as genai
import json

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AceGrammar: Banking English Master",
    page_icon="🏦",
    layout="wide"
)

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #1e3a8a; color: white; font-weight: bold; }
    .sentence-box { background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #1e3a8a; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); color: #1e293b; }
    .pos-tag { background-color: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 4px; font-size: 0.75em; font-weight: bold; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- API SETUP ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.sidebar.warning("⚠️ API Key not found in Secrets. Enter it below for testing:")
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    # Using a standard stable model name
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.info("👋 Welcome! Please add your Gemini API Key in the sidebar or Streamlit Secrets to begin.")
    st.stop()

# --- AI FUNCTIONS ---
def analyze_text(text):
    prompt = f"""
    Analyze the following text for English grammar and vocabulary, specifically for Indian banking exams (SBI/IBPS PO/Clerk). 
    Return the result in STRICT JSON format with the following keys:
    "sentences": [ {{"text": "", "subject": "", "verb": "", "object": "", "tense": "", "voice": "", "parts_of_speech": [{{"word": "", "pos": "", "explanation": ""}}], "logical_breakdown": ""}} ],
    "vocabulary": [ {{"word": "", "meaning": "", "synonyms": [], "usage": ""}} ],
    "idioms": [ {{"phrase": "", "meaning": ""}} ]

    Text: "{text}"
    """
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Analysis Error: {e}")
        return None

def get_questions(text, level, qtype, count):
    prompt = f"""
    Based on the text, generate {count} {level} level banking exam questions.
    Type: {qtype} (Error Spotting, Fillers, RC, Cloze Test).
    Match SBI/IBPS PO/Clerk patterns. Provide answers and logical explanations.
    Return as a JSON list of objects: [{{"question": "", "options": [], "answer": "", "explanation": ""}}]
    Text: "{text}"
    """
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Question Error: {e}")
        return None

# --- MAIN UI ---
st.title("🏦 AceGrammar: Banking English Master")
st.caption("Logical Grammar Decoder & Question Generator for SBI, IBPS, and RRB Aspirants")

col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("📝 Source Content")
    input_text = st.text_area("Paste Editorial / Article here:", height=300, placeholder="Example: The inflation rate has surged recently...")
    
    st.divider()
    st.subheader("⚙️ Question Settings")
    q_level = st.selectbox("Exam Level", ["Prelims", "Mains", "Mix (Pre + Mains)"])
    q_type = st.selectbox("Question Type", ["Mixed Pattern", "Error Spotting", "Cloze Test", "Reading Comprehension", "Fillers"])
    q_count = st.slider("Number of Questions", 1, 10, 5)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        btn_decode = st.button("🔍 Decode Grammar")
    with col_btn2:
        btn_qs = st.button("✨ Generate Qs")

with col2:
    if input_text:
        if btn_decode:
            with st.spinner("Decoding logically..."):
                data = analyze_text(input_text)
                if data:
                    t1, t2, t3 = st.tabs(["🧠 Decoder", "📖 Vocab", "🚩 Idioms"])
                    with t1:
                        for i, s in enumerate(data.get('sentences', [])):
                            st.markdown(f"<div class='sentence-box'><b>Sentence {i+1}:</b> {s['text']}</div>", unsafe_allow_html=True)
                            c1, c2, c3 = st.columns(3)
                            c1.metric("Subject", s.get('subject', 'N/A'))
                            c2.metric("Verb", s.get('verb', 'N/A'))
                            c3.metric("Object", s.get('object', 'N/A'))
                            st.write(f"**Tense:** {s.get('tense')} | **Voice:** {s.get('voice')}")
                            with st.expander("View Word-by-Word Logical Analysis"):
                                for word in s.get('parts_of_speech', []):
                                    st.markdown(f"**{word['word']}** <span class='pos-tag'>{word['pos']}</span>: {word['explanation']}", unsafe_allow_html=True)
                            st.info(f"**Logical Implementation:** {s.get('logical_breakdown')}")
                    with t2:
                        for v in data.get('vocabulary', []):
                            st.markdown(f"#### {v['word']}")
                            st.write(f"**Meaning:** {v['meaning']}")
                            st.write(f"**Synonyms:** {', '.join(v.get('synonyms', []))}")
                            st.write(f"*Usage:* {v['usage']}")
                            st.divider()
                    with t3:
                        for idm in data.get('idioms', []):
                            st.warning(f"**{idm.get('phrase', idm)}**")
                            if isinstance(idm, dict): 
                                st.write(idm.get('meaning', ''))

        if btn_qs:
            with st.spinner("Generating Exam Questions..."):
                qs = get_questions(input_text, q_level, q_type, q_count)
                if qs:
                    for i, q in enumerate(qs):
                        st.markdown(f"**Q{i+1}. {q['question']}**")
                        if 'options' in q and q['options']:
                            for opt in q['options']: 
                                st.write(f"- {opt}")
                        with st.expander("View Answer & Explanation"):
                            st.success(f"Answer: {q['answer']}")
                            st.write(q['explanation'])
                        st.divider()
    else:
        st.info("Please paste text in the left panel to begin.")
