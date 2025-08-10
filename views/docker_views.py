import streamlit as st
import json
import time
import os
from utils.ssh_utils import execute_ssh_command

def display_docker_container_management_tasks(host, username, password):
    st.subheader("Docker Container Management")
    st.info("Manage Docker containers on the remote Linux machine. Requires Docker to be installed and running.")

    if st.button("List Running Containers (docker ps)"):
        output, error = execute_ssh_command(host, username, password, "sudo docker ps")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("List All Containers (docker ps -a)"):
        output, error = execute_ssh_command(host, username, password, "sudo docker ps -a")
        if output: st.code(output)
        if error: st.error(error)

    container_name_id = st.text_input("Container Name/ID", key="docker_container_name_id")

    if st.button("Start Container"):
        if container_name_id:
            output, error = execute_ssh_command(host, username, password, f"sudo docker start {container_name_id}")
            if output: st.success(f"Container '{container_name_id}' started.")
            if error: st.error(error)
        else: st.warning("Please enter a container name or ID.")

    if st.button("Stop Container"):
        if container_name_id:
            output, error = execute_ssh_command(host, username, password, f"sudo docker stop {container_name_id}")
            if output: st.success(f"Container '{container_name_id}' stopped.")
            if error: st.error(error)
        else: st.warning("Please enter a container name or ID.")

    if st.button("Restart Container"):
        if container_name_id:
            output, error = execute_ssh_command(host, username, password, f"sudo docker restart {container_name_id}")
            if output: st.success(f"Container '{container_name_id}' restarted.")
            if error: st.error(error)
        else: st.warning("Please enter a container name or ID.")

    if st.button("Remove Container (docker rm)"):
        if container_name_id:
            st.warning(f"This will permanently remove container '{container_name_id}'. Confirm to proceed.")
            if st.checkbox(f"Confirm removal of container {container_name_id}", key=f"confirm_rm_container_{container_name_id}"):
                output, error = execute_ssh_command(host, username, password, f"sudo docker rm {container_name_id}")
                if output: st.success(f"Container '{container_name_id}' removed.")
                if error: st.error(error)
        else: st.warning("Please enter a container name or ID.")

    if st.button("View Container Logs (docker logs)"):
        if container_name_id:
            output, error = execute_ssh_command(host, username, password, f"sudo docker logs {container_name_id}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a container name or ID.")

    run_image_name = st.text_input("Image to Run (e.g., nginx:latest)", key="docker_run_image")
    run_container_name = st.text_input("New Container Name (optional)", key="docker_new_container_name")
    run_ports = st.text_input("Ports (e.g., -p 80:80)", key="docker_run_ports")
    run_options = st.text_input("Other Options (e.g., -d --name myweb)", key="docker_run_options")
    if st.button("Run New Container"):
        if run_image_name:
            cmd = f"sudo docker run {run_ports} {run_options} {run_image_name}"
            if run_container_name:
                cmd = f"sudo docker run {run_ports} {run_options} --name {run_container_name} {run_image_name}"
            output, error = execute_ssh_command(host, username, password, cmd)
            if output: st.success(f"Container from '{run_image_name}' initiated.")
            if error: st.error(error)
        else: st.warning("Please enter an image name to run.")

    exec_container_name_id = st.text_input("Container for Exec", key="docker_exec_container_name_id")
    exec_command = st.text_input("Command to Exec (e.g., ls -l /app)", key="docker_exec_command")
    if st.button("Execute Command in Container"):
        if exec_container_name_id and exec_command:
            output, error = execute_ssh_command(host, username, password, f"sudo docker exec {exec_container_name_id} {exec_command}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter container name/ID and command.")

    if st.button("Inspect Container"):
        if container_name_id:
            output, error = execute_ssh_command(host, username, password, f"sudo docker inspect {container_name_id}")
            if output: st.json(output)
            if error: st.error(error)
        else: st.warning("Please enter a container name or ID.")

    st.markdown("---")
    st.write("### Advanced Container Operations")
    container_stats_name = st.text_input("Container Name/ID for Stats", key="container_stats_name")
    if st.button("View Container Resource Stats (docker stats)"):
        if container_stats_name:
            output, error = execute_ssh_command(host, username, password, f"sudo docker stats --no-stream {container_stats_name}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a container name or ID.")

