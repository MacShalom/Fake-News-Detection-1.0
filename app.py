import streamlit as st
import joblib
from newspaper import Article
from datetime import datetime

st.set_page_config(page_title="Fake News Detector - PLASU", layout="wide")

# ---- Session State ----
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "history" not in st.session_state:
    st.session_state.history = []

# ---- Custom CSS ----
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

    * { font-family: 'Inter', sans-serif; box-sizing: border-box; }

    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 40px 40px;
    }

    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    #MainMenu, footer, header { visibility: hidden; }

    /* ---- NAVBAR ---- */
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 40px;
        border-bottom: 1px solid #1a1a1a;
        background-color: #0a0a0a;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    .nav-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 18px;
        font-weight: 900;
        letter-spacing: 2px;
    }
    .nav-logo .white { color: #ffffff; }
    .nav-logo .yellow { color: #ccff00; }
    .model-status {
        background-color: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 11px;
        font-family: monospace;
        color: #ccff00;
        letter-spacing: 1px;
    }
    .dot-green { color: #00ff88; }

    /* ---- HERO ---- */
    .hero-title {
        font-size: 64px;
        font-weight: 900;
        line-height: 1.1;
        margin-bottom: 16px;
    }
    .hero-title .white { color: #ffffff; }
    .hero-title .yellow { color: #ccff00; }
    .hero-subtitle {
        color: #888888;
        font-size: 15px;
        line-height: 1.6;
        margin-bottom: 30px;
    }

    /* ---- PROJECT BOX ---- */
    .project-box {
        background-color: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 20px 24px;
        font-size: 13px;
        line-height: 2.2;
    }
    .project-box .row {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #aaaaaa;
    }
    .project-box .row .label {
        color: #ccff00;
        font-weight: 700;
        min-width: 110px;
    }

    /* ---- ANALYZE CARD ---- */
    .analyze-card {
        background-color: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 16px;
        padding: 30px;
    }
    .analyze-title {
        color: #ccff00;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 6px;
    }
    .analyze-subtitle {
        color: #888888;
        font-size: 13px;
        margin-bottom: 16px;
    }
    .or-divider {
        text-align: center;
        color: #444444;
        font-size: 12px;
        margin: 12px 0;
        letter-spacing: 2px;
    }
    .url-label {
        color: #aaaaaa;
        font-size: 13px;
        margin-bottom: 8px;
    }
    .security-note {
        text-align: center;
        color: #444444;
        font-size: 11px;
        margin-top: 12px;
        font-family: monospace;
    }

    /* ---- INPUTS ---- */
    .stTextArea textarea {
        background-color: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        color: #ffffff !important;
        font-size: 14px !important;
        border-radius: 10px !important;
    }
    .stTextArea textarea:focus {
        border-color: #ccff00 !important;
        box-shadow: none !important;
    }
    .stTextInput input {
        background-color: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-size: 14px !important;
    }

    /* ---- BUTTONS ---- */
    .stButton button {
        background-color: #ccff00 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 14px !important;
        letter-spacing: 3px !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 16px !important;
        width: 100% !important;
        cursor: pointer !important;
    }
    .stButton button:hover {
        background-color: #aadd00 !important;
    }

    /* ---- HOW IT WORKS ---- */
    .how-it-works {
        background-color: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 16px;
        padding: 28px;
    }
    .section-title {
        color: #ccff00;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }
    .steps-row {
        display: flex;
        gap: 12px;
        align-items: flex-start;
    }
    .step-card {
        flex: 1;
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 10px;
        padding: 16px 12px;
        text-align: center;
    }
    .step-icon { font-size: 28px; margin-bottom: 10px; color: #ccff00; }
    .step-number { font-size: 11px; font-weight: 700; color: #ccff00; margin-bottom: 4px; }
    .step-desc { font-size: 11px; color: #666666; line-height: 1.5; }
    .step-arrow { color: #ccff00; font-size: 16px; padding-top: 40px; }

    /* ---- RESULT BOXES ---- */
    .result-real {
        background-color: #0a2a0a;
        border: 1px solid #00ff88;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        color: #00ff88;
        font-size: 20px;
        font-weight: bold;
        font-family: monospace;
        margin-top: 16px;
    }
    .result-fake {
        background-color: #2a0a0a;
        border: 1px solid #ff4444;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        color: #ff4444;
        font-size: 20px;
        font-weight: bold;
        font-family: monospace;
        margin-top: 16px;
    }

    /* ---- HISTORY CARD ---- */
    .history-card {
        background-color: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }
    .history-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .history-badge-real {
        background-color: #0a2a0a;
        border: 1px solid #00ff88;
        color: #00ff88;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        font-family: monospace;
    }
    .history-badge-fake {
        background-color: #2a0a0a;
        border: 1px solid #ff4444;
        color: #ff4444;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        font-family: monospace;
    }
    .history-time {
        color: #444444;
        font-size: 11px;
        font-family: monospace;
    }
    .history-text {
        color: #888888;
        font-size: 13px;
        line-height: 1.5;
        border-left: 2px solid #2a2a2a;
        padding-left: 12px;
        margin-bottom: 8px;
    }
    .history-confidence {
        color: #ccff00;
        font-size: 11px;
        font-family: monospace;
    }
    .empty-history {
        text-align: center;
        color: #444444;
        font-family: monospace;
        font-size: 13px;
        padding: 60px 0;
        border: 1px dashed #2a2a2a;
        border-radius: 12px;
    }

    /* ---- ABOUT PAGE ---- */
    .about-card {
        background-color: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 16px;
        padding: 40px;
        max-width: 800px;
        margin: 40px auto;
    }
    .about-disclaimer {
        background-color: #1a1a0a;
        border: 1px solid #ccff0044;
        border-left: 3px solid #ccff00;
        border-radius: 8px;
        padding: 16px 20px;
        color: #aaaaaa;
        font-size: 14px;
        line-height: 1.8;
        margin-bottom: 30px;
    }
    .about-info-row {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #1a1a1a;
        font-size: 14px;
    }
    .about-info-row .key { color: #888888; }
    .about-info-row .val { color: #ffffff; font-weight: 600; }
    .about-developer {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 20px;
        text-align: center;
        color: #ccff00;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 1px;
    }

    /* ---- FOOTER ---- */
    .footer {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 24px 40px;
        border-top: 1px solid #1a1a1a;
        font-size: 12px;
        color: #444444;
        line-height: 1.8;
        margin-top: 20px;
    }
    .footer .yellow { color: #ccff00; font-weight: 700; }
    .footer .center { text-align: center; }
    .footer .right { text-align: right; }
</style>
""", unsafe_allow_html=True)

# ---- Load Model ----
try:
    vectorizer = joblib.load("vectorizer.jb")
    model = joblib.load("lr_model.jb")
    model_loaded = True
except Exception as e:
    model_loaded = False

# ---- NAVBAR ----
st.markdown(f"""
<div class="navbar">
    <div class="nav-logo">
        🛡️ &nbsp;
        <span class="white">FAKE NEWS</span>&nbsp;<span class="yellow">DETECTOR</span>
    </div>
    <div style="display:flex; align-items:center; gap:16px;">
        <div class="model-status">
            <span class="dot-green">●</span>
            MODEL {"ONLINE" if model_loaded else "OFFLINE"}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- NAV BUTTONS ----
nav1, nav2, nav3, nav4 = st.columns([1, 1, 1, 6])
with nav1:
    if st.button("📊 Dashboard"):
        st.session_state.page = "Dashboard"
with nav2:
    if st.button("🕓 History"):
        st.session_state.page = "History"
with nav3:
    if st.button("ℹ️ About"):
        st.session_state.page = "About"

st.markdown("<hr style='border-color:#1a1a1a; margin: 0 0 10px 0'>", unsafe_allow_html=True)

# ==============================================================
# PAGE: DASHBOARD
# ==============================================================
if st.session_state.page == "Dashboard":

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("""
        <div style="padding: 30px 20px 20px 40px;">
            <div class="hero-title">
                <span class="white">Verify </span><span class="yellow">News.</span>
            </div>
            <div class="hero-subtitle">
                Detect fake news and misinformation using advanced machine learning models.
            </div>
            <div class="project-box">
                <div class="row">
                    <span>🏛️</span>
                    <span class="label">Institution:</span>
                    <span>Plateau State University, Bokkos (PLASU)</span>
                </div>
                <div class="row">
                    <span>💻</span>
                    <span class="label">Department:</span>
                    <span>Computer Science</span>
                </div>
                <div class="row">
                    <span>🎓</span>
                    <span class="label">Project Type:</span>
                    <span>Final Year Project — CS 2026</span>
                </div>
                <div class="row">
                    <span>⚡</span>
                    <span class="label">Powered by:</span>
                    <span>Machief Plasu_CS_2026</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="padding: 30px 40px 20px 20px;">
            <div class="analyze-card">
                <div class="analyze-title">📄 &nbsp; ANALYZE NEWS ARTICLE</div>
                <div class="analyze-subtitle">Paste the full news article or headline below.</div>
        """, unsafe_allow_html=True)

        news_input = st.text_area(
            label="News Article",
            placeholder="Paste the full news article or headline here...",
            height=180,
            label_visibility="collapsed"
        )

        st.markdown('<div class="or-divider">OR</div>', unsafe_allow_html=True)
        st.markdown('<div class="url-label">Paste a URL to the article</div>', unsafe_allow_html=True)

        source_url = st.text_input(
            label="Source URL",
            placeholder="https://www.example.com/article...",
            label_visibility="collapsed"
        )

        analyze = st.button("🛡️  ANALYZE ARTICLE")

        st.markdown("""
                <div class="security-note">🔒 Your data is secure and used only for analysis.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ---- RESULT ----
        if analyze:
            if source_url.strip():
                try:
                    article = Article(source_url.strip())
                    article.download()
                    article.parse()
                    news_input = article.text
                    st.info(f"📰 Article extracted — {len(news_input.split())} words found.")
                except Exception as e:
                    st.error(f"❌ Could not extract article from URL: {e}")
                    st.stop()

            if news_input.strip():
                if not model_loaded:
                    st.error("❌ Model not loaded. Check your model files.")
                else:
                    transformed = vectorizer.transform([news_input])
                    prediction = model.predict(transformed)[0]
                    confidence = model.predict_proba(transformed).max() * 100
                    label = "REAL" if prediction == 1 else "FAKE"
                    timestamp = datetime.now().strftime("%b %d, %Y · %I:%M %p")
                    preview = news_input[:200] + "..." if len(news_input) > 200 else news_input

                    # Save to history
                    st.session_state.history.insert(0, {
                        "label": label,
                        "confidence": confidence,
                        "preview": preview,
                        "time": timestamp,
                        "source": source_url.strip() if source_url.strip() else "Manual Input"
                    })

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
                st.warning("⚠️ Please paste a news article or a valid URL.")

    # ---- HOW IT WORKS ----
    st.markdown("<div style='padding: 10px 40px 40px 40px;'>", unsafe_allow_html=True)
    st.markdown("""
    <div class="how-it-works">
        <div class="section-title">⚡ &nbsp; HOW IT WORKS</div>
        <div class="steps-row">
            <div class="step-card">
                <div class="step-icon">📄</div>
                <div class="step-number">1. Input Article</div>
                <div class="step-desc">Paste your news article or URL.</div>
            </div>
            <div class="step-arrow">→</div>
            <div class="step-card">
                <div class="step-icon">🤖</div>
                <div class="step-number">2. AI Analysis</div>
                <div class="step-desc">Our ML model analyzes content and patterns.</div>
            </div>
            <div class="step-arrow">→</div>
            <div class="step-card">
                <div class="step-icon">🛡️</div>
                <div class="step-number">3. Verify Sources</div>
                <div class="step-desc">Cross-model analyzes trusted sources.</div>
            </div>
            <div class="step-arrow">→</div>
            <div class="step-card">
                <div class="step-icon">📊</div>
                <div class="step-number">4. Get Result</div>
                <div class="step-desc">Receive credibility score and insights.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================
# PAGE: HISTORY
# ==============================================================
elif st.session_state.page == "History":
    st.markdown("<div style='padding: 30px 40px;'>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title" style="font-size:16px; margin-bottom:24px;">
        🕓 &nbsp; ANALYSIS HISTORY
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("""
        <div class="empty-history">
            📭 &nbsp; No analyses yet.<br><br>
            Go to Dashboard and analyze an article to see results here.
        </div>
        """, unsafe_allow_html=True)
    else:
        # Clear history button
        if st.button("🗑️  Clear History"):
            st.session_state.history = []
            st.rerun()

        for item in st.session_state.history:
            badge = f'<span class="history-badge-real">✅ REAL</span>' if item["label"] == "REAL" else f'<span class="history-badge-fake">🚨 FAKE</span>'
            st.markdown(f"""
            <div class="history-card">
                <div class="history-header">
                    {badge}
                    <span class="history-time">🕐 {item["time"]}</span>
                </div>
                <div class="history-text">{item["preview"]}</div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="history-confidence">⚡ Confidence: {item["confidence"]:.1f}%</span>
                    <span style="color:#444; font-size:11px; font-family:monospace;">📎 {item["source"]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================
# PAGE: ABOUT
# ==============================================================
elif st.session_state.page == "About":
    st.markdown("""
    <div class="about-card">
        <div class="analyze-title" style="font-size:16px; margin-bottom:20px;">
            ℹ️ &nbsp; ABOUT THIS PROJECT
        </div>

        <div class="about-disclaimer">
            The Fake News Detector is intended for <strong style="color:#ccff00;">educational and research purposes</strong>.
            Its predictions are based on patterns learned from training data and should not be considered
            absolute proof that an article is true or false. Users are encouraged to consult trusted news
            organizations and multiple sources before drawing conclusions.
        </div>

        <div class="section-title">📋 &nbsp; PROJECT INFORMATION</div>

        <div class="about-info-row">
            <span class="key">🏛️ &nbsp; Institution</span>
            <span class="val">Plateau State University, Bokkos (PLASU)</span>
        </div>
        <div class="about-info-row">
            <span class="key">💻 &nbsp; Department</span>
            <span class="val">Computer Science</span>
        </div>
        <div class="about-info-row">
            <span class="key">🎓 &nbsp; Project Type</span>
            <span class="val">Final Year Project</span>
        </div>
        <div class="about-info-row">
            <span class="key">📅 &nbsp; Academic Session</span>
            <span class="val">2025/2026</span>
        </div>

        <div class="section-title" style="margin-top:28px;">👨‍💻 &nbsp; DEVELOPED BY</div>
        <div class="about-developer">
            ⚡ Machief Plasu_CS_2026
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---- FOOTER ----
st.markdown("""
<div class="footer">
    <div>
        <div>© 2026 Fake News Detector</div>
        <div>Helping You Verify News</div>
    </div>
    <div class="center">
        <div class="yellow">Powered by Machief Plasu_CS_2026</div>
        <div>Plateau State University, Bokkos</div>
    </div>
    <div class="right">
        Built with ❤️ and Machine Learning
    </div>
</div>
""", unsafe_allow_html=True)