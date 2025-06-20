import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import textwrap # For formatting output

# --- Configuration ---
# Load API key from environment variable
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except KeyError:
    st.error("Error: GOOGLE_API_KEY environment variable not set.")
    st.info("Please set it before running the app (e.g., export GOOGLE_API_KEY='YOUR_API_KEY' or set GOOGLE_API_KEY=...).")
    st.stop() # Stop the app if API key is not set

# --- Lesson Plan Generation Function (from previous section) ---
def generate_lesson_plan(
    topic: str,
    grade_level: str,
    duration: str,
    learning_style: str = "standard",
    additional_notes: str = ""
) -> str:
    model = genai.GenerativeModel('gemini-2.0-flash')

    base_prompt = f"""
    You are an expert educator and curriculum designer. Your task is to generate a comprehensive and engaging lesson plan based on the following details.

    **Topic:** {topic}
    **Grade Level:** {grade_level}
    **Duration:** {duration}
    """

    style_prompt = ""
    if learning_style == "Active Learning":
        style_prompt = "Emphasize active student participation, group work, and hands-on activities."
    elif learning_style == "Project-Based":
        style_prompt = "Design the lesson around a central project or investigation, with students building or creating something."
    elif learning_style == "Inquiry-Based":
        style_prompt = "Focus on student-led questions, exploration, and discovery."
    elif learning_style == "Discussion-Heavy":
        style_prompt = "Structure the lesson around facilitated discussions and debates."
    else: # "Standard" or default
        style_prompt = "Provide a balanced lesson plan suitable for a general classroom setting."

    notes_prompt = f"Additional notes/requirements: {additional_notes}" if additional_notes else ""

    full_prompt = f"""
    {base_prompt}
    **Learning Style Emphasis:** {style_prompt}
    {notes_prompt}

    Please structure the lesson plan clearly with the following sections using Markdown formatting:

    ## Lesson Plan: [Your Suggested Lesson Title]

    ### 1. Learning Objectives
    * [List 3-5 clear, measurable learning objectives (e.g., "Students will be able to explain...", "Students will be able to identify...")]

    ### 2. Materials and Resources
    * [List all necessary materials, e.g., whiteboard, markers, handouts, projector, specific websites/videos, physical objects]

    ### 3. Introduction (Engage) - [Suggested Time: X min]
    * [Brief activity or discussion to hook students and activate prior knowledge]

    ### 4. Direct Instruction (Explore/Explain) - [Suggested Time: X min]
    * [Core content delivery, key concepts, explanations]

    ### 5. Guided Practice (Elaborate) - [Suggested Time: X min]
    * [Activities where students practice with teacher support, e.g., group work, guided exercises]

    ### 6. Independent Practice (Evaluate) - [Suggested Time: X min]
    * [Activities where students apply knowledge independently, e.g., worksheets, short assignments]

    ### 7. Assessment
    * [How student understanding will be checked (formative/summative, e.g., quick quiz, observation, exit ticket, project rubric)]

    ### 8. Differentiation Strategies
    * [Ideas for supporting struggling learners and challenging advanced learners]

    ### 9. Homework/Extension Activities (Optional)
    * [Suggestions for follow-up work or deeper exploration]

    Ensure the suggested times for each section add up approximately to the total lesson duration.
    """
    
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while generating the lesson plan: {e}"

# --- Streamlit App Layout ---

st.set_page_config(page_title="AI-Powered Lesson Plan Generator", layout="wide")
st.title("📚 AI-Powered Lesson Plan Generator")
st.markdown("Generate comprehensive lesson plans based on your topic and preferences using GenAI!")

# Initialize session state for lesson plan text if it doesn't exist
if 'lesson_plan_text' not in st.session_state:
    st.session_state.lesson_plan_text = ""
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = ""


# Input fields for lesson plan details
with st.form("lesson_plan_form"):
    topic = st.text_input("Lesson Topic (e.g., 'The Water Cycle', 'Algebraic Equations', 'Shakespearean Sonnets')", "The Solar System")
    
    col1, col2 = st.columns(2)
    with col1:
        grade_level = st.selectbox(
            "Target Grade Level:",
            ["Kindergarten", "1st Grade", "2nd Grade", "3rd Grade", "4th Grade", "5th Grade",
             "6th Grade", "7th Grade", "8th Grade", "High School (General)", "High School (Specific Subject e.g. Biology, Chemistry, etc.)", "College/University"]
        )
    with col2:
        duration = st.text_input("Lesson Duration (e.g., '45 minutes', '2 hours', 'One Class Period')", "50 minutes")
    
    learning_style = st.selectbox(
        "Preferred Learning Style/Approach:",
        ["Standard", "Active Learning", "Project-Based", "Inquiry-Based", "Discussion-Heavy"],
        help="Choose a pedagogical approach to emphasize in the lesson plan."
    )
    
    additional_notes = st.text_area(
        "Any additional notes or specific requirements?",
        "e.g., 'Include a hands-on activity.', 'Focus on real-world applications.', 'Keep language simple for ESL students.'"
    )

    submitted = st.form_submit_button("Generate Lesson Plan")

    if submitted:
        if not topic or not grade_level or not duration:
            st.error("Please fill in the Topic, Grade Level, and Duration.")
        else:
            with st.spinner("Generating your lesson plan... This might take a moment."):
                generated_plan = generate_lesson_plan(
                    topic=topic,
                    grade_level=grade_level,
                    duration=duration,
                    learning_style=learning_style,
                    additional_notes=additional_notes
                )
            # Store the generated plan and topic in session state
            st.session_state.lesson_plan_text = generated_plan
            st.session_state.current_topic = topic
            st.rerun() # Rerun to display the generated plan and download button outside the form

# Display the lesson plan and download button outside the form, conditioned on content
if st.session_state.lesson_plan_text:
    st.subheader("Generated Lesson Plan:")
    # Use st.markdown with a code block for better readability of the generated Markdown
    st.markdown(st.session_state.lesson_plan_text)
    
    # Place the download button outside the form
    st.download_button(
        label="Download Lesson Plan as Markdown",
        data=st.session_state.lesson_plan_text,
        file_name=f"{st.session_state.current_topic.replace(' ', '_').lower()}_lesson_plan.md",
        mime="text/markdown"
    )

st.markdown("---")
st.markdown("Powered by Google Gemini AI")
