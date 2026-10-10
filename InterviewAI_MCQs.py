
import os
import json
import re
from pathlib import Path
from datetime import datetime

import streamlit as st

# ==================================================
# CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="InterviewAI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

APP_DIR = Path(__file__).parent
HISTORY_FILE = APP_DIR / "interview_history.json"
MODEL_NAME = "gemini-3.8-flash"

# ==================================================
# INTERVIEW QUESTIONS
# ==================================================

QUESTION_BANK = {
    "Python Developer": [
        ("What is Python?", ["A compiled-only language", "A high-level interpreted programming language", "A database", "An operating system"], 1, "Python is a high-level interpreted language."),
        ("Which data type is mutable?", ["Tuple", "String", "List", "Integer"], 2, "Lists can be changed after creation."),
        ("What does == compare?", ["Object identity", "Value equality", "Memory address only", "Variable names"], 1, "== checks whether values are equal."),
        ("What does the is operator compare?", ["Value equality", "Object identity", "Data types only", "String length"], 1, "is checks whether two references point to the same object."),
        ("Which keyword defines a function?", ["func", "function", "def", "define"], 2, "Python functions are defined with def."),
        ("Which block handles an exception?", ["catch", "except", "error", "final"], 1, "except handles exceptions raised in a try block."),
        ("How is a dictionary organized?", ["Indexed values only", "Key-value pairs", "Rows and columns", "A sequence of characters"], 1, "Dictionaries map keys to values.")
    ],
    "Java Developer": [
        ("Why is Java considered platform independent?", ["It runs without any runtime", "Bytecode runs on a JVM", "It only runs in browsers", "It is interpreted by HTML"], 1, "Java bytecode can run on compatible JVM implementations."),
        ("What does JVM stand for?", ["Java Variable Method", "Java Virtual Machine", "Joint Virtual Memory", "Java Verified Mode"], 1, "JVM means Java Virtual Machine."),
        ("Which is NOT one of the four OOP pillars?", ["Encapsulation", "Inheritance", "Compilation", "Polymorphism"], 2, "Compilation is not an OOP pillar; abstraction is the fourth pillar."),
        ("What is method overloading?", ["Same method name with different parameter lists", "Deleting a method", "Changing a class name", "Calling a method repeatedly"], 0, "Overloaded methods share a name but differ in parameters."),
        ("Which keyword is commonly used to handle an exception?", ["try", "check", "error", "throws-only"], 0, "A try block encloses code that may throw an exception."),
        ("What is an interface mainly used for?", ["Storing object data only", "Defining a contract for implementing classes", "Replacing the JVM", "Creating packages automatically"], 1, "An interface defines methods/constants that implementing classes agree to provide."),
        ("What is a constructor used for?", ["Destroying a class", "Initializing a new object", "Compiling a package", "Handling network requests only"], 1, "A constructor initializes an object when it is created.")
    ],
    "Web Developer": [
        ("What does HTML primarily define?", ["Page structure and content", "Database permissions", "Server hardware", "Network routing"], 0, "HTML structures the content of a web page."),
        ("What is CSS used for?", ["Styling page elements", "Querying databases", "Compiling Java", "Encrypting passwords"], 0, "CSS controls presentation and layout."),
        ("What is JavaScript commonly used for on websites?", ["Adding interactivity and behavior", "Replacing all network protocols", "Creating only images", "Managing computer BIOS"], 0, "JavaScript can make web pages interactive."),
        ("What is responsive web design?", ["A site that adapts to different screen sizes", "A site that only works on phones", "A faster database", "A type of encryption"], 0, "Responsive design adapts layouts to different devices and viewports."),
        ("What does API stand for?", ["Application Programming Interface", "Applied Program Internet", "Automated Page Index", "Application Process Integration"], 0, "An API defines how software components communicate."),
        ("What is the main difference between HTTP and HTTPS?", ["HTTPS adds TLS-based security", "HTTP is always faster and encrypted", "HTTPS cannot transfer pages", "There is no difference"], 0, "HTTPS protects HTTP communication using TLS."),
        ("What does the DOM represent?", ["A structured object model of a document", "A domain hosting plan", "A database backup", "A programming language"], 0, "The DOM represents page elements as objects that scripts can access.")
    ],
    "Cyber Security": [
        ("What is authentication?", ["Checking a user's identity", "Assigning file permissions", "Compressing data", "Deleting logs"], 0, "Authentication verifies identity."),
        ("What is authorization?", ["Verifying identity", "Determining permitted actions or resources", "Encrypting every file", "Updating software"], 1, "Authorization determines what an authenticated user is allowed to do."),
        ("What is phishing?", ["A fraudulent attempt to trick people into revealing information", "A secure backup method", "A network cable type", "A software update"], 0, "Phishing commonly uses deceptive messages or websites."),
        ("What does encryption do?", ["Converts readable data into protected ciphertext", "Deletes a password", "Creates a user account", "Improves screen resolution"], 0, "Encryption transforms plaintext into ciphertext using a method and key."),
        ("What is a firewall designed to do?", ["Filter network traffic according to rules", "Create spreadsheets", "Repair hardware", "Replace all passwords"], 0, "Firewalls control network traffic based on configured rules."),
        ("In asymmetric cryptography, which keys are used?", ["One shared key only", "A public/private key pair", "No keys", "A different password for every byte"], 1, "Asymmetric cryptography uses related public and private keys."),
        ("What is multi-factor authentication?", ["Using two or more different categories of verification", "Using the same password twice", "Changing a username", "Disabling login checks"], 0, "MFA combines distinct factor types, such as knowledge and possession.")
    ],
    "Data Analyst": [
        ("What is data analysis?", ["Examining data to find patterns and insights", "Deleting every data point", "Writing only web pages", "Installing an operating system"], 0, "Data analysis helps derive insights that support decisions."),
        ("What is the mean?", ["The middle value after sorting", "The most frequent value", "The sum of values divided by their count", "The largest value"], 2, "The arithmetic mean is the total divided by the number of values."),
        ("What is the median?", ["The middle value in sorted data", "The total of all values", "The most frequent value", "The range"], 0, "The median is the central value after sorting."),
        ("What is data cleaning?", ["Finding and correcting missing, duplicate, or inconsistent data", "Making charts colorful", "Encrypting every record", "Deleting all outliers automatically"], 0, "Data cleaning improves data quality and consistency."),
        ("Which SQL clause filters rows before grouping?", ["HAVING", "WHERE", "ORDER BY", "COUNT"], 1, "WHERE filters rows before GROUP BY aggregation."),
        ("Which chart is generally suitable for comparing categories?", ["Bar chart", "Line chart only", "Map only", "Word cloud only"], 0, "Bar charts make category comparisons clear."),
        ("What is a primary key?", ["A field that uniquely identifies each record", "A field that always contains duplicate values", "A chart title", "A temporary filter"], 0, "A primary key uniquely identifies rows in a table.")
    ]
}

