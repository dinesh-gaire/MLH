import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image

# Configure the Gemini API key
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except KeyError:
    st.error("Error: GOOGLE_API_KEY environment variable not set.")
    st.info("Please set it before running the app (e.g., in your terminal: export GOOGLE_API_KEY='YOUR_API_KEY').")
    st.stop() # Stop the app if API key is not set

def generate_caption(image_data, caption_style: str) -> str:
    """
    Generates an AI caption for the given image using the Gemini Pro Vision model.
    """
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Craft the prompt based on the desired style
    if caption_style == "Fun":
        prompt = "Generate a fun and lighthearted caption for this image:"
    elif caption_style == "Quirky":
        prompt = "Generate a quirky, imaginative, and slightly unusual caption for this image:"
    else: # Descriptive
        prompt = "Generate a detailed and descriptive caption for this image:"

    try:
        response = model.generate_content([prompt, image_data])
        return response.text
    except Exception as e:
        return f"An error occurred while generating caption: {e}"

st.set_page_config(page_title="AI Image Captioner with Gemini", layout="centered")
st.title("📸 AI Image Captioner")
st.markdown("Upload an image and get AI-generated captions!")

# Image Upload
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Caption Style Selection
    caption_style = st.radio(
        "Choose your caption style:",
        ("Descriptive", "Fun", "Quirky")
    )

    if st.button("Generate Caption"):
        with st.spinner("Generating caption..."):
            caption = generate_caption(image, caption_style)
            st.success("Caption Generated!")
            st.write("---")
            st.subheader(f"{caption_style} Caption:")
            st.write(caption)
            st.write("---")

else:
    st.info("Please upload an image to get started.")

st.markdown("---")
st.markdown("Powered by Google Gemini AI")