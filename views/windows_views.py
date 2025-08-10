import streamlit as st
import os
import shutil
import subprocess
import smtplib
from email.mime.text import MIMEText
import webbrowser
import zipfile
import time
import platform
import pandas as pd

# Conditional imports
try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import psutil
except ImportError:
    psutil = None

# WMI is Windows-specific and might not be available
try:
    import wmi
except ImportError:
    wmi = None

try:
    import pywhatkit
except ImportError:
    pywhatkit = None

# Twilio imports for SMS and Call (add this to requirements.txt if used)
# from twilio.rest import Client


def display_windows_system_info_tasks():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 2rem; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 2rem;">
        <h3 style="color: #1e293b; margin-bottom: 1rem; display: flex; align-items: center;">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">📊</span>
            System Information & Monitoring
        </h3>
        <p style="color: #64748b; margin-bottom: 0;">Monitor your system performance and get detailed information about your Windows environment.</p>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced OS Information section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 1rem;">
            <h4 style="color: #1e293b; margin-bottom: 1rem; display: flex; align-items: center;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">💻</span>
                System Information
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Get OS Information", key="get_os_info_btn"):
            st.markdown("""
            <div style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #3b82f6; margin: 1rem 0;">
                <h5 style="color: #1e40af; margin-bottom: 1rem;">System Details</h5>
            </div>
            """, unsafe_allow_html=True)
            st.write(f"**Operating System:** {os.name}")
            st.write(f"**Platform:** {platform.system()} {platform.release()} ({platform.version()})")
            st.write(f"**Machine:** {platform.machine()}")
            st.write(f"**Processor:** {platform.processor()}")
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 1rem;">
            <h4 style="color: #1e293b; margin-bottom: 1rem; display: flex; align-items: center;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">📈</span>
                Performance Monitoring
            </h4>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Monitor CPU & RAM Usage", key="monitor_cpu_ram_btn"):
            if psutil:
                cpu_percent = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory()
                
                # Enhanced display with progress bars and better styling
                st.markdown("""
                <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #22c55e; margin: 1rem 0;">
                    <h5 style="color: #166534; margin-bottom: 1rem;">Performance Metrics</h5>
                </div>
                """, unsafe_allow_html=True)
                
                # CPU Usage with progress bar
                st.markdown(f"""
                <div style="margin: 1rem 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="font-weight: 600; color: #1e293b;">CPU Usage</span>
                        <span style="font-weight: 600; color: #1e293b;">{cpu_percent}%</span>
                    </div>
                    <div style="background: #e2e8f0; border-radius: 8px; height: 8px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #3b82f6, #1d4ed8); height: 100%; width: {cpu_percent}%; transition: width 0.3s ease;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # RAM Usage with progress bar
                st.markdown(f"""
                <div style="margin: 1rem 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="font-weight: 600; color: #1e293b;">RAM Usage</span>
                        <span style="font-weight: 600; color: #1e293b;">{ram.percent}%</span>
                    </div>
                    <div style="background: #e2e8f0; border-radius: 8px; height: 8px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #10b981, #059669); height: 100%; width: {ram.percent}%; transition: width 0.3s ease;"></div>
                    </div>
                    <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #64748b;">
                        Used: {ram.used / (1024**3):.2f} GB / Total: {ram.total / (1024**3):.2f} GB
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("`psutil` not found. Install with `pip install psutil` for this functionality.")

        if st.button("List Running Processes", key="list_processes_btn"):
            if psutil:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f59e0b; margin: 1rem 0;">
                    <h5 style="color: #92400e; margin-bottom: 1rem;">Running Processes (Top 20 by CPU)</h5>
                </div>
                """, unsafe_allow_html=True)
                
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                    try:
                        pinfo = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_info'])
                        pinfo['memory_mb'] = pinfo['memory_info'].rss / (1024 * 1024)
                        processes.append(pinfo)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass

                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
                df = pd.DataFrame(processes[:20]).drop(columns=['memory_info'])
                
                # Enhanced dataframe display
                st.markdown("""
                <div style="background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                """, unsafe_allow_html=True)
                st.dataframe(df, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("`psutil` not found. Install with `pip install psutil` for this functionality.")


def display_windows_file_folder_operations_tasks():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 2rem; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 2rem;">
        <h3 style="color: #1e293b; margin-bottom: 1rem; display: flex; align-items: center;">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">📁</span>
            File & Folder Operations
        </h3>
        <p style="color: #64748b; margin-bottom: 0;">Manage files and folders on your Windows system with powerful automation tools.</p>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced form section
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 2rem;">
        <h4 style="color: #1e293b; margin-bottom: 1.5rem; display: flex; align-items: center;">
            <span style="font-size: 1.2rem; margin-right: 0.5rem;">⚙️</span>
            Configuration
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.text_input("Base Path (Server-side)", key="base_file_path_input", value=os.getcwd(), 
                  help="Set the base directory for file operations")

    # Enhanced folder creation section
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 2rem;">
        <h4 style="color: #1e293b; margin-bottom: 1.5rem; display: flex; align-items: center;">
            <span style="font-size: 1.2rem; margin-right: 0.5rem;">📂</span>
            Create New Folder
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    new_folder_name = st.text_input("New Folder Name", key="create_folder_name_file_ops", 
                                   placeholder="Enter folder name...")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Create New Folder", key="create_folder_btn"):
            if new_folder_name:
                try:
                    folder_path = os.path.join(st.session_state.base_file_path_input, new_folder_name)
                    os.makedirs(folder_path, exist_ok=True)
                    st.success(f"✅ Folder '{folder_path}' created successfully!")
                except Exception as e:
                    st.error(f"❌ Error creating folder: {e}")
            else:
                st.warning("⚠️ Please enter a folder name.")

    # Enhanced delete operations section
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 2rem;">
        <h4 style="color: #1e293b; margin-bottom: 1.5rem; display: flex; align-items: center;">
            <span style="font-size: 1.2rem; margin-right: 0.5rem;">🗑️</span>
            Delete Operations
        </h4>
        <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;">
            ⚠️ <strong>Warning:</strong> This action cannot be undone. Please be careful when deleting files or folders.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    delete_path_input = st.text_input("File/Folder to Delete (Full Path)", key="delete_path_input_file_ops",
                                     placeholder="Enter full path to file or folder...",
                                     help="Provide the complete path to the file or folder you want to delete")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Delete File/Folder", key="delete_file_folder_btn"):
            if delete_path_input:
                try:
                    if os.path.isfile(delete_path_input):
                        os.remove(delete_path_input)
                        st.success(f"✅ File '{delete_path_input}' deleted successfully!")
                    elif os.path.isdir(delete_path_input):
                        shutil.rmtree(delete_path_input)
                        st.success(f"✅ Folder '{delete_path_input}' and its contents deleted successfully!")
                    else:
                        st.warning("⚠️ Path does not exist or is not a file/folder.")
                except Exception as e:
                    st.error(f"❌ Error deleting: {e}")
            else:
                st.warning("⚠️ Please enter a path to delete.")

    # Enhanced copy operations section
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 2rem;">
        <h4 style="color: #1e293b; margin-bottom: 1.5rem; display: flex; align-items: center;">
            <span style="font-size: 1.2rem; margin-right: 0.5rem;">📋</span>
            Copy Operations
        </h4>
        <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;">
            Copy files and folders to new locations while preserving the original.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        source_path_copy = st.text_input("Source Path to Copy", key="source_copy_file_ops",
                                        placeholder="Enter source file/folder path...",
                                        help="Path to the file or folder you want to copy")
    with col2:
        destination_path_copy = st.text_input("Destination Path for Copy", key="dest_copy_file_ops",
                                             placeholder="Enter destination path...",
                                             help="Path where you want to copy the file/folder")
    
    if st.button("Copy File/Folder", key="copy_file_folder_btn"):
        if source_path_copy and destination_path_copy:
            try:
                if os.path.isfile(source_path_copy):
                    shutil.copy2(source_path_copy, destination_path_copy)
                    st.success(f"✅ File '{source_path_copy}' copied to '{destination_path_copy}' successfully!")
                elif os.path.isdir(source_path_copy):
                    shutil.copytree(source_path_copy, destination_path_copy)
                    st.success(f"✅ Folder '{source_path_copy}' copied to '{destination_path_copy}' successfully!")
                else:
                    st.warning("⚠️ Source path does not exist or is not a file/folder.")
            except Exception as e:
                st.error(f"❌ Error copying: {e}")
        else:
            st.warning("⚠️ Please enter source and destination paths.")

    # Enhanced move operations section
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 2rem;">
        <h4 style="color: #1e293b; margin-bottom: 1.5rem; display: flex; align-items: center;">
            <span style="font-size: 1.2rem; margin-right: 0.5rem;">🚚</span>
            Move Operations
        </h4>
        <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;">
            Move files and folders to new locations (original will be removed).
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        source_path_move = st.text_input("Source Path to Move", key="source_move_file_ops",
                                        placeholder="Enter source file/folder path...",
                                        help="Path to the file or folder you want to move")
    with col2:
        destination_path_move = st.text_input("Destination Path for Move", key="dest_move_file_ops",
                                             placeholder="Enter destination path...",
                                             help="Path where you want to move the file/folder")
    
    if st.button("Move File/Folder", key="move_file_folder_btn"):
        if source_path_move and destination_path_move:
            try:
                shutil.move(source_path_move, destination_path_move)
                st.success(f"✅ '{source_path_move}' moved to '{destination_path_move}' successfully!")
            except Exception as e:
                st.error(f"❌ Error moving: {e}")
        else:
            st.warning("⚠️ Please enter source and destination paths.")

    # Enhanced rename operations section
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 2rem;">
        <h4 style="color: #1e293b; margin-bottom: 1.5rem; display: flex; align-items: center;">
            <span style="font-size: 1.2rem; margin-right: 0.5rem;">✏️</span>
            Rename Operations
        </h4>
        <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;">
            Rename files and folders with new names.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        old_name = st.text_input("Old Name (Full Path)", key="old_name_file_ops",
                                placeholder="Enter current file/folder path...",
                                help="Current path and name of the file or folder")
    with col2:
        new_name = st.text_input("New Name (Full Path)", key="new_name_file_ops",
                                placeholder="Enter new file/folder path...",
                                help="New path and name for the file or folder")
    
    if st.button("Rename File/Folder", key="rename_file_folder_btn"):
        if old_name and new_name:
            try:
                os.rename(old_name, new_name)
                st.success(f"✅ '{old_name}' renamed to '{new_name}' successfully!")
            except Exception as e:
                st.error(f"❌ Error renaming: {e}")
        else:
            st.warning("⚠️ Please enter old and new names.")

    # Enhanced file search section
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 2rem;">
        <h4 style="color: #1e293b; margin-bottom: 1.5rem; display: flex; align-items: center;">
            <span style="font-size: 1.2rem; margin-right: 0.5rem;">🔍</span>
            File Search
        </h4>
        <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;">
            Search for files by name or extension within a directory.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        search_path = st.text_input("Search Path (e.g., C:\\)", key="search_path_input_file_ops", value=os.getcwd())
    with col2:
        search_term = st.text_input("Search Term (e.g., .txt)", key="search_term_input_file_ops")
    
    if st.button("Search for Files", key="search_files_btn"):
        if search_path and search_term:
            found_files = []
            for root, _, files in os.walk(search_path):
                for file in files:
                    if search_term.lower() in file.lower():
                        found_files.append(os.path.join(root, file))
            if found_files:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                    <h4 style="color: white; margin-bottom: 1rem;">🔍 Found Files:</h4>
                </div>
                """, unsafe_allow_html=True)
                for f in found_files:
                    st.markdown(f"""
                    <div style="background: white; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #667eea;">
                        <span style="color: #1e293b; font-family: 'Courier New', monospace;">{f}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("🔍 No files found matching the search term.")
        else:
            st.warning("⚠️ Please enter a search path and term.")

    folder_to_zip = st.text_input("Folder to Compress (Full Path)", key="folder_to_zip_file_ops")
    zip_output_name = st.text_input("Output Zip File Name (e.g., my_archive.zip)", key="zip_output_name_file_ops")
    if st.button("Compress Folder (ZIP)"):
        if folder_to_zip and zip_output_name:
            try:
                shutil.make_archive(zip_output_name.replace(".zip", ""), 'zip', folder_to_zip)
                st.success(f"Folder '{folder_to_zip}' compressed to '{zip_output_name}' on the server.")
            except Exception as e:
                st.error(f"Error compressing folder: {e}")
        else:
            st.warning("Please enter folder to compress and output zip name.")

    zip_file_to_extract = st.text_input("Zip File to Extract (Full Path)", key="zip_file_to_extract_file_ops")
    extract_destination = st.text_input("Extraction Destination Folder", key="extract_destination_file_ops", value=os.getcwd())
    if st.button("Extract Files (Unzip)"):
        if zip_file_to_extract and extract_destination:
            try:
                with zipfile.ZipFile(zip_file_to_extract, 'r') as zip_ref:
                    zip_ref.extractall(extract_destination)
                st.success(f"'{zip_file_to_extract}' extracted to '{extract_destination}' on the server.")
            except FileNotFoundError:
                st.error("Zip file not found.")
            except zipfile.BadZipFile:
                st.error("Invalid zip file.")
            except Exception as e:
                st.error(f"Error extracting files: {e}")
        else:
            st.warning("Please enter zip file and extraction destination.")

    st.markdown("---")
    st.write("### Advanced File Operations")
    file_content_search_path = st.text_input("Path to search for content (e.g., C:\\MyDocs)", key="file_content_search_path")
    file_content_search_term = st.text_input("Text to search within files", key="file_content_search_term")
    if st.button("Search Text in Files"):
        if file_content_search_path and file_content_search_term:
            found_files_with_content = []
            for root, _, files in os.walk(file_content_search_path):
                for file in files:
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            if file_content_search_term.lower() in f.read().lower():
                                found_files_with_content.append(filepath)
                    except Exception as e:
                        st.warning(f"Could not read file {filepath}: {e}")
            if found_files_with_content:
                st.write("### Files Containing Search Term:")
                for f in found_files_with_content:
                    st.write(f)
            else:
                st.info("No files found containing the search term.")
        else:
            st.warning("Please enter a search path and term.")

def display_application_management_tasks():
    st.subheader("Application Management Tasks")

    if st.button("Open Calculator"):
        try:
            subprocess.Popen(["calc.exe"])
            st.success("Attempted to open Calculator.")
        except FileNotFoundError:
            st.error("Calculator (calc.exe) not found.")
        except Exception as e:
            st.error(f"Error opening Calculator: {e}")

    if st.button("Open Notepad"):
        try:
            subprocess.Popen(["notepad.exe"])
            st.success("Attempted to open Notepad.")
        except FileNotFoundError:
            st.error("Notepad (notepad.exe) not found.")
        except Exception as e:
            st.error(f"Error opening Notepad: {e}")

    if st.button("Open Command Prompt"):
        try:
            subprocess.Popen(["cmd.exe"])
            st.success("Attempted to open Command Prompt.")
        except FileNotFoundError:
            st.error("Command Prompt (cmd.exe) not found.")
        except Exception as e:
            st.error(f"Error opening Command Prompt: {e}")

    if st.button("Open PowerShell"):
        try:
            subprocess.Popen(["powershell.exe"])
            st.success("Attempted to open PowerShell.")
        except FileNotFoundError:
            st.error("PowerShell (powershell.exe) not found.")
        except Exception as e:
            st.error(f"Error opening PowerShell: {e}")

    if st.button("Open Control Panel"):
        try:
            subprocess.Popen(["control.exe"])
            st.success("Attempted to open Control Panel.")
        except FileNotFoundError:
            st.error("Control Panel (control.exe) not found.")
        except Exception as e:
            st.error(f"Error opening Control Panel: {e}")

    if st.button("Open Settings App"):
        try:
            subprocess.Popen(["start", "ms-settings:"], shell=True)
            st.success("Attempted to open Windows Settings app.")
        except Exception as e:
            st.error(f"Error opening Settings app: {e}")

    st.markdown("---")
    st.write("### Web Applications & Browser")

    if st.button("Open Chrome"):
        try:
            subprocess.Popen(["start", "chrome"], shell=True)
            st.success("Attempted to open Chrome. Ensure Chrome is installed and in your system's PATH.")
        except FileNotFoundError:
            st.error("Chrome executable not found. Please ensure Chrome is installed and its path is correctly configured.")
        except Exception as e:
            st.error(f"Error opening Chrome: {e}")

    if st.button("Open YouTube"):
        try:
            webbrowser.open("https://www.youtube.com/")
            st.success("Opening YouTube in your default web browser.")
        except Exception as e:
            st.error(f"Error opening YouTube: {e}")

    if st.button("Open Google Photos"):
        try:
            webbrowser.open("https://photos.google.com/")
            st.success("Opening Google Photos in your default web browser.")
        except Exception as e:
            st.error(f"Error opening Google Photos: {e}")

    if st.button("Open ChatGPT"):
        try:
            webbrowser.open("https://chat.openai.com/")
            st.success("Opening ChatGPT in your default web browser.")
        except Exception as e:
            st.error(f"Error opening ChatGPT: {e}")

    if st.button("Open Spotify Web Player"):
        try:
            webbrowser.open("https://open.spotify.com/")
            st.success("Opening Spotify Web Player in your default web browser.")
        except Exception as e:
            st.error(f"Error opening Spotify Web Player: {e}")

    st.markdown("---")
    st.write("### System Management")

    service_name_win = st.text_input("Windows Service Name (e.g., 'Spooler')", key="win_service_name")
    col_win_svc1, col_win_svc2, col_win_svc3 = st.columns(3)
    with col_win_svc1:
        if st.button("Start Service", key="start_win_svc"):
            if service_name_win:
                try:
                    subprocess.run(["net", "start", service_name_win], check=True, capture_output=True, text=True)
                    st.success(f"Service '{service_name_win}' started.")
                except subprocess.CalledProcessError as e:
                    st.error(f"Error starting service: {e.stderr}")
            else: st.warning("Please enter a service name.")
    with col_win_svc2:
        if st.button("Stop Service", key="stop_win_svc"):
            if service_name_win:
                try:
                    subprocess.run(["net", "stop", service_name_win], check=True, capture_output=True, text=True)
                    st.success(f"Service '{service_name_win}' stopped.")
                except subprocess.CalledProcessError as e:
                    st.error(f"Error stopping service: {e.stderr}")
            else: st.warning("Please enter a service name.")
    with col_win_svc3:
        if st.button("Restart Service", key="restart_win_svc"):
            if service_name_win:
                try:
                    st.info(f"Attempting to restart service '{service_name_win}'...")
                    subprocess.run(["net", "stop", service_name_win], check=True, capture_output=True, text=True)
                    time.sleep(1)
                    subprocess.run(["net", "start", service_name_win], check=True, capture_output=True, text=True)
                    st.success(f"Service '{service_name_win}' restarted.")
                except subprocess.CalledProcessError as e:
                    st.error(f"Error restarting service: {e.stderr}")
            else: st.warning("Please enter a service name.")

    if st.button("List All Services"):
        try:
            result = subprocess.run(["sc", "query", "state=", "all"], check=True, capture_output=True, text=True)
            st.code(result.stdout)
        except subprocess.CalledProcessError as e:
            st.error(f"Error listing services: {e.stderr}")

    st.markdown("---")
    st.write("### Scheduled Tasks")
    if st.button("List Scheduled Tasks"):
        try:
            result = subprocess.run(["schtasks", "/query", "/fo", "list", "/v"], check=True, capture_output=True, text=True)
            st.code(result.stdout)
        except subprocess.CalledProcessError as e:
            st.error(f"Error listing scheduled tasks: {e.stderr}")

    task_name_sch = st.text_input("Scheduled Task Name", key="sch_task_name")
    col_sch_task1, col_sch_task2 = st.columns(2)
    with col_sch_task1:
        if st.button("Disable Task", key="disable_sch_task"):
            if task_name_sch:
                try:
                    subprocess.run(["schtasks", "/change", "/tn", task_name_sch, "/disable"], check=True, capture_output=True, text=True)
                    st.success(f"Scheduled task '{task_name_sch}' disabled.")
                except subprocess.CalledProcessError as e:
                    st.error(f"Error disabling task: {e.stderr}")
            else: st.warning("Please enter a task name.")
    with col_sch_task2:
        if st.button("Enable Task", key="enable_sch_task"):
            if task_name_sch:
                try:
                    subprocess.run(["schtasks", "/change", "/tn", task_name_sch, "/enable"], check=True, capture_output=True, text=True)
                    st.success(f"Scheduled task '{task_name_sch}' enabled.")
                except subprocess.CalledProcessError as e:
                    st.error(f"Error enabling task: {e.stderr}")
            else: st.warning("Please enter a task name.")

def display_connectivity_network_tasks():
    st.subheader("Connectivity & Network Tasks")
    ping_host = st.text_input("Host to Ping", key="ping_host", value="google.com")
    if st.button("Ping Host"):
        if ping_host:
            try:
                command = ["ping", "-n", "4", ping_host] if os.name == 'nt' else ["ping", "-c", "4", ping_host]
                result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=10)
                st.code(result.stdout)
                if result.stderr:
                    st.error(result.stderr)
            except subprocess.CalledProcessError as e:
                st.error(f"Ping failed: {e.stderr}")
            except subprocess.TimeoutExpired:
                st.error(f"Ping command timed out after 10 seconds.")
            except Exception as e:
                st.error(f"Error executing ping: {e}")
        else:
            st.warning("Please enter a host to ping.")

    tracert_host = st.text_input("Host for Trace Route", key="tracert_host", value="google.com")
    if st.button("Trace Route"):
        if tracert_host:
            try:
                command = ["tracert", tracert_host] if os.name == 'nt' else ["traceroute", tracert_host]
                result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
                st.code(result.stdout)
                if result.stderr:
                    st.error(result.stderr)
            except subprocess.CalledProcessError as e:
                st.error(f"Trace route failed: {e.stderr}")
            except subprocess.TimeoutExpired:
                st.error(f"Trace route command timed out after 30 seconds.")
            except Exception as e:
                st.error(f"Error executing trace route: {e}")
        else:
            st.warning("Please enter a host for trace route.")

    if st.button("View Wi-Fi Profiles (No Passwords)"):
        try:
            st.info("Listing Wi-Fi profiles. Passwords are not displayed for security reasons and require specific administrative permissions.")
            result = subprocess.run(["netsh", "wlan", "show", "profile"], capture_output=True, text=True, check=True)
            st.code(result.stdout)
            if result.stderr:
                st.error(result.stderr)
        except subprocess.CalledProcessError as e:
            st.error(f"Failed to show Wi-Fi profiles: {e.stderr}. (Requires Administrator privileges)")
        except Exception as e:
            st.error(f"Error viewing Wi-fi profiles: {e}")

    st.markdown("---")
    st.write("### Network Drive & Folder Sharing")
    share_folder_path = st.text_input("Folder Path to Share", key="share_folder_path")
    share_name = st.text_input("Share Name", key="share_name")
    if st.button("Share Folder"):
        if share_folder_path and share_name:
            try:
                result = subprocess.run(["net", "share", share_name, share_folder_path, "/grant:Everyone,Full"], capture_output=True, text=True, check=True)
                st.code(result.stdout)
                st.success(f"Folder '{share_folder_path}' shared as '{share_name}'. (Requires Administrator privileges)")
            except subprocess.CalledProcessError as e:
                st.error(f"Failed to share folder: {e.stderr}. (Requires Administrator privileges)")
            except Exception as e:
                st.error(f"Error sharing folder: {e}")
            else:
                st.warning("Please enter folder path and share name.")

    map_drive_path = st.text_input("Network Path to Map (e.g., \\\\server\\share)", key="map_drive_path")
    drive_letter = st.text_input("Drive Letter (e.g., Z:)", key="drive_letter")
    if st.button("Map Network Drive"):
        if map_drive_path and drive_letter:
            try:
                result = subprocess.run(["net", "use", drive_letter, map_drive_path], capture_output=True, text=True, check=True)
                st.code(result.stdout)
                st.success(f"Network path '{map_drive_path}' mapped to '{drive_letter}'.")
            except subprocess.CalledProcessError as e:
                st.error(f"Failed to map network drive: {e.stderr}. (May require credentials or admin rights)")
            except Exception as e:
                st.error(f"Error mapping network drive: {e}")
            else:
                st.warning("Please enter network path and drive letter.")

    st.markdown("---")
    st.write("### Network Adapter Management")
    adapter_name = st.text_input("Network Adapter Name (e.g., 'Ethernet')", key="adapter_name")
    if st.button("Disable Network Adapter"):
        if adapter_name:
            try:
                st.warning(f"Attempting to disable '{adapter_name}'. This will disconnect you from the network. Requires Administrator privileges.")
                subprocess.run(["netsh", "interface", "set", "interface", adapter_name, "admin=disable"], capture_output=True, text=True, check=True)
                st.success(f"Network adapter '{adapter_name}' disabled.")
            except subprocess.CalledProcessError as e:
                st.error(f"Failed to disable adapter: {e.stderr}. (Requires Administrator privileges)")
            except Exception as e:
                st.error(f"Error disabling adapter: {e}")
            else:
                st.warning("Please enter the network adapter name.")

    if st.button("Enable Network Adapter"):
        if adapter_name:
            try:
                st.warning(f"Attempting to enable '{adapter_name}'. Requires Administrator privileges.")
                subprocess.run(["netsh", "interface", "set", "interface", adapter_name, "admin=enable"], capture_output=True, text=True, check=True)
                st.success(f"Network adapter '{adapter_name}' enabled.")
            except Exception as e:
                st.error(f"Error enabling adapter: {e}")
            else:
                st.warning("Please enter the network adapter name.")