def display_docker_image_management_tasks(host, username, password):
    st.subheader("Docker Image Management")

    if st.button("List Images (docker images)"):
        output, error = execute_ssh_command(host, username, password, "sudo docker images")
        if output: st.code(output)
        if error: st.error(error)

    pull_image_name = st.text_input("Image to Pull (e.g., ubuntu:latest)", key="docker_pull_image")
    if st.button("Pull Image"):
        if pull_image_name:
            output, error = execute_ssh_command(host, username, password, f"sudo docker pull {pull_image_name}")
            if output: st.success(f"Image '{pull_image_name}' pulled.")
            if error: st.error(error)
        else: st.warning("Please enter an image name to pull.")

    remove_image_name_id = st.text_input("Image Name/ID to Remove", key="docker_remove_image")
    if st.button("Remove Image (docker rmi)"):
        if remove_image_name_id:
            st.warning(f"This will remove image '{remove_image_name_id}'. Confirm to proceed.")
            if st.checkbox(f"Confirm removal of image {remove_image_name_id}", key=f"confirm_rm_image_{remove_image_name_id}"):
                output, error = execute_ssh_command(host, username, password, f"sudo docker rmi {remove_image_name_id}")
                if output: st.success(f"Image '{remove_image_name_id}' removed.")
                if error: st.error(error)
        else: st.warning("Please enter an image name or ID.")

    inspect_image_name_id = st.text_input("Image Name/ID to Inspect", key="docker_inspect_image")
    if st.button("Inspect Image"):
        if inspect_image_name_id:
            output, error = execute_ssh_command(host, username, password, f"sudo docker inspect {inspect_image_name_id}")
            if output: st.json(output)
            if error: st.error(error)
        else: st.warning("Please enter an image name or ID.")

    tag_source_image = st.text_input("Source Image (Name:Tag)", key="docker_tag_source")
    tag_target_image = st.text_input("Target Image (NewName:NewTag)", key="docker_tag_target")
    if st.button("Tag Image"):
        if tag_source_image and tag_target_image:
            output, error = execute_ssh_command(host, username, password, f"sudo docker tag {tag_source_image} {tag_target_image}")
            if output: st.success(f"Image '{tag_source_image}' tagged as '{tag_target_image}'.")
            if error: st.error(error)
        else: st.warning("Please enter source and target image names.")

    st.markdown("---")
    st.write("### Image Building")
    dockerfile_content = st.text_area("Dockerfile Content", height=200, key="dockerfile_content")
    image_name_to_build = st.text_input("New Image Name (e.g., myapp:latest)", key="image_name_to_build")
    if st.button("Build Image from Dockerfile"):
        if dockerfile_content and image_name_to_build:
            st.warning("Building images requires creating a temporary file on the remote server. Ensure the user has write permissions in the target directory.")
            temp_dir = f"/tmp/docker_build_{int(time.time())}"
            dockerfile_path = f"{temp_dir}/Dockerfile"

            output, error = execute_ssh_command(host, username, password, f"mkdir -p {temp_dir}")
            if error: st.error(f"Error creating temp dir: {error}"); return

            escaped_dockerfile_content = dockerfile_content.replace("'", "'\\''")
            output, error = execute_ssh_command(host, username, password, f"echo '{escaped_dockerfile_content}' > {dockerfile_path}")
            if error: st.error(f"Error writing Dockerfile: {error}"); return

            build_cmd = f"sudo docker build -t {image_name_to_build} {temp_dir}"
            output, error = execute_ssh_command(host, username, password, build_cmd)
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Image '{image_name_to_build}' built successfully.")

            execute_ssh_command(host, username, password, f"rm -rf {temp_dir}")
        else: st.warning("Please provide Dockerfile content and a new image name.")

    st.markdown("---")
    st.write("### Registry Operations")
    registry_image_name = st.text_input("Image to Push/Pull (e.g., myregistry/myimage:tag)", key="registry_image_name")
    registry_username = st.text_input("Registry Username (optional)", key="registry_username")
    registry_password = st.text_input("Registry Password (optional)", type="password", key="registry_password")

    col_reg1, col_reg2 = st.columns(2)
    with col_reg1:
        if st.button("Push Image to Registry"):
            if registry_image_name:
                login_cmd = ""
                if registry_username and registry_password:
                    login_cmd = f"echo '{registry_password}' | sudo docker login --username {registry_username} --password-stdin && "
                cmd = f"{login_cmd}sudo docker push {registry_image_name}"
                output, error = execute_ssh_command(host, username, password, cmd)
                if output: st.code(output)
                if error: st.error(error)
                if not error: st.success(f"Image '{registry_image_name}' pushed.")
            else: st.warning("Please enter an image name for the registry.")
    with col_reg2:
        if st.button("Pull Image from Registry"):
            if registry_image_name:
                login_cmd = ""
                if registry_username and registry_password:
                    login_cmd = f"echo '{registry_password}' | sudo docker login --username {registry_username} --password-stdin && "
                cmd = f"{login_cmd}sudo docker pull {registry_image_name}"
                output, error = execute_ssh_command(host, username, password, cmd)
                if output: st.code(output)
                if error: st.error(error)
                if not error: st.success(f"Image '{registry_image_name}' pulled.")
            else: st.warning("Please enter an image name for the registry.")