# ==================================================
# GEMINI EVALUATION
# ==================================================

def evaluate_answer(question, answer, keywords, difficulty, focus):
    """Evaluate an interview answer with Gemini."""

    if not answer.strip():
        return {
            "score": 0,
            "grade": "Not answered",
            "matched": [],
            "feedback": "No answer was provided.",
            "suggestion": "Try answering in your own words.",
            "model": MODEL_NAME
        }

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Save the key in Windows "
            "and restart Streamlit from a new PowerShell window."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are a fair technical interview evaluator.

Evaluate the candidate's answer accurately and constructively.

Question: {question}
Candidate answer: {answer}
Difficulty: {difficulty}
Interview focus: {focus}
Relevant concepts: {", ".join(keywords)}

Scoring guidelines:
- Score from 0 to 100 based on technical correctness, relevance,
  explanation, and completeness.
- Do not reward length alone.
- Do not require every listed concept if the answer is otherwise correct.
- Do not invent information about the candidate.
- Give specific, respectful feedback.
- Return only JSON matching this structure:
{{
  "score": 0,
  "grade": "Excellent",
  "matched": ["concepts actually demonstrated"],
  "feedback": "Specific feedback about the answer",
  "suggestion": "A concrete way to improve the answer"
}}

The grade should be one of:
Excellent, Good, Needs improvement, Weak answer.
The score must be an integer between 0 and 100.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.2,
                "max_output_tokens": 700
            }
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        result = json.loads(response.text)

        score = max(0, min(100, int(result["score"])))
        grade = str(result.get("grade", "Evaluated"))
        matched = result.get("matched", [])
        feedback = str(result.get("feedback", "No feedback returned."))
        suggestion = str(
            result.get("suggestion", "Try adding a practical example.")
        )

        if not isinstance(matched, list):
            matched = []

        return {
            "score": score,
            "grade": grade,
            "matched": matched,
            "feedback": feedback,
            "suggestion": suggestion,
            "model": MODEL_NAME
        }

    except Exception as exc:
        # Preserve the actual error category for troubleshooting.
        raise RuntimeError(
            f"Gemini evaluation failed: {type(exc).__name__}: {exc}"
        ) from exc

