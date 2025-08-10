import streamlit as st
from utils.ssh_utils import execute_ssh_command

def display_linux_system_info_tasks(host, username, password):
    st.subheader("Linux System Information")
    st.info("Retrieve basic system details from the remote Linux machine.")

    if st.button("Get Hostname"):
        output, error = execute_ssh_command(host, username, password, "hostname")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("Get Kernel Version (uname -a)"):
        output, error = execute_ssh_command(host, username, password, "uname -a")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("Check Disk Usage (df -h)"):
        output, error = execute_ssh_command(host, username, password, "df -h")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("Check Memory Usage (free -h)"):
        output, error = execute_ssh_command(host, username, password, "free -h")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("Get System Uptime (uptime)"):
        output, error = execute_ssh_command(host, username, password, "uptime")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("Get OS Release Info (cat /etc/os-release)"):
        output, error = execute_ssh_command(host, username, password, "cat /etc/os-release")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("List CPU Information (lscpu)"):
        output, error = execute_ssh_command(host, username, password, "lscpu")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("List Block Devices (lsblk)"):
        output, error = execute_ssh_command(host, username, password, "lsblk")
        if output: st.code(output)
        if error: st.error(error)

def display_linux_file_system_tasks(host, username, password):
    st.subheader("Linux File System Management")
    st.info("Perform file and folder operations on the remote Linux machine.")

    ls_path = st.text_input("Path to list (ls -l)", key="ls_path", value="~")
    if st.button("List Directory Contents"):
        output, error = execute_ssh_command(host, username, password, f"ls -l {ls_path}")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("Get Current Working Directory (pwd)"):
        output, error = execute_ssh_command(host, username, password, "pwd")
        if output: st.code(output)
        if error: st.error(error)

    mkdir_path = st.text_input("Directory to create (mkdir)", key="mkdir_path")
    if st.button("Create Directory"):
        if mkdir_path:
            output, error = execute_ssh_command(host, username, password, f"sudo mkdir {mkdir_path}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Directory '{mkdir_path}' created.")
        else: st.warning("Please enter a directory name.")

    rm_path = st.text_input("File/Directory to remove (rm -rf)", key="rm_path")
    if st.button("Remove File/Directory (rm -rf)"):
        if rm_path:
            st.warning(f"This will permanently delete '{rm_path}'. Confirm to proceed. Requires `sudo`.")
            if st.checkbox(f"Confirm deletion of {rm_path}", key=f"confirm_rm_{rm_path}"):
                output, error = execute_ssh_command(host, username, password, f"sudo rm -rf {rm_path}")
                if output: st.code(output)
                if error: st.error(error)
                if not error: st.success(f"'{rm_path}' removed.")
        else: st.warning("Please enter a file/directory to remove.")

    cp_source = st.text_input("Source path to copy (cp)", key="cp_source")
    cp_dest = st.text_input("Destination path for copy (cp)", key="cp_dest")
    if st.button("Copy File/Directory"):
        if cp_source and cp_dest:
            st.warning(f"Copying to/from system paths may require `sudo`.")
            output, error = execute_ssh_command(host, username, password, f"sudo cp -r {cp_source} {cp_dest}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"'{cp_source}' copied to '{cp_dest}'.")
        else: st.warning("Please enter source and destination paths.")

    mv_source = st.text_input("Source path to move (mv)", key="mv_source")
    mv_dest = st.text_input("Destination path for move (mv)", key="mv_dest")
    if st.button("Move File/Directory"):
        if mv_source and mv_dest:
            st.warning(f"Moving to/from system paths may require `sudo`.")
            output, error = execute_ssh_command(host, username, password, f"sudo mv {mv_source} {mv_dest}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"'{mv_source}' moved to '{mv_dest}'.")
        else: st.warning("Please enter source and destination paths.")

    cat_file = st.text_input("File to view (cat)", key="cat_file")
    if st.button("View File Content (cat)"):
        if cat_file:
            st.warning("Viewing restricted files may require `sudo`.")
            output, error = execute_ssh_command(host, username, password, f"sudo cat {cat_file}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a file path.")

    echo_file = st.text_input("File to write to (echo >)", key="echo_file")
    echo_content = st.text_area("Content to write", key="echo_content")
    if st.button("Create/Overwrite File"):
        if echo_file and echo_content:
            st.warning("Writing to restricted files/paths may require `sudo`.")
            escaped_content = echo_content.replace("'", "'\\''")
            output, error = execute_ssh_command(host, username, password, f"sudo echo '{escaped_content}' > {echo_file}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Content written to '{echo_file}'.")
        else: st.warning("Please enter file path and content.")

    chmod_path = st.text_input("File/Directory for chmod", key="chmod_path")
    chmod_perms = st.text_input("Permissions (e.g., 755)", key="chmod_perms")
    if st.button("Change Permissions (chmod)"):
        if chmod_path and chmod_perms:
            st.warning("Changing permissions of system files may require `sudo`.")
            output, error = execute_ssh_command(host, username, password, f"sudo chmod {chmod_perms} {chmod_path}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Permissions of '{chmod_path}' changed to '{chmod_perms}'.")
        else: st.warning("Please enter path and permissions.")

    chown_path = st.text_input("File/Directory for chown", key="chown_path")
    chown_owner_group = st.text_input("Owner:Group (e.g., user:group)", key="chown_owner_group")
    if st.button("Change Ownership (chown)"):
        if chown_path and chown_owner_group:
            st.warning("This command requires `sudo` privileges on the remote machine. Ensure your user has `NOPASSWD` configured for `sudo` to avoid hanging.")
            output, error = execute_ssh_command(host, username, password, f"sudo chown {chown_owner_group} {chown_path}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Ownership of '{chown_path}' changed to '{chown_owner_group}'. (Requires sudo)")
        else: st.warning("Please enter path and owner:group.")

    find_path = st.text_input("Path to search (find)", key="find_path", value="~")
    find_name = st.text_input("File name pattern (e.g., *.log)", key="find_name")
    if st.button("Find Files"):
        if find_path and find_name:
            st.warning("Searching restricted directories may require `sudo`.")
            output, error = execute_ssh_command(host, username, password, f"sudo find {find_path} -name '{find_name}'")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter search path and file name pattern.")


def display_linux_process_management_tasks(host, username, password):
    st.subheader("Linux Process Management")
    st.info("Manage running processes on the remote Linux machine.")

    if st.button("List All Processes (ps aux)"):
        st.warning("Listing all processes may require `sudo` to see details for other users/root processes.")
        output, error = execute_ssh_command(host, username, password, "sudo ps aux")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("View Top Processes (top -bn1 | head -n 10)"):
        st.warning("Viewing top processes may require `sudo` to see full details.")
        output, error = execute_ssh_command(host, username, password, "sudo top -bn1 | head -n 10")
        if output: st.code(output)
        if error: st.error(error)

    kill_pid = st.text_input("PID to Kill", key="kill_pid")
    if st.button("Kill Process (kill -9)"):
        if kill_pid:
            st.warning(f"This will forcefully terminate PID {kill_pid}. Confirm to proceed. Requires `sudo` if not your process.")
            if st.checkbox(f"Confirm kill PID {kill_pid}", key=f"confirm_kill_{kill_pid}"):
                output, error = execute_ssh_command(host, username, password, f"sudo kill -9 {kill_pid}")
                if output: st.code(output)
                if error: st.error(error)
                if not error: st.success(f"Process with PID {kill_pid} killed.")
        else: st.warning("Please enter a PID to kill.")

    service_name_status = st.text_input("Service Name (for systemctl status)", key="service_name_status")
    if st.button("Check Service Status"):
        if service_name_status:
            st.warning("Checking status for some services may require `sudo`.")
            output, error = execute_ssh_command(host, username, password, f"sudo systemctl status {service_name_status}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a service name.")

def display_linux_network_tasks(host, username, password):
    st.subheader("Linux Network Management")
    st.info("Perform network-related tasks on the remote Linux machine.")

    if st.button("Show IP Addresses (ip a)"):
        output, error = execute_ssh_command(host, username, password, "sudo ip a")
        if output: st.code(output)
        if error: st.error(error)

    ping_target = st.text_input("Host to Ping (ping -c 4)", key="ping_target", value="google.com")
    if st.button("Ping Host"):
        if ping_target:
            output, error = execute_ssh_command(host, username, password, f"ping -c 4 {ping_target}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a host to ping.")

    if st.button("List Open Ports (ss -tuln)"):
        st.warning("Listing all open ports may require `sudo` to see details for all processes.")
        output, error = execute_ssh_command(host, username, password, "sudo ss -tuln")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("List Open Ports (netstat -tuln)"):
        output, error = execute_ssh_command(host, username, password, "sudo netstat -tuln")
        if output: st.code(output)
        if error: st.error(error)

    curl_url = st.text_input("URL to Curl", key="curl_url", value="http://example.com")
    if st.button("Fetch URL Content (curl)"):
        if curl_url:
            output, error = execute_ssh_command(host, username, password, f"curl -s {curl_url}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a URL.")

    st.markdown("---")
    st.write("### Network Diagnostics")
    dns_host = st.text_input("Host for DNS Lookup (e.g., google.com)", key="dns_host")
    if st.button("Perform DNS Lookup (dig)"):
        if dns_host:
            output, error = execute_ssh_command(host, username, password, f"dig {dns_host}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a hostname for DNS lookup.")

    if st.button("Show Active Network Connections (ss -tunlp)"):
        st.warning("Requires `sudo` to see process names/PIDs.")
        output, error = execute_ssh_command(host, username, password, "sudo ss -tunlp")
        if output: st.code(output)
        if error: st.error(error)

def display_linux_user_management_tasks(host, username, password):
    st.subheader("Linux User & Group Management")
    st.info("Manage users and groups on the remote Linux machine.")

    if st.button("Get Current User (whoami)"):
        output, error = execute_ssh_command(host, username, password, "whoami")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("Get User ID and Group Info (id)"):
        output, error = execute_ssh_command(host, username, password, "id")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("View /etc/passwd (User Accounts)"):
        st.warning("Viewing /etc/passwd may require `sudo` if permissions are restricted.")
        output, error = execute_ssh_command(host, username, password, "sudo cat /etc/passwd")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("View /etc/group (Groups)"):
        st.warning("Viewing /etc/group may require `sudo` if permissions are restricted.")
        output, error = execute_ssh_command(host, username, password, "sudo cat /etc/group")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("Check Sudo Access (sudo whoami)"):
        st.warning("This command requires `sudo` privileges on the remote machine. Ensure your user has `NOPASSWD` configured for `sudo` to avoid hanging.")
        output, error = execute_ssh_command(host, username, password, "sudo whoami")
        if output: st.code(output)
        if error: st.error(error)

    st.markdown("---")
    st.write("### User & Group Operations")
    new_username = st.text_input("New Username to Create", key="new_linux_user")
    if st.button("Create New User"):
        if new_username:
            st.warning("This requires `sudo`.")
            output, error = execute_ssh_command(host, username, password, f"sudo useradd -m {new_username}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"User '{new_username}' created.")
        else: st.warning("Please enter a username.")

    user_to_delete = st.text_input("Username to Delete", key="del_linux_user")
    if st.button("Delete User"):
        if user_to_delete:
            st.warning("This will delete the user and their home directory. Requires `sudo`.")
            if st.checkbox(f"Confirm deletion of user {user_to_delete}", key=f"confirm_del_user_{user_to_delete}"):
                output, error = execute_ssh_command(host, username, password, f"sudo userdel -r {user_to_delete}")
                if output: st.code(output)
                if error: st.error(error)
                if not error: st.success(f"User '{user_to_delete}' deleted.")
        else: st.warning("Please enter a username.")

    user_for_password = st.text_input("User to Set Password For", key="passwd_linux_user")
    new_password = st.text_input("New Password", type="password", key="new_linux_password")
    if st.button("Set User Password"):
        if user_for_password and new_password:
            st.warning("This requires `sudo`. The password will be sent in plain text over SSH.")
            output, error = execute_ssh_command(host, username, password, f"echo '{user_for_password}:{new_password}' | sudo chpasswd")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Password set for user '{user_for_password}'.")
        else: st.warning("Please enter username and new password.")

def display_linux_package_management_tasks(host, username, password):
    st.subheader("Linux Package Management (RHEL/CentOS - dnf/yum)")
    st.info("Manage software packages on the remote Linux machine. Many operations require `sudo`.")

    if st.button("List Installed Packages (dnf list installed | head -n 20)"):
        output, error = execute_ssh_command(host, username, password, "dnf list installed | head -n 20")
        if output: st.code(output)
        if error: st.error(error)

    package_to_install = st.text_input("Package to Install (e.g., nano)", key="pkg_install")
    if st.button("Install Package (sudo dnf install -y)"):
        if package_to_install:
            st.warning(f"This will install '{package_to_install}'. Requires `sudo`. Ensure your user has `NOPASSWD` configured for `sudo` to avoid hanging.")
            output, error = execute_ssh_command(host, username, password, f"sudo dnf install -y {package_to_install}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Package '{package_to_install}' installation command issued.")
        else: st.warning("Please enter a package name.")

    package_to_remove = st.text_input("Package to Remove (e.g., nano)", key="pkg_remove")
    if st.button("Remove Package (sudo dnf remove -y)"):
        if package_to_remove:
            st.warning(f"This will remove '{package_to_remove}'. Confirm to proceed. Requires `sudo`. Ensure your user has `NOPASSWD` configured for `sudo` to avoid hanging.")
            if st.checkbox(f"Confirm removal of {package_to_remove}", key=f"confirm_rm_pkg_{package_to_remove}"):
                output, error = execute_ssh_command(host, username, password, f"sudo dnf remove -y {package_to_remove}")
                if output: st.code(output)
                if error: st.error(error)
                if not error: st.success(f"Package '{package_to_remove}' removal command issued.")
        else: st.warning("Please enter a package name.")

    if st.button("Update All Packages (sudo dnf update -y)"):
        st.warning("This will update all packages on the system. Requires `sudo` and can take time. Ensure your user has `NOPASSWD` configured for `sudo` to avoid hanging.")
        if st.checkbox("Confirm full system update", key="confirm_dnf_update"):
            output, error = execute_ssh_command(host, username, password, "sudo dnf update -y")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success("System update command issued.")

    package_to_search = st.text_input("Package to Search (e.g., httpd)", key="pkg_search")
    if st.button("Search Package (dnf search)"):
        if package_to_search:
            output, error = execute_ssh_command(host, username, password, f"dnf search {package_to_search}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a package name to search.")

    st.markdown("---")
    st.write("### Advanced Package Operations")
    pkg_to_list_files = st.text_input("Package to list files for (e.g., httpd)", key="pkg_list_files")
    if st.button("List Package Files (rpm -ql)"):
        if pkg_to_list_files:
            output, error = execute_ssh_command(host, username, password, f"rpm -ql {pkg_to_list_files}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a package name.")

    if st.button("Check for Available Updates (dnf check-update)"):
        output, error = execute_ssh_command(host, username, password, "dnf check-update")
        if output: st.code(output)
        if error: st.error(error)

def display_linux_service_management_tasks(host, username, password):
    st.subheader("Linux Service Management (systemctl)")
    st.info("Manage system services on the remote Linux machine. Most operations require `sudo`.")

    service_name_action = st.text_input("Service Name (e.g., httpd)", key="service_name_action")

    if st.button("Start Service (sudo systemctl start)"):
        if service_name_action:
            st.warning("This command requires `sudo` privileges on the remote machine. Ensure your user has `NOPASSWD` configured for `sudo` to avoid hanging.")
            output, error = execute_ssh_command(host, username, password, f"sudo systemctl start {service_name_action}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Service '{service_name_action}' start command issued.")
        else: st.warning("Please enter a service name.")

    if st.button("Stop Service (sudo systemctl stop)"):
        if service_name_action:
            st.warning("This command requires `sudo` privileges on the remote machine. Ensure your user has `NOPASSWD` configured for `sudo` to avoid hanging.")
            output, error = execute_ssh_command(host, username, password, f"sudo systemctl stop {service_name_action}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Service '{service_name_action}' stop command issued.")
        else: st.warning("Please enter a service name.")

    if st.button("Restart Service (sudo systemctl restart)"):
        if service_name_action:
            st.warning("This command requires `sudo` privileges on the remote machine. Ensure your user has `NOPASSWD` configured for `sudo` to avoid hanging.")
            output, error = execute_ssh_command(host, username, password, f"sudo systemctl restart {service_name_action}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Service '{service_name_action}' restart command issued.")
        else: st.warning("Please enter a service name.")

    if st.button("Enable Service (sudo systemctl enable)"):
        if service_name_action:
            st.warning("This command requires `sudo` privileges on the remote machine. Ensure your user has `NOPASSWD` configured for `sudo` to avoid hanging.")
            output, error = execute_ssh_command(host, username, password, f"sudo systemctl enable {service_name_action}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Service '{service_name_action}' enable command issued.")
        else: st.warning("Please enter a service name.")

    if st.button("Disable Service (sudo systemctl disable)"):
        if service_name_action:
            st.warning("This command requires `sudo` privileges on the remote machine. Ensure your user has `NOPASSWD` configured for `sudo` to avoid hanging.")
            output, error = execute_ssh_command(host, username, password, f"sudo systemctl disable {service_name_action}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Service '{service_name_action}' disable command issued.")
        else: st.warning("Please enter a service name.")

def display_linux_log_management_tasks(host, username, password):
    st.subheader("Linux Log Management")

    log_file_path = st.text_input("Log File Path (e.g., /var/log/messages)", key="log_file_path", value="/var/log/messages")
    num_lines = st.slider("Number of lines to show (tail -n)", 5, 100, 20, key="num_lines_log")

    if st.button("View Last Lines of Log File"):
        if log_file_path:
            st.warning("Viewing restricted log files may require `sudo`.")
            output, error = execute_ssh_command(host, username, password, f"sudo tail -n {num_lines} {log_file_path}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a log file path.")

    if st.button("View Journalctl Logs (last 20 lines)"):
        output, error = execute_ssh_command(host, username, password, "sudo journalctl -xe | tail -n 20")
        if output: st.code(output)
        if error: st.error(error)

    st.markdown("---")
    st.write("### Cron Job Management")
    cron_user = st.text_input("User for Cron Jobs (leave blank for current user)", key="cron_user")
    if st.button("List Cron Jobs"):
        cmd = f"crontab -l"
        if cron_user:
            cmd = f"sudo crontab -l -u {cron_user}"
        output, error = execute_ssh_command(host, username, password, cmd)
        if output: st.code(output)
        if error: st.error(error)

    new_cron_job = st.text_area("New Cron Job Entry (e.g., '0 0 * * * /path/to/script.sh')", key="new_cron_job")
    if st.button("Add Cron Job"):
        if new_cron_job:
            cmd = f"(crontab -l; echo '{new_cron_job}') | crontab -"
            if cron_user:
                cmd = f"sudo bash -c \"(crontab -l -u {cron_user} 2>/dev/null; echo '{new_cron_job}') | crontab -u {cron_user} -\""
            st.warning("Adding cron jobs requires careful syntax. Ensure your entry is correct.")
            output, error = execute_ssh_command(host, username, password, cmd)
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success("Cron job added.")
        else: st.warning("Please enter a cron job entry.")

def display_linux_firewall_tasks(host, username, password):
    st.subheader("Linux Firewall Management (firewalld)")

    if st.button("List All Firewall Rules (firewall-cmd --list-all)"):
        output, error = execute_ssh_command(host, username, password, "sudo firewall-cmd --list-all")
        if output: st.code(output)
        if error: st.error(error)

    port_to_manage = st.text_input("Port (e.g., 8080)", key="fw_port")
    protocol = st.selectbox("Protocol", ["tcp", "udp"], key="fw_protocol")
    zone = st.text_input("Zone (e.g., public)", value="public", key="fw_zone")

    col_fw1, col_fw2 = st.columns(2)
    with col_fw1:
        if st.button("Open Port (Permanent)", key="open_port_perm"):
            if port_to_manage:
                cmd = f"sudo firewall-cmd --zone={zone} --add-port={port_to_manage}/{protocol} --permanent && sudo firewall-cmd --reload"
                output, error = execute_ssh_command(host, username, password, cmd)
                if output: st.code(output)
                if error: st.error(error)
                if not error: st.success(f"Port {port_to_manage}/{protocol} opened permanently in zone {zone}.")
            else: st.warning("Please enter a port.")
    with col_fw2:
        if st.button("Close Port (Permanent)", key="close_port_perm"):
            if port_to_manage:
                cmd = f"sudo firewall-cmd --zone={zone} --remove-port={port_to_manage}/{protocol} --permanent && sudo firewall-cmd --reload"
                output, error = execute_ssh_command(host, username, password, cmd)
                if output: st.code(output)
                if error: st.error(error)
                if not error: st.success(f"Port {port_to_manage}/{protocol} closed permanently in zone {zone}.")
            else: st.warning("Please enter a port.")

def display_linux_ssh_key_management_tasks(host, username, password):
    st.subheader("Linux SSH Key Management")

    if st.button("View Public Key (cat ~/.ssh/id_rsa.pub)"):
        output, error = execute_ssh_command(host, username, password, "cat ~/.ssh/id_rsa.pub")
        if output: st.code(output)
        if error: st.error(error)

    public_key_to_add = st.text_area("Public Key to Add to authorized_keys", key="public_key_to_add")
    if st.button("Add Public Key to authorized_keys"):
        if public_key_to_add:
            st.warning("This will add the provided public key to the current user's `~/.ssh/authorized_keys` file. Requires correct permissions.")
            cmd = f"mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '{public_key_to_add}' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
            output, error = execute_ssh_command(host, username, password, cmd)
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success("Public key added to authorized_keys.")
        else: st.warning("Please paste a public key.")

def display_linux_sub_menu():
    st.title("Linux Tasks Sub-Categories")
    st.write("Enter your SSH connection details for the RHEL9 machine:")

    if 'ssh_connected' not in st.session_state:
        st.session_state.ssh_connected = False
    if 'ssh_host' not in st.session_state:
        st.session_state.ssh_host = ""
    if 'ssh_username' not in st.session_state:
        st.session_state.ssh_username = ""
    if 'ssh_password' not in st.session_state:
        st.session_state.ssh_password = ""

    ssh_host = st.text_input("RHEL9 IP Address/Hostname", key="ssh_host_input", value=st.session_state.ssh_host)
    ssh_username = st.text_input("Username", key="ssh_username_input", value=st.session_state.ssh_username)
    ssh_password = st.text_input("Password", type="password", key="ssh_password_input", value=st.session_state.ssh_password)

    if st.button("Connect to Linux Machine", key="connect_linux_btn"):
        if ssh_host and ssh_username and ssh_password:
            test_output, test_error = execute_ssh_command(ssh_host, ssh_username, ssh_password, "echo 'Connection Test Successful'")
            if not test_error:
                st.session_state.ssh_host = ssh_host
                st.session_state.ssh_username = ssh_username
                st.session_state.ssh_password = ssh_password
                st.session_state.ssh_connected = True
                st.success("SSH connection successful! Select a task category below.")
            else:
                st.session_state.ssh_connected = False
                st.error(f"SSH connection failed: {test_error}")
        else:
            st.error("Please provide all SSH connection details.")

    st.markdown("---")
    st.write("Select a sub-category to view specific tasks.")

    if st.button("⬅️ Back to Main Menu", key="back_to_main_linux"):
        st.session_state.current_view = "main_menu"
        st.session_state.selected_category = None
        st.session_state.selected_sub_category = None
        st.session_state.ssh_connected = False
        st.rerun()

    st.markdown("---")

    # Linux Sub-Category Buttons (arranged in three rows)
    # Row 1: System Information, File System Management, Process Management
    col_l1_r1, col_l2_r1, col_l3_r1 = st.columns(3)
    with col_l1_r1:
        if st.button("System Information", key="linux_sys_info_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "linux_tasks_detail"
            st.session_state.selected_sub_category = "System Information"
            st.rerun()
    with col_l2_r1:
        if st.button("File System Management", key="linux_file_sys_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "linux_tasks_detail"
            st.session_state.selected_sub_category = "File System Management"
            st.rerun()
    with col_l3_r1:
        if st.button("Process Management", key="linux_proc_mgmt_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "linux_tasks_detail"
            st.session_state.selected_sub_category = "Process Management"
            st.rerun()

    # Row 2: Network Management, User & Group Management, Package Management
    col_l1_r2, col_l2_r2, col_l3_r2 = st.columns(3)
    with col_l1_r2:
        if st.button("Network Management", key="linux_net_mgmt_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "linux_tasks_detail"
            st.session_state.selected_sub_category = "Network Management"
            st.rerun()
    with col_l2_r2:
        if st.button("User & Group Management", key="linux_user_mgmt_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "linux_tasks_detail"
            st.session_state.selected_sub_category = "User & Group Management"
            st.rerun()
    with col_l3_r2:
        if st.button("Package Management", key="linux_pkg_mgmt_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "linux_tasks_detail"
            st.session_state.selected_sub_category = "Package Management"
            st.rerun()

    # Row 3: Service Management, Log & Cron Management, Firewall Management, SSH Key Management
    col_l1_r3, col_l2_r3, col_l3_r3 = st.columns(3)
    with col_l1_r3:
        if st.button("Service Management", key="linux_svc_mgmt_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "linux_tasks_detail"
            st.session_state.selected_sub_category = "Service Management"
            st.rerun()
    with col_l2_r3:
        if st.button("Log & Cron Management", key="linux_log_cron_mgmt_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "linux_tasks_detail"
            st.session_state.selected_sub_category = "Log & Cron Management"
            st.rerun()
    with col_l3_r3:
        if st.button("Firewall Management", key="linux_firewall_mgmt_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "linux_tasks_detail"
            st.session_state.selected_sub_category = "Firewall Management"
            st.rerun()

    col_l1_r4, _, _ = st.columns(3)
    with col_l1_r4:
        if st.button("SSH Key Management", key="linux_ssh_key_mgmt_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "linux_tasks_detail"
            st.session_state.selected_sub_category = "SSH Key Management"
            st.rerun()

def display_linux_tasks_detail():
    st.title(f"{st.session_state.selected_category} - {st.session_state.selected_sub_category}")

    if st.button(f"⬅️ Back to {st.session_state.selected_category} Sub-Categories", key="back_to_linux_sub"):
        st.session_state.current_view = "linux_sub_menu"
        st.session_state.selected_sub_category = None
        st.rerun()

    st.markdown("---")

    if not st.session_state.get('ssh_connected', False):
        st.error("Please connect to the Linux machine first by entering SSH credentials on the previous page.")
        return

    host = st.session_state.ssh_host
    username = st.session_state.ssh_username
    password = st.session_state.ssh_password

    if st.session_state.selected_sub_category == "System Information":
        display_linux_system_info_tasks(host, username, password)
    elif st.session_state.selected_sub_category == "File System Management":
        display_linux_file_system_tasks(host, username, password)
    elif st.session_state.selected_sub_category == "Process Management":
        display_linux_process_management_tasks(host, username, password)
    elif st.session_state.selected_sub_category == "Network Management":
        display_linux_network_tasks(host, username, password)
    elif st.session_state.selected_sub_category == "User & Group Management":
        display_linux_user_management_tasks(host, username, password)
    elif st.session_state.selected_sub_category == "Package Management":
        display_linux_package_management_tasks(host, username, password)
    elif st.session_state.selected_sub_category == "Service Management":
        display_linux_service_management_tasks(host, username, password)
    elif st.session_state.selected_sub_category == "Log & Cron Management":
        display_linux_log_management_tasks(host, username, password)
    elif st.session_state.selected_sub_category == "Firewall Management":
        display_linux_firewall_tasks(host, username, password)
    elif st.session_state.selected_sub_category == "SSH Key Management":
        display_linux_ssh_key_management_tasks(host, username, password)