def display_docker_network_management_tasks(host, username, password):
    st.subheader("Docker Network Management")
    st.info("Manage Docker networks on the remote Linux machine.")

    if st.button("List Networks (docker network ls)"):
        output, error = execute_ssh_command(host, username, password, "sudo docker network ls")
        if output: st.code(output)
        if error: st.error(error)

    create_network_name = st.text_input("Network Name to Create", key="docker_create_network")
    if st.button("Create Network"):
        if create_network_name:
            output, error = execute_ssh_command(host, username, password, f"sudo docker network create {create_network_name}")
            if output: st.success(f"Network '{create_network_name}' created.")
            if error: st.error(error)
        else: st.warning("Please enter a network name.")

    remove_network_name = st.text_input("Network Name to Remove", key="docker_remove_network")
    if st.button("Remove Network"):
        if remove_network_name:
            st.warning(f"This will remove network '{remove_network_name}'. Confirm to proceed.")
            if st.checkbox(f"Confirm removal of network {remove_network_name}", key=f"confirm_rm_network_{remove_network_name}"):
                output, error = execute_ssh_command(host, username, password, f"sudo docker network rm {remove_network_name}")
                if output: st.success(f"Network '{remove_network_name}' removed.")
                if error: st.error(error)
        else: st.warning("Please enter a network name.")

    inspect_network_name = st.text_input("Network Name to Inspect", key="docker_inspect_network")
    if st.button("Inspect Network"):
        if inspect_network_name:
            output, error = execute_ssh_command(host, username, password, f"sudo docker inspect {inspect_network_name}")
            if output: st.json(output)
            if error: st.error(error)
        else: st.warning("Please enter a network name.")

