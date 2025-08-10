# views/kubernetes_local_tasks.py
import streamlit as st
import subprocess
import time
import os

# Helper function to execute local kubectl commands
def execute_kubectl_command_local(command, working_dir=None):
    """Executes a kubectl command locally and returns stdout and stderr."""
    try:
        # Use shell=True for commands with pipes or redirects.
        # Adding timeout to prevent hanging.
        result = subprocess.run(
            f"kubectl {command}",
            shell=True,
            check=True,  # Raise CalledProcessError for non-zero exit codes
            capture_output=True,
            text=True,
            timeout=60, # Increased timeout for potentially longer K8s operations
            cwd=working_dir
        )
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr # Return stdout/stderr even on error for debugging
    except subprocess.TimeoutExpired:
        return "", f"Command timed out after 60 seconds."
    except FileNotFoundError:
        return "", "kubectl command not found. Ensure Kubernetes is installed and kubectl is in your system's PATH."
    except Exception as e:
        return "", f"An unexpected error occurred: {e}"

# --- Individual Kubernetes Task Group Content Functions ---
# These functions display the actual lists of kubectl tasks

def display_k8s_cluster_overview_tasks_content():
    st.subheader("Cluster Overview Tasks")
    st.info("Retrieve general information about the Kubernetes cluster.")

    # 1
    if st.button("Get Nodes (kubectl get nodes)"):
        output, error = execute_kubectl_command_local("get nodes -o wide")
        if output: st.code(output)
        if error: st.error(error)

    # 2
    node_name_desc = st.text_input("Node Name to Describe", key="k8s_node_desc")
    if st.button("Describe Node (kubectl describe node)"):
        if node_name_desc:
            output, error = execute_kubectl_command_local(f"describe node {node_name_desc}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a node name.")
    
    # 3
    if st.button("Get Cluster Info (kubectl cluster-info)"):
        output, error = execute_kubectl_command_local("cluster-info")
        if output: st.code(output)
        if error: st.error(error)

    # 4
    if st.button("Get Kubernetes Version (kubectl version --short)"):
        output, error = execute_kubectl_command_local("version --short")
        if output: st.code(output)
        if error: st.error(error)

    # 5
    if st.button("Get All Namespaces (kubectl get namespaces)"):
        output, error = execute_kubectl_command_local("get namespaces")
        if output: st.code(output)
        if error: st.error(error)

    # 6
    namespace_name_switch = st.text_input("Namespace to Switch To", key="k8s_namespace_switch")
    if st.button("Switch to Namespace (kubectl config set-context)"):
        if namespace_name_switch:
            output, error = execute_kubectl_command_local(f"config set-context --current --namespace={namespace_name_switch}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Context switched to namespace '{namespace_name_switch}'.")
        else: st.warning("Please enter a namespace name.")

    # 7
    if st.button("Get Current Context (kubectl config current-context)"):
        output, error = execute_kubectl_command_local("config current-context")
        if output: st.code(output)
        if error: st.error(error)

    # 8
    if st.button("List All Contexts (kubectl config get-contexts)"):
        output, error = execute_kubectl_command_local("config get-contexts")
        if output: st.code(output)
        if error: st.error(error)

    # 9
    if st.button("Get Cluster Role Bindings (kubectl get clusterrolebindings)"):
        output, error = execute_kubectl_command_local("get clusterrolebindings")
        if output: st.code(output)
        if error: st.error(error)

    # 10
    if st.button("Get Component Status (kubectl get componentstatuses)"):
        output, error = execute_kubectl_command_local("get componentstatuses")
        if output: st.code(output)
        if error: st.error(error)

    # 11
    if st.button("List API Resources (kubectl api-resources)"):
        output, error = execute_kubectl_command_local("api-resources")
        if output: st.code(output)
        if error: st.error(error)
        
    st.markdown("---")
    st.write("### Node Operations")
    node_name_cordon = st.text_input("Node Name to Cordon/Uncordon", key="k8s_node_cordon_name")
    # 12
    if st.button("Cordon Node"):
        if node_name_cordon:
            st.warning(f"This will mark node '{node_name_cordon}' as unschedulable.")
            output, error = execute_kubectl_command_local(f"cordon {node_name_cordon}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Node '{node_name_cordon}' cordoned.")
        else: st.warning("Please enter a node name.")
    # 13
    if st.button("Uncordon Node"):
        if node_name_cordon:
            st.info(f"This will mark node '{node_name_cordon}' as schedulable.")
            output, error = execute_kubectl_command_local(f"uncordon {node_name_cordon}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Node '{node_name_cordon}' uncordoned.")
        else: st.warning("Please enter a node name.")

    # 14
    node_name_drain = st.text_input("Node Name to Drain", key="k8s_node_drain_name")
    if st.button("Drain Node"):
        if node_name_drain:
            st.warning(f"This will drain node '{node_name_drain}', evicting all pods. Use with extreme caution. Requires --ignore-daemonsets --delete-emptydir-data flags usually.")
            if st.checkbox(f"Confirm drain node {node_name_drain}", key=f"confirm_drain_node_{node_name_drain}"):
                output, error = execute_kubectl_command_local(f"drain {node_name_drain} --ignore-daemonsets --delete-emptydir-data --force") # Added --force
                if output: st.code(output)
                if error: st.error(error)
                if not error: st.success(f"Node '{node_name_drain}' drained (may not succeed without correct flags/permissions).")
        else: st.warning("Please enter a node name.")