def display_camera_operations_tasks():
    st.subheader("Camera Operations")
    st.info("Captured photos and recorded videos will be saved to your system's Downloads folder.")

    downloads_path = os.path.expanduser('~/Downloads')
    if not os.path.exists(downloads_path):
        try:
            os.makedirs(downloads_path)
            st.success(f"Created Downloads directory: {downloads_path}")
        except Exception as e:
            st.error(f"Could not create Downloads directory: {e}. Please ensure it exists or create it manually.")
            downloads_path = os.getcwd()

    st.markdown("**Take Photo**")
    if st.button("Take Photo", key="task_take_photo"):
        if cv2:
            st.info("Capturing photo from default webcam...")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                st.error("Could not open webcam. Make sure it's not in use and drivers are installed.")
            else:
                try:
                    ret, frame = cap.read()
                    if ret:
                        timestamp = time.strftime("%Y%m%d-%H%M%S")
                        photo_filename = f"captured_photo_{timestamp}.png"
                        photo_filepath = os.path.join(downloads_path, photo_filename)
                        cv2.imwrite(photo_filepath, frame)
                        st.success(f"Photo captured successfully and saved to '{photo_filepath}'.")
                        st.image(frame, channels="BGR", caption="Captured Photo")
                    else:
                        st.error("Failed to capture photo.")
                except Exception as e:
                    st.error(f"Error during photo capture: {e}")
                finally:
                    cap.release()
        else:
            st.error("OpenCV not imported. Please install `opencv-python`.")


    st.markdown("---")
    st.markdown("**Record Video**")
    record_duration = st.slider("Recording Duration (seconds)", 1, 10, 3, key="record_duration_task")
    if st.button(f"Record {record_duration} Seconds of Video", key="task_record_video"):
        if cv2:
            st.info(f"Recording video for {record_duration} seconds from default webcam...")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                st.error("Could not open webcam. Make sure it's not in use and drivers are installed.")
            else:
                try:
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    video_filename = f"recorded_video_{timestamp}.avi"
                    video_filepath = os.path.join(downloads_path, video_filename)

                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    if width == 0 or height == 0:
                        width, height = 640, 480
                        st.warning("Could not detect webcam resolution, using default 640x480.")
                    out = cv2.VideoWriter(video_filepath, fourcc, 20.0, (width, height))

                    start_time = time.time()
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    while(cap.isOpened()):
                        ret, frame = cap.read()
                        if ret:
                            out.write(frame)
                            elapsed_time = time.time() - start_time
                            progress = min(1.0, elapsed_time / record_duration)
                            progress_bar.progress(progress)
                            status_text.text(f"Recording... {int(elapsed_time)}/{record_duration} seconds")
                            if elapsed_time > record_duration:
                                break
                        else:
                            break
                    cap.release()
                    out.release()
                    st.success(f"Video recorded successfully to '{video_filepath}'.")
                    status_text.empty()
                    progress_bar.empty()
                except Exception as e:
                    st.error(f"Error during video recording: {e}")
                finally:
                    if cap.isOpened(): cap.release()
                    if 'out' in locals() and out.isOpened(): out.release()
        else:
            st.error("OpenCV not imported. Please install `opencv-python`.")

