# views/agentic_ai_views.py
import streamlit as st
import subprocess
import os
import platform
import time
import json
import boto3
import pandas as pd
from datetime import datetime
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI # Correct import for Gemini
from langchain_core.tools import tool
from langchain_experimental.tools.python.tool import PythonREPLTool

# Helper for secure API key handling
def get_or_set_api_key():
    """Gets API key from session state, secrets file, or user input."""
    if "google_api_key" not in st.session_state:
        try:
            st.session_state.google_api_key = st.secrets["GOOGLE_API_KEY"]
        except (KeyError, FileNotFoundError):
            st.session_state.google_api_key = None
    return st.session_state.google_api_key

# --- Agent Tools ---
@tool
def run_powershell_command(command: str) -> str:
    """Executes a PowerShell command on the local Windows machine.
    Use this for tasks like getting system info, managing services, or file operations.
    Input should be a valid PowerShell command string, e.g., 'Get-Service'.
    """
    try:
        if not platform.system() == 'Windows':
            return "This tool is for Windows only."
        result = subprocess.run(
            ["powershell.exe", "-Command", command],
            capture_output=True, text=True, check=True, timeout=30
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error executing PowerShell command: {e.stderr}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool
def run_aws_command(service_name: str, method_name: str, params: str = '{}') -> str:
    """Executes a boto3 command for a specified AWS service.
    
    Use this to interact with AWS APIs. Input should be the service name, method name,
    and a dictionary of parameters.
    
    Args:
        service_name: The name of the AWS service (e.g., 's3', 'ec2', 'lambda').
        method_name: The boto3 client method to call (e.g., 'list_buckets', 'describe_instances').
        params: A dictionary of parameters for the method.
        
    Returns:
        The JSON string representation of the API response.
        
    Example:
        run_aws_command('ec2', 'describe_instances', '{"Filters": [{"Name": "instance-state-name", "Values": ["running"]}]}')
    """
    try:
        aws_client = boto3.client(service_name)
        method = getattr(aws_client, method_name)
        
        # Check if params is a string and try to parse it into a dictionary
        if isinstance(params, str):
            try:
                parsed_params = json.loads(params)
            except json.JSONDecodeError:
                return f"Error: The 'params' argument is an invalid JSON string. Please provide a valid dictionary representation. Received: {params}"
        else:
            parsed_params = params
            
        response = method(**parsed_params)
        
        def json_serial(obj):
            if isinstance(obj, (bytes, datetime)):
                return str(obj)
            raise TypeError ("Type %s not serializable" % type(obj))
        
        return json.dumps(response, default=json_serial, indent=2)
    except Exception as e:
        return f"Error executing AWS command: {e}"

@tool
def run_kubectl_command(command: str) -> str:
    """Executes a kubectl command on the local machine.
    
    This tool requires kubectl to be installed and configured on the local system.
    Use this to interact with Kubernetes clusters.
    
    Args:
        command: The kubectl command to run (without 'kubectl'), e.g., 'get pods'.
        
    Returns:
        The output of the command or an error message.
    """
    try:
        result = subprocess.run(
            f"kubectl {command}",
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error executing kubectl command: {e.stderr}"
    except FileNotFoundError:
        return "kubectl not found in PATH."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """Sends an email to a specified recipient.
    
    This tool requires SMTP settings to be pre-configured on the host machine.
    
    Args:
        recipient: The email address of the recipient.
        subject: The subject line of the email.
        body: The body content of the email.
    
    Returns:
        A success or failure message.
    """
    if "@" in recipient:
        return f"Simulated: Email with subject '{subject}' sent to {recipient}."
    else:
        return "Invalid email recipient format."

@tool
def get_current_date() -> str:
    """Returns the current date and time."""
    return f"Current date and time is: {time.strftime('%Y-%m-%d %H:%M:%S')}"


# --- Agentic AI UI ---
def display_agentic_ai_tasks():
    st.title("🤖 Agentic AI")

    if st.button("⬅️ Back to Main Menu", key="back_to_main_ai"):
        st.session_state.current_view = "main_menu"
        st.session_state.selected_category = None
        st.session_state.selected_ai_sub_category = None
        st.rerun()
    
    st.markdown("---")
    st.write("### 🔑 Gemini API Key Configuration")
    st.info("To use the AI agent, you must provide your Google API key. This key can be used for the current session or saved securely to `.streamlit/secrets.toml`.")
    
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
    st.write("### 🧠 Run AI Agent")
    
    if not st.session_state.get("google_api_key"):
        st.warning("Please save or enter your Google API key above to enable the AI agent.")
        return

    # Initialize LLM now that key is available
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, google_api_key=st.session_state.google_api_key)

    # Define the list of tools the agent can use
    tools = [
        run_powershell_command,
        run_aws_command,
        run_kubectl_command,
        send_email,
        PythonREPLTool(),
    ]
    
    # Define the Agent's Prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a powerful AI assistant with access to various tools for managing system tasks. Your goal is to help the user by executing tasks using the available tools. Be concise and provide a clear final answer."),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    # Construct and run the agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # UI for user interaction
    with st.form(key="agent_form"):
        user_prompt = st.text_area(
            "Enter your task for the AI Agent:",
            placeholder="e.g., Get a list of all S3 buckets and send the list via email to test@example.com."
        )
        submit_button = st.form_submit_button(label="Run AI Agent")

    if submit_button and user_prompt:
        with st.spinner("Thinking and executing tasks..."):
            try:
                response = agent_executor.invoke({"input": user_prompt})
                st.success("✅ Task Completed!")
                st.write("### Agent's Final Answer:")
                st.write(response["output"])
            except Exception as e:
                st.error(f"An error occurred during agent execution: {e}")
    
    st.markdown("---")
    st.write("### Example Tasks:")
    st.markdown("""
    * "What is the current time and date?"
    * "Get a list of all S3 buckets in my account."
    * "Get a list of all Kubernetes pods in the current namespace."
    * "Run the powershell command 'Get-Process | Select-Object -First 5'."
    * "List all EC2 instances and send the list to test@example.com with the subject 'EC2 Instance Report'."
    """)