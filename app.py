import os
import sys
import PyPDF2
import random
import logging
import datetime
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("PDF Quiz Generator Application Using AI")

# Load environment variables
load_dotenv()

# Custom CSS for enhanced UI
def load_custom_css():
    # Get the current theme color
    theme_color = st.session_state.theme_color.lower()
    
    # Define theme color mappings
    theme_colors = {
        "blue": {
            "primary": "#1E3A8A",
            "secondary": "#3B82F6",
            "light": "#EFF6FF",
            "border": "#DBEAFE",
            "gradient_start": "#F0F9FF",
            "gradient_end": "#E6F7FF"
        },
        "purple": {
            "primary": "#4C1D95",
            "secondary": "#8B5CF6",
            "light": "#F5F3FF",
            "border": "#E9D5FF",
            "gradient_start": "#F5F3FF",
            "gradient_end": "#EDE9FE"
        },
        "green": {
            "primary": "#065F46",
            "secondary": "#10B981",
            "light": "#ECFDF5",
            "border": "#D1FAE5",
            "gradient_start": "#ECFDF5",
            "gradient_end": "#D1FAE5"
        }
    }
    
    # Get colors for current theme
    colors = theme_colors.get(theme_color, theme_colors["blue"])
    
    st.markdown(f"""
    <style>
    /* Main styling */
    .main-title {{
        font-size: 42px !important;
        color: {colors["primary"]} !important;
        margin-bottom: 10px !important;
        font-weight: 800 !important;
        text-align: center;
        padding: 20px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }}
    
    .sub-title {{
        font-size: 24px !important;
        color: {colors["secondary"]} !important;
        font-weight: 600 !important;
        margin-bottom: 20px !important;
        text-align: center;
    }}
    
    .card {{
        background-color: #F9FAFB;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }}
    
    .info-box {{
        background-color: {colors["light"]};
        border-left: 5px solid {colors["secondary"]};
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }}
    
    .success-box {{
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }}
    
    .warning-box {{
        background-color: #FFFBEB;
        border-left: 5px solid #F59E0B;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }}
    
    .question-card {{
        background: linear-gradient(135deg, {colors["gradient_start"]} 0%, {colors["gradient_end"]} 100%);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        margin: 20px 0;
        border: 1px solid {colors["border"]};
    }}
    
    .option-selected {{
        background-color: {colors["border"]} !important;
        border-left: 4px solid {colors["secondary"]} !important;
    }}
    
    .result-number {{
        font-size: 60px !important;
        font-weight: 700 !important;
        text-align: center;
        color: {colors["primary"]};
    }}
    
    .result-label {{
        text-align: center;
        font-size: 16px;
        color: #6B7280;
        margin-top: -15px;
    }}
    
    .result-card {{
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin: 10px;
        text-align: center;
        transition: transform 0.2s;
    }}
    
    .result-card:hover {{
        transform: translateY(-5px);
    }}
    
    .stButton>button {{
        width: 100%;
        border-radius: 8px !important;
        height: 3em;
        font-weight: 600 !important;
    }}
    
    /* Beautify the quiz interface */
    div[data-testid="stRadio"] > div {{
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid #E5E7EB;
        transition: all 0.2s;
    }}
    
    div[data-testid="stRadio"] > div:hover {{
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-color: {colors["border"]};
    }}
    
    /* Progress bar styling */
    div.stProgress > div > div > div > div {{
        background-color: {colors["secondary"]} !important;
    }}
    
    /* Banner for top of app */
    .app-banner {{
        background: linear-gradient(135deg, {colors["primary"]} 0%, {colors["secondary"]} 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    
    .banner-text {{
        font-size: 24px;
        font-weight: 600;
    }}
    
    /* Feedback cards */
    .feedback-card {{
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }}
    
    .feedback-title {{
        font-weight: 600;
        color: {colors["primary"]};
        margin-bottom: 10px;
    }}
    
    /* Animated button */
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
        100% {{ transform: scale(1); }}
    }}
    
    .animated-button {{
        animation: pulse 2s infinite;
        background-color: {colors["secondary"]} !important;
        color: white !important;
    }}
    
    /* Sidebar styling */
    .sidebar-title {{
        font-size: 24px;
        font-weight: 700;
        color: {colors["primary"]};
        margin-bottom: 20px;
    }}
    
    .sidebar-subtitle {{
        font-size: 18px;
        font-weight: 600;
        color: {colors["secondary"]};
        margin: 20px 0 10px 0;
    }}
    
    /* File uploader styling */
    div[data-testid="stFileUploader"] {{
        border: 2px dashed {colors["border"]};
        border-radius: 10px;
        padding: 20px;
        background-color: {colors["light"]};
    }}
    
    div[data-testid="stFileUploader"]:hover {{
        border-color: {colors["secondary"]};
    }}
    
    /* Question numbering */
    .question-number {{
        display: inline-block;
        background-color: {colors["secondary"]};
        color: white;
        width: 30px;
        height: 30px;
        text-align: center;
        line-height: 30px;
        border-radius: 50%;
        margin-right: 10px;
    }}
    
    /* Expander styling */
    .streamlit-expanderHeader {{
        background-color: #F3F4F6;
        border-radius: 8px;
        font-weight: 600 !important;
    }}
    
    .streamlit-expanderHeader:hover {{
        background-color: #E5E7EB;
    }}
    
    /* Answer results */
    .correct-answer {{
        color: #10B981;
        font-weight: 600;
    }}
    
    .incorrect-answer {{
        color: #EF4444;
        font-weight: 600;
    }}
    
    /* Button styles */
    .primary-button {{
        background-color: {colors["secondary"]} !important;
        color: white !important;
    }}
    
    .success-button {{
        background-color: #10B981 !important;
        color: white !important;
    }}
    
    .warning-button {{
        background-color: #F59E0B !important;
        color: white !important;
    }}
    
    
    </style>
    """, unsafe_allow_html=True)



