# Multi-Task Dashboard

This Streamlit application provides a multi-purpose dashboard for managing Windows, Linux, Docker, Machine Learning, Kubernetes, and AWS tasks through a user-friendly interface.

## Project Structure

multi_task_dashboard/
├── app.py                     # Main Streamlit application entry point
├── utils/
│   ├── init.py            # Makes utils a Python package
│   └── ssh_utils.py           # Contains SSH command execution logic
├── views/
│   ├── init.py            # Makes views a Python package
│   ├── main_menu.py           # Defines the main category selection menu
│   ├── windows_views.py       # Contains all Windows-specific sub-menus and tasks
│   ├── linux_views.py         # Contains all Linux-specific sub-menus and tasks (SSH based)
│   ├── docker_views.py        # Contains all Docker-specific sub-menus and tasks (SSH based)
│   ├── ml_views.py            # Contains all Machine Learning related sub-menus and tasks
│   ├── kubernetes_local_tasks.py # Contains local Kubernetes tasks using kubectl
│   └── aws_views.py           # Contains AWS service-specific tasks using boto3
└── requirements.txt         # Lists all required Python packages


## Setup and Installation

1.  **Clone the repository (or create the file structure manually):**
    ```bash
    git clone <your-repo-link> # Replace with your actual repo link if applicable
    cd multi_task_dashboard
    ```
    (If you're creating files manually, ensure the directory structure above is replicated.)

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    * On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    * On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Install optional libraries for full functionality:**
    Some functionalities (like webcam access, system monitoring, WhatsApp messages, SSH, XGBoost, LightGBM) require additional libraries. Install them if you need those features:
    ```bash
    pip install twilio pyautogui opencv-python psutil wmi pywhatkit paramiko xgboost lightgbm
    ```
    * **Note for `wmi`**: `wmi` is a Windows-specific library. It will fail to install on non-Windows systems. This is expected.
    * **Note for `paramiko`**: SSH functionality relies on `paramiko` (for Linux/Docker sections).
    * **Note for `opencv-python`**: For Camera tasks on Windows.

## How to Run

From the `multi_task_dashboard` directory (where `app.py` is located), run the Streamlit application:

```bash
streamlit run app.py