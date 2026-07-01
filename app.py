import streamlit as st
import joblib
import os

# Streamlit page configuration
st.set_page_config(page_title="🕵️ Fake News Detector", layout="centered")

# Load the correct vectorizer and model
vectorizer = joblib.load(r"vectorizer.jb")
model = joblib.load(r"lr_model.jb")


st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🕵️‍♂️ Fake News Detector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Enter a news article below to check whether it is <strong>Fake</strong> or <strong>Real</strong>.</p>", unsafe_allow_html=True)

news_input = st.text_area("📰 News Article", placeholder="Paste the news article content here...", height=200)

if st.button("🔍 Check News"):
    if news_input.strip():
        transformed_input = vectorizer.transform([news_input])
        prediction = model.predict(transformed_input)

        if prediction[0] == 1:
            st.success("✅ The News is **Real**.")
        else:
            st.error("🚨 The News is **Fake**.")
    else:
        st.warning("⚠️ Please enter some text to analyze.")