class AimockMCQGenerator:
    """A class to generate MCQs from PDF content using OpenAI API."""
    
    def __init__(self):
        # Get API key from environment variable or from session state
        api_key = os.getenv("OPENAI_API_KEY") or st.session_state.get("openai_api_key", "")
       
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
    def extract_text_from_pdf(self, pdf_file):
        """Extract text from a PDF file."""
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            
            # Basic text cleaning
            text = text.replace('\n', ' ').replace('  ', ' ')
            
            if not text.strip():
                logger.warning(f"No text extracted from PDF")
                st.warning("No text could be extracted from the PDF. Please try a different file.")
                return ""
            return text
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            st.error(f"Error reading PDF: {e}")
            return ""

    def generate_mcq(self, content, difficulty="Medium", topic=None):
        """Generate MCQs using OpenAI API with context-aware options."""
        if not content.strip():
            logger.warning("Empty content provided for MCQ generation")
            return None
        
        # Split content into manageable chunks
        paragraphs = content.split(". ")
        filtered_paragraphs = [p for p in paragraphs if len(p.split()) > 10]
        
        if not filtered_paragraphs:
            logger.warning("No suitable paragraphs found for MCQ generation")
            return None
        
        # Select the most informative paragraph
        paragraph = random.choice(filtered_paragraphs) + "."
        
        # Difficulty-based prompting
        difficulty_map = {
            "Easy": {
                "prompt": "Generate straightforward distractors with clear differences from the correct answer",
                "temp": 0.5
            },
            "Medium": {
                "prompt": "Generate moderately challenging distractors that are plausible but incorrect",
                "temp": 0.7
            },
            "Hard": {
                "prompt": "Generate sophisticated distractors that require careful analysis to distinguish from the correct answer",
                "temp": 0.8
            }
        }
        
        difficulty_settings = difficulty_map.get(difficulty, difficulty_map["Medium"])
        topic_prompt = f" focused on the topic of {topic}" if topic else ""
        
        prompt = f"""
        Based on the following paragraph from an educational text{topic_prompt}:
        
        "{paragraph}"
        
        Create a challenging multiple-choice question that tests understanding of a key concept or fact from this paragraph.
        
        Requirements:
        1. The question should be clear, concise, and academically rigorous
        2. Create exactly 4 options labeled a, b, c, and d
        3. One option must be correct and clearly supported by the text
        4. Three options must be incorrect but plausible ({difficulty_settings['prompt']})
        5. All options should be similar in length and structure
        6. Ensure the correct answer isn't always in the same position
        
        Format the response EXACTLY as:
        Question: [Your question]
        a. [Option 1]
        b. [Option 2]
        c. [Option 3]
        d. [Option 4]
        Correct: [just the letter of the correct option, e.g., "a"]
        Explanation: [Brief explanation of why the correct answer is right]
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,  
                messages=[{"role": "user", "content": prompt}],
                max_tokens=350,
                temperature=difficulty_settings['temp']
            )
            result = response.choices[0].message.content.strip()
            
            # Parse the response
            lines = result.split("\n")
            
            # Extract question
            question = ""
            for line in lines:
                if line.startswith("Question:"):
                    question = line.replace("Question:", "").strip()
                    break
            
            if not question:
                logger.warning("Failed to extract question from API response")
                return None
            
            # Extract options
            options = []
            for letter in ['a', 'b', 'c', 'd']:
                option_prefix = f"{letter}."
                for line in lines:
                    if line.lower().startswith(option_prefix):
                        option_text = line[len(option_prefix):].strip()
                        options.append(option_text)
                        break
            
            if len(options) != 4:
                logger.warning(f"Expected 4 options but got {len(options)}")
                return None
            
            # Extract correct answer
            correct_answer = ""
            for line in lines:
                if line.startswith("Correct:"):
                    correct_answer = line.replace("Correct:", "").strip().lower()
                    break
                    
            if not correct_answer or correct_answer not in 'abcd':
                logger.warning(f"Invalid correct answer: {correct_answer}")
                return None
                
            # Extract explanation
            explanation = ""
            for i, line in enumerate(lines):
                if line.startswith("Explanation:"):
                    explanation = line.replace("Explanation:", "").strip()
                    # If explanation continues on next lines
                    j = i + 1
                    while j < len(lines) and not lines[j].startswith(('Question:', 'a.', 'b.', 'c.', 'd.', 'Correct:')):
                        explanation += " " + lines[j].strip()
                        j += 1
                    break
            
            correct_option = options[ord(correct_answer) - ord('a')]
            
            return {
                "question": question,
                "options": options,
                "correct_answer": correct_answer,
                "correct_option": correct_option,
                "explanation": explanation,
                "difficulty": difficulty,
                "paragraph": paragraph,
            }
                
        except Exception as e:
            logger.error(f"Error with OpenAI API: {e}")
            st.error(f"Error generating question: {e}")
            return None

    def generate_ai_feedback(self, questions, user_answers, final_score):
        """Generate personalized AI feedback based on test performance."""
        try:
            # Create summary of performance
            correct_count = sum(1 for i, ans in enumerate(user_answers) 
                              if ans == questions[i]['correct_answer'])
            incorrect_count = len(user_answers) - correct_count
            
            # Identify patterns in wrong answers
            wrong_questions = []
            for i, ans in enumerate(user_answers):
                if ans != questions[i]['correct_answer']:
                    wrong_questions.append({
                        'question': questions[i]['question'],
                        'user_answer': ans,
                        'correct_answer': questions[i]['correct_answer'],
                        'explanation': questions[i].get('explanation', '')
                    })
            
            if not wrong_questions:
                patterns = "You answered all questions correctly!"
            else:
                # Create prompt for AI to analyze wrong answers
                prompt_wrong = f"""
                Based on the following incorrect answers from a multiple-choice test:
                
                {wrong_questions}
                
                Please provide:
                1. A brief analysis of any patterns in the mistakes
                2. 3-4 specific recommendations for improvement
                3. A supportive and encouraging message
                
                Format as:
                Analysis:
                Recommendations:
                Message:
                """
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt_wrong}],
                    max_tokens=350,
                    temperature=0.7
                )
                patterns = response.choices[0].message.content.strip()
            
            # Generate overall feedback based on score
            prompt_feedback = f"""
            You are an encouraging education AI assistant. A student just took a test and scored {final_score}% 
            (got {correct_count} correct and {incorrect_count} wrong out of {len(questions)}).
            
            Please provide constructive, personalized feedback (about 150 words) that:
            1. Acknowledges their effort and current performance level
            2. Offers 2-3 specific strategies to improve their understanding
            3. Ends on a motivational note
            
            Keep the tone supportive and actionable. Focus on learning and growth.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt_feedback}],
                max_tokens=300,
                temperature=0.7
            )
            
            general_feedback = response.choices[0].message.content.strip()
            
            return {
                "patterns": patterns,
                "general_feedback": general_feedback
            }
            
        except Exception as e:
            logger.error(f"Error generating AI feedback: {e}")
            return {
                "patterns": "Unable to generate pattern analysis.",
                "general_feedback": "Thank you for taking the test. Keep practicing to improve your knowledge."
            }

    def create_detailed_report(self, pdf_name, questions, user_answers, final_score):
        """Create a visually appealing PDF report with detailed analytics."""
        # Generate output filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"PDF Quiz Generator Application Using AI_{timestamp}.pdf"
        
        # Generate AI feedback
        feedback = self.generate_ai_feedback(questions, user_answers, final_score)
        
        try:
            # Create document
            doc = SimpleDocTemplate(output_file, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'CustomTitle', 
                parent=styles['Title'],
                fontSize=24,
                spaceAfter=20,
                textColor=colors.darkblue
            )
            
            subtitle_style = ParagraphStyle(
                'SubTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.darkblue,
                spaceAfter=12
            )
            
            section_style = ParagraphStyle(
                'SectionTitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.darkblue,
                spaceBefore=15,
                spaceAfter=10
            )
            
            question_style = ParagraphStyle(
                'QuestionStyle',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=colors.black,
                spaceBefore=15,
                spaceAfter=5
            )
            
            correct_style = ParagraphStyle(
                'CorrectStyle',
                parent=styles['BodyText'],
                fontSize=11,
                textColor=colors.green,
                leftIndent=20
            )
            
            incorrect_style = ParagraphStyle(
                'IncorrectStyle',
                parent=styles['BodyText'],
                fontSize=11,
                textColor=colors.red,
                leftIndent=20
            )
            
            option_style = ParagraphStyle(
                'OptionStyle',
                parent=styles['BodyText'],
                fontSize=11,
                leftIndent=20
            )
            
            explanation_style = ParagraphStyle(
                'ExplanationStyle',
                parent=styles['BodyText'],
                fontSize=10,
                textColor=colors.blue,
                leftIndent=20,
                spaceBefore=5,
                spaceAfter=10
            )
            
            footer_style = ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.gray,
                alignment=1  # Center alignment
            )
            
            feedback_style = ParagraphStyle(
                'FeedbackStyle',
                parent=styles['BodyText'],
                fontSize=11,
                leftIndent=10,
                rightIndent=10,
                spaceBefore=5,
                spaceAfter=5
            )
            
            # Start building the document
            story = []
            
            # Title
            story.append(Paragraph(f"PDF Quiz Generator Application Using AI Assessment Report", title_style))
            story.append(Paragraph(f"Generated from: {pdf_name}", styles["Italic"]))
            
            # Date
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            story.append(Paragraph(f"Date: {current_date}", styles["Normal"]))
            story.append(Spacer(1, 20))
            
            # Performance summary
            story.append(Paragraph("Performance Summary", subtitle_style))
            
            # Create a pie chart for correct vs incorrect
            correct_count = sum(1 for i, ans in enumerate(user_answers) 
                              if ans == questions[i]['correct_answer'])
            incorrect_count = len(user_answers) - correct_count
            
            drawing = Drawing(400, 200)
            pie = Pie()
            pie.x = 150
            pie.y = 50
            pie.width = 100
            pie.height = 100
            pie.data = [correct_count, incorrect_count]
            pie.labels = [f'Correct ({correct_count})', f'Incorrect ({incorrect_count})']
            pie.slices.strokeWidth = 0.5
            pie.slices[0].fillColor = colors.lightgreen
            pie.slices[1].fillColor = colors.lightcoral
            drawing.add(pie)
            story.append(drawing)
            
            # Score summary
            score_data = [
                ['Total Score:', f"{final_score}%"],
                ['Questions Attempted:', f"{len(user_answers)}/{len(questions)}"],
                ['Correct Answers:', f"{correct_count}"],
                ['Incorrect Answers:', f"{incorrect_count}"]
            ]
            
            score_table = Table(score_data, colWidths=[2*inch, 2*inch])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ]))
            story.append(score_table)
            story.append(Spacer(1, 20))
            
            # AI Feedback
            story.append(Paragraph("AI Analysis & Recommendations", subtitle_style))
            
            story.append(Paragraph(feedback['general_feedback'], feedback_style))
            story.append(Spacer(1, 10))
            
            if 'patterns' in feedback and feedback['patterns'] and feedback['patterns'] != "You answered all questions correctly!":
                story.append(Paragraph("Pattern Analysis:", section_style))
                story.append(Paragraph(feedback['patterns'], feedback_style))
            
            story.append(Spacer(1, 20))
            
            # Detailed Question Analysis
            story.append(Paragraph("Detailed Question Analysis", subtitle_style))
            
            for i, q in enumerate(questions, 1):
                user_answer = user_answers[i-1] if i-1 < len(user_answers) else None
                is_correct = user_answer == q['correct_answer'] if user_answer else False
                
                # Question number and text
                story.append(Paragraph(f"Question {i}: {q['question']}", question_style))
                
                # Display each option
                for j, opt in enumerate(q['options']):
                    option_letter = chr(97 + j)
                    is_correct_option = option_letter == q['correct_answer']
                    is_user_option = option_letter == user_answer
                    
                    option_text = f"{option_letter}. {opt}"
                    
                    # Format differently based on correctness
                    if is_correct_option and is_user_option:
                        # User selected correctly
                        story.append(Paragraph(f"✓ {option_text}", correct_style))
                    elif is_correct_option and not is_user_option:
                        # User missed the correct answer
                        story.append(Paragraph(f"✓ {option_text} (Correct Answer)", correct_style))
                    elif not is_correct_option and is_user_option:
                        # User selected incorrectly
                        story.append(Paragraph(f"✗ {option_text} (Your Answer)", incorrect_style))
                    else:
                        # Regular option
                        story.append(Paragraph(option_text, option_style))
                
                # Explanation
                if 'explanation' in q and q['explanation']:
                    story.append(Paragraph(f"Explanation: {q['explanation']}", explanation_style))
                
                story.append(Spacer(1, 10))
            
            # Footer
            story.append(Spacer(1, 30))
            story.append(Paragraph("Generated by PDF Quiz Generator Application Using AI| © 2025", footer_style))
            
            # Build document
            doc.build(story)
            logger.info(f"Detailed report exported to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error creating detailed report: {e}")
            st.error(f"Error creating report: {e}")
            return None