def display_messaging_communication_tasks():
    st.subheader("Messaging & Communication")

    st.markdown("**WhatsApp Message **")
    whatsapp_number = st.text_input("WhatsApp Number (e.g., +919876543210)", key="whatsapp_num_task")
    whatsapp_message = st.text_area("WhatsApp Message", key="whatsapp_msg_task")
    if st.button("Send WhatsApp Message", key="task_whatsapp"):
        if whatsapp_number and whatsapp_message:
            if pywhatkit:
                try:
                    st.info("Opening WhatsApp Web in your browser to send the message. Please ensure you are logged in.")
                    pywhatkit.sendwatmsg_instantly(whatsapp_number, whatsapp_message)
                    st.success("WhatsApp message command issued. Check your browser.")
                except Exception as e:
                    st.error(f"Failed to send WhatsApp message: {e}. Make sure pywhatkit is installed and WhatsApp Web is accessible.")
            else:
                st.error("PyWhatKit not imported. Please install it with `pip install pywhatkit`.")
        else:
            st.error("Please enter a WhatsApp number and message.")

    st.markdown("---")
    st.markdown("**Twilio SMS & Call **")
    twilio_to_number = st.text_input("Twilio Recipient Number (e.g., +1234567890)", key="twilio_to_num_task")
    twilio_message = st.text_area("Twilio Text Message", key="twilio_msg_task")
    if st.button("Send Text Message via Twilio", key="task_twilio_sms"):
        if twilio_to_number and twilio_message:
            try:
                from twilio.rest import Client
                account_sid = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # Your Account SID
                auth_token = "your_auth_token"
                twilio_phone_number = "+15017122661"
                client = Client(account_sid, auth_token)
                message = client.messages.create(to=twilio_to_number, from_=twilio_phone_number, body=twilio_message)
                st.success(f"Message sent successfully! SID: {message.sid}")
            except ImportError: st.error("Twilio library not found. Please install it: `pip install twilio`")
            except Exception as e: st.error(f"Failed to send SMS via Twilio. Check credentials and network: {e}")
        else: st.error("Please enter recipient number and message.")

    twilio_call_number = st.text_input("Twilio Call Number (e.g., +1234567890)", key="twilio_call_num_task")
    if st.button("Make Call via Twilio", key="task_twilio_call"):
        if twilio_call_number:
            try:
                from twilio.rest import Client
                account_sid = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # Your Account SID
                auth_token = "your_auth_token"
                twilio_phone_number = "+15017122661"
                client = Client(account_sid, auth_token)
                call = client.calls.create(to=twilio_call_number, from_=twilio_phone_number, url="http://demo.twilio.com/docs/voice.xml")
                st.success(f"Call initiated successfully! SID: {call.sid}")
            except ImportError: st.error("Twilio library not found. Please install it: `pip install twilio`")
            except Exception as e: st.error(f"Failed to make call via Twilio. Check credentials and network: {e}")
        else: st.error("Please enter a call number.")

    st.markdown("---")
    st.markdown("**Send Email**")
    email_recipient = st.text_input("Email Recipient", key="email_rec_task")
    email_subject = st.text_input("Email Subject", key="email_sub_task")
    email_body = st.text_area("Email Body", key="email_body_task")
    email_sender = st.text_input("Your Email Address (Sender)", key="email_sender_addr_task")
    email_password = st.text_input("Your Email Password (App Password Recommended)", type="password", key="email_sender_pass_task")
    if st.button("Send Email", key="task_send_email"):
        if email_recipient and email_subject and email_body and email_sender and email_password:
            try:
                msg = MIMEText(email_body)
                msg['Subject'] = email_subject
                msg['From'] = email_sender
                msg['To'] = email_recipient
                smtp_server = "smtp.gmail.com"
                smtp_port = 465
                with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                    smtp.login(email_sender, email_password)
                    smtp.send_message(msg)
                st.success("Email sent successfully!")
            except Exception as e: st.error(f"Failed to send email. Check sender credentials, SMTP settings, and network: {e}")
        else: st.error("Please fill in all email fields.")