# ==================================================

# AUTHENTICATION AND HISTORY STORAGE
import sqlite3
import hashlib
import hmac
import secrets

DB_FILE = APP_DIR / "interviewai.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users "
            "(email TEXT PRIMARY KEY, salt TEXT NOT NULL, "
            "password_hash TEXT NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS interview_history "
            "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "email TEXT NOT NULL, record_json TEXT NOT NULL)"
        )

def make_password_hash(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"),
        bytes.fromhex(salt), 300000
    ).hex()

def register_user(email, password):
    email = email.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return "Enter a valid email address."
    if len(password) < 8:
        return "Password must contain at least 8 characters."
    salt = secrets.token_hex(16)
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                "INSERT INTO users VALUES (?, ?, ?)",
                (email, salt, make_password_hash(password, salt))
            )
        return None
    except sqlite3.IntegrityError:
        return "An account with this email already exists."

def authenticate_user(email, password):
    email = email.strip().lower()
    with sqlite3.connect(DB_FILE) as conn:
        row = conn.execute(
            "SELECT salt, password_hash FROM users WHERE email = ?",
            (email,)
        ).fetchone()
    if row and hmac.compare_digest(
        make_password_hash(password, row[0]), row[1]
    ):
        return email
    return None

def load_history(email):
    if not email:
        return []
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute(
            "SELECT record_json FROM interview_history "
            "WHERE email = ? ORDER BY id",
            (email,)
        ).fetchall()
    return [json.loads(row[0]) for row in rows]

def save_history(history, email):
    if not email:
        raise ValueError("Guest history must not be saved.")
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "DELETE FROM interview_history WHERE email = ?", (email,)
        )
        conn.executemany(
            "INSERT INTO interview_history (email, record_json) "
            "VALUES (?, ?)",
            [
                (email, json.dumps(item, ensure_ascii=False))
                for item in history
            ]
        )

init_db()

if "auth_user" not in st.session_state:
    st.session_state.auth_user = None

if st.session_state.auth_user is None:
    st.title("🎯 InterviewAI")
    st.subheader("Sign in or practise as a guest")
    sign_in_tab, create_tab = st.tabs(["Sign in", "Create account"])

    with sign_in_tab:
        with st.form("auth_sign_in"):
            email_in = st.text_input("Gmail address or email")
            password_in = st.text_input("Password", type="password")
            submit_sign_in = st.form_submit_button("Sign in")
        if submit_sign_in:
            account = authenticate_user(email_in, password_in)
            if account:
                st.session_state.auth_user = {
                    "mode": "account", "email": account
                }
                st.session_state.history = load_history(account)
                st.rerun()
            else:
                st.error("Email or password is incorrect.")

    with create_tab:
        with st.form("auth_create"):
            new_email = st.text_input("Email address")
            new_password = st.text_input(
                "Create password (8+ characters)", type="password"
            )
            confirm_password = st.text_input(
                "Confirm password", type="password"
            )
            submit_create = st.form_submit_button("Create account")
        if submit_create:
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                message = register_user(new_email, new_password)
                if message:
                    st.error(message)
                else:
                    st.success("Account created. Please sign in.")

    if st.button("Continue as Guest", type="secondary"):
        st.session_state.auth_user = {"mode": "guest"}
        st.session_state.history = []
        st.rerun()
    st.stop()

user = st.session_state.auth_user
if "history" not in st.session_state:
    st.session_state.history = (
        load_history(user["email"])
        if user["mode"] == "account" else []
    )

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "answers" not in st.session_state:
    st.session_state.answers = []
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "interview_active" not in st.session_state:
    st.session_state.interview_active = False
if "saved_current_interview" not in st.session_state:
    st.session_state.saved_current_interview = False

# SIDEBAR
# ==================================================