def display_k8s_workloads_tasks_content():
    st.subheader("Workloads Management Tasks")
    st.info("Manage Pods, Deployments, StatefulSets, DaemonSets, and ReplicaSets.")

    # Pods
    # 15
    if st.button("Get Pods (kubectl get pods)"):
        output, error = execute_kubectl_command_local("get pods -o wide")
        if output: st.code(output)
        if error: st.error(error)

    # 16
    pod_name_desc = st.text_input("Pod Name to Describe", key="k8s_pod_desc_name")
    if st.button("Describe Pod (kubectl describe pod)"):
        if pod_name_desc:
            output, error = execute_kubectl_command_local(f"describe pod {pod_name_desc}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a pod name.")

    # 17
    pod_name_logs = st.text_input("Pod Name for Logs", key="k8s_pod_logs_name")
    if st.button("Get Pod Logs (kubectl logs)"):
        if pod_name_logs:
            output, error = execute_kubectl_command_local(f"logs {pod_name_logs}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a pod name.")
        
    # 18
    pod_name_exec = st.text_input("Pod Name for Exec", key="k8s_pod_exec_name")
    exec_command = st.text_input("Command to Execute in Pod (e.g., ls -l /)", key="k8s_exec_cmd")
    if st.button("Exec Command in Pod (kubectl exec)"):
        if pod_name_exec and exec_command:
            # Note: Interactive 'exec -it' is hard in Streamlit. This will just run the command.
            output, error = execute_kubectl_command_local(f"exec {pod_name_exec} -- {exec_command}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter pod name and command.")

    # 19
    pod_name_del = st.text_input("Pod Name to Delete", key="k8s_pod_del_name")
    if st.button("Delete Pod (kubectl delete pod)"):
        if pod_name_del:
            st.warning(f"This will delete pod '{pod_name_del}'. Confirm to proceed.")
            if st.checkbox(f"Confirm deletion of pod {pod_name_del}", key=f"confirm_del_pod_{pod_name_del}"):
                output, error = execute_kubectl_command_local(f"delete pod {pod_name_del}")
                if output: st.code(output)
                if error: st.error(error)
                if not error: st.success(f"Pod '{pod_name_del}' deleted.")
        else: st.warning("Please enter a pod name.")

    st.markdown("---")
    # Deployments
    # 20
    if st.button("Get Deployments (kubectl get deployments)"):
        output, error = execute_kubectl_command_local("get deployments -o wide")
        if output: st.code(output)
        if error: st.error(error)

    # 21
    deployment_name_create = st.text_input("Deployment Name to Create", key="k8s_dep_create_name")
    deployment_file = st.text_input("Deployment YAML File (e.g., my-app.yaml)", key="k8s_dep_create_file")
    if st.button("Create Deployment (kubectl create -f)"):
        if deployment_name_create and deployment_file:
            st.warning("Ensure the YAML file exists in your current working directory.")
            output, error = execute_kubectl_command_local(f"create -f {deployment_file}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Deployment '{deployment_name_create}' created from file '{deployment_file}'.")
        else: st.warning("Please enter a deployment name and YAML file path.")

    # 22
    deployment_name_desc = st.text_input("Deployment Name to Describe", key="k8s_dep_desc_name")
    if st.button("Describe Deployment (kubectl describe deployment)"):
        if deployment_name_desc:
            output, error = execute_kubectl_command_local(f"describe deployment {deployment_name_desc}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a deployment name.")
    
    # 23
    deployment_name_image = st.text_input("Deployment Name to Update Image", key="k8s_dep_image_name")
    container_name = st.text_input("Container Name", key="k8s_container_name")
    new_image = st.text_input("New Image (e.g., nginx:1.20)", key="k8s_new_image")
    if st.button("Update Deployment Image (kubectl set image)"):
        if deployment_name_image and container_name and new_image:
            output, error = execute_kubectl_command_local(f"set image deployment/{deployment_name_image} {container_name}={new_image}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Deployment '{deployment_name_image}' image updated to '{new_image}'.")
        else: st.warning("Please enter deployment name, container name, and new image.")

    # 24
    deployment_name_scale = st.text_input("Deployment Name to Scale", key="k8s_dep_scale_name")
    replicas = st.number_input("Number of Replicas", min_value=0, value=1, key="k8s_dep_replicas")
    if st.button("Scale Deployment (kubectl scale)"):
        if deployment_name_scale is not None and replicas is not None:
            output, error = execute_kubectl_command_local(f"scale deployment {deployment_name_scale} --replicas={replicas}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Deployment '{deployment_name_scale}' scaled to {replicas} replicas.")
        else: st.warning("Please enter a deployment name and number of replicas.")

    # 25
    deployment_name_autosca = st.text_input("Deployment Name to Autoscale", key="k8s_dep_autosca_name")
    min_replicas_hpa = st.number_input("Min Replicas", min_value=1, value=1, key="k8s_hpa_min_reps")
    max_replicas_hpa = st.number_input("Max Replicas", min_value=1, value=5, key="k8s_hpa_max_reps")
    cpu_percent_hpa = st.number_input("Target CPU Utilization (%)", min_value=1, value=80, key="k8s_hpa_cpu_percent")
    if st.button("Autoscale Deployment (kubectl autoscale)"):
        if deployment_name_autosca and min_replicas_hpa and max_replicas_hpa and cpu_percent_hpa:
            output, error = execute_kubectl_command_local(f"autoscale deployment {deployment_name_autosca} --min={min_replicas_hpa} --max={max_replicas_hpa} --cpu-percent={cpu_percent_hpa}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"HPA configured for deployment '{deployment_name_autosca}'.")
        else: st.warning("Please fill all autoscale fields.")

    # 26
    deployment_name_rollback = st.text_input("Deployment Name to Rollback", key="k8s_dep_rollback")
    if st.button("Rollback Deployment (kubectl rollout undo)"):
        if deployment_name_rollback:
            st.warning(f"This will rollback the deployment '{deployment_name_rollback}' to its previous revision.")
            output, error = execute_kubectl_command_local(f"rollout undo deployment/{deployment_name_rollback}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Deployment '{deployment_name_rollback}' rolled back.")
        else: st.warning("Please enter a deployment name.")

    # 27
    deployment_name_del = st.text_input("Deployment Name to Delete", key="k8s_dep_del_name")
    if st.button("Delete Deployment (kubectl delete deployment)"):
        if deployment_name_del:
            st.warning(f"This will delete deployment '{deployment_name_del}'. Confirm to proceed.")
            if st.checkbox(f"Confirm deletion of deployment {deployment_name_del}", key=f"confirm_del_dep_{deployment_name_del}"):
                output, error = execute_kubectl_command_local(f"delete deployment {deployment_name_del}")
                if output: st.code(output)
                if error: st.error(error)
                if not error: st.success(f"Deployment '{deployment_name_del}' deleted.")
        else: st.warning("Please enter a deployment name.")

    st.markdown("---")
    # StatefulSets
    # 28
    if st.button("Get StatefulSets (kubectl get statefulsets)"):
        output, error = execute_kubectl_command_local("get statefulsets -o wide")
        if output: st.code(output)
        if error: st.error(error)

    # 29
    ss_name = st.text_input("StatefulSet Name to Describe", key="k8s_ss_desc")
    if st.button("Describe StatefulSet"):
        if ss_name:
            output, error = execute_kubectl_command_local(f"describe statefulset {ss_name}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a StatefulSet name.")

    # DaemonSets
    # 30
    if st.button("Get DaemonSets (kubectl get daemonsets)"):
        output, error = execute_kubectl_command_local("get daemonsets -o wide")
        if output: st.code(output)
        if error: st.error(error)

    # 31
    ds_name = st.text_input("DaemonSet Name to Describe", key="k8s_ds_desc")
    if st.button("Describe DaemonSet"):
        if ds_name:
            output, error = execute_kubectl_command_local(f"describe daemonset {ds_name}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a DaemonSet name.")

    # 32
    if st.button("Get ReplicaSets"):
        output, error = execute_kubectl_command_local("get replicasets -o wide")
        if output: st.code(output)
        if error: st.error(error)

def display_k8s_networking_tasks_content():
    st.subheader("Networking Management Tasks")
    st.info("Manage Services, Ingresses, and Network Policies.")

    # Services
    # 33
    if st.button("Get Services (kubectl get services)"):
        output, error = execute_kubectl_command_local("get services -o wide")
        if output: st.code(output)
        if error: st.error(error)

    # 34
    svc_name_desc = st.text_input("Service Name to Describe", key="k8s_svc_desc_name")
    if st.button("Describe Service (kubectl describe service)"):
        if svc_name_desc:
            output, error = execute_kubectl_command_local(f"describe service {svc_name_desc}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a service name.")
    
    # 35
    deployment_to_expose = st.text_input("Deployment Name to Expose", key="k8s_expose_deployment")
    expose_type = st.selectbox("Service Type", ("ClusterIP", "NodePort", "LoadBalancer"), key="k8s_expose_type")
    expose_port = st.number_input("Service Port", min_value=1, value=80, key="k8s_expose_port")
    if st.button("Expose Deployment as a Service"):
        if deployment_to_expose and expose_type and expose_port:
            output, error = execute_kubectl_command_local(f"expose deployment {deployment_to_expose} --type={expose_type} --port={expose_port}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Deployment '{deployment_to_expose}' exposed as a {expose_type} service on port {expose_port}.")
        else: st.warning("Please fill all service exposure fields.")

    # 36
    svc_name_del = st.text_input("Service Name to Delete", key="k8s_svc_del_name")
    if st.button("Delete Service"):
        if svc_name_del:
            st.warning(f"This will delete service '{svc_name_del}'. Confirm to proceed.")
            if st.checkbox(f"Confirm deletion of service {svc_name_del}", key=f"confirm_del_svc_{svc_name_del}"):
                output, error = execute_kubectl_command_local(f"delete service {svc_name_del}")
                if output: st.code(output)
                if error: st.error(error)
                if not error: st.success(f"Service '{svc_name_del}' deleted.")
        else: st.warning("Please enter a service name.")

    # 37
    if st.button("Get Endpoints"):
        output, error = execute_kubectl_command_local("get endpoints -o wide")
        if output: st.code(output)
        if error: st.error(error)

    st.markdown("---")
    # Ingresses
    # 38
    if st.button("Get Ingresses (kubectl get ingress)"):
        output, error = execute_kubectl_command_local("get ingress -o wide")
        if output: st.code(output)
        if error: st.error(error)

    # 39
    ing_name_desc = st.text_input("Ingress Name to Describe", key="k8s_ing_desc_name")
    if st.button("Describe Ingress (kubectl describe ingress)"):
        if ing_name_desc:
            output, error = execute_kubectl_command_local(f"describe ingress {ing_name_desc}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter an ingress name.")

    # 40
    ing_name_del = st.text_input("Ingress Name to Delete", key="k8s_ing_del_name")
    if st.button("Delete Ingress"):
        if ing_name_del:
            st.warning(f"This will delete ingress '{ing_name_del}'. Confirm to proceed.")
            if st.checkbox(f"Confirm deletion of ingress {ing_name_del}", key=f"confirm_del_ing_{ing_name_del}"):
                output, error = execute_kubectl_command_local(f"delete ingress {ing_name_del}")
                if output: st.code(output)
                if error: st.error(error)
                if not error: st.success(f"Ingress '{ing_name_del}' deleted.")
        else: st.warning("Please enter an ingress name.")

    st.markdown("---")
    # NetworkPolicies
    # 41
    if st.button("Get NetworkPolicies (kubectl get networkpolicies)"):
        output, error = execute_kubectl_command_local("get networkpolicies -o wide")
        if output: st.code(output)
        if error: st.error(error)

def display_k8s_config_storage_tasks_content():
    st.subheader("Configuration & Storage Management Tasks")
    st.info("Manage ConfigMaps, Secrets, Persistent Volumes, and Persistent Volume Claims.")

    # ConfigMaps
    # 42
    if st.button("Get ConfigMaps (kubectl get configmaps)"):
        output, error = execute_kubectl_command_local("get configmaps -o wide")
        if output: st.code(output)
        if error: st.error(error)
    
    # 43
    cm_name_create = st.text_input("ConfigMap Name to Create", key="k8s_cm_create_name")
    cm_file = st.text_input("File Path for ConfigMap (e.g., config.txt)", key="k8s_cm_file")
    if st.button("Create ConfigMap (kubectl create configmap)"):
        if cm_name_create and cm_file:
            st.warning("Ensure the file exists in your current working directory.")
            output, error = execute_kubectl_command_local(f"create configmap {cm_name_create} --from-file={cm_file}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"ConfigMap '{cm_name_create}' created from file '{cm_file}'.")
        else: st.warning("Please enter a ConfigMap name and a file path.")

    # 44
    cm_name_desc = st.text_input("ConfigMap Name to Describe", key="k8s_cm_desc_name")
    if st.button("Describe ConfigMap"):
        if cm_name_desc:
            output, error = execute_kubectl_command_local(f"describe configmap {cm_name_desc}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a ConfigMap name.")

    # 45
    cm_name_del = st.text_input("ConfigMap Name to Delete", key="k8s_cm_del_name")
    if st.button("Delete ConfigMap"):
        if cm_name_del:
            st.warning(f"This will delete ConfigMap '{cm_name_del}'. Confirm to proceed.")
            if st.checkbox(f"Confirm deletion of ConfigMap {cm_name_del}", key=f"confirm_del_cm_{cm_name_del}"):
                output, error = execute_kubectl_command_local(f"delete configmap {cm_name_del}")
                if output: st.code(output)
                if error: st.error(error)
                if not error: st.success(f"ConfigMap '{cm_name_del}' deleted.")
        else: st.warning("Please enter a ConfigMap name.")

    st.markdown("---")
    # Secrets
    # 46
    if st.button("Get Secrets (kubectl get secrets)"):
        st.warning("Displaying secrets directly may expose sensitive information. Use caution.")
        output, error = execute_kubectl_command_local("get secrets")
        if output: st.code(output)
        if error: st.error(error)
    
    # 47
    secret_name_create = st.text_input("Secret Name to Create", key="k8s_secret_create_name")
    secret_key_val = st.text_input("Key=Value for Secret (e.g., username=admin)", key="k8s_secret_key_val")
    if st.button("Create Secret (kubectl create secret)"):
        if secret_name_create and secret_key_val:
            output, error = execute_kubectl_command_local(f"create secret generic {secret_name_create} --from-literal={secret_key_val}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Secret '{secret_name_create}' created.")
        else: st.warning("Please enter a secret name and a key-value pair.")

    # 48
    secret_name_desc = st.text_input("Secret Name to Describe (not decode)", key="k8s_secret_desc_name")
    if st.button("Describe Secret"):
        if secret_name_desc:
            st.warning("Describing secrets shows base64 encoded data. Decoding not performed for security.")
            output, error = execute_kubectl_command_local(f"describe secret {secret_name_desc}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a Secret name.")

    # 49
    secret_name_del = st.text_input("Secret Name to Delete", key="k8s_secret_del_name")
    if st.button("Delete Secret"):
        if secret_name_del:
            st.warning(f"This will delete Secret '{secret_name_del}'. Confirm to proceed.")
            if st.checkbox(f"Confirm deletion of Secret {secret_name_del}", key=f"confirm_del_secret_{secret_name_del}"):
                output, error = execute_kubectl_command_local(f"delete secret {secret_name_del}")
                if output: st.code(output)
                if error: st.error(error)
                if not error: st.success(f"Secret '{secret_name_del}' deleted.")
        else: st.warning("Please enter a Secret name.")

    st.markdown("---")
    # Persistent Volumes
    # 50
    if st.button("Get Persistent Volumes (kubectl get pv)"):
        output, error = execute_kubectl_command_local("get pv -o wide")
        if output: st.code(output)
        if error: st.error(error)

    # 51
    if st.button("Get Persistent Volume Claims (kubectl get pvc)"):
        output, error = execute_kubectl_command_local("get pvc -o wide")
        if output: st.code(output)
        if error: st.error(error)

    # 52
    pvc_name_desc = st.text_input("PVC Name to Describe", key="k8s_pvc_desc_name")
    if st.button("Describe PVC"):
        if pvc_name_desc:
            output, error = execute_kubectl_command_local(f"describe pvc {pvc_name_desc}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a PVC name.")


def display_k8s_advanced_tasks_content():
    st.subheader("Advanced Operations Tasks")
    st.info("Execute advanced operations including applying YAML and patching resources.")

    st.markdown("### Apply/Delete YAML Manifests")
    yaml_content = st.text_area("Kubernetes YAML Manifest Content", height=300, key="k8s_yaml_content")
    yaml_filename = st.text_input("Temporary YAML Filename (e.g., my-app.yaml)", "temp-k8s-manifest.yaml")

    # 53
    if st.button("Apply YAML (kubectl apply -f)"):
        if yaml_content and yaml_filename:
            temp_path = os.path.join(os.getcwd(), yaml_filename) # Use current working dir for temp file

            try:
                with open(temp_path, "w") as f:
                    f.write(yaml_content)
                st.info(f"Temporary YAML file created at: {temp_path}")
            except Exception as e:
                st.error(f"Error writing YAML file locally: {e}")
                return

            apply_output, apply_error = execute_kubectl_command_local(f"apply -f {temp_path}")
            if apply_output: st.code(apply_output)
            if apply_error: st.error(apply_error)
            if not apply_error: st.success(f"Manifest '{yaml_filename}' applied.")

            # Clean up temporary file
            try:
                os.remove(temp_path)
                st.info(f"Cleaned up temporary YAML file: {temp_path}")
            except Exception as e:
                st.warning(f"Could not remove temporary YAML file: {e}")
        else: st.warning("Please provide YAML content and a filename.")

    # 54
    if st.button("Delete YAML (kubectl delete -f)"):
        if yaml_content and yaml_filename:
            temp_path = os.path.join(os.getcwd(), yaml_filename)

            try:
                with open(temp_path, "w") as f:
                    f.write(yaml_content)
                st.info(f"Temporary YAML file created at: {temp_path}")
            except Exception as e:
                st.error(f"Error writing YAML file locally: {e}")
                return

            st.warning(f"This will delete resources defined in '{yaml_filename}'. Confirm to proceed.")
            if st.checkbox(f"Confirm deletion of resources from {yaml_filename}", key=f"confirm_del_yaml_{yaml_filename}"):
                delete_output, delete_error = execute_kubectl_command_local(f"delete -f {temp_path}")
                if delete_output: st.code(delete_output)
                if delete_error: st.error(delete_error)
                if not delete_error: st.success(f"Resources from '{yaml_filename}' deleted.")

            try:
                os.remove(temp_path)
                st.info(f"Cleaned up temporary YAML file: {temp_path}")
            except Exception as e:
                st.warning(f"Could not remove temporary YAML file: {e}")
        else: st.warning("Please provide YAML content and a filename.")

    st.markdown("---")
    st.write("### Label & Taint Nodes")
    node_name_label = st.text_input("Node Name for Label/Taint", key="k8s_node_label_name")
    # 55
    label_string = st.text_input("Label (e.g., disktype=ssd)", key="k8s_node_label_str")
    if st.button("Add Label to Node"):
        if node_name_label and label_string:
            output, error = execute_kubectl_command_local(f"label node {node_name_label} {label_string}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Label '{label_string}' added to node '{node_name_label}'.")
        else: st.warning("Please enter node name and label string.")

    # 56
    taint_string = st.text_input("Taint (e.g., key=value:NoSchedule)", key="k8s_node_taint_str")
    if st.button("Add Taint to Node"):
        if node_name_label and taint_string:
            output, error = execute_kubectl_command_local(f"taint node {node_name_label} {taint_string}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Taint '{taint_string}' added to node '{node_name_label}'.")
        else: st.warning("Please enter node name and taint string.")

    # 57
    if st.button("Remove Taint from Node"):
        if node_name_label and taint_string:
            output, error = execute_kubectl_command_local(f"taint node {node_name_label} {taint_string}-")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Taint '{taint_string}' removed from node '{node_name_label}'.")
        else: st.warning("Please enter node name and taint string.")

def display_k8s_troubleshooting_tasks_content():
    st.subheader("Troubleshooting & Debugging Tasks")
    st.info("Tools to help diagnose issues in your cluster.")

    # 58
    if st.button("View Pod Logs (kubectl logs)"):
        pod_name_logs_troubleshoot = st.text_input("Pod Name for Logs", key="k8s_pod_logs_name_ts")
        if pod_name_logs_troubleshoot:
            output, error = execute_kubectl_command_local(f"logs {pod_name_logs_troubleshoot}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a pod name.")

    # 59
    if st.button("Stream Pod Logs (kubectl logs -f)"):
        pod_name_log_filter = st.text_input("Pod Name to Stream Logs", key="pod_name_log_filter")
        if pod_name_log_filter:
            st.info(f"Streaming logs for pod '{pod_name_log_filter}'. This will block until the app is re-run or the stream is broken.")
            output, error = execute_kubectl_command_local(f"logs -f {pod_name_log_filter}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a pod name to stream logs.")

    # 60
    if st.button("Execute a Command in a Container"):
        exec_pod_name_ts = st.text_input("Pod name", key="exec_pod_name_ts")
        exec_command_ts = st.text_input("Command (e.g., ls -l)", key="exec_command_ts")
        if exec_pod_name_ts and exec_command_ts:
            output, error = execute_kubectl_command_local(f"exec {exec_pod_name_ts} -- {exec_command_ts}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a pod name and command.")
    
    # 61
    if st.button("Get All Events (kubectl get events --sort-by='.lastTimestamp' | tail -n 20)"):
        output, error = execute_kubectl_command_local("get events --sort-by='.lastTimestamp' | tail -n 20")
        if output: st.code(output)
        if error: st.error(error)

    # 62
    node_name_debug = st.text_input("Node Name to Describe (for troubleshooting)", key="k8s_node_debug_name")
    if st.button("Describe Node (for troubleshooting)"):
        if node_name_debug:
            output, error = execute_kubectl_command_local(f"describe node {node_name_debug}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a node name.")

    # 63
    if st.button("Get All Resources in All Namespaces (kubectl get all -A)"):
        output, error = execute_kubectl_command_local("get all --all-namespaces")
        if output: st.code(output)
        if error: st.error(error)

    # 64
    if st.button("Get Top Nodes (kubectl top nodes)"):
        st.info("Requires Kubernetes Metrics Server to be installed in your cluster.")
        output, error = execute_kubectl_command_local("top nodes")
        if output: st.code(output)
        if error: st.error(error)

    # 65
    if st.button("Get Top Pods (kubectl top pods)"):
        st.info("Requires Kubernetes Metrics Server to be installed in your cluster.")
        output, error = execute_kubectl_command_local("top pods")
        if output: st.code(output)
        if error: st.error(error)

    # 66
    if st.button("Check `kube-system` Pod Status"):
        output, error = execute_kubectl_command_local("get pods -n kube-system -o wide")
        if output: st.code(output)
        if error: st.error(error)

    # 67
    if st.button("Get Failed Pods"):
        output, error = execute_kubectl_command_local("get pods --field-selector=status.phase=Failed")
        if output: st.code(output)
        if error: st.error(error)

    # 68
    if st.button("Debug Pod (kubectl debug)"):
        debug_pod_name = st.text_input("Pod name to debug", key="debug_pod_name")
        if debug_pod_name:
            st.warning("This creates an ephemeral debug container. Requires `kubectl debug` and a compatible K8s version.")
            output, error = execute_kubectl_command_local(f"debug {debug_pod_name} -it --image=busybox --target={debug_pod_name}")
            if output: st.code(output)
            if error: st.error(error)
            if not error: st.success(f"Debug container attached to pod '{debug_pod_name}'. You might need to open a separate terminal to interact.")
        else: st.warning("Please enter a pod name to debug.")
    
    # 69
    resource_name = st.text_input("Resource Name (e.g., my-pod)", key="troubleshoot_res_name")
    resource_type = st.text_input("Resource Type (e.g., pod)", key="troubleshoot_res_type")
    if st.button("Get Pods by Owner Reference"):
        if resource_name and resource_type:
            output, error = execute_kubectl_command_local(f"get pods --field-selector=metadata.ownerReferences[0].name={resource_name},metadata.ownerReferences[0].kind={resource_type}")
            if output: st.code(output)
            if error: st.error(error)
        else: st.warning("Please enter a resource name and type.")


# --- Kubernetes Main Sub-Menu and Task Detail Page ---

def display_k8s_sub_menu():
    st.title("Kubernetes Tasks Sub-Categories")
    st.write("These tasks will execute `kubectl` commands directly on this local machine. Ensure `kubectl` is installed and configured in your system's PATH, and has access to your Kubernetes cluster.")

    # Local kubectl doesn't need explicit "connection" button in UI,
    # but we can do a check for `kubectl` presence.
    if st.button("Verify Local kubectl Setup"):
        output, error = execute_kubectl_command_local("version --client")
        if not error and "Client Version" in output:
            st.session_state.kubectl_local_ready = True
            st.success(f"Local kubectl client detected and ready! {output.splitlines()[0]}")
        else:
            st.session_state.kubectl_local_ready = False
            st.error(f"kubectl not ready: {error}. Please ensure kubectl is installed and in your PATH.")

    if 'kubectl_local_ready' not in st.session_state:
        st.session_state.kubectl_local_ready = False # Initialize it

    st.markdown("---")
    st.write("Select a sub-category to view specific Kubernetes tasks.")

    if st.button("⬅️ Back to Main Menu", key="back_to_main_k8s"):
        st.session_state.current_view = "main_menu"
        st.session_state.selected_category = None
        st.session_state.selected_sub_category = None
        st.session_state.selected_ml_sub_category = None
        st.session_state.selected_k8s_sub_category = None # Ensure this is reset
        st.session_state.kubectl_local_ready = False # Reset local kubectl check
        st.rerun()

    st.markdown("---")

    # Arrange Kubernetes Sub-Category Buttons in columns
    col_k8s_1, col_k8s_2, col_k8s_3 = st.columns(3)
    with col_k8s_1:
        if st.button("Cluster Overview", key="k8s_cluster_overview_sub_btn", disabled=not st.session_state.kubectl_local_ready):
            st.session_state.current_view = "k8s_tasks_detail" # Navigate to the detail page for K8s sub-tasks
            st.session_state.selected_k8s_sub_category = "Cluster Overview"
            st.rerun()
        if st.button("Workloads Management", key="k8s_workloads_sub_btn", disabled=not st.session_state.kubectl_local_ready):
            st.session_state.current_view = "k8s_tasks_detail"
            st.session_state.selected_k8s_sub_category = "Workloads Management"
            st.rerun()
    with col_k8s_2:
        if st.button("Networking Management", key="k8s_networking_sub_btn", disabled=not st.session_state.kubectl_local_ready):
            st.session_state.current_view = "k8s_tasks_detail"
            st.session_state.selected_k8s_sub_category = "Networking Management"
            st.rerun()
        if st.button("Config & Storage Management", key="k8s_config_storage_sub_btn", disabled=not st.session_state.kubectl_local_ready):
            st.session_state.current_view = "k8s_tasks_detail"
            st.session_state.selected_k8s_sub_category = "Config & Storage Management"
            st.rerun()
    with col_k8s_3:
        if st.button("Advanced Operations", key="k8s_advanced_sub_btn", disabled=not st.session_state.kubectl_local_ready):
            st.session_state.current_view = "k8s_tasks_detail"
            st.session_state.selected_k8s_sub_category = "Advanced Operations"
            st.rerun()
        if st.button("Troubleshooting & Debugging", key="k8s_troubleshooting_sub_btn", disabled=not st.session_state.kubectl_local_ready):
            st.session_state.current_view = "k8s_tasks_detail"
            st.session_state.selected_k8s_sub_category = "Troubleshooting & Debugging"
            st.rerun()


def display_k8s_tasks_detail(): # This now acts as the task *displayer* for selected K8s sub-category
    st.title(f"{st.session_state.selected_category} - {st.session_state.selected_k8s_sub_category}")

    # Back button to K8s sub-menu (one level up)
    if st.button(f"⬅️ Back to {st.session_state.selected_category} Sub-Categories", key="back_to_k8s_main_sub_menu"):
        st.session_state.current_view = "k8s_sub_menu"
        st.session_state.selected_k8s_sub_category = None # Clear detailed K8s sub-category
        st.rerun()

    st.markdown("---")

    # If kubectl isn't verified as ready, show a warning
    if not st.session_state.get('kubectl_local_ready', False):
        st.warning("kubectl client is not verified as ready. Please go back to 'Kubernetes Tasks' and click 'Verify Local kubectl Setup' first.")
        return

    # Call the appropriate content function based on the selected K8s sub-category
    if st.session_state.selected_k8s_sub_category == "Cluster Overview":
        display_k8s_cluster_overview_tasks_content()
    elif st.session_state.selected_k8s_sub_category == "Workloads Management":
        display_k8s_workloads_tasks_content()
    elif st.session_state.selected_k8s_sub_category == "Networking Management":
        display_k8s_networking_tasks_content()
    elif st.session_state.selected_k8s_sub_category == "Config & Storage Management":
        display_k8s_config_storage_tasks_content()
    elif st.session_state.selected_k8s_sub_category == "Advanced Operations":
        display_k8s_advanced_tasks_content()
    elif st.session_state.selected_k8s_sub_category == "Troubleshooting & Debugging":
        display_k8s_troubleshooting_tasks_content()