import json
import openai
import streamlit as st
openai.api_key = st.secrets["OPENAI_API_KEY"]

created_style = """
    color: #888888; /* Light gray color */
    font-size: 99px; /* Increased font size */
"""
header_style = """
    text-align: center;
    color: white;
    background-color: #800080;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 30px;
"""

@st.cache_data(show_spinner=False)
def generate_theoretical_questions(topic, number, difficulty):
    "This function will generate a list of questions which will have a number of questions on the related topic."
    system_content = """You are a Question Generator for students who generate a number of theoretical questions on a specific topic given to you by the user which should have a specific dificulty level. The topic of questions, number of questions required and the difficulty level will be given by the user. The difficulty level will be "easy", "medium" "difficult" or "hardest". The user will give the prompt in the following format:
  {topic: "Artificial Intelligence", number = 10, difficulty = "easy"}
  Please keep the following thing in mind:
 Please adhere to the following guidelines:
  1. Ensure that the generated questions are conceptually sound and effectively assess the student's understanding.
  2. You should ask the user only short questions. Keep the questions concise, avoiding lengthy explanations that may lead to verbose answers.
  3. Structure the response in the following format:
   ["Define Artificial Intelligence?", "What is Supervised Machine Learning?", "What is Reinforcement Learning?"]
  4. Difficulty Level Adjustment:
   - Allow for dynamic adjustment of question difficulty based on the user's specified level.
   - Tailor the complexity of questions to align with the chosen difficulty setting.

  5. Randomization:
   - Introduce variability in question generation to present a diverse set of challenges to the user.
   - Prevent repetition of questions within the same session to enhance engagement.
  6_Hardest questions:
   If the use selects the hardest difficulty then generate so much difficult questions that should be almost impossible to answer for a normal student.
  """
    user_content = {f"topic: \"{topic}\", number = \"{number}\", difficulty = \"{difficulty}\""}
    user_content = str(user_content)
    messages = [
        {'role': 'system', 'content': system_content},
        {'role': 'user', 'content': user_content}
    ]
    response = openai.chat.completions.create(
        model='gpt-3.5-turbo-0125', messages=messages)
    return response
#This function will use the openai api to marking the answers of questions and then it will display them the marks
@st.cache_data(show_spinner=False)
def theoretical_answers_checker(answer, question):
    "This function will use the openai api to marking the answers of questions and then it will display them the marks"
    system_content = """You are an answer examiner and answer marker. 
    You will be given the question and the corresponding answer provided by the student.
    These will be theoretical Question/Answers.
    You have to mark the answer between 0 and 10 according to its relevance and correctness.
    The user will input in the following format:
    {question: "Define Artificial Intelligence?", answer: "Artificial intelligence is the science of making machins that can think like humans. It can do things that are considered smarter than humans. It can do anything else that humans can do."}
    And
    Your output format should be as follows:
    {"marks": 7, "mistakes" = "1_There is a spelling mistake in your answer: machins
      2_You write that it can do anything else that humans can do. It is a wrong concept.", "feedback_and_corrections" = "Correction 1: It is machines instead of machins. 
      Correction 2: So far AI is not that much strong and mature that it could do anything which humans can do. It is may be possible in the future but not yet possible."}
    1. Ensure that the answer directly addresses the question asked and provides relevant information.
    2. Consider the clarity and coherence of the answer; deduct marks for vague or unclear responses.
    3. Check for spelling and grammatical errors, and deduct marks accordingly.
    4. Assess the accuracy and correctness of the answer; marks should reflect the degree of correctness.
    5. Don't expect long answers. Concise and comprehensive should be considered good.
    6. Marks will be assigned based on the quality of the answer, with 10 being the highest score for a perfect answer. And if the answer consits nothing relevant give it a zero score.
    7. If the answer is really impressive than you can also give the student a nine or ten(perfect) marks.
    8. If the answer contains factual inaccuracies or misunderstandings then deduct marks accordingly.
    9. Additionally, you will identify any mistakes in the answer, such as spelling mistakes, wrong answers, lack of clarity, or any other discrepancies.
    10. If there are multiple mistakes these should be reported separately with numbering on new lines.
    And also the feedback and corrections should be reported separately with numbering on new lines. 
    11. If there are no mistakes so in mistakes you should return "NIce to see No Mistakes"
    """
    user_content = {f"question: \"{question}\", answer: \"{answer}\""}
    user_content = str(user_content)

    messages = [
        {'role': 'system', 'content': f'{system_content}'},
        {'role': 'user', 'content': f'{user_content}'}
    ]
    response = openai.chat.completions.create(
        model='gpt-3.5-turbo-0125', messages=messages)
    return response

class SessionState:
    def __init__(self):
        self.questions = []
        self.answers = {}

# Initialize session state
session_state = SessionState()

def main():
    # Initialize session state
    st.set_page_config(page_title="Student Examiner APP", page_icon="❓")
    st.markdown("<p style='{}'>➡️created by 'Muhammad Zain Attiq'</p>".format(created_style), unsafe_allow_html=True)
    st.markdown(f"<h1 style='{header_style}'>AI Powered Student Examiner App</h1>", unsafe_allow_html=True)
    with st.expander("About the app:"):
        st.markdown('**What can this app do?**')
        st.info('This app is designed for students to validate their knowledge on any topic. It can generate a number of Questions for you on your desired topic. It also the abilities to mark your answers bw 0 and 10 using the power of AI LLMs.')
        st.markdown('**How to use the app?**')
        st.markdown('''
- To engage with the app:
  1. Enter the topic of your interest in the input text box.
  2. Enter the number of questions you want to have.
  3. Select the difficulty level you want to have in the questions.
  4. The questions will appear on the screen, and below them, an input text box will appear.
  5. In the input text box, you have to write your answer and then press the button "Submit&Check".
  6. The answer will get checked, and the result will be displayed.
''')

    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'answers' not in st.session_state:
        st.session_state.answers = {}

    topic = st.text_input("Enter the topic of the questions: ")
    with st.sidebar:
        number = st.number_input("Enter the number of questions you want: (Max 10)", 1, 10)
        difficulty = st.selectbox("Select the difficulty level: ", ["Easy", "Medium", "Difficult", "Hardest"])

    if st.button("Generate Questions"):
        with st.spinner("Generating questions..."):
            questions = generate_theoretical_questions(topic, number, difficulty)
            questions = questions.choices[0].message.content
            st.session_state.questions = json.loads(questions)

    # Iterate over the questions stored in the session state
    # Iterate over the questions stored in the session state
    for index, question in enumerate(st.session_state.questions):
        st.write("-----------------------------------------------------------------------------")
        st.write(f"Question No {index+1}: ", question)

        answer_key = f"answer_{question}"
        answer = st.text_input("Enter the answer: ", key=answer_key)

        # Store the answer in the session state
        st.session_state.answers[question] = answer

        # Append the question's index to the button's key to make it unique
        if st.button(f"Submit&Check", key=f"submit_check_{index}"):
            with st.spinner(f"Checking your answers..."):
                # Retrieve the answer from the session state
                answer = st.session_state.answers.get(question, "")

                # Call the theoretical_answers_checker function
                result = theoretical_answers_checker(answer, question)
                result = result.choices[0].message.content
                result = json.loads(result)
                st.markdown(f"## Marks: {result['marks']} / 10")
                st.markdown(f"### Mistakes:")
                st.markdown(result['mistakes'])
                st.markdown(f"### Corrections & Feedback :")
                st.markdown(result['feedback_and_corrections'])

if __name__ == "__main__":
    main()