def display_docker_volume_management_tasks(host, username, password):
    st.subheader("Docker Volume Management")
    st.info("Manage Docker volumes on the remote Linux machine.")

    if st.button("List Volumes (docker volume ls)"):
        output, error = execute_ssh_command(host, username, password, "sudo docker volume ls")
        if output: st.code(output)
        if error: st.error(error)

    create_volume_name = st.text_input("Volume Name to Create", key="docker_create_volume")
    if st.button("Create Volume"):
        if create_volume_name:
            output, error = execute_ssh_command(host, username, password, f"sudo docker volume create {create_volume_name}")
            if output: st.success(f"Volume '{create_volume_name}' created.")
            if error: st.error(error)
        else: st.warning("Please enter a volume name.")

    remove_volume_name = st.text_input("Volume Name to Remove", key="docker_remove_volume")
    if st.button("Remove Volume"):
        if remove_volume_name:
            st.warning(f"This will remove volume '{remove_volume_name}'. Confirm to proceed.")
            if st.checkbox(f"Confirm removal of volume {remove_volume_name}", key=f"confirm_rm_volume_{remove_volume_name}"):
                output, error = execute_ssh_command(host, username, password, f"sudo docker volume rm {remove_volume_name}")
                if output: st.success(f"Volume '{remove_volume_name}' removed.")
                if error: st.error(error)
        else: st.warning("Please enter a volume name.")

    inspect_volume_name = st.text_input("Volume Name to Inspect", key="docker_inspect_volume")
    if st.button("Inspect Volume"):
        if inspect_volume_name:
            output, error = execute_ssh_command(host, username, password, f"sudo docker inspect {inspect_volume_name}")
            if output: st.json(output)
            if error: st.error(error)
        else: st.warning("Please enter a volume name.")

def display_docker_system_tasks(host, username, password):
    st.subheader("Docker System Information & Cleanup")
    st.info("Get Docker system-wide information and perform cleanup operations.")

    if st.button("Show Docker Info (docker info)"):
        output, error = execute_ssh_command(host, username, password, "sudo docker info")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("Show Docker Version (docker version)"):
        output, error = execute_ssh_command(host, username, password, "sudo docker version")
        if output: st.code(output)
        if error: st.error(error)

    if st.button("Show Disk Usage (docker system df)"):
        output, error = execute_ssh_command(host, username, password, "sudo docker system df")
        if output: st.code(output)
        if error: st.error(error)

    st.markdown("---")
    st.write("### Docker Cleanup")
    if st.button("Prune System (docker system prune -f)"):
        st.warning("This will remove all stopped containers, dangling images, unused networks, and build cache. Confirm to proceed.")
        if st.checkbox("Confirm Docker system prune", key="confirm_docker_prune"):
            output, error = execute_ssh_command(host, username, password, "sudo docker system prune -f")
            if output: st.success("Docker system pruned.")
            if error: st.error(error)

    if st.button("Prune Containers (docker container prune -f)"):
        st.warning("This will remove all stopped containers. Confirm to proceed.")
        if st.checkbox("Confirm Docker container prune", key="confirm_docker_container_prune"):
            output, error = execute_ssh_command(host, username, password, "sudo docker container prune -f")
            if output: st.success("Docker containers pruned.")
            if error: st.error(error)

    if st.button("Prune Images (docker image prune -f)"):
        st.warning("This will remove all dangling images. Confirm to proceed.")
        if st.checkbox("Confirm Docker image prune", key="confirm_docker_image_prune"):
            output, error = execute_ssh_command(host, username, password, "sudo docker image prune -f")
            if output: st.success("Docker images pruned.")
            if error: st.error(error)

    if st.button("Prune Volumes (docker volume prune -f)"):
        st.warning("This will remove all unused local volumes. Confirm to proceed.")
        if st.checkbox("Confirm Docker volume prune", key="confirm_docker_volume_prune"):
            output, error = execute_ssh_command(host, username, password, "sudo docker volume prune -f")
            if output: st.success("Docker volumes pruned.")
            if error: st.error(error)

    if st.button("Prune Networks (docker network prune -f)"):
        st.warning("This will remove all unused networks. Confirm to proceed.")
        if st.checkbox("Confirm Docker network prune", key="confirm_docker_network_prune"):
            output, error = execute_ssh_command(host, username, password, "sudo docker network prune -f")
            if output: st.success("Docker networks pruned.")
            if error: st.error(error)

