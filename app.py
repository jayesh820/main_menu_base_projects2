import streamlit as st
import os
import platform
import time
# Import functions from your refactored modules
from views.main_menu import display_main_menu
from views.windows_views import display_windows_sub_menu, display_windows_tasks_detail
from views.linux_views import display_linux_sub_menu, display_linux_tasks_detail
from views.docker_views import display_docker_sub_menu, display_docker_tasks_detail
from views.ml_views import display_ml_sub_menu, display_ml_tasks_detail
from views.kubernetes_local_tasks import display_k8s_sub_menu, display_k8s_tasks_detail
from views.aws_views import display_aws_sub_menu, display_aws_tasks_detail
from views.agentic_ai_views import display_agentic_ai_tasks
from views.prompt_engineering_views import display_prompt_engineering_tasks # NEW IMPORT

# --- Set Page Config (MUST BE THE FIRST STREAMLIT COMMAND) ---
st.set_page_config(
    page_title="Multi-Task Dashboard",
    page_icon="🛠️",
    layout="wide"
)
# --- End Set Page Config ---

# --- GUI Styling ---
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global styles */
* {
    font-family: 'Inter', sans-serif;
}

/* Custom CSS Variables */
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    --warning-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    --info-gradient: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    --dark-gradient: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    --light-gradient: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    --shadow-light: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-medium: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-heavy: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    --border-radius: 16px;
    --border-radius-small: 8px;
}

/* Page background */
.main .block-container {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    min-height: 100vh;
    padding: 2rem;
}

/* Title styling */
h1 {
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
    font-size: 3rem;
    text-align: center;
    margin-bottom: 2rem;
    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h2 {
    background: var(--secondary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 600;
    font-size: 2rem;
    margin-bottom: 1.5rem;
}

h3 {
    color: #2c3e50;
    font-weight: 600;
    font-size: 1.5rem;
    margin-bottom: 1rem;
}

/* Main menu button styling - Enhanced with gradients and modern design */
div.stButton > button {
    background: var(--primary-gradient);
    color: white;
    padding: 2rem 1.5rem;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0.75rem;
    cursor: pointer;
    border-radius: var(--border-radius);
    border: none;
    box-shadow: var(--shadow-medium);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    width: 100%;
    height: 160px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}

div.stButton > button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s;
}

div.stButton > button:hover::before {
    left: 100%;
}

div.stButton > button:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-heavy);
    background: var(--secondary-gradient);
}

/* Sub-category button styling - Modern card design */
.st-emotion-cache-1ds16w3 button {
    background: var(--success-gradient);
    color: white;
    padding: 1.5rem;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 1rem;
    font-weight: 500;
    margin: 0.5rem;
    cursor: pointer;
    border-radius: var(--border-radius);
    border: none;
    box-shadow: var(--shadow-light);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    width: 200px;
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    word-wrap: break-word;
    white-space: normal;
    position: relative;
    overflow: hidden;
}

.st-emotion-cache-1ds16w3 button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s;
}

.st-emotion-cache-1ds16w3 button:hover::before {
    left: 100%;
}

.st-emotion-cache-1ds16w3 button:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: var(--shadow-medium);
    background: var(--warning-gradient);
}

/* Task button styling - Clean and modern */
.st-emotion-cache-1ds16w3 button.task-button {
    background: var(--info-gradient);
    color: #2c3e50;
    padding: 0.75rem 1.5rem;
    font-size: 0.9rem;
    font-weight: 500;
    margin: 0.5rem;
    border-radius: var(--border-radius-small);
    box-shadow: var(--shadow-light);
    transition: all 0.3s ease;
    border: 2px solid transparent;
}

.st-emotion-cache-1ds16w3 button.task-button:hover {
    background: var(--light-gradient);
    transform: translateY(-2px);
    box-shadow: var(--shadow-medium);
    border-color: #667eea;
}

/* Back button styling - Professional design */
.back-button {
    background: var(--dark-gradient) !important;
    color: white !important;
    padding: 0.75rem 1.5rem !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    margin-top: 1.5rem !important;
    border-radius: var(--border-radius-small) !important;
    box-shadow: var(--shadow-light) !important;
    transition: all 0.3s ease !important;
    border: none !important;
}

.back-button:hover {
    background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-medium) !important;
}

