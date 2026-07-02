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

# ---- Load Models ----
@st.cache_resource
def load_models():
    vectorizer = joblib.load("vectorizer.jb")
    models = {}
    model_files = {
        "Logistic Regression": "lr_model.jb",
        "Random Forest": "rf_model.jb",
        "Naive Bayes": "nb_model.jb",
        "Decision Tree": "dt_model.jb",
    }
    for name, filename in model_files.items():
        try:
            models[name] = joblib.load(filename)
        except:
            pass
    return vectorizer, models

vectorizer, models = load_models()
model_loaded = len(models) > 0

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
    .block-container { padding: 0 !important; max-width: 100% !important; }
    #MainMenu, footer, header { visibility: hidden; }

    /* NAVBAR */
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

    /* HERO */
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

    /* PROJECT BOX */
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

    /* ANALYZE CARD */
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
    .url-label { color: #aaaaaa; font-size: 13px; margin-bottom: 8px; }
    .model-label {
        color: #ccff00;
        font-size: 11px;
        font-family: monospace;
        letter-spacing: 2px;
        margin: 14px 0 6px 0;
    }
    .security-note {
        text-align: center;
        color: #444444;
        font-size: 11px;
        margin-top: 12px;
        font-family: monospace;
    }

    /* INPUTS */
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
    .stSelectbox > div > div {
        background-color: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }

    /* BUTTONS */
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
    .stButton button:hover { background-color: #aadd00 !important; }

    /* RESULT BOXES */
    .result-real {
        background-color: #0a2a0a;
        border: 1px solid #00ff88;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        color: #00ff88;
        font-size: 18px;
        font-weight: bold;
        font-family: monospace;
        margin-top: 16px;
        line-height: 2;
    }
    .result-fake {
        background-color: #2a0a0a;
        border: 1px solid #ff4444;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        color: #ff4444;
        font-size: 18px;
        font-weight: bold;
        font-family: monospace;
        margin-top: 16px;
        line-height: 2;
    }

    /* ENSEMBLE VOTES */
    .vote-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 10px 16px;
        margin-bottom: 8px;
        font-family: monospace;
        font-size: 12px;
    }
    .vote-name { color: #aaaaaa; }
    .vote-real { color: #00ff88; font-weight: 700; }
    .vote-fake { color: #ff4444; font-weight: 700; }
    .vote-conf { color: #ccff00; }

    /* HOW IT WORKS */
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
    .steps-row { display: flex; gap: 12px; align-items: flex-start; }
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

    /* HISTORY */
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
    .history-time { color: #444444; font-size: 11px; font-family: monospace; }
    .history-text {
        color: #888888;
        font-size: 13px;
        line-height: 1.5;
        border-left: 2px solid #2a2a2a;
        padding-left: 12px;
        margin-bottom: 8px;
    }
    .history-confidence { color: #ccff00; font-size: 11px; font-family: monospace; }
    .empty-history {
        text-align: center;
        color: #444444;
        font-family: monospace;
        font-size: 13px;
        padding: 60px 0;
        border: 1px dashed #2a2a2a;
        border-radius: 12px;
    }

    /* FOOTER */
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

# ---- NAVBAR ----
st.markdown(f"""
<div class="navbar">
    <div class="nav-logo">
        🛡️ &nbsp;
        <span class="white">FAKE NEWS</span>&nbsp;<span class="yellow">DETECTOR</span>
    </div>
    <div class="model-status">
        ● MODEL {"ONLINE" if model_loaded else "OFFLINE"} &nbsp;·&nbsp; {len(models)} MODEL(S) LOADED
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

st.markdown("<hr style='border-color:#1a1a1a; margin:0 0 10px 0'>", unsafe_allow_html=True)

# ---- HELPER: Run Prediction ----
def run_prediction(news_text, selected_model_name):
    transformed = vectorizer.transform([news_text])

    if selected_model_name == "🗳️ Ensemble (All Models Vote)":
        votes = []
        confidences = []
        vote_details = []

        for name, mdl in models.items():
            pred = mdl.predict(transformed)[0]
            conf = mdl.predict_proba(transformed).max() * 100
            votes.append(pred)
            confidences.append(conf)
            vote_details.append({
                "name": name,
                "pred": pred,
                "conf": conf
            })

        final_pred = max(set(votes), key=votes.count)
        avg_conf = sum(confidences) / len(confidences)
        return final_pred, avg_conf, vote_details

    else:
        mdl = models[selected_model_name]
        pred = mdl.predict(transformed)[0]
        conf = mdl.predict_proba(transformed).max() * 100
        return pred, conf, None


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
            height=160,
            label_visibility="collapsed"
        )

        st.markdown('<div class="or-divider">OR</div>', unsafe_allow_html=True)
        st.markdown('<div class="url-label">Paste a URL to the article</div>', unsafe_allow_html=True)

        source_url = st.text_input(
            label="Source URL",
            placeholder="https://www.example.com/article...",
            label_visibility="collapsed"
        )

        st.markdown('<div class="model-label">SELECT MODEL</div>', unsafe_allow_html=True)

        model_options = list(models.keys()) + ["🗳️ Ensemble (All Models Vote)"]
        selected_model_name = st.selectbox(
            label="Select Model",
            options=model_options,
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
                    prediction, confidence, vote_details = run_prediction(
                        news_input, selected_model_name
                    )
                    label = "REAL" if prediction == 1 else "FAKE"
                    timestamp = datetime.now().strftime("%b %d, %Y · %I:%M %p")
                    preview = news_input[:200] + "..." if len(news_input) > 200 else news_input

                    # Save to history
                    st.session_state.history.insert(0, {
                        "label": label,
                        "confidence": confidence,
                        "preview": preview,
                        "time": timestamp,
                        "source": source_url.strip() if source_url.strip() else "Manual Input",
                        "model": selected_model_name
                    })

                    # Show result
                    if prediction == 1:
                        st.markdown(f"""
                        <div class="result-real">
                            ✅ REAL NEWS<br>
                            <span style="font-size:13px; color:#aaaaaa;">
                                Model: {selected_model_name} &nbsp;·&nbsp; Confidence: {confidence:.1f}%
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="result-fake">
                            🚨 FAKE NEWS<br>
                            <span style="font-size:13px; color:#aaaaaa;">
                                Model: {selected_model_name} &nbsp;·&nbsp; Confidence: {confidence:.1f}%
                            </span>
                        </div>
                        """, unsafe_allow_html=True)

                    # Show ensemble vote breakdown
                    if vote_details:
                        st.markdown("""
                        <div style="margin-top:16px;">
                            <div class="model-label">🗳️ INDIVIDUAL MODEL VOTES</div>
                        </div>
                        """, unsafe_allow_html=True)

                        for v in vote_details:
                            vote_label = "✅ REAL" if v["pred"] == 1 else "🚨 FAKE"
                            vote_class = "vote-real" if v["pred"] == 1 else "vote-fake"
                            st.markdown(f"""
                            <div class="vote-row">
                                <span class="vote-name">🤖 {v["name"]}</span>
                                <span class="{vote_class}">{vote_label}</span>
                                <span class="vote-conf">⚡ {v["conf"]:.1f}%</span>
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
                <div class="step-number">2. Select Model</div>
                <div class="step-desc">Choose a model or use Ensemble for best accuracy.</div>
            </div>
            <div class="step-arrow">→</div>
            <div class="step-card">
                <div class="step-icon">🛡️</div>
                <div class="step-number">3. AI Analysis</div>
                <div class="step-desc">Model analyzes content and text patterns.</div>
            </div>
            <div class="step-arrow">→</div>
            <div class="step-card">
                <div class="step-icon">📊</div>
                <div class="step-number">4. Get Result</div>
                <div class="step-desc">Receive credibility score and confidence level.</div>
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
        if st.button("🗑️  Clear History"):
            st.session_state.history = []
            st.rerun()

        for item in st.session_state.history:
            badge = '<span class="history-badge-real">✅ REAL</span>' if item["label"] == "REAL" \
                else '<span class="history-badge-fake">🚨 FAKE</span>'
            st.markdown(f"""
            <div class="history-card">
                <div class="history-header">
                    {badge}
                    <span class="history-time">🕐 {item["time"]}</span>
                </div>
                <div class="history-text">{item["preview"]}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                    <span class="history-confidence">⚡ Confidence: {item["confidence"]:.1f}%</span>
                    <span style="color:#ccff00; font-size:11px; font-family:monospace;">
                        🤖 {item["model"]}
                    </span>
                    <span style="color:#444; font-size:11px; font-family:monospace;">
                        📎 {item["source"]}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================
# PAGE: ABOUT
# ==============================================================
elif st.session_state.page == "About":
    st.markdown("<div style='padding: 30px 40px;'>", unsafe_allow_html=True)

    st.info("""
📌 **Disclaimer**

The Fake News Detector is intended for **educational and research purposes**.
Its predictions are based on patterns learned from training data and should not be considered absolute proof that an article is true or false.
Users are encouraged to consult trusted news organizations and multiple sources before drawing conclusions.
    """)

    st.markdown("---")
    st.markdown("### 📋 Project Information")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        <div style='background-color:#111111; border:1px solid #2a2a2a; border-radius:10px;
                    padding:20px; line-height:2.4; font-size:14px;'>
            <div><span style='color:#888;'>🏛️ &nbsp; Institution</span></div>
            <div style='color:#fff; font-weight:600; margin-bottom:10px;'>
                Plateau State University, Bokkos (PLASU)
            </div>
            <div><span style='color:#888;'>💻 &nbsp; Department</span></div>
            <div style='color:#fff; font-weight:600;'>Computer Science</div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div style='background-color:#111111; border:1px solid #2a2a2a; border-radius:10px;
                    padding:20px; line-height:2.4; font-size:14px;'>
            <div><span style='color:#888;'>🎓 &nbsp; Project Type</span></div>
            <div style='color:#fff; font-weight:600; margin-bottom:10px;'>Final Year Project</div>
            <div><span style='color:#888;'>📅 &nbsp; Academic Session</span></div>
            <div style='color:#fff; font-weight:600;'>2025/2026</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🤖 Models Available")

    model_descriptions = {
        "Logistic Regression": "Fast and reliable baseline model. Great for text classification tasks.",
        "Random Forest": "Ensemble of decision trees. Handles complex patterns well.",
        "Naive Bayes": "Probabilistic model optimized specifically for text data.",
        "Decision Tree": "Interpretable model that makes decisions based on feature splits.",
        "🗳️ Ensemble": "All models vote together — majority wins. Most accurate overall."
    }

    for name, desc in model_descriptions.items():
        available = name in models or name == "🗳️ Ensemble"
        status = "🟢 Available" if available else "🔴 Not Loaded"
        st.markdown(f"""
        <div style='background-color:#111111; border:1px solid #2a2a2a; border-radius:10px;
                    padding:14px 20px; margin-bottom:10px; display:flex;
                    justify-content:space-between; align-items:center;'>
            <div>
                <div style='color:#ccff00; font-weight:700; font-size:13px;'>{name}</div>
                <div style='color:#888; font-size:12px; margin-top:4px;'>{desc}</div>
            </div>
            <div style='color:#aaa; font-size:11px; font-family:monospace;'>{status}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 👨‍💻 Developed By")

    st.markdown("""
    <div style='background-color:#1a1a1a; border:1px solid #ccff0055; border-radius:10px;
                padding:24px; text-align:center; color:#ccff00;
                font-size:20px; font-weight:900; letter-spacing:2px;'>
        ⚡ Machief Plasu_CS_2026
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


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