def display_system_power_operations_tasks():
    st.subheader("System Power Operations ")
    st.error("⚠️ **These actions will immediately affect the machine ** Use with extreme caution.")

    if st.button("Shutdown", key="task_shutdown"):
        if st.checkbox("Confirm Shutdown", key="confirm_shutdown_task"):
            st.warning("Shutting down in 5 seconds...")
            time.sleep(5)
            try: os.system('shutdown /s /t 1'); st.success("Shutdown command issued.")
            except Exception as e: st.error(f"Error issuing shutdown command: {e}")
        else: st.info("Check the confirmation box to enable shutdown.")

    if st.button("Restart", key="task_restart"):
        if st.checkbox("Confirm Restart", key="confirm_restart_task"):
            st.warning("Restarting in 5 seconds...")
            time.sleep(5)
            try: os.system('shutdown /r /t 1'); st.success("Restart command issued.")
            except Exception as e: st.error(f"Error issuing restart command: {e}")
        else: st.info("Check the confirmation box to enable restart.")

    if st.button("Sleep", key="task_sleep"):
        if st.checkbox("Confirm Sleep", key="confirm_sleep_task"):
            st.warning("Attempting to put the system to sleep...")
            try: subprocess.Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"]); st.success("Sleep command issued.")
            except Exception as e: st.error(f"Error issuing sleep command: {e}")
        else: st.info("Check the confirmation box to enable sleep.")


