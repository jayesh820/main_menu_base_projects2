# views/prompt_engineering_views.py
import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Helper for secure API key handling
def get_or_set_api_key():
    """Gets API key from session state, secrets file, or user input."""
    if "google_api_key" not in st.session_state:
        try:
            st.session_state.google_api_key = st.secrets["GOOGLE_API_KEY"]
        except (KeyError, FileNotFoundError):
            st.session_state.google_api_key = None
    return st.session_state.google_api_key

def display_prompt_engineering_tasks():
    st.title("💡 Prompt Engineering Playground")

    if st.button("⬅️ Back to Main Menu", key="back_to_main_prompt"):
        st.session_state.current_view = "main_menu"
        st.session_state.selected_category = None
        st.session_state.selected_pe_sub_category = None
        st.rerun()

    st.markdown("---")
    st.write("### 🔑 Gemini API Key Configuration")
    st.info("To use the Prompt Engineering playground, you must provide your Google API key. This key can be used for the current session or saved securely to `.streamlit/secrets.toml`.")

    # API Key input and saving functionality
    api_key = get_or_set_api_key()
    key_input = st.text_input(
        "Enter your Google API Key:",
        type="password",
        placeholder="AIza...",
        value=api_key if api_key else ""
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Use Key for Session"):
            if key_input and key_input.startswith("AIza"):
                st.session_state.google_api_key = key_input
                st.success("API Key set for the current session.")
                st.rerun()
            else:
                st.error("Please enter a valid Google API key.")
    with col2:
        if st.button("Save Key to Secrets.toml"):
            if key_input and key_input.startswith("AIza"):
                if not os.path.exists(".streamlit"):
                    os.makedirs(".streamlit")
                with open(".streamlit/secrets.toml", "w") as f:
                    f.write(f'GOOGLE_API_KEY = "{key_input}"\n')
                st.session_state.google_api_key = key_input
                st.success("API Key saved to secrets.toml. The application will now use this key.")
                st.rerun()
            else:
                st.error("Please enter a valid Google API key.")

    st.markdown("---")
    st.write("### ✍️ Simple Prompt Interface")

    if not st.session_state.get("google_api_key"):
        st.warning("Please save or enter your Google API key above to enable the Prompt Engineering Playground.")
        return

    # User input for a single, direct prompt
    user_prompt = st.text_area(
        "Enter your prompt here:",
        "Explain the concept of quantum computing in simple terms.",
        height=200
    )

    if st.button("Generate Response"):
        if not user_prompt:
            st.warning("Please enter a prompt.")
            return

        with st.spinner("Generating response..."):
            try:
                # Initialize LLM with Gemini
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7, google_api_key=st.session_state.google_api_key)

                # Create a simple chain with just the user's input
                prompt_template = ChatPromptTemplate.from_template("{user_prompt}")
                chain = LLMChain(llm=llm, prompt=prompt_template)

                # Generate the response
                response = chain.run(user_prompt=user_prompt)
                
                st.write("### LLM's Response:")
                st.info(response)
                
            except Exception as e:
                st.error(f"An error occurred while calling the LLM: {e}")