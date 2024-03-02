from dotenv import load_dotenv

load_dotenv() ## Loading environment variables

import os

import google.generativeai as genai
import streamlit as st
from PIL import Image

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## function to load Gemini Pro model and get responses

model=genai.GenerativeModel("gemini-pro-vision")

def get_gemini_response(input, image):
    if input:
        response = model.generate_content(input, image)
    else:
        response = model.generate_content(image)
    return response.text

## Initialize our streamlit app

st.set_page_config(page_title="Gemini Image Demo")

st.header("Gemini Vision Application")

input = st.text_input("Input Prompt: ",key="input")

uploaded_file = st.file_uploader("Choose an image...",
                                 type=["jpg", "jpeg", "png"])
image = ""
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

submit = st.button("Tell me about the image")

if submit:
    response = get_gemini_response(input, image)
    st.subheader("The Response is")
    st.write(response)

# streamlit run Google_Gemini/01_gemini_vision.py --server.port 5050