def display_docker_compose_tasks(host, username, password):
    st.subheader("Docker Compose Management")
    st.info("Manage Docker Compose applications on the remote Linux machine. Requires Docker Compose installed.")

    docker_compose_content = st.text_area("docker-compose.yml Content", height=300, key="docker_compose_content")
    compose_project_path = st.text_input("Project Path (e.g., /opt/my_app)", key="compose_project_path", value="/tmp/docker_compose_project")

    if st.button("Deploy Docker Compose (Up)"):
        if docker_compose_content and compose_project_path:
            st.warning("This will create a temporary directory and `docker-compose.yml` on the remote server.")
            compose_file_path = os.path.join(compose_project_path, "docker-compose.yml")

            output, error = execute_ssh_command(host, username, password, f"mkdir -p {compose_project_path}")
            if error: st.error(f"Error creating project dir: {error}"); return

            escaped_compose_content = docker_compose_content.replace("'", "'\\''")
            output, error = execute_ssh_command(host, username, password, f"echo '{escaped_compose_content}' > {compose_file_path}")
            if error: st.error(f"Error writing docker-compose.yml: {error}"); return

            cmd = f"cd {compose_project_path} && sudo docker-compose up -d"
            output, error = execute_ssh_command(host, username, password, cmd)
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success("Docker Compose application deployed.")
        else: st.warning("Please provide docker-compose.yml content and a project path.")

    if st.button("Stop Docker Compose (Down)"):
        if compose_project_path:
            cmd = f"cd {compose_project_path} && sudo docker-compose down"
            output, error = execute_ssh_command(host, username, password, cmd)
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success("Docker Compose application stopped and removed.")
        else: st.warning("Please enter the project path.")

    if st.button("List Docker Compose Services (docker-compose ps)"):
        if compose_project_path:
            cmd = f"cd {compose_project_path} && sudo docker-compose ps"
            output, error = execute_ssh_command(host, username, password, cmd)
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter the project path.")

def display_docker_swarm_tasks(host, username, password):
    st.subheader("Docker Swarm Management")
    st.info("Manage Docker Swarm on the remote Linux machine. Requires Docker Swarm enabled.")

    if st.button("Initialize Docker Swarm"):
        st.warning("This will initialize a new Docker Swarm on the host. Only run on one manager node.")
        if st.checkbox("Confirm Swarm Initialization", key="confirm_swarm_init"):
            output, error = execute_ssh_command(host, username, password, "sudo docker swarm init")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success("Docker Swarm initialized.")

    swarm_join_token = st.text_input("Swarm Join Token (e.g., from 'docker swarm join-token worker')", key="swarm_join_token")
    swarm_manager_ip = st.text_input("Swarm Manager IP:Port (e.g., 192.168.1.100:2377)", key="swarm_manager_ip")
    if st.button("Join Docker Swarm"):
        if swarm_join_token and swarm_manager_ip:
            st.warning("This node will join the specified Docker Swarm.")
            cmd = f"sudo docker swarm join --token {swarm_join_token} {swarm_manager_ip}"
            output, error = execute_ssh_command(host, username, password, cmd)
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success("Node joined Docker Swarm.")
        else: st.warning("Please provide join token and manager IP.")

    if st.button("List Swarm Nodes (docker node ls)"):
        output, error = execute_ssh_command(host, username, password, "sudo docker node ls")
        if output: st.code(output)
        if error: st.error(error)

