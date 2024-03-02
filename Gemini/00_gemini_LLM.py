from dotenv import load_dotenv

load_dotenv() ## Loading environment variables

import os

import google.generativeai as genai
import streamlit as st

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## function to load Gemini Pro model and get responses

model=genai.GenerativeModel("gemini-pro")

def get_gemini_response(question):
    response = model.generate_content(question)
    return response.text

## Initialize our streamlit app

st.set_page_config(page_title="Q&A Demo")

st.header("Gemini LLM Application")

input=st.text_input("Input: ",key="input")
submit = st.button("Ask the question")

if submit:
    response = get_gemini_response(input)
    st.subheader("The Response is")
    st.write(response)

# streamlit run Google_Gemini/00_gemini_LLM.py --server.port 5050