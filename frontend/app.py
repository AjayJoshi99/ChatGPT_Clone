import requests
import streamlit as st

BASE_URL = "http://localhost:8000"

session = requests.Session()


if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "selected_conversation" not in st.session_state:
    st.session_state.selected_conversation = None

if "messages" not in st.session_state:
    st.session_state.messages = []


def get_headers():
    if st.session_state.access_token:
        return {
            "Authorization": f"Bearer {st.session_state.access_token}"
        }
    return {}


def login(username, password):

    response = session.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": username,
            "password": password
        }
    )

    if response.status_code == 200:
        data = response.json()

        st.session_state.access_token = data["access_token"]

        return True

    return False


def register(username, email, password):

    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )

    return response


def get_conversations():

    response = session.get(
        f"{BASE_URL}/conversations/",
        headers=get_headers()
    )

    if response.status_code == 200:
        return response.json()

    return []


def create_conversation(title):

    response = session.post(
        f"{BASE_URL}/conversations",
        headers=get_headers(),
        json={
            "title": title
        }
    )

    if response.status_code == 200:
        return response.json()

    return None


def delete_conversation(conversation_id):

    session.delete(
        f"{BASE_URL}/conversations/{conversation_id}",
        headers=get_headers()
    )


def get_messages(conversation_id):

    response = session.get(
        f"{BASE_URL}/conversations/{conversation_id}/messages",
        headers=get_headers()
    )

    if response.status_code == 200:
        return response.json()

    return []


def send_message(conversation_id, message):

    response = session.post(
        f"{BASE_URL}/conversations/{conversation_id}/messages",
        headers=get_headers(),
        json={
            "message": message
        }
    )

    if response.status_code == 200:
        return response.json()

    return None


def upload_document(conversation_id, file):

    files = {
        "file": (
            file.name,
            file,
            "application/pdf"
        )
    }

    response = session.post(
        f"{BASE_URL}/conversations/{conversation_id}/documents",
        headers=get_headers(),
        files=files
    )

    return response


if not st.session_state.access_token:

    st.title("AI Assistant")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:

        username = st.text_input("Username")
        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            success = login(
                username,
                password
            )

            if success:
                st.success("Logged in")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:

        reg_username = st.text_input(
            "Register Username"
        )

        reg_email = st.text_input(
            "Email"
        )

        reg_password = st.text_input(
            "Register Password",
            type="password"
        )

        if st.button("Register"):

            response = register(
                reg_username,
                reg_email,
                reg_password
            )

            if response.status_code == 200:
                st.success("Registered Successfully")
            else:
                st.error(response.text)

    st.stop()


st.sidebar.title("Conversations")

new_title = st.sidebar.text_input(
    "Conversation title"
)

if st.sidebar.button("Create Conversation"):

    create_conversation(new_title)

    st.rerun()

conversations = get_conversations()

for conv in conversations:

    col1, col2 = st.sidebar.columns([4, 1])

    with col1:

        if st.button(
            conv["title"],
            key=f"conv_{conv['id']}"
        ):

            st.session_state.selected_conversation = conv["id"]

            st.session_state.messages = get_messages(
                conv["id"]
            )

            st.rerun()

    with col2:

        if st.button(
            "🗑️",
            key=f"del_{conv['id']}"
        ):

            delete_conversation(
                conv["id"]
            )

            st.rerun()



st.title("AI Chatbot")

if not st.session_state.selected_conversation:

    st.info("Select conversation")

    st.stop()

conversation_id = st.session_state.selected_conversation



with st.expander("Upload PDF"):

    pdf = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if pdf:

        if st.button("Upload"):

            response = upload_document(
                conversation_id,
                pdf
            )

            if response.status_code == 200:

                st.success(
                    "Document uploaded. Processing started."
                )

            else:

                st.error(
                    response.text
                )



if not st.session_state.messages:

    st.session_state.messages = get_messages(
        conversation_id
    )

for msg in st.session_state.messages:

    role = msg["role"]

    with st.chat_message(role):

        st.markdown(
            msg["content"]
        )



prompt = st.chat_input(
    "Ask something..."
)

if prompt:

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.spinner("Thinking..."):

        response = send_message(
            conversation_id,
            prompt
        )

    if response:

        ai_message = response["response"]

        with st.chat_message("assistant"):
            st.markdown(ai_message)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": ai_message
            }
        )

    st.rerun()