def display_windows_sub_menu():
    # Enhanced header
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem;">
            🪟 {st.session_state.selected_category}
        </h1>
        <p style="font-size: 1.1rem; color: #64748b; font-weight: 500;">
            Select a sub-category to access specialized Windows management tools
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced back button
    if st.button("⬅️ Back to Main Menu", key="back_to_main_win", help="Go back to the main category selection"):
        st.session_state.current_view = "main_menu"
        st.session_state.selected_category = None
        st.session_state.selected_sub_category = None
        st.rerun()

    st.markdown("---")

    # Enhanced sub-categories with icons and descriptions
    col1_row1, col2_row1, col3_row1 = st.columns(3)
    
    with col1_row1:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💬</div>
            <h4 style="color: #1e293b; margin-bottom: 0.5rem;">Messaging & Communication</h4>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Email, SMS, and communication tools</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Messaging & Communication", key="msg_comm_sub_btn"):
            st.session_state.current_view = "windows_tasks_detail"
            st.session_state.selected_sub_category = "Messaging & Communication"
            st.rerun()
    
    with col2_row1:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📁</div>
            <h4 style="color: #1e293b; margin-bottom: 0.5rem;">File & Folder Operations</h4>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">File management and organization</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("File & Folder Operations", key="file_ops_sub_btn"):
            st.session_state.current_view = "windows_tasks_detail"
            st.session_state.selected_sub_category = "File & Folder Operations"
            st.rerun()
    
    with col3_row1:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚙️</div>
            <h4 style="color: #1e293b; margin-bottom: 0.5rem;">Application & System Management</h4>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">App control and system administration</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Application & System Management", key="app_sys_mgmt_sub_btn"):
            st.session_state.current_view = "windows_tasks_detail"
            st.session_state.selected_sub_category = "Open Applications"
            st.rerun()

    col1_row2, col2_row2, col3_row2 = st.columns(3)
    
    with col1_row2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌐</div>
            <h4 style="color: #1e293b; margin-bottom: 0.5rem;">Connectivity & Network</h4>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Network configuration and monitoring</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Connectivity & Network", key="net_conn_sub_btn"):
            st.session_state.current_view = "windows_tasks_detail"
            st.session_state.selected_sub_category = "Connectivity & Network"
            st.rerun()
    
    with col2_row2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔋</div>
            <h4 style="color: #1e293b; margin-bottom: 0.5rem;">System Power Operations</h4>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Power management and system control</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("System Power Operations", key="power_ops_sub_btn"):
            st.session_state.current_view = "windows_tasks_detail"
            st.session_state.selected_sub_category = "System Power Operations"
            st.rerun()
    
    with col3_row2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📷</div>
            <h4 style="color: #1e293b; margin-bottom: 0.5rem;">Camera</h4>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Camera capture and image processing</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Camera", key="camera_sub_btn"):
            st.session_state.current_view = "windows_tasks_detail"
            st.session_state.selected_sub_category = "Camera"
            st.rerun()

    col1_row3, _, _ = st.columns(3)
    
    with col1_row3:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
            <h4 style="color: #1e293b; margin-bottom: 0.5rem;">System Monitoring & Info</h4>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">System diagnostics and monitoring</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("System Monitoring & Info", key="sys_mon_info_sub_btn"):
            st.session_state.current_view = "windows_tasks_detail"
            st.session_state.selected_sub_category = "System Monitoring & Info"
            st.rerun()