def display_docker_sub_menu():
    st.title("Docker Tasks Sub-Categories")
    st.write("Enter your SSH connection details for the RHEL9 machine where Docker is installed:")

    if 'ssh_connected' not in st.session_state:
        st.session_state.ssh_connected = False
    if 'ssh_host' not in st.session_state:
        st.session_state.ssh_host = ""
    if 'ssh_username' not in st.session_state:
        st.session_state.ssh_username = ""
    if 'ssh_password' not in st.session_state:
        st.session_state.ssh_password = ""

    ssh_host = st.text_input("RHEL9 IP Address/Hostname", key="docker_ssh_host_input", value=st.session_state.ssh_host)
    ssh_username = st.text_input("Username", key="docker_ssh_username_input", value=st.session_state.ssh_username)
    ssh_password = st.text_input("Password", type="password", key="docker_ssh_password_input", value=st.session_state.ssh_password)

    if st.button("Connect to Linux Machine for Docker", key="connect_docker_linux_btn"):
        if ssh_host and ssh_username and ssh_password:
            test_output, test_error = execute_ssh_command(ssh_host, ssh_username, ssh_password, "echo 'Docker Connection Test Successful'")
            if not test_error:
                st.session_state.ssh_host = ssh_host
                st.session_state.ssh_username = ssh_username
                st.session_state.ssh_password = ssh_password
                st.session_state.ssh_connected = True
                st.success("SSH connection successful for Docker tasks! Select a task category below.")
            else:
                st.session_state.ssh_connected = False
                st.error(f"SSH connection failed: {test_error}")
        else:
            st.error("Please provide all SSH connection details.")

    st.markdown("---")
    st.write("Select a sub-category to view specific Docker tasks.")

    if st.button("⬅️ Back to Main Menu", key="back_to_main_docker"):
        st.session_state.current_view = "main_menu"
        st.session_state.selected_category = None
        st.session_state.selected_sub_category = None
        st.session_state.ssh_connected = False
        st.rerun()

    st.markdown("---")

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        if st.button("Container Management", key="docker_container_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "docker_tasks_detail"
            st.session_state.selected_sub_category = "Container Management"
            st.rerun()
        if st.button("Image Management", key="docker_image_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "docker_tasks_detail"
            st.session_state.selected_sub_category = "Image Management"
            st.rerun()
    with col_d2:
        if st.button("Network Management", key="docker_network_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "docker_tasks_detail"
            st.session_state.selected_sub_category = "Network Management"
            st.rerun()
        if st.button("Volume Management", key="docker_volume_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "docker_tasks_detail"
            st.session_state.selected_sub_category = "Volume Management"
            st.rerun()
    with col_d3:
        if st.button("System & Info", key="docker_system_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "docker_tasks_detail"
            st.session_state.selected_sub_category = "System & Info"
            st.rerun()

    col_d4, col_d5, _ = st.columns(3)
    with col_d4:
        if st.button("Docker Compose", key="docker_compose_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "docker_tasks_detail"
            st.session_state.selected_sub_category = "Docker Compose"
            st.rerun()
    with col_d5:
        if st.button("Docker Swarm", key="docker_swarm_sub_btn", disabled=not st.session_state.ssh_connected):
            st.session_state.current_view = "docker_tasks_detail"
            st.session_state.selected_sub_category = "Docker Swarm"
            st.rerun()


def display_docker_tasks_detail():
    st.title(f"{st.session_state.selected_category} - {st.session_state.selected_sub_category}")

    if st.button(f"⬅️ Back to {st.session_state.selected_category} Sub-Categories", key="back_to_docker_sub"):
        st.session_state.current_view = "docker_sub_menu"
        st.session_state.selected_sub_category = None
        st.rerun()

    st.markdown("---")

    if not st.session_state.get('ssh_connected', False):
        st.error("Please connect to the Linux machine first by entering SSH credentials on the Docker sub-menu page.")
        return

    host = st.session_state.ssh_host
    username = st.session_state.ssh_username
    password = st.session_state.ssh_password

    if st.session_state.selected_sub_category == "Container Management":
        display_docker_container_management_tasks(host, username, password)
    elif st.session_state.selected_sub_category == "Image Management":
        display_docker_image_management_tasks(host, username, password)
    elif st.session_state.selected_sub_category == "Network Management":
        display_docker_network_management_tasks(host, username, password)
    elif st.session_state.selected_sub_category == "Volume Management":
        display_docker_volume_management_tasks(host, username, password)
    elif st.session_state.selected_sub_category == "System & Info":
        display_docker_system_tasks(host, username, password)
    elif st.session_state.selected_sub_category == "Docker Compose":
        display_docker_compose_tasks(host, username, password)
    elif st.session_state.selected_sub_category == "Docker Swarm":
        display_docker_swarm_tasks(host, username, password)