st.sidebar.title("🎯 InterviewAI")
st.sidebar.caption("Smart Interview Practice")
st.sidebar.caption(
    "Guest mode" if user["mode"] == "guest"
    else "Signed in: " + user["email"]
)
if st.sidebar.button("Log out / Exit"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
st.sidebar.divider()

pages = ["Dashboard", "New Interview", "Interview", "Results", "History"]

selected_page = st.sidebar.radio(
    "Navigation",
    pages,
    index=pages.index(st.session_state.page)
)

if selected_page != st.session_state.page:
    st.session_state.page = selected_page

st.sidebar.divider()
st.sidebar.caption("Evaluation model: Gemini")
st.sidebar.caption(f"Model: {MODEL_NAME}")

if os.getenv("GEMINI_API_KEY"):
    st.sidebar.success("Gemini key detected")
else:
    st.sidebar.warning("Gemini key not detected")

# ==================================================
# DASHBOARD
# ==================================================

if st.session_state.page == "Dashboard":
    st.title("🎯 InterviewAI")
    st.subheader("Practice. Improve. Get interview-ready.")

    st.write(
        "Prepare for technical interviews with role-based questions, "
        "AI feedback, scores, and interview history."
    )

    history = st.session_state.history
    completed_scores = [
        item.get("average_score")
        for item in history
        if isinstance(item.get("average_score"), (int, float))
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric("Interviews Completed", len(history))
    col2.metric(
        "Average Score",
        f"{sum(completed_scores) / len(completed_scores):.1f}/100"
        if completed_scores else "N/A"
    )
    col3.metric("Available Roles", len(QUESTION_BANK))

    st.divider()
    st.subheader("Available Roles")

    cols = st.columns(3)
    for index, role in enumerate(QUESTION_BANK):
        with cols[index % 3]:
            st.markdown(f"### {role}")
            st.caption(f"{len(QUESTION_BANK[role])} questions")

    if st.button("Start a New Interview", type="primary"):
        st.session_state.page = "New Interview"
        st.rerun()

# ==================================================
# NEW INTERVIEW
# ==================================================

elif st.session_state.page == "New Interview":
    st.title("📝 New Interview")
    st.write("Configure your interview before starting.")

    with st.form("interview_setup"):
        role = st.selectbox("Choose your role", list(QUESTION_BANK.keys()))
        difficulty = st.selectbox(
            "Difficulty", ["Easy", "Medium", "Hard"]
        )
        question_count = st.selectbox(
            "Number of questions", [3, 5, 7], index=1
        )
        focus = st.selectbox(
            "Focus area",
            [
                "General technical knowledge",
                "Fundamentals",
                "Practical application"
            ]
        )

        start = st.form_submit_button("Start Interview", type="primary")

    if start:
        st.session_state.role = role
        st.session_state.difficulty = difficulty
        st.session_state.focus = focus
        st.session_state.questions = QUESTION_BANK[role][:question_count]
        st.session_state.answers = []
        st.session_state.current_question = 0
        st.session_state.interview_active = True
        st.session_state.saved_current_interview = False
        st.session_state.page = "Interview"
        st.rerun()

# ==================================================
# INTERVIEW
# ==================================================

elif st.session_state.page == "Interview":
    st.title("💬 Interview")

    if not st.session_state.interview_active:
        st.info("There is no active interview.")
        if st.button("Set Up an Interview"):
            st.session_state.page = "New Interview"
            st.rerun()
    else:
        questions = st.session_state.questions
        index = st.session_state.current_question
        total = len(questions)

        if index >= total:
            st.session_state.page = "Results"
            st.rerun()

        question, options, correct_index, explanation = questions[index]

        st.caption(
            f"{st.session_state.role} · "
            f"{st.session_state.difficulty} difficulty"
        )
        st.progress((index + 1) / total)
        st.write(f"Question {index + 1} of {total}")
        st.subheader(question)

        with st.form(f"answer_form_{index}"):
            selected_option = st.radio(
                "Choose one answer:",
                options,
                index=None,
                key=f"mcq_answer_{index}"
            )
            submitted = st.form_submit_button(
                "Submit Answer", type="primary"
            )

        if submitted:
            if selected_option is None:
                st.warning("Please select an option before continuing.")
            else:
                selected_index = options.index(selected_option)
                is_correct = selected_index == correct_index
                evaluation = {
                    "score": 100 if is_correct else 0,
                    "grade": "Correct" if is_correct else "Incorrect",
                    "matched": ["Correct option"] if is_correct else [],
                    "feedback": (
                        "Correct! " + explanation if is_correct
                        else "Not quite. " + explanation
                    ),
                    "suggestion": (
                        "Great work. Continue to the next question."
                        if is_correct
                        else "Review the explanation and remember the correct concept."
                    ),
                    "model": "MCQ answer key"
                }

                st.session_state.answers.append({
                    "question": question,
                    "answer": selected_option,
                    "correct_answer": options[correct_index],
                    "evaluation": evaluation
                })

                st.session_state.current_question += 1

                if st.session_state.current_question >= total:
                    st.session_state.page = "Results"

                st.rerun()

# ==================================================
# RESULTS
# ==================================================

elif st.session_state.page == "Results":
    st.title("📊 Interview Results")

    answers = st.session_state.answers

    if not answers:
        st.info("No evaluated answers are available yet.")
        if st.button("Start an Interview"):
            st.session_state.page = "New Interview"
            st.rerun()
    else:
        scores = [item["evaluation"]["score"] for item in answers]
        average = round(sum(scores) / len(scores), 1)

        col1, col2, col3 = st.columns(3)
        col1.metric("Average Score", f"{average}/100")
        col2.metric(
            "Questions Evaluated",
            f"{len(answers)}/{len(st.session_state.questions)}"
        )
        col3.metric("Gemini Evaluations", f"{len(answers)}/{len(answers)}")

        st.progress(average / 100)
        st.caption(f"Evaluation model: {MODEL_NAME}")

        st.subheader("Answer Review")

        for i, item in enumerate(answers, start=1):
            evaluation = item["evaluation"]

            with st.expander(
                f"Question {i} · {evaluation['score']}/100 · "
                f"{evaluation['grade']}"
            ):
                st.markdown("**Question**")
                st.write(item["question"])

                st.markdown("**Your Answer**")
                st.write(item["answer"] or "No answer provided.")

                st.markdown("**Gemini Feedback**")
                st.write(evaluation["feedback"])

                st.markdown("**Concepts Demonstrated**")
                matched = evaluation.get("matched", [])
                st.write(", ".join(map(str, matched)) if matched else "None listed")

                st.markdown("**Suggested Improvement**")
                st.write(evaluation["suggestion"])

        if not st.session_state.saved_current_interview:
            if st.button("Finish Guest Interview" if user["mode"] == "guest" else "Save Results to History", type="primary"):
                record = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "role": st.session_state.role,
                    "difficulty": st.session_state.difficulty,
                    "focus": st.session_state.focus,
                    "question_count": len(answers),
                    "average_score": average,
                    "answers": answers
                }

                try:
                    if user["mode"] == "guest":
                        st.session_state.saved_current_interview = True
                        st.session_state.interview_active = False
                        st.info("Guest results are temporary and were not saved.")
                    else:
                        st.session_state.history.append(record)
                        save_history(
                            st.session_state.history, user["email"]
                        )
                        st.session_state.saved_current_interview = True
                        st.session_state.interview_active = False
                        st.success("Results saved to your account history.")
                    st.rerun()
                except (OSError, sqlite3.Error, ValueError) as exc:
                    st.error(f"Could not save history: {exc}")
                    if user["mode"] == "account" and st.session_state.history:
                        st.session_state.history.pop()

        else:
            st.success("This interview has been saved to history.")

        if st.button("Start Another Interview"):
            st.session_state.interview_active = False
            st.session_state.page = "New Interview"
            st.rerun()

# ==================================================
# HISTORY
# ==================================================

elif st.session_state.page == "History":
    st.title("📚 Interview History")

    history = st.session_state.history

    if not history:
        st.info("No saved interviews yet.")
    else:
        for record in reversed(history):
            with st.expander(
                f"{record.get('date', 'Unknown date')} · "
                f"{record.get('role', 'Unknown role')} · "
                f"{record.get('average_score', 0)}/100"
            ):
                st.write(f"**Difficulty:** {record.get('difficulty', 'N/A')}")
                st.write(f"**Focus:** {record.get('focus', 'N/A')}")
                st.write(f"**Questions:** {record.get('question_count', 0)}")

                for i, item in enumerate(record.get("answers", []), start=1):
                    evaluation = item.get("evaluation", {})
                    st.markdown(
                        f"**Question {i}:** {item.get('question', '')}"
                    )
                    st.write(
                        f"Score: {evaluation.get('score', 'N/A')}/100"
                    )
                    st.write(
                        f"Feedback: {evaluation.get('feedback', '')}"
                    )

# ==================================================
# FOOTER
# ==================================================

st.sidebar.divider()
st.sidebar.caption("InterviewAI · Powered by Google Gemini")
