import streamlit as st
import joblib

st.set_page_config(page_title="FakeShield", layout="centered")

# ---- Custom CSS ----
st.markdown("""
<style>
    /* Background with grid lines */
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        background-attachment: fixed;
    }

    /* Make sure content sits above grid */
    .block-container {
        position: relative;
        z-index: 1;
        padding-top: 2rem;
    }

    section[data-testid="stSidebar"],
    .stApp > div {
        position: relative;
        z-index: 1;
    }

    /* Hide default streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}

    /* Top badge */
    .badge {
        text-align: center;
        margin-bottom: 10px;
    }
    .badge span {
        background-color: #1a1a1a;
        border: 1px solid #444;
        color: #ccff00;
        padding: 6px 16px;
        font-size: 11px;
        font-family: monospace;
        letter-spacing: 2px;
        border-radius: 4px;
    }

    /* Title */
    .title {
        text-align: center;
        font-size: 72px;
        font-weight: 900;
        font-family: 'Arial Black', sans-serif;
        line-height: 1;
        margin: 10px 0;
    }
    .title .white { color: #ffffff; }
    .title .yellow { color: #ccff00; }

    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #888888;
        font-size: 14px;
        font-family: monospace;
        margin-bottom: 30px;
        letter-spacing: 1px;
    }

    /* Card container */
    .card {
        background-color: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 20px;
    }

    /* Label */
    .input-label {
        font-family: monospace;
        font-size: 11px;
        letter-spacing: 2px;
        color: #888888;
        margin-bottom: 10px;
    }

    /* Text area override */
    .stTextArea textarea {
        background-color: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        color: #ffffff !important;
        font-size: 15px !important;
        border-radius: 8px !important;
    }
    .stTextInput input {
        background-color: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }

    /* Analyze button */
    .stButton button {
        background-color: #ccff00 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 15px !important;
        letter-spacing: 2px !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 14px 40px !important;
        width: 100% !important;
        cursor: pointer !important;
    }
    .stButton button:hover {
        background-color: #aadd00 !important;
    }

    /* Result boxes */
    .result-real {
        background-color: #0a2a0a;
        border: 1px solid #00ff88;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        color: #00ff88;
        font-size: 22px;
        font-weight: bold;
        font-family: monospace;
        margin-top: 20px;
    }
    .result-fake {
        background-color: #2a0a0a;
        border: 1px solid #ff4444;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        color: #ff4444;
        font-size: 22px;
        font-weight: bold;
        font-family: monospace;
        margin-top: 20px;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #444444;
        font-family: monospace;
        font-size: 11px;
        margin-top: 40px;
        letter-spacing: 1px;
    }
    .footer span { color: #666666; margin: 0 8px; }
</style>
""", unsafe_allow_html=True)

# ---- Load Model ----
try:
    vectorizer = joblib.load("vectorizer.jb")
    model = joblib.load("lr_model.jb")
except Exception as e:
    st.error(f"❌ Error loading model: {e}")
    st.stop()

# ---- Badge ----
st.markdown("""
<div class="badge">
    <span>FAKE NEWS DETECTOR</span>
</div>
""", unsafe_allow_html=True)

# ---- Title ----
st.markdown("""
<div class="title">
    <span class="white">FAKE</span><span class="yellow">SHIELD</span>
</div>
""", unsafe_allow_html=True)

# ---- Subtitle ----
st.markdown("""
<div class="subtitle">
    News Authenticity Analysis · Powered by Machine Learning
</div>
""", unsafe_allow_html=True)

# ---- Input Card ----
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="input-label">NEWS ARTICLE TEXT</div>', unsafe_allow_html=True)

news_input = st.text_area(
    label="News Article",
    placeholder="Paste the full news article or headline here...\n\nThe more text you provide, the more accurate the analysis will be.",
    height=200,
    label_visibility="collapsed"
)

source_url = st.text_input(
    label="Source URL",
    placeholder="Source URL (optional)",
    label_visibility="collapsed"
)

analyze = st.button("ANALYZE")
st.markdown('</div>', unsafe_allow_html=True)

# ---- Result ----
if analyze:
    if news_input.strip():
        transformed = vectorizer.transform([news_input])
        prediction = model.predict(transformed)[0]
        confidence = model.predict_proba(transformed).max() * 100

        if prediction == 1:
            st.markdown(f"""
            <div class="result-real">
                ✅ REAL NEWS &nbsp;·&nbsp; Confidence: {confidence:.1f}%
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-fake">
                🚨 FAKE NEWS &nbsp;·&nbsp; Confidence: {confidence:.1f}%
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please paste a news article to analyze.")

# ---- Footer ----
st.markdown("""
<div class="footer">
    © 2026 FakeShield <span>·</span> Helping You Verify News
</div>
""", unsafe_allow_html=True)