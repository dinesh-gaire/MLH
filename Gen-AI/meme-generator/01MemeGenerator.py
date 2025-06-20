import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_meme_caption(topic):
    """
    Generates a humorous meme caption using the Google Gemini API.
    """
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"Generate a short, witty, and humorous meme caption about '{topic}' in two parts. Just return the top text and bottom text as two lines, without labels like 'Top text' or 'Bottom text'."
    response = model.generate_content(prompt)
    return response.text

import requests

def get_popular_meme_templates():
    """
    Fetches popular meme templates from the Imgflip API.
    """
    url = "https://api.imgflip.com/get_memes"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']['memes']
    else:
        return None


from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap

def create_meme(image_url, top_text, bottom_text, font_path="impact.ttf", font_size=50):
    """
    Creates a meme by adding top and bottom text to an image.
    """
    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        draw = ImageDraw.Draw(img)

        try:
            # Try to load the Impact font
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            # If Impact font is not found, use the default font
            print("Impact font not found. Using default font.")
            font = ImageFont.load_default(size=font_size)

        img_width, img_height = img.size

        # Function to draw text with a black outline for better readability
        def draw_text_with_outline(draw_object, text, x, y, font, fill_color, outline_color):
            # Draw outline
            draw_object.text((x-2, y-2), text, font=font, fill=outline_color)
            draw_object.text((x+2, y-2), text, font=font, fill=outline_color)
            draw_object.text((x-2, y+2), text, font=font, fill=outline_color)
            draw_object.text((x+2, y+2), text, font=font, fill=outline_color)
            # Draw text fill
            draw_object.text((x, y), text, font=font, fill=fill_color)

        # Wrap text to fit the image width
        wrapper = textwrap.TextWrapper(width=25)

        # --- Top Text ---
        top_lines = wrapper.wrap(top_text.upper())
        y_text = 10
        for line in top_lines:
            # --- THIS IS THE FIX ---
            # Get the bounding box of the text
            bbox = font.getbbox(line)
            line_width = bbox[2] - bbox[0]  # width = right - left
            line_height = bbox[3] - bbox[1] # height = bottom - top
            # ----------------------
            x = (img_width - line_width) / 2
            draw_text_with_outline(draw, line, x, y_text, font, "white", "black")
            y_text += line_height + 5 # Add a small gap between lines

        # --- Bottom Text ---
        bottom_lines = wrapper.wrap(bottom_text.upper())
        # Calculate the total height of the bottom text block to position it correctly
        total_bottom_text_height = sum([(font.getbbox(line)[3] - font.getbbox(line)[1]) + 5 for line in bottom_lines])
        y_text = img_height - total_bottom_text_height - 15

        for line in bottom_lines:
            # --- THIS IS THE FIX ---
            bbox = font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
            # ----------------------
            x = (img_width - line_width) / 2
            draw_text_with_outline(draw, line, x, y_text, font, "white", "black")
            y_text += line_height + 5

        # Save the final meme
        img.save("meme.png")
        print("\n Meme created successfully as meme.png!")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    topic = input("Enter a topic for your meme: ")
    print("Generating a witty caption for your meme...")
    caption = generate_meme_caption(topic)

    if caption:
        try:
            top_text, bottom_text = caption.split('\n', 1)
        except ValueError:
            top_text = caption
            bottom_text = ""

        print(f"\nGenerated Caption:\nTop: {top_text}\nBottom: {bottom_text}\n")

        print("Fetching popular meme templates...")
        templates = get_popular_meme_templates()

        if templates:
            print("Please choose a meme template by entering its number:")
            for i, template in enumerate(templates[:10]):  # Display top 10 templates
                print(f"{i+1}. {template['name']}")

            try:
                choice = int(input("Enter your choice (1-10): ")) - 1
                if 0 <= choice < 10:
                    selected_template_url = templates[choice]['url']
                    print(f"Creating your meme with the '{templates[choice]['name']}' template...")
                    create_meme(selected_template_url, top_text, bottom_text)
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        else:
            print("Could not fetch meme templates.")
    else:
        print("Could not generate a meme caption.")