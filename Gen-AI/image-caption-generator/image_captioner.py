import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

# 1. Configure the Gemini API key
# It's best practice to load the API key from environment variables
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except KeyError:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    print("Please set it before running the script (e.g., export GOOGLE_API_KEY='YOUR_API_KEY').")
    exit()

def generate_image_caption(image_path: str, caption_style: str = "descriptive") -> str:
    """
    Generates an AI caption for the given image using the Gemini Pro Vision model.

    Args:
        image_path (str): The path to the image file.
        caption_style (str): The desired style of the caption. 
                             Options: "descriptive", "fun", "quirky".
    Returns:
        str: The AI-generated caption.
    """
    try:
        # Load the Gemini Pro Vision model
        model = genai.GenerativeModel('gemini-pro-vision')

        # Open the image using Pillow
        img = Image.open(image_path)

        # Craft the prompt based on the desired style
        if caption_style == "fun":
            prompt = "Generate a fun and lighthearted caption for this image:"
        elif caption_style == "quirky":
            prompt = "Generate a quirky, imaginative, and slightly unusual caption for this image:"
        else: # descriptive
            prompt = "Generate a detailed and descriptive caption for this image:"

        # Generate content with the image and text prompt
        response = model.generate_content([prompt, img])

        # Return the generated text
        return response.text

    except FileNotFoundError:
        return f"Error: Image file not found at {image_path}"
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Example Usage:

    # Make sure you have an image file in the same directory or provide its full path
    # For testing, you can download a sample image or use one you have.
    # e.g., create a file named 'sample_image.jpg' in the same directory.
    
    sample_image_path = "sample_image.jpg" # Replace with your image path

    # --- Descriptive Caption ---
    print(f"\n--- Generating Descriptive Caption for {sample_image_path} ---")
    descriptive_caption = generate_image_caption(sample_image_path, "descriptive")
    print(descriptive_caption)

    # --- Fun Caption ---
    print(f"\n--- Generating Fun Caption for {sample_image_path} ---")
    fun_caption = generate_image_caption(sample_image_path, "fun")
    print(fun_caption)

    # --- Quirky Caption ---
    print(f"\n--- Generating Quirky Caption for {sample_image_path} ---")
    quirky_caption = generate_image_caption(sample_image_path, "quirky")
    print(quirky_caption)

    # Example with a non-existent file
    print(f"\n--- Testing with a non-existent image ---")
    non_existent_caption = generate_image_caption("non_existent_image.png")
    print(non_existent_caption)