def display_windows_tasks_detail():
    # Enhanced header with breadcrumb
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; margin-bottom: 1rem; color: #64748b; font-size: 0.9rem;">
            <span>🪟 Windows Tasks</span>
            <span style="margin: 0 0.5rem;">›</span>
            <span>{st.session_state.selected_sub_category}</span>
        </div>
        <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem;">
            {st.session_state.selected_sub_category}
        </h1>
        <p style="font-size: 1.1rem; color: #64748b; font-weight: 500;">
            Access specialized tools and automation for {st.session_state.selected_sub_category.lower()}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced back button
    if st.button(f"⬅️ Back to {st.session_state.selected_category} Sub-Categories", key="back_to_win_sub"):
        st.session_state.current_view = "windows_sub_menu"
        st.session_state.selected_sub_category = None
        st.rerun()

    st.markdown("---")

    if st.session_state.selected_sub_category == "Camera":
        display_camera_operations_tasks()
    elif st.session_state.selected_sub_category == "Messaging & Communication":
        display_messaging_communication_tasks()
    elif st.session_state.selected_sub_category == "File & Folder Operations":
        display_windows_file_folder_operations_tasks()
    elif st.session_state.selected_sub_category == "Open Applications":
        display_application_management_tasks()
    elif st.session_state.selected_sub_category == "Connectivity & Network":
        display_connectivity_network_tasks()
    elif st.session_state.selected_sub_category == "System Power Operations":
        display_system_power_operations_tasks()
    elif st.session_state.selected_sub_category == "System Monitoring & Info":
        display_windows_system_info_tasks()