/* Enhanced form elements */
.stTextInput > div > div > input {
    border-radius: var(--border-radius-small);
    border: 2px solid #e2e8f0;
    padding: 0.75rem;
    font-size: 0.9rem;
    transition: all 0.3s ease;
}

.stTextInput > div > div > input:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Enhanced selectbox */
.stSelectbox > div > div > div {
    border-radius: var(--border-radius-small);
    border: 2px solid #e2e8f0;
}

/* Enhanced textarea */
.stTextArea > div > div > textarea {
    border-radius: var(--border-radius-small);
    border: 2px solid #e2e8f0;
    padding: 0.75rem;
    font-size: 0.9rem;
}

/* Success, warning, error, info message styling */
.stAlert {
    border-radius: var(--border-radius-small);
    border: none;
    box-shadow: var(--shadow-light);
}

/* Dataframe styling */
.dataframe {
    border-radius: var(--border-radius-small);
    overflow: hidden;
    box-shadow: var(--shadow-light);
}

/* Code block styling */
.stCodeBlock {
    border-radius: var(--border-radius-small);
    border: 2px solid #e2e8f0;
    background: #f8fafc;
}

/* Divider styling */
hr {
    border: none;
    height: 2px;
    background: var(--primary-gradient);
    margin: 2rem 0;
    border-radius: 1px;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: var(--primary-gradient);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--secondary-gradient);
}

/* Loading spinner enhancement */
.stSpinner > div {
    border: 3px solid #f3f3f3;
    border-top: 3px solid #667eea;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Responsive design improvements */
@media (max-width: 768px) {
    h1 {
        font-size: 2rem;
    }
    
    h2 {
        font-size: 1.5rem;
    }
    
    div.stButton > button {
        height: 120px;
        font-size: 1rem;
        padding: 1rem;
    }
    
    .st-emotion-cache-1ds16w3 button {
        width: 150px;
        height: 150px;
        font-size: 0.9rem;
    }
}

/* Animation for page transitions */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.main .block-container {
    animation: fadeIn 0.5s ease-out;
}

/* Enhanced button icons */
button::before {
    margin-right: 0.5rem;
}

/* Custom card styling for content sections */
.content-card {
    background: white;
    border-radius: var(--border-radius);
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: var(--shadow-light);
    border: 1px solid #e2e8f0;
}

/* Enhanced sidebar styling */
.sidebar .sidebar-content {
    background: var(--light-gradient);
}

/* Progress bar styling */
.stProgress > div > div > div {
    background: var(--primary-gradient);
}

/* Metric styling */
.metric-container {
    background: white;
    border-radius: var(--border-radius-small);
    padding: 1rem;
    margin: 0.5rem 0;
    box-shadow: var(--shadow-light);
    border-left: 4px solid #667eea;
}

/* Enhanced checkbox styling */
.stCheckbox > label {
    font-weight: 500;
    color: #2c3e50;
}

/* Enhanced radio button styling */
.stRadio > label {
    font-weight: 500;
    color: #2c3e50;
}

/* File uploader styling */
.stFileUploader > div {
    border-radius: var(--border-radius-small);
    border: 2px dashed #667eea;
    background: #f8fafc;
    transition: all 0.3s ease;
}

.stFileUploader > div:hover {
    border-color: #764ba2;
    background: #f1f5f9;
}

/* Enhanced multiselect styling */
.stMultiSelect > div > div > div {
    border-radius: var(--border-radius-small);
    border: 2px solid #e2e8f0;
}

/* Number input styling */
.stNumberInput > div > div > input {
    border-radius: var(--border-radius-small);
    border: 2px solid #e2e8f0;
    padding: 0.75rem;
}

/* Date input styling */
.stDateInput > div > div > input {
    border-radius: var(--border-radius-small);
    border: 2px solid #e2e8f0;
    padding: 0.75rem;
}

/* Time input styling */
.stTimeInput > div > div > input {
    border-radius: var(--border-radius-small);
    border: 2px solid #e2e8f0;
    padding: 0.75rem;
}

/* Enhanced expander styling */
.streamlit-expanderHeader {
    background: var(--light-gradient);
    border-radius: var(--border-radius-small);
    font-weight: 600;
    color: #2c3e50;
}

/* Enhanced tabs styling */
.stTabs > div > div > div > div {
    background: var(--light-gradient);
    border-radius: var(--border-radius-small);
}

.stTabs > div > div > div > div[data-baseweb="tab"] {
    font-weight: 500;
    color: #2c3e50;
}

/* Enhanced columns spacing */
.row-widget.stHorizontal {
    gap: 1rem;
}

/* Enhanced container spacing */
.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
}