# Initialize session state variables
def init_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'pdf_content' not in st.session_state:
        st.session_state.pdf_content = None
    if 'pdf_name' not in st.session_state:
        st.session_state.pdf_name = None
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY", "")
    if 'theme_color' not in st.session_state:
        st.session_state.theme_color = 'blue'


def go_to_home():
    st.session_state.page = 'home'
    st.session_state.pdf_content = None
    st.session_state.pdf_name = None
    st.session_state.questions = []
    st.session_state.current_question = 0
    st.session_state.user_answers = []


def go_to_setup():
    st.session_state.page = 'setup'


def go_to_test():
    st.session_state.page = 'test'
    st.session_state.current_question = 0
    st.session_state.user_answers = []


def go_to_results():
    st.session_state.page = 'results'


def submit_answer(answer):
    """
    Record the user's answer and move to the next question or results page.
    This updated version ensures the state updates properly when submitting answers.
    """
    # Add the answer to user_answers list
    st.session_state.user_answers.append(answer)
    
    # Move to next question or results page
    if st.session_state.current_question < len(st.session_state.questions) - 1:
        st.session_state.current_question += 1
        # Force a rerun to update the UI immediately
        st.rerun()
    else:
        # When we've reached the last question, go to results
        st.session_state.page = 'results'
        st.rerun()


