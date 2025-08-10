import streamlit as st
import paramiko

def execute_ssh_command(host, username, password, command):
    """Executes a command over SSH and returns stdout and stderr."""
    if not paramiko:
        return "", "Paramiko library not found. Please install it with `pip install paramiko`."

    try:
        with st.spinner(f"Executing '{command}' on {host}..."):
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=host, username=username, password=password, timeout=10)

            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()

            client.close()
            return output, error
    except paramiko.AuthenticationException:
        return "", "Authentication failed. Please check your username and password."
    except paramiko.SSHException as ssh_err:
        return "", f"SSH connection error: {ssh_err}. Ensure SSH server is running and accessible (e.g., SSH service is active, firewall allows port 22)."
    except Exception as e:
        return "", f"An unexpected error occurred during SSH command execution: {e}"