/* Enhanced markdown styling */
.markdown-text-container {
    line-height: 1.6;
    color: #374151;
}

/* Enhanced code styling */
.code-block {
    background: #1f2937;
    color: #f9fafb;
    padding: 1rem;
    border-radius: var(--border-radius-small);
    font-family: 'Courier New', monospace;
    overflow-x: auto;
}

/* Enhanced table styling */
table {
    border-radius: var(--border-radius-small);
    overflow: hidden;
    box-shadow: var(--shadow-light);
}

th {
    background: var(--primary-gradient);
    color: white;
    font-weight: 600;
    padding: 1rem;
}

td {
    padding: 0.75rem;
    border-bottom: 1px solid #e5e7eb;
}

tr:hover {
    background: #f9fafb;
}
</style>
""", unsafe_allow_html=True)
# --- End GUI Styling ---

def main():
    """Main function to run the Streamlit application."""
    # Initialize session state for navigation
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'main_menu'

    # Initialize session state for categories and sub-categories
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = None
    if 'selected_sub_category' not in st.session_state:
        st.session_state.selected_sub_category = None
    if 'selected_ml_sub_category' not in st.session_state:
        st.session_state.selected_ml_sub_category = None
    if 'selected_k8s_sub_category' not in st.session_state:
        st.session_state.selected_k8s_sub_category = None
    if 'selected_aws_sub_category' not in st.session_state:
        st.session_state.selected_aws_sub_category = None
    if 'selected_ai_sub_category' not in st.session_state:
        st.session_state.selected_ai_sub_category = None
    if 'selected_pe_sub_category' not in st.session_state: # New Prompt Engineering state
        st.session_state.selected_pe_sub_category = None


    # Initialize session state for ML dataframes and models
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'filtered_df' not in st.session_state:
        st.session_state.filtered_df = None
    if 'best_trained_model' not in st.session_state:
        st.session_state.best_trained_model = None
    if 'loaded_model' not in st.session_state:
        st.session_state.loaded_model = None

    # Initialize SSH connection details (moved here for consistency)
    if 'ssh_connected' not in st.session_state:
        st.session_state.ssh_connected = False
    if 'ssh_host' not in st.session_state:
        st.session_state.ssh_host = ""
    if 'ssh_username' not in st.session_state:
        st.session_state.ssh_username = ""
    if 'ssh_password' not in st.session_state:
        st.session_state.ssh_password = ""
    # Local kubectl readiness flag
    if 'kubectl_local_ready' not in st.session_state:
        st.session_state.kubectl_local_ready = False


    if st.session_state.current_view == 'main_menu':
        display_main_menu()
    elif st.session_state.current_view == 'windows_sub_menu':
        display_windows_sub_menu()
    elif st.session_state.current_view == 'linux_sub_menu':
        display_linux_sub_menu()
    elif st.session_state.current_view == 'docker_sub_menu':
        display_docker_sub_menu()
    elif st.session_state.current_view == 'ml_sub_menu':
        display_ml_sub_menu()
    elif st.session_state.current_view == 'k8s_sub_menu':
        display_k8s_sub_menu()
    elif st.session_state.current_view == 'aws_sub_menu':
        display_aws_sub_menu()
    elif st.session_state.current_view == 'ai_sub_menu':
        display_agentic_ai_tasks()
    elif st.session_state.current_view == 'pe_sub_menu':
        display_prompt_engineering_tasks()
    elif st.session_state.current_view == 'windows_tasks_detail':
        display_windows_tasks_detail()
    elif st.session_state.current_view == 'linux_tasks_detail':
        display_linux_tasks_detail()
    elif st.session_state.current_view == 'docker_tasks_detail':
        display_docker_tasks_detail()
    elif st.session_state.current_view == 'ml_tasks_detail':
        display_ml_tasks_detail()
    elif st.session_state.current_view == 'k8s_tasks_detail':
        display_k8s_tasks_detail()
    elif st.session_state.current_view == 'aws_tasks_detail':
        display_aws_tasks_detail()

if __name__ == "__main__":
    main()