def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-title">PDF Quiz Generator Application Using AI</div>', unsafe_allow_html=True)
        st.image("https://img.icons8.com/fluency/96/000000/quiz.png", width=80)
        
        st.markdown('<div class="sidebar-subtitle">Navigation</div>', unsafe_allow_html=True)
        
        # Only show navigation when appropriate
        if st.session_state.page != 'home':
            if st.button("🏠 Back to Home", key="home_nav", use_container_width=True):
                go_to_home()
        
        if st.session_state.page == 'results':
            if st.button("🔄 New Quiz (Same PDF)", key="new_quiz_nav", use_container_width=True):
                go_to_setup()
        
        st.markdown('<hr style="margin: 20px 0;">', unsafe_allow_html=True)
        
        # # API Key input with fixed label
        # st.markdown('<div class="sidebar-subtitle">OpenAI API Settings</div>', unsafe_allow_html=True)
        
        # Create a secure container for API key
        api_key_container = st.container()
        
        with api_key_container:
            # If key is not set, show input field
            if not st.session_state.openai_api_key:
                st.markdown("API Key not set. Please enter your OpenAI API key.")
                new_api_key = st.text_input(
                    "OpenAI API Key", 
                    value="",
                    type="password",
                    key="new_api_key_input",
                    placeholder="Enter your OpenAI API key"
                )
                if st.button("Save API Key", key="save_api_key"):
                    if new_api_key:
                        st.session_state.openai_api_key = new_api_key
                        st.rerun()
            # If key is set, just show a confirmation and option to reset
            else:
                st.markdown("✅ API Key is set")
                if st.button("Reset API Key", key="reset_api_key"):
                    st.session_state.openai_api_key = ""
                    st.rerun()
            
        model = st.selectbox(
            "Model",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            index=0,
            key="model_select"
        )
        os.environ["OPENAI_MODEL"] = model
        
        # Theme settings - Fixed to update session state properly
        st.markdown('<div class="sidebar-subtitle">App Settings</div>', unsafe_allow_html=True)
        
        theme_options = ["Blue", "Purple", "Green"]
        theme_index = theme_options.index(st.session_state.theme_color.capitalize()) if st.session_state.theme_color.capitalize() in theme_options else 0
        
        theme = st.selectbox(
            "Theme",
            theme_options,
            index=theme_index,
            key="theme_select"
        )
        
        # Update theme color and immediately apply changes
        if theme.lower() != st.session_state.theme_color:
            st.session_state.theme_color = theme.lower()
            st.rerun()  # Force rerun to apply theme changes
        
        # Help and About
        st.markdown('<hr style="margin: 20px 0;">', unsafe_allow_html=True)
        with st.expander("ℹ️ About"):
            st.markdown("""
            **PDF Quiz Generator Application Using AI** helps you learn more effectively by transforming your study materials into interactive quizzes.
            
            - Upload any PDF document
            - Get AI-generated questions
            - Receive personalized feedback
            - Track your progress over time
            
            Version 2.0 | © 2025
            """)
        
        with st.expander("❓ Help"):
            st.markdown("""
            **Need help?**
            
            1. Make sure your PDF has readable text content
            2. Enter your OpenAI API key in the sidebar
            3. For best results, use PDFs with educational content
            4. Try different difficulty levels to match your knowledge
            
            For more information, contact support@yourpdfyourquiz.com
            """)
        
        st.markdown('<hr style="margin: 20px 0;">', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 12px; color: #6B7280; text-align: center;">© 2025 PDF Quiz Generator Application Using AI</p>', unsafe_allow_html=True)


# Fixed the home page to avoid empty label warnings
def render_home_page():
    # Display app banner
    st.markdown("""
    <div class="app-banner">
        <div class="banner-text">📚 PDF Quiz Generator Application Using AI</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main title with animation
    st.markdown('<h1 class="main-title">Transform Your PDFs into Interactive Quizzes</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Learn faster, remember longer with AI-powered questions</p>', unsafe_allow_html=True)
    
    # Three column feature showcase
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3 style="color: #3B82F6; text-align: center;">📑 Upload Any PDF</h3>
            <p style="text-align: center;">Turn study materials, textbooks, or notes into custom quizzes</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="card">
            <h3 style="color: #3B82F6; text-align: center;">🤖 AI-Generated Questions</h3>
            <p style="text-align: center;">Smart MCQs adapt to your content with customizable difficulty</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="card">
            <h3 style="color: #3B82F6; text-align: center;">📊 Detailed Analysis</h3>
            <p style="text-align: center;">Get personalized feedback and improvement strategies</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Info box with instructions
    st.markdown("""
    <div class="info-box">
        <h3>How It Works:</h3>
        <ol>
            <li>Upload your PDF document</li>
            <li>Customize your quiz settings</li>
            <li>Take the interactive quiz</li>
            <li>Receive AI-powered feedback and a detailed report</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # Animated file uploader section
    st.markdown("<h2 style='text-align: center; margin-top: 30px;'>Start Your Learning Journey</h2>", unsafe_allow_html=True)
    
    # Fixed file uploader with label
    uploaded_file = st.file_uploader("Upload Your PDF", type=["pdf"], key="pdf_uploader")
    
    if uploaded_file is not None:
        # if not st.session_state.openai_api_key:
        #     st.markdown("""
        #     <div class="warning-box">
        #         <h3>API Key Required</h3>
        #         <p>Please enter your OpenAI API key in the sidebar first.</p>
        #     </div>
        #     """, unsafe_allow_html=True)
        #     return
        
        with st.spinner("Extracting content from your PDF..."):
            # Add success animation
            st.markdown("""
            <div style="display: flex; justify-content: center; margin: 20px 0;">
                <img src="https://img.icons8.com/fluency/96/000000/pdf.png" width="80">
            </div>
            """, unsafe_allow_html=True)
            
            generator = AimockMCQGenerator()
            pdf_content = generator.extract_text_from_pdf(uploaded_file)
            
            if pdf_content:
                st.session_state.pdf_content = pdf_content
                st.session_state.pdf_name = uploaded_file.name
                
                st.markdown(f"""
                <div class="success-box">
                    <h3>Success! 🎉</h3>
                    <p>We've successfully extracted content from <b>{uploaded_file.name}</b>.</p>
                    <p>Your PDF is ready to be transformed into a personalized quiz!</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create an animated continue button
                st.markdown("""
                <style>
                .stButton>button.continue-btn {
                    background-color: #2563EB;
                    color: white;
                    font-weight: bold;
                    padding: 0.75rem 1.5rem;
                    border-radius: 0.5rem;
                    border: none;
                    margin-top: 1rem;
                    animation: pulse 2s infinite;
                }
                </style>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.button("Continue to Quiz Setup ➡️", on_click=go_to_setup, key="continue_btn")
            else:
                st.markdown("""
                <div class="warning-box">
                    <h3>Extraction Failed</h3>
                    <p>Could not extract text from the PDF. Please try a different file or ensure the PDF contains readable text.</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Rest of the function remains the same...
    # Testimonials section
    st.markdown("<hr style='margin: 40px 0;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>What Our Users Say</h2>", unsafe_allow_html=True)
    
    test_col1, test_col2, test_col3 = st.columns(3)
    
    with test_col1:
        st.markdown("""
        <div class="card" style="height: 200px;">
            <p style="font-style: italic;">"This tool transformed my study routine. The AI-generated questions really helped me understand complex topics."</p>
            <p style="text-align: right; font-weight: bold;">— Medical Student</p>
        </div>
        """, unsafe_allow_html=True)
        
    with test_col2:
        st.markdown("""
        <div class="card" style="height: 200px;">
            <p style="font-style: italic;">"I use this for my classroom material. My students love the interactive quizzes - engagement has never been higher!"</p>
            <p style="text-align: right; font-weight: bold;">— University Professor</p>
        </div>
        """, unsafe_allow_html=True)
        
    with test_col3:
        st.markdown("""
        <div class="card" style="height: 200px;">
            <p style="font-style: italic;">"The detailed analytics and personalized feedback help me focus my study time on the areas where I need the most improvement."</p>
            <p style="text-align: right; font-weight: bold;">— Graduate Student</p>
        </div>
        """, unsafe_allow_html=True)


def render_setup_page():
    # Display app banner
    st.markdown("""
    <div class="app-banner">
        <div class="banner-text">📚 PDF Quiz Generator Application Using AI</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-title">Customize Your Quiz</h1>', unsafe_allow_html=True)
    
    # File info card
    st.markdown(f"""
    <div class="card" style="background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);">
        <div style="display: flex; align-items: center;">
            <img src="https://img.icons8.com/fluency/48/000000/pdf.png" style="margin-right: 15px;">
            <div>
                <h3 style="margin: 0; color: #1E3A8A;">Selected Document</h3>
                <p style="margin: 5px 0 0 0;">{st.session_state.pdf_name}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Settings card
    st.markdown("""
    <div class="card">
        <h3 style="color: #3B82F6;">Quiz Settings</h3>
        <p>Customize your quiz to match your learning goals</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quiz settings in a nice layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<p style='font-weight: 600; color: #4B5563;'>Number of Questions</p>", unsafe_allow_html=True)
        num_questions = st.slider("", min_value=1, max_value=20, value=5, key="num_questions_slider")
        
        st.markdown("<p style='font-weight: 600; color: #4B5563; margin-top: 20px;'>Focus Topic (Optional)</p>", unsafe_allow_html=True)
        topic = st.text_input("", placeholder="E.g., Photosynthesis, World War II, Machine Learning...", key="topic_input")
    
    with col2:
        st.markdown("<p style='font-weight: 600; color: #4B5563;'>Difficulty Level</p>", unsafe_allow_html=True)
        
        # Custom radio buttons with better styling
        difficulty_options = ["Easy", "Medium", "Hard"]
        difficulty_descriptions = [
            "Basic recall and simple concepts",
            "Application and understanding",
            "Analysis and advanced concepts"
        ]
        
        difficulty = st.radio(
            "",
            difficulty_options,
            format_func=lambda x: f"{x} - {difficulty_descriptions[difficulty_options.index(x)]}",
            index=1,
            key="difficulty_radio"
        )
    
    # Generate test button with animation
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    
    generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
    
    with generate_col2:
        generate_button = st.button("🚀 Generate My Quiz", key="generate_quiz_btn")
        
    if generate_button:
        # if not st.session_state.openai_api_key:
        #     st.markdown("""
        #     <div class="warning-box">
        #         <h3>API Key Required</h3>
        #         <p>Please enter your OpenAI API key in the sidebar first.</p>
        #     </div>
        #     """, unsafe_allow_html=True)
        #     return
            
        with st.spinner(f"Creating your personalized quiz with {num_questions} questions..."):
            generator = AimockMCQGenerator()
            questions = []
            
            # Improved progress tracking
            progress_container = st.container()
            progress_bar = progress_container.progress(0)
            progress_text = progress_container.empty()
            
            for i in range(num_questions):
                progress_text.markdown(f"""
                <div style='text-align: center;'>
                    <p>Generating question {i+1}/{num_questions}</p>
                    <p style='font-size: 12px; color: #6B7280;'>Analyzing content and creating challenging questions...</p>
                </div>
                """, unsafe_allow_html=True)
                
                mcq = generator.generate_mcq(st.session_state.pdf_content, difficulty, topic if topic else None)
                if mcq:
                    questions.append(mcq)
                else:
                    # Try once more
                    mcq = generator.generate_mcq(st.session_state.pdf_content, difficulty, topic if topic else None)
                    if mcq:
                        questions.append(mcq)
                
                progress_bar.progress((i + 1) / num_questions)
            
            progress_text.empty()
            
            if questions:
                st.session_state.questions = questions
                
                # Success animation
                st.balloons()
                
                st.markdown(f"""
                <div class="success-box">
                    <h3>Quiz Generated Successfully! 🎉</h3>
                    <p>Your personalized quiz with {len(questions)} questions is ready to take.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Preview of the first question
                st.markdown("""
                <div class="card question-card">
                    <h4 style="color: #3B82F6;">Sample Question Preview:</h4>
                """, unsafe_allow_html=True)
                
                st.markdown(f"<p><b>{questions[0]['question']}</b></p>", unsafe_allow_html=True)
                
                for i, option in enumerate(questions[0]['options']):
                    st.markdown(f"<p>{chr(97 + i)}. {option}</p>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Start test button
                st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.button("Start Quiz Now ➡️", on_click=go_to_test, key="start_test_btn", type="primary")
            else:
                st.markdown("""
                <div class="warning-box">
                    <h3>Generation Failed</h3>
                    <p>Could not generate questions from the content. Please try different settings or upload a different PDF with more textual content.</p>
                </div>
                """, unsafe_allow_html=True)


def render_test_page():
    # Display app banner with progress
    q_idx = st.session_state.current_question
    total_q = len(st.session_state.questions)
    progress_percent = (q_idx) / total_q
    
    st.markdown(f"""
    <div class="app-banner">
        <div class="banner-text">📝 Question {q_idx + 1} of {total_q}</div>
        <div style="width: 150px; text-align: right;">{int(progress_percent * 100)}% Complete</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    st.progress(progress_percent)
    
    if q_idx < total_q:
        question = st.session_state.questions[q_idx]
        
        # Question card with nice styling
        st.markdown(f"""
        <div class="question-card">
            <span class="question-number">{q_idx + 1}</span>
            <span style="font-size: 20px; font-weight: 600;">{question['question']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Store the current answer in session state
        if f"answer_{q_idx}" not in st.session_state:
            st.session_state[f"answer_{q_idx}"] = ""
        
        # Use radio buttons for options with better styling
        options = {f"{chr(97 + i)}": opt for i, opt in enumerate(question['options'])}
        answer = st.radio(
            "Select your answer:", 
            options.keys(), 
            format_func=lambda x: f"{x}. {options[x]}",
            key=f"radio_{q_idx}"
        )
        
        # Timer element (just visual, not functional in this implementation)
        st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <p style="color: #6B7280; font-size: 14px;">Take your time to consider each option carefully</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create two columns for the submit and skip buttons
        col1, col2 = st.columns([1, 1])
        
        with col1:
            submit_btn = st.button("📝 Submit Answer", key=f"submit_{q_idx}", use_container_width=True)
            if submit_btn:
                submit_answer(answer)
        
        with col2:
            skip_btn = st.button("⏭️ Skip Question", key=f"skip_{q_idx}", use_container_width=True)
            if skip_btn:
                submit_answer("")
        
        # Show difficulty level
        st.markdown(f"""
        <div style="text-align: right; margin-top: 20px;">
            <span style="background-color: #EFF6FF; padding: 5px 10px; border-radius: 20px; font-size: 12px; color: #3B82F6;">
                {question['difficulty']} Difficulty
            </span>
        </div>
        """, unsafe_allow_html=True)


def render_results_page():
    # Calculate score
    questions = st.session_state.questions
    user_answers = st.session_state.user_answers
    correct_count = sum(1 for i, ans in enumerate(user_answers) if ans == questions[i]['correct_answer'])
    total_questions = len(questions)
    final_score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
    
    # Determine performance level and color
    if final_score < 50:
        performance = "Needs Improvement"
        performance_color = "#EF4444"  # Red
    elif final_score < 70:
        performance = "Good"
        performance_color = "#F59E0B"  # Amber
    elif final_score < 90:
        performance = "Very Good"
        performance_color = "#10B981"  # Green
    else:
        performance = "Excellent"
        performance_color = "#047857"  # Dark green
    
    # Display app banner
    st.markdown(f"""
    <div class="app-banner">
        <div class="banner-text">🏆 Quiz Results</div>
        <div style="width: 150px; text-align: right;">Score: {final_score}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Results header with animation
    st.markdown('<h1 class="main-title">Your Performance Analysis</h1>', unsafe_allow_html=True)
    
    # Congratulations card
    st.markdown(f"""
    <div class="card" style="text-align: center; background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);">
        <h2 style="color: {performance_color};">{performance}!</h2>
        <p>You've completed the quiz on {st.session_state.pdf_name}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display score in a visually appealing way
    score_col1, score_col2, score_col3 = st.columns(3)
    
    with score_col1:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-number">{correct_count}/{total_questions}</div>
            <div class="result-label">Correct Answers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with score_col2:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-number">{final_score}%</div>
            <div class="result-label">Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    with score_col3:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-number">{performance}</div>
            <div class="result-label">Overall Rating</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Generate and display AI feedback
    with st.spinner("Generating personalized feedback..."):
        generator = AimockMCQGenerator()
        feedback = generator.generate_ai_feedback(questions, user_answers, final_score)
        
        st.markdown("""
        <div style="margin-top: 40px;">
            <h2 style="color: #3B82F6;">AI-Powered Feedback</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="feedback-card" style="background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);">
            <div style="display: flex; align-items: flex-start;">
                <img src="https://img.icons8.com/color/48/000000/artificial-intelligence.png" style="margin-right: 15px;">
                <div>
                    <div class="feedback-title">Performance Analysis</div>
                    <p>{feedback['general_feedback']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if 'patterns' in feedback and feedback['patterns'] and feedback['patterns'] != "You answered all questions correctly!":
            st.markdown(f"""
            <div class="feedback-card" style="background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);">
                <div style="display: flex; align-items: flex-start;">
                    <img src="https://img.icons8.com/color/48/000000/brain.png" style="margin-right: 15px;">
                    <div>
                        <div class="feedback-title">Learning Pattern Analysis</div>
                        <p>{feedback['patterns']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Question Review
    st.markdown("""
    <div style="margin-top: 40px;">
        <h2 style="color: #3B82F6;">Question Review</h2>
        <p>Review your answers and learn from mistakes</p>
    </div>
    """, unsafe_allow_html=True)
    
    for i, q in enumerate(questions):
        with st.expander(f"Question {i+1}: {q['question']}"):
            user_answer = user_answers[i] if i < len(user_answers) else ""
            
            for j, opt in enumerate(q['options']):
                option_letter = chr(97 + j)
                is_correct_option = option_letter == q['correct_answer']
                is_user_option = option_letter == user_answer
                
                if is_correct_option and is_user_option:
                    st.markdown(f"""
                    <div style="padding: 10px; background-color: #ECFDF5; border-radius: 5px; margin: 5px 0;">
                        <span class="correct-answer">✅ {option_letter}. {opt}</span> (Your answer - Correct)
                    </div>
                    """, unsafe_allow_html=True)
                elif is_correct_option and not is_user_option:
                    st.markdown(f"""
                    <div style="padding: 10px; background-color: #ECFDF5; border-radius: 5px; margin: 5px 0;">
                        <span class="correct-answer">✅ {option_letter}. {opt}</span> (Correct answer)
                    </div>
                    """, unsafe_allow_html=True)
                elif not is_correct_option and is_user_option:
                    st.markdown(f"""
                    <div style="padding: 10px; background-color: #FEF2F2; border-radius: 5px; margin: 5px 0;">
                        <span class="incorrect-answer">❌ {option_letter}. {opt}</span> (Your answer)
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="padding: 10px; background-color: #F9FAFB; border-radius: 5px; margin: 5px 0;">
                        {option_letter}. {opt}
                    </div>
                    """, unsafe_allow_html=True)
            
            if q.get('explanation'):
                st.markdown(f"""
                <div style="padding: 15px; background-color: #EFF6FF; border-radius: 5px; margin-top: 15px;">
                    <p style="font-weight: 600; color: #3B82F6;">Explanation:</p>
                    <p>{q['explanation']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Generate detailed report
    st.markdown("""
    <div style="margin-top: 40px;">
        <h2 style="color: #3B82F6;">Detailed Report</h2>
        <p>Get a comprehensive PDF report of your performance</p>
    </div>
    """, unsafe_allow_html=True)
    
    report_col1, report_col2 = st.columns([1, 2])
    
    with report_col1:
        st.markdown("""
        <img src="https://img.icons8.com/fluency/96/000000/pdf.png" width="80" style="display: block; margin: 0 auto;">
        """, unsafe_allow_html=True)
    
    with report_col2:
        if st.button("📊 Generate Detailed PDF Report", key="generate_report_btn", use_container_width=True):
            with st.spinner("Creating your personalized performance report..."):
                generator = AimockMCQGenerator()
                report_path = generator.create_detailed_report(
                    st.session_state.pdf_name, questions, user_answers, final_score
                )
                
                if report_path:
                    # Read the PDF file
                    with open(report_path, "rb") as file:
                        pdf_data = file.read()
                    
                    # Success animation
                    st.success("Report generated successfully!")
                    
                    # Provide download button
                    st.download_button(
                        label="📥 Download Your Report",
                        data=pdf_data,
                        file_name=os.path.basename(report_path),
                        mime="application/pdf",
                        key="download_report_btn",
                        use_container_width=True
                    )
                else:
                    st.error("Failed to generate report. Please try again.")
    
    # Next steps section
    st.markdown("""
    <div style="margin-top: 40px;">
        <h2 style="color: #3B82F6;">What's Next?</h2>
    </div>
    """, unsafe_allow_html=True)
    
    next_col1, next_col2 = st.columns(2)
    
    with next_col1:
        st.markdown("""
        <div class="card" style="height: 180px;">
            <h3 style="color: #3B82F6; text-align: center;">Try Another Quiz</h3>
            <p style="text-align: center;">Use the same PDF but with different settings</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("New Quiz, Same PDF ↺", on_click=go_to_setup, use_container_width=True)
    
    with next_col2:
        st.markdown("""
        <div class="card" style="height: 180px;">
            <h3 style="color: #3B82F6; text-align: center;">Start Fresh</h3>
            <p style="text-align: center;">Upload a different PDF for a new learning experience</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Back to Home 🏠", on_click=go_to_home, use_container_width=True)


def main():
    # Set page config
    st.set_page_config(
        page_title="PDF Quiz Generator Application Using AI",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Load custom CSS - this will apply the theme
    load_custom_css()
    
    # Render the sidebar with all settings
    render_sidebar()
    
    # Render appropriate page based on session state
    if st.session_state.page == 'home':
        render_home_page()
    elif st.session_state.page == 'setup':
        render_setup_page()
    elif st.session_state.page == 'test':
        render_test_page()
    elif st.session_state.page == 'results':
        render_results_page()


if __name__ == "__main__":
    main()