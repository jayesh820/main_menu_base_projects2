# views/aws_views.py
import streamlit as st
import boto3
import pandas as pd
import json
import time
import base64 # For Lambda ZIP file encoding

# Helper function to display AWS operation results
def display_aws_result(output, error=""):
    if error:
        st.error(f"AWS Error: {error}")
    if output:
        if isinstance(output, (dict, list)):
            st.json(output)
        else:
            st.code(output)

# --- Individual AWS Service Task Content Functions ---

def display_ec2_tasks():
    st.subheader("EC2 (Elastic Compute Cloud) Tasks")
    ec2_client = boto3.client('ec2')

    if st.button("List All EC2 Instances"):
        try:
            response = ec2_client.describe_instances()
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    instance_type = instance['InstanceType']
                    state = instance['State']['Name']
                    launch_time = instance['LaunchTime']
                    public_ip = instance.get('PublicIpAddress', 'N/A')
                    private_ip = instance.get('PrivateIpAddress', 'N/A')
                    name_tag = 'N/A'
                    for tag in instance.get('Tags', []):
                        if tag['Key'] == 'Name':
                            name_tag = tag['Value']
                            break
                    instances.append({
                        'Name': name_tag,
                        'InstanceId': instance_id,
                        'InstanceType': instance_type,
                        'State': state,
                        'LaunchTime': launch_time,
                        'PublicIp': public_ip,
                        'PrivateIp': private_ip
                    })
            if instances:
                st.dataframe(pd.DataFrame(instances))
            else:
                st.info("No EC2 instances found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Manage Existing Instances")
    instance_id = st.text_input("Instance ID (e.g., i-0abcdef1234567890)", key="ec2_instance_id")
    if st.button("Start Instance"):
        if instance_id:
            try:
                response = ec2_client.start_instances(InstanceIds=[instance_id])
                display_aws_result(response)
                st.success(f"Attempted to start instance {instance_id}")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide an Instance ID.")
    if st.button("Stop Instance"):
        if instance_id:
            try:
                response = ec2_client.stop_instances(InstanceIds=[instance_id])
                display_aws_result(response)
                st.success(f"Attempted to stop instance {instance_id}")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide an Instance ID.")
    if st.button("Reboot Instance"):
        if instance_id:
            try:
                response = ec2_client.reboot_instances(InstanceIds=[instance_id])
                display_aws_result(response)
                st.success(f"Attempted to reboot instance {instance_id}")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide an Instance ID.")
    
    st.markdown("---")
    st.write("### Launch New Instances")
    ami_id = st.text_input("AMI ID (e.g., ami-0abcdef1234567890 for Amazon Linux 2)", "ami-0abcdef1234567890", help="Find valid AMI IDs for your region in EC2 console or AWS Docs.")
    instance_type = st.selectbox("Instance Type", ["t2.micro", "t2.small", "t2.medium", "t3.micro", "t3.small"], index=0)
    min_count = st.number_input("Minimum Instances", min_value=1, value=1)
    max_count = st.number_input("Maximum Instances", min_value=1, value=1)
    key_pair_name = st.text_input("Key Pair Name (optional)", help="Name of an existing EC2 Key Pair for SSH access.")

    if st.button("Launch EC2 Instance(s)"):
        if ami_id and instance_type:
            try:
                launch_params = {
                    'ImageId': ami_id,
                    'InstanceType': instance_type,
                    'MinCount': min_count,
                    'MaxCount': max_count,
                }
                if key_pair_name:
                    launch_params['KeyName'] = key_pair_name

                response = ec2_client.run_instances(**launch_params)
                display_aws_result(response)
                st.success(f"Launched {min_count}-{max_count} instances of type {instance_type} from AMI {ami_id}.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide AMI ID and Instance Type.")

    st.markdown("---")
    st.write("### Terminate Instances")
    terminate_instance_id = st.text_input("Instance ID to Terminate", key="ec2_terminate_instance_id")
    if st.button("Terminate Instance"):
        if terminate_instance_id:
            st.warning(f"This will TERMINATE instance {terminate_instance_id}. This action is irreversible.")
            if st.checkbox(f"Confirm termination of {terminate_instance_id}", key="confirm_terminate_ec2"):
                try:
                    response = ec2_client.terminate_instances(InstanceIds=[terminate_instance_id])
                    display_aws_result(response)
                    st.success(f"Attempted to terminate instance {terminate_instance_id}")
                except Exception as e:
                    display_aws_result(None, e)
        else: st.warning("Please provide an Instance ID to terminate.")


def display_s3_tasks():
    st.subheader("S3 (Simple Storage Service) Tasks")
    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')

    if st.button("List All S3 Buckets"):
        try:
            response = s3_client.list_buckets()
            buckets = [{'Name': b['Name'], 'CreationDate': b['CreationDate']} for b in response['Buckets']]
            if buckets:
                st.dataframe(pd.DataFrame(buckets))
            else:
                st.info("No S3 buckets found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Manage Buckets")
    bucket_name = st.text_input("Bucket Name", key="s3_bucket_name")
    if st.button("Create Bucket"):
        if bucket_name:
            try:
                # Note: Region-specific bucket creation is recommended for new buckets
                response = s3_client.create_bucket(Bucket=bucket_name) # , CreateBucketConfiguration={'LocationConstraint': s3_client.meta.region_name}
                display_aws_result(response)
                st.success(f"Bucket '{bucket_name}' created.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a bucket name.")

    if st.button("Delete Bucket"):
        if bucket_name:
            st.warning(f"This will DELETE bucket '{bucket_name}' and ALL its contents. This action is irreversible.")
            if st.checkbox(f"Confirm deletion of bucket {bucket_name}", key="confirm_delete_s3_bucket"):
                try:
                    s3_resource.Bucket(bucket_name).objects.all().delete() # Delete all objects first
                    response = s3_client.delete_bucket(Bucket=bucket_name)
                    display_aws_result(response)
                    st.success(f"Bucket '{bucket_name}' deleted.")
                except Exception as e:
                    display_aws_result(None, e)
        else: st.warning("Please provide a bucket name.")

    st.markdown("---")
    st.write("### Manage Objects in Bucket")
    bucket_name_obj = st.text_input("Bucket Name for Objects", key="s3_bucket_name_obj")
    if st.button("List Objects in Selected Bucket"):
        if bucket_name_obj:
            try:
                response = s3_client.list_objects_v2(Bucket=bucket_name_obj)
                contents = response.get('Contents', [])
                objects = [{'Key': obj['Key'], 'Size': obj['Size'], 'LastModified': obj['LastModified']} for obj in contents]
                if objects:
                    st.dataframe(pd.DataFrame(objects))
                else:
                    st.info(f"No objects found in bucket '{bucket_name_obj}'.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a bucket name for objects.")

    object_key_upload = st.text_input("Object Key for Upload (e.g., myfolder/myfile.txt)", key="s3_object_key_upload")
    uploaded_file = st.file_uploader("Upload File to S3", type=None, key="s3_upload_file") # Any file type
    if st.button("Upload Object"):
        if bucket_name_obj and object_key_upload and uploaded_file:
            try:
                s3_resource.Bucket(bucket_name_obj).upload_fileobj(uploaded_file, object_key_upload)
                st.success(f"Object '{object_key_upload}' uploaded to bucket '{bucket_name_obj}'.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide bucket name, object key, and upload a file.")
    
    object_key_download = st.text_input("Object Key for Download", key="s3_object_key_download")
    if st.button("Download Object"):
        if bucket_name_obj and object_key_download:
            try:
                # Provide a buffer to download into, then offer for download
                buffer = io.BytesIO()
                s3_client.download_fileobj(bucket_name_obj, object_key_download, buffer)
                buffer.seek(0)
                st.download_button(
                    label=f"Download {object_key_download}",
                    data=buffer.getvalue(),
                    file_name=object_key_download.split('/')[-1], # Use just the filename
                    mime="application/octet-stream"
                )
                st.success(f"Object '{object_key_download}' ready for download from '{bucket_name_obj}'.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide bucket name and object key for download.")

    object_key_delete = st.text_input("Object Key for Delete", key="s3_object_key_delete")
    if st.button("Delete Object"):
        if bucket_name_obj and object_key_delete:
            try:
                response = s3_client.delete_object(Bucket=bucket_name_obj, Key=object_key_delete)
                display_aws_result(response)
                st.success(f"Object '{object_key_delete}' deleted from bucket '{bucket_name_obj}'.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide bucket name and object key.")


def display_lambda_tasks():
    st.subheader("Lambda (Serverless Compute) Tasks")
    lambda_client = boto3.client('lambda')

    if st.button("List All Lambda Functions"):
        try:
            response = lambda_client.list_functions()
            functions = [{'FunctionName': f['FunctionName'], 'Runtime': f['Runtime'], 'Memory': f['Memory'], 'Timeout': f['Timeout'], 'LastModified': f['LastModified']} for f in response['Functions']]
            if functions:
                st.dataframe(pd.DataFrame(functions))
            else:
                st.info("No Lambda functions found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Create New Lambda Function")
    create_func_name = st.text_input("New Function Name", key="lambda_create_func_name")
    create_func_runtime = st.selectbox("Runtime", ["python3.9", "python3.8", "nodejs16.x", "java11"], key="lambda_create_func_runtime")
    create_func_handler = st.text_input("Handler (e.g., index.handler)", "index.handler", key="lambda_create_func_handler")
    create_func_role_arn = st.text_input("Execution Role ARN", help="e.g., arn:aws:iam::123456789012:role/lambda-ex-role")
    uploaded_zip_file = st.file_uploader("Upload ZIP deployment package", type="zip", key="lambda_upload_zip")

    if st.button("Create Lambda Function"):
        if create_func_name and create_func_runtime and create_func_handler and create_func_role_arn and uploaded_zip_file:
            try:
                zip_content = uploaded_zip_file.getvalue()
                response = lambda_client.create_function(
                    FunctionName=create_func_name,
                    Runtime=create_func_runtime,
                    Role=create_func_role_arn,
                    Handler=create_func_handler,
                    Code={'ZipFile': zip_content},
                    Publish=True,
                    Timeout=30,
                    MemorySize=128
                )
                display_aws_result(response)
                st.success(f"Lambda function '{create_func_name}' created!")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please fill all required fields and upload a ZIP file.")

    st.markdown("---")
    st.write("### Manage Existing Functions")
    function_name = st.text_input("Lambda Function Name", key="lambda_function_name")
    if st.button("Get Function Configuration"):
        if function_name:
            try:
                response = lambda_client.get_function_configuration(FunctionName=function_name)
                display_aws_result(response)
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a function name.")

    payload = st.text_area("Payload (JSON)", value="{}", key="lambda_invoke_payload")
    if st.button("Invoke Function (Synchronous)"):
        if function_name:
            try:
                invoke_response = lambda_client.invoke(
                    FunctionName=function_name,
                    InvocationType='RequestResponse',
                    Payload=payload
                )
                response_payload = invoke_response['Payload'].read().decode('utf-8')
                st.write("Invocation Response:")
                st.json(json.loads(response_payload))
                display_aws_result(invoke_response)
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a function name.")
    
    if st.button("Invoke Function (Asynchronous)"):
        if function_name:
            try:
                invoke_response = lambda_client.invoke(
                    FunctionName=function_name,
                    InvocationType='Event', # Asynchronous invocation
                    Payload=payload
                )
                display_aws_result(invoke_response)
                st.success(f"Asynchronous invocation request sent for '{function_name}'.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a function name.")

    if st.button("Delete Function"):
        if function_name:
            st.warning(f"This will DELETE function '{function_name}'. This action is irreversible.")
            if st.checkbox(f"Confirm deletion of {function_name}", key="confirm_delete_lambda"):
                try:
                    response = lambda_client.delete_function(FunctionName=function_name)
                    display_aws_result(response)
                    st.success(f"Function '{function_name}' deleted.")
                except Exception as e:
                    display_aws_result(None, e)
        else: st.warning("Please provide a function name to delete.")


def display_iam_tasks():
    st.subheader("IAM (Identity and Access Management) Tasks")
    iam_client = boto3.client('iam')

    if st.button("List All IAM Users"):
        try:
            response = iam_client.list_users()
            users = [{'UserName': u['UserName'], 'CreateDate': u['CreateDate']} for u in response['Users']]
            if users:
                st.dataframe(pd.DataFrame(users))
            else:
                st.info("No IAM users found.")
        except Exception as e:
            display_aws_result(None, e)

    if st.button("List All IAM Roles"):
        try:
            response = iam_client.list_roles()
            roles = [{'RoleName': r['RoleName'], 'CreateDate': r['CreateDate']} for r in response['Roles']]
            if roles:
                st.dataframe(pd.DataFrame(roles))
            else:
                st.info("No IAM roles found.")
        except Exception as e:
            display_aws_result(None, e)

    if st.button("List All IAM Policies"):
        try:
            response = iam_client.list_policies(Scope='Local') # Filter for customer managed policies
            policies = [{'PolicyName': p['PolicyName'], 'Arn': p['Arn'], 'CreateDate': p['CreateDate']} for p in response['Policies']]
            if policies:
                st.dataframe(pd.DataFrame(policies))
            else:
                st.info("No customer managed IAM policies found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Manage IAM Users")
    user_name = st.text_input("IAM User Name", key="iam_user_name")
    if st.button("Get User Details"):
        if user_name:
            try:
                response = iam_client.get_user(UserName=user_name)
                display_aws_result(response['User'])
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a user name.")
    
    new_user_name = st.text_input("New IAM User Name to Create", key="iam_new_user_name")
    if st.button("Create IAM User"):
        if new_user_name:
            try:
                response = iam_client.create_user(UserName=new_user_name)
                display_aws_result(response)
                st.success(f"User '{new_user_name}' created. Remember to create access keys for programmatic access via IAM console if needed.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a new user name.")

    delete_user_name = st.text_input("IAM User Name to Delete", key="iam_delete_user_name")
    if st.button("Delete IAM User"):
        if delete_user_name:
            st.warning(f"This will DELETE user '{delete_user_name}'. Ensure all associated keys, policies, and groups are removed first via IAM console.")
            if st.checkbox(f"Confirm deletion of {delete_user_name}", key="confirm_delete_iam_user"):
                try:
                    response = iam_client.delete_user(UserName=delete_user_name)
                    display_aws_result(response)
                    st.success(f"User '{delete_user_name}' deleted.")
                except Exception as e:
                    display_aws_result(None, e)
        else: st.warning("Please provide a user name to delete.")


def display_rds_tasks():
    st.subheader("RDS (Relational Database Service) Tasks")
    rds_client = boto3.client('rds')

    if st.button("List All DB Instances"):
        try:
            response = rds_client.describe_db_instances()
            instances = []
            for db_instance in response['DBInstances']:
                instances.append({
                    'DBInstanceIdentifier': db_instance['DBInstanceIdentifier'],
                    'Engine': db_instance['Engine'],
                    'DBInstanceClass': db_instance['DBInstanceClass'],
                    'DBInstanceStatus': db_instance['DBInstanceStatus'],
                    'EndpointAddress': db_instance.get('Endpoint', {}).get('Address', 'N/A'),
                    'AllocatedStorageGB': db_instance['AllocatedStorage']
                })
            if instances:
                st.dataframe(pd.DataFrame(instances))
            else:
                st.info("No RDS DB instances found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Manage Existing DB Instances")
    db_instance_id = st.text_input("DB Instance Identifier", key="rds_db_instance_id")
    if st.button("Reboot DB Instance"):
        if db_instance_id:
            try:
                response = rds_client.reboot_db_instance(DBInstanceIdentifier=db_instance_id)
                display_aws_result(response)
                st.success(f"Attempted to reboot DB instance {db_instance_id}")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a DB Instance Identifier.")
    
    st.markdown("---")
    st.write("### Create New DB Instance (Basic)")
    new_db_id = st.text_input("New DB Instance Identifier", key="rds_new_db_id")
    new_db_engine = st.selectbox("Engine", ["mysql", "postgres", "aurora", "mariadb"], index=0)
    new_db_engine_version = st.text_input("Engine Version (e.g., 8.0.35)", "8.0.35") # Common for MySQL
    new_db_class = st.selectbox("DB Instance Class", ["db.t3.micro", "db.t3.small", "db.t2.micro"], index=0)
    master_username = st.text_input("Master Username", key="rds_master_user")
    master_password = st.text_input("Master Password", type="password", key="rds_master_pass")
    
    if st.button("Create DB Instance"):
        if new_db_id and new_db_engine and new_db_engine_version and new_db_class and master_username and master_password:
            try:
                response = rds_client.create_db_instance(
                    DBInstanceIdentifier=new_db_id,
                    DBInstanceClass=new_db_class,
                    Engine=new_db_engine,
                    EngineVersion=new_db_engine_version,
                    MasterUsername=master_username,
                    MasterUserPassword=master_password,
                    AllocatedStorage=20, # Minimum 20GB for many engines
                    PubliclyAccessible=False, # Recommended for security
                    VpcSecurityGroupIds=[], # Provide actual Security Group IDs if needed
                    DBSubnetGroupName=None, # Provide DB Subnet Group Name if using custom VPC
                    BackupRetentionPeriod=0 # Set to 0 for no backups, or higher for production
                )
                display_aws_result(response)
                st.success(f"DB Instance '{new_db_id}' creation initiated. Check RDS console for status.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please fill all required fields for new DB instance.")

    st.markdown("---")
    st.write("### Delete DB Instance")
    delete_db_id = st.text_input("DB Instance Identifier to Delete", key="rds_delete_db_id")
    if st.button("Delete DB Instance"):
        if delete_db_id:
            st.warning(f"This will DELETE DB instance '{delete_db_id}'. This action is irreversible.")
            if st.checkbox(f"Confirm deletion of {delete_db_id}", key="confirm_delete_rds"):
                try:
                    response = rds_client.delete_db_instance(
                        DBInstanceIdentifier=delete_db_id,
                        SkipFinalSnapshot=True, # Set to False and provide DBSnapshotIdentifier for final snapshot
                        DeleteAutomatedBackups=True
                    )
                    display_aws_result(response)
                    st.success(f"DB Instance '{delete_db_id}' deletion initiated.")
                except Exception as e:
                    display_aws_result(None, e)
        else: st.warning("Please provide a DB Instance Identifier to delete.")


def display_dynamodb_tasks():
    st.subheader("DynamoDB (NoSQL Database) Tasks")
    dynamodb_client = boto3.client('dynamodb')

    if st.button("List All DynamoDB Tables"):
        try:
            response = dynamodb_client.list_tables()
            if response['TableNames']:
                st.write(response['TableNames'])
            else:
                st.info("No DynamoDB tables found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Manage Tables")
    table_name = st.text_input("Table Name", key="dynamodb_table_name")
    if st.button("Describe Table"):
        if table_name:
            try:
                response = dynamodb_client.describe_table(TableName=table_name)
                display_aws_result(response['Table'])
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a table name.")

    new_table_name = st.text_input("New Table Name", key="dynamodb_new_table_name")
    partition_key = st.text_input("Partition Key Name", key="dynamodb_partition_key")
    partition_key_type = st.selectbox("Partition Key Type", ["S", "N", "B"], index=0, key="dynamodb_pk_type")
    
    if st.button("Create Table"):
        if new_table_name and partition_key and partition_key_type:
            try:
                response = dynamodb_client.create_table(
                    TableName=new_table_name,
                    KeySchema=[{'AttributeName': partition_key, 'KeyType': 'HASH'}],
                    AttributeDefinitions=[{'AttributeName': partition_key, 'AttributeType': partition_key_type}],
                    BillingMode='PAY_PER_REQUEST' # Or PROVISIONED for throughput
                )
                display_aws_result(response)
                st.success(f"Table '{new_table_name}' creation initiated.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide table name, partition key, and its type.")

    delete_table_name = st.text_input("Table Name to Delete", key="dynamodb_delete_table_name")
    if st.button("Delete Table"):
        if delete_table_name:
            st.warning(f"This will DELETE table '{delete_table_name}' and ALL its data. This action is irreversible.")
            if st.checkbox(f"Confirm deletion of {delete_table_name}", key="confirm_delete_dynamodb"):
                try:
                    response = dynamodb_client.delete_table(TableName=delete_table_name)
                    display_aws_result(response)
                    st.success(f"Table '{delete_table_name}' deletion initiated.")
                except Exception as e:
                    display_aws_result(None, e)
        else: st.warning("Please provide a table name to delete.")


def display_vpc_tasks():
    st.subheader("VPC (Virtual Private Cloud) Tasks")
    ec2_client = boto3.client('ec2') # VPC resources are managed via EC2 client

    if st.button("List All VPCs"):
        try:
            response = ec2_client.describe_vpcs()
            vpcs = [{'VpcId': v['VpcId'], 'CidrBlock': v['CidrBlock'], 'IsDefault': v['IsDefault']} for v in response['Vpcs']]
            if vpcs:
                st.dataframe(pd.DataFrame(vpcs))
            else:
                st.info("No VPCs found.")
        except Exception as e:
            display_aws_result(None, e)

    if st.button("List All Subnets"):
        try:
            response = ec2_client.describe_subnets()
            subnets = [{'SubnetId': s['SubnetId'], 'VpcId': s['VpcId'], 'CidrBlock': s['CidrBlock'], 'AvailabilityZone': s['AvailabilityZone']} for s in response['Subnets']]
            if subnets:
                st.dataframe(pd.DataFrame(subnets))
            else:
                st.info("No Subnets found.")
        except Exception as e:
            display_aws_result(None, e)

    if st.button("List All Security Groups"):
        try:
            response = ec2_client.describe_security_groups()
            sgs = [{'GroupId': sg['GroupId'], 'GroupName': sg['GroupName'], 'Description': sg['Description']} for sg in response['SecurityGroups']]
            if sgs:
                st.dataframe(pd.DataFrame(sgs))
            else:
                st.info("No Security Groups found.")
        except Exception as e:
            display_aws_result(None, e)
    
    st.markdown("---")
    st.write("### Create VPC Resources")
    new_vpc_cidr = st.text_input("New VPC CIDR Block (e.g., 10.0.0.0/16)", key="vpc_new_vpc_cidr")
    if st.button("Create VPC"):
        if new_vpc_cidr:
            try:
                response = ec2_client.create_vpc(CidrBlock=new_vpc_cidr)
                display_aws_result(response)
                st.success(f"VPC with CIDR '{new_vpc_cidr}' created.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a CIDR Block.")

    subnet_vpc_id = st.text_input("VPC ID for Subnet", key="vpc_subnet_vpc_id")
    subnet_cidr = st.text_input("Subnet CIDR Block (e.g., 10.0.1.0/24)", key="vpc_subnet_cidr")
    az_subnet = st.text_input("Availability Zone (e.g., us-east-1a)", key="vpc_az_subnet")
    if st.button("Create Subnet"):
        if subnet_vpc_id and subnet_cidr and az_subnet:
            try:
                response = ec2_client.create_subnet(VpcId=subnet_vpc_id, CidrBlock=subnet_cidr, AvailabilityZone=az_subnet)
                display_aws_result(response)
                st.success(f"Subnet '{subnet_cidr}' created in VPC '{subnet_vpc_id}'.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide VPC ID, CIDR Block, and Availability Zone for subnet.")

    sg_vpc_id = st.text_input("VPC ID for Security Group", key="vpc_sg_vpc_id")
    sg_name = st.text_input("Security Group Name", key="vpc_sg_name")
    sg_description = st.text_input("Security Group Description", key="vpc_sg_desc")
    if st.button("Create Security Group"):
        if sg_vpc_id and sg_name and sg_description:
            try:
                response = ec2_client.create_security_group(
                    GroupName=sg_name, Description=sg_description, VpcId=sg_vpc_id
                )
                display_aws_result(response)
                st.success(f"Security Group '{sg_name}' created in VPC '{sg_vpc_id}'.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide VPC ID, Name, and Description for Security Group.")

    st.markdown("---")
    st.write("### Delete VPC Resources")
    delete_vpc_id = st.text_input("VPC ID to Delete", key="vpc_delete_vpc_id")
    if st.button("Delete VPC"):
        if delete_vpc_id:
            st.warning(f"This will DELETE VPC '{delete_vpc_id}' and all associated resources (subnets, gateways, etc.). This action is irreversible.")
            if st.checkbox(f"Confirm deletion of {delete_vpc_id}", key="confirm_delete_vpc"):
                try:
                    response = ec2_client.delete_vpc(VpcId=delete_vpc_id)
                    display_aws_result(response)
                    st.success(f"VPC '{delete_vpc_id}' deletion initiated.")
                except Exception as e:
                    display_aws_result(None, e)
        else: st.warning("Please provide a VPC ID to delete.")


def display_sqs_tasks():
    st.subheader("SQS (Simple Queue Service) Tasks")
    sqs_client = boto3.client('sqs')

    if st.button("List All SQS Queues"):
        try:
            response = sqs_client.list_queues()
            if 'QueueUrls' in response:
                st.write(response['QueueUrls'])
            else:
                st.info("No SQS queues found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Manage Queues")
    queue_name = st.text_input("Queue Name (e.g., my-queue)", key="sqs_queue_name")
    if st.button("Create Queue"):
        if queue_name:
            try:
                response = sqs_client.create_queue(QueueName=queue_name)
                display_aws_result(response)
                st.success(f"Queue '{queue_name}' created.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a queue name.")
    
    delete_queue_url = st.text_input("Queue URL to Delete", key="sqs_delete_queue_url")
    if st.button("Delete Queue"):
        if delete_queue_url:
            st.warning(f"This will DELETE queue '{delete_queue_url}'. This action is irreversible.")
            if st.checkbox(f"Confirm deletion of {delete_queue_url}", key="confirm_delete_sqs"):
                try:
                    response = sqs_client.delete_queue(QueueUrl=delete_queue_url)
                    display_aws_result(response)
                    st.success(f"Queue '{delete_queue_url}' deleted.")
                except Exception as e:
                    display_aws_result(None, e)
        else: st.warning("Please provide a Queue URL to delete.")

    st.markdown("---")
    st.write("### Send/Receive Messages")
    queue_url = st.text_input("Queue URL (e.g., https://sqs.us-east-1.amazonaws.com/123456789012/my-queue)", key="sqs_queue_url_msg")
    message_body = st.text_area("Message Body", key="sqs_message_body")
    if st.button("Send Message"):
        if queue_url and message_body:
            try:
                response = sqs_client.send_message(QueueUrl=queue_url, MessageBody=message_body)
                display_aws_result(response)
                st.success("Message sent.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide queue URL and message body.")

    if st.button("Receive Messages (max 10)"):
        if queue_url:
            try:
                response = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, VisibilityTimeout=20)
                messages = response.get('Messages', [])
                if messages:
                    st.write("Received Messages:")
                    for msg in messages:
                        st.json(msg['Body'])
                else:
                    st.info("No messages available in the queue.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a queue URL.")

def display_sns_tasks():
    st.subheader("SNS (Simple Notification Service) Tasks")
    sns_client = boto3.client('sns')

    if st.button("List All SNS Topics"):
        try:
            response = sns_client.list_topics()
            topics = [{'TopicArn': t['TopicArn']} for t in response['Topics']]
            if topics:
                st.dataframe(pd.DataFrame(topics))
            else:
                st.info("No SNS topics found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Manage Topics")
    topic_name = st.text_input("Topic Name (e.g., my-topic)", key="sns_topic_name")
    if st.button("Create Topic"):
        if topic_name:
            try:
                response = sns_client.create_topic(Name=topic_name)
                display_aws_result(response)
                st.success(f"Topic '{topic_name}' created.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a topic name.")

    delete_topic_arn = st.text_input("Topic ARN to Delete", key="sns_delete_topic_arn")
    if st.button("Delete Topic"):
        if delete_topic_arn:
            st.warning(f"This will DELETE topic '{delete_topic_arn}'. This action is irreversible.")
            if st.checkbox(f"Confirm deletion of {delete_topic_arn}", key="confirm_delete_sns_topic"):
                try:
                    response = sns_client.delete_topic(TopicArn=delete_topic_arn)
                    display_aws_result(response)
                    st.success(f"Topic '{delete_topic_arn}' deleted.")
                except Exception as e:
                    display_aws_result(None, e)
        else: st.warning("Please provide a Topic ARN to delete.")

    st.markdown("---")
    st.write("### Publish Messages")
    topic_arn_pub = st.text_input("Topic ARN to Publish", key="sns_topic_arn_pub")
    message_sns = st.text_area("Message to Publish", key="sns_message_body")
    if st.button("Publish Message to Topic"):
        if topic_arn_pub and message_sns:
            try:
                response = sns_client.publish(TopicArn=topic_arn_pub, Message=message_sns)
                display_aws_result(response)
                st.success("Message published.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide topic ARN and message.")
    
    st.markdown("---")
    st.write("### Manage Subscriptions")
    subscribe_topic_arn = st.text_input("Topic ARN to Subscribe", key="sns_subscribe_topic_arn")
    protocol_sub = st.selectbox("Protocol", ["sms", "email", "sqs", "lambda", "application", "http", "https"], key="sns_protocol_sub")
    endpoint_sub = st.text_input("Endpoint (e.g., +1234567890 for SMS, email@example.com for email)", key="sns_endpoint_sub")
    if st.button("Subscribe Endpoint"):
        if subscribe_topic_arn and protocol_sub and endpoint_sub:
            try:
                response = sns_client.subscribe(TopicArn=subscribe_topic_arn, Protocol=protocol_sub, Endpoint=endpoint_sub)
                display_aws_result(response)
                st.success(f"Subscription initiated to {endpoint_sub} for topic {subscribe_topic_arn}. (Confirmation might be required).")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide Topic ARN, Protocol, and Endpoint.")


def display_cloudwatch_tasks():
    st.subheader("CloudWatch (Monitoring and Observability) Tasks")
    cloudwatch_client = boto3.client('cloudwatch')

    if st.button("List All Alarms"):
        try:
            response = cloudwatch_client.describe_alarms()
            alarms = [{'AlarmName': a['AlarmName'], 'StateValue': a['StateValue'], 'MetricName': a['MetricName']} for a in response['MetricAlarms']]
            if alarms:
                st.dataframe(pd.DataFrame(alarms))
            else:
                st.info("No CloudWatch alarms found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Get Metric Statistics")
    metric_namespace = st.text_input("Metric Namespace (e.g., AWS/EC2)", key="cw_metric_ns")
    metric_name = st.text_input("Metric Name (e.g., CPUUtilization)", key="cw_metric_name")
    if st.button("Get Metric Statistics (Last 1 hour)"):
        if metric_namespace and metric_name:
            try:
                response = cloudwatch_client.get_metric_statistics(
                    Namespace=metric_namespace,
                    MetricName=metric_name,
                    StartTime=pd.Timestamp.now(tz='UTC') - pd.Timedelta(hours=1),
                    EndTime=pd.Timestamp.now(tz='UTC'),
                    Period=300, # 5 minutes
                    Statistics=['Average']
                )
                datapoints = response.get('Datapoints', [])
                if datapoints:
                    st.write(f"Average {metric_name} over last hour:")
                    for dp in datapoints:
                        st.write(f"Timestamp: {dp['Timestamp']}, Average: {dp['Average']:.2f}")
                else:
                    st.info("No datapoints found for this metric.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide metric namespace and name.")
    
    st.markdown("---")
    st.write("### Create/Delete Alarms")
    alarm_name = st.text_input("Alarm Name", key="cw_alarm_name")
    alarm_metric_name = st.text_input("Alarm Metric Name", key="cw_alarm_metric_name", value="CPUUtilization")
    alarm_namespace = st.text_input("Alarm Namespace", key="cw_alarm_namespace", value="AWS/EC2")
    alarm_dimension_name = st.text_input("Alarm Dimension Name (e.g., InstanceId)", key="cw_alarm_dim_name")
    alarm_dimension_value = st.text_input("Alarm Dimension Value (e.g., i-0abcdef1234567890)", key="cw_alarm_dim_value")
    threshold = st.number_input("Threshold", min_value=0.0, value=70.0)
    
    if st.button("Create CPU Utilization Alarm"):
        if alarm_name and alarm_metric_name and alarm_namespace and alarm_dimension_name and alarm_dimension_value:
            try:
                response = cloudwatch_client.put_metric_alarm(
                    AlarmName=alarm_name,
                    AlarmDescription=f'Alarm when {alarm_metric_name} exceeds {threshold}% for {alarm_dimension_value}',
                    ActionsEnabled=False, # Set to True for actual actions, specify SNS topic/Lambda ARN in AlarmActions
                    MetricName=alarm_metric_name,
                    Namespace=alarm_namespace,
                    Statistic='Average',
                    Period=300,
                    EvaluationPeriods=1,
                    Threshold=threshold,
                    ComparisonOperator='GreaterThanThreshold',
                    Dimensions=[
                        {'Name': alarm_dimension_name, 'Value': alarm_dimension_value},
                    ]
                )
                display_aws_result(response)
                st.success(f"Alarm '{alarm_name}' created. Remember to add actions (e.g., SNS topic) via CloudWatch console.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide all required alarm details.")

    delete_alarm_name = st.text_input("Alarm Name to Delete", key="cw_delete_alarm_name")
    if st.button("Delete Alarm"):
        if delete_alarm_name:
            st.warning(f"This will DELETE alarm '{delete_alarm_name}'.")
            if st.checkbox(f"Confirm deletion of {delete_alarm_name}", key="confirm_delete_alarm"):
                try:
                    response = cloudwatch_client.delete_alarms(AlarmNames=[delete_alarm_name])
                    display_aws_result(response)
                    st.success(f"Alarm '{delete_alarm_name}' deleted.")
                except Exception as e:
                    display_aws_result(None, e)
        else: st.warning("Please provide an alarm name to delete.")


def display_cloudformation_tasks():
    st.subheader("CloudFormation (Infrastructure as Code) Tasks")
    cf_client = boto3.client('cloudformation')

    if st.button("List All Stacks"):
        try:
            response = cf_client.list_stacks()
            stacks = [{'StackName': s['StackName'], 'StackStatus': s['StackStatus'], 'CreationTime': s['CreationTime']} for s in response['StackSummaries']]
            if stacks:
                st.dataframe(pd.DataFrame(stacks))
            else:
                st.info("No CloudFormation stacks found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Manage Stacks")
    stack_name = st.text_input("Stack Name", key="cf_stack_name")
    if st.button("Describe Stack"):
        if stack_name:
            try:
                response = cf_client.describe_stacks(StackName=stack_name)
                display_aws_result(response['Stacks'][0])
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a stack name.")

    template_body = st.text_area("CloudFormation Template (YAML/JSON)", height=300, key="cf_template_body")
    if st.button("Create Stack"):
        if stack_name and template_body:
            try:
                response = cf_client.create_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND'] # Required for IAM resources
                )
                display_aws_result(response)
                st.success(f"Stack '{stack_name}' creation initiated.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide stack name and template.")

    if st.button("Delete Stack"):
        if stack_name:
            st.warning(f"This will DELETE stack '{stack_name}'. Confirm to proceed.")
            if st.checkbox(f"Confirm deletion of stack {stack_name}", key=f"confirm_del_cf_stack_{stack_name}"):
                try:
                    response = cf_client.delete_stack(StackName=stack_name)
                    display_aws_result(response)
                    st.success(f"Stack '{stack_name}' deletion initiated.")
                except Exception as e:
                    display_aws_result(None, e)
        else: st.warning("Please provide a stack name.")

def display_route53_tasks():
    st.subheader("Route 53 (DNS Web Service) Tasks")
    route53_client = boto3.client('route53')

    if st.button("List Hosted Zones"):
        try:
            response = route53_client.list_hosted_zones()
            zones = [{'Name': z['Name'], 'Id': z['Id'].split('/')[-1], 'PrivateZone': z['Config']['PrivateZone']} for z in response['HostedZones']]
            if zones:
                st.dataframe(pd.DataFrame(zones))
            else:
                st.info("No Route 53 hosted zones found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Manage Record Sets")
    zone_id = st.text_input("Hosted Zone ID (e.g., Z1ABCDEFG12345)", key="r53_zone_id")
    if st.button("List Record Sets in Zone"):
        if zone_id:
            try:
                response = route53_client.list_resource_record_sets(HostedZoneId=zone_id)
                records = [{'Name': r['Name'], 'Type': r['Type'], 'TTL': r.get('TTL', 'N/A'), 'ResourceRecords': [rr['Value'] for rr in r.get('ResourceRecords', [])]} for r in response['ResourceRecordSets']]
                if records:
                    st.dataframe(pd.DataFrame(records))
                else:
                    st.info(f"No record sets found in zone '{zone_id}'.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a Hosted Zone ID.")
    
    record_zone_id = st.text_input("Hosted Zone ID for Record Set", key="r53_record_zone_id")
    record_name = st.text_input("Record Name (e.g., www.example.com.)", key="r53_record_name")
    record_type = st.selectbox("Record Type", ["A", "AAAA", "CNAME", "MX", "NS", "PTR", "SOA", "SPF", "SRV", "TXT"], key="r53_record_type")
    record_value = st.text_input("Record Value (e.g., 192.0.2.1 or d123.cloudfront.net)", key="r53_record_value")
    record_ttl = st.number_input("TTL (seconds)", min_value=1, value=300, key="r53_record_ttl")

    if st.button("Create/Upsert Record Set (A/CNAME etc.)"):
        if record_zone_id and record_name and record_type and record_value:
            try:
                change_batch = {
                    'Changes': [
                        {
                            'Action': 'UPSERT', # CREATE, DELETE, UPSERT
                            'ResourceRecordSet': {
                                'Name': record_name,
                                'Type': record_type,
                                'TTL': int(record_ttl),
                                'ResourceRecords': [{'Value': record_value}]
                            }
                        }
                    ]
                }
                response = route53_client.change_resource_record_sets(
                    HostedZoneId=record_zone_id,
                    ChangeBatch=change_batch
                )
                display_aws_result(response)
                st.success(f"Record set '{record_name}' ({record_type}) created/upserted.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide all record set details.")

def display_cloudfront_tasks():
    st.subheader("CloudFront (Content Delivery Network) Tasks")
    cf_client = boto3.client('cloudfront')

    if st.button("List All Distributions"):
        try:
            response = cf_client.list_distributions()
            distributions = []
            if 'Items' in response['DistributionList']:
                for dist in response['DistributionList']['Items']:
                    distributions.append({
                        'Id': dist['Id'],
                        'DomainName': dist['DomainName'],
                        'Status': dist['Status'],
                        'Enabled': dist['Enabled'],
                        'Origins': [o['Id'] for o in dist['Origins']['Items']]
                    })
            if distributions:
                st.dataframe(pd.DataFrame(distributions))
            else:
                st.info("No CloudFront distributions found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Manage Distributions")
    distribution_id = st.text_input("Distribution ID (e.g., E12345ABCDEF)", key="cf_dist_id")
    if st.button("Get Distribution Config"):
        if distribution_id:
            try:
                response = cf_client.get_distribution_config(Id=distribution_id)
                display_aws_result(response['DistributionConfig'])
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a distribution ID.")
    
    invalidation_dist_id = st.text_input("Distribution ID for Invalidation", key="cf_invalidation_dist_id")
    invalidation_paths = st.text_area("Paths to Invalidate (one per line, e.g., /images/* /index.html)", key="cf_invalidation_paths")
    if st.button("Create Invalidation"):
        if invalidation_dist_id and invalidation_paths:
            paths_list = [p.strip() for p in invalidation_paths.split('\n') if p.strip()]
            if not paths_list:
                st.warning("Please enter at least one path to invalidate.")
                return
            try:
                response = cf_client.create_invalidation(
                    DistributionId=invalidation_dist_id,
                    InvalidationBatch={
                        'Paths': {'Quantity': len(paths_list), 'Items': paths_list},
                        'CallerReference': str(time.time()).replace('.', '') # Unique reference
                    }
                )
                display_aws_result(response)
                st.success(f"Invalidation created for {len(paths_list)} paths on distribution {invalidation_dist_id}.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide distribution ID and paths for invalidation.")


def display_secrets_manager_tasks():
    st.subheader("Secrets Manager Tasks")
    sm_client = boto3.client('secretsmanager')

    if st.button("List All Secrets"):
        try:
            response = sm_client.list_secrets()
            secrets = [{'Name': s['Name'], 'Description': s.get('Description', 'N/A'), 'LastChangedDate': s.get('LastChangedDate', 'N/A')} for s in response['SecretList']]
            if secrets:
                st.dataframe(pd.DataFrame(secrets))
            else:
                st.info("No secrets found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Manage Secrets")
    secret_name = st.text_input("Secret Name/ARN", key="sm_secret_name")
    if st.button("Get Secret Value"):
        if secret_name:
            try:
                response = sm_client.get_secret_value(SecretId=secret_name)
                # For security, only display if user confirms or if it's not a live system
                # Here, we'll just display directly as this is a dashboard tool.
                if 'SecretString' in response:
                    st.write("Secret String:")
                    st.code(response['SecretString'])
                elif 'SecretBinary' in response:
                    st.write("Secret Binary (Base64 Encoded):")
                    st.code(response['SecretBinary'].decode('utf-8'))
                display_aws_result(response)
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a secret name/ARN.")

    new_secret_name = st.text_input("New Secret Name", key="sm_new_secret_name")
    new_secret_value = st.text_area("New Secret Value (JSON or plain text)", key="sm_new_secret_value")
    if st.button("Create New Secret"):
        if new_secret_name and new_secret_value:
            try:
                # Attempt to parse as JSON if it looks like one, else treat as string
                try:
                    json.loads(new_secret_value) # Test if it's valid JSON
                    secret_string = new_secret_value
                except json.JSONDecodeError:
                    secret_string = new_secret_value # Not JSON, treat as plain string

                response = sm_client.create_secret(
                    Name=new_secret_name,
                    SecretString=secret_string
                )
                display_aws_result(response)
                st.success(f"Secret '{new_secret_name}' created.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a new secret name and value.")

    delete_secret_name = st.text_input("Secret Name to Delete", key="sm_delete_secret_name")
    if st.button("Delete Secret"):
        if delete_secret_name:
            st.warning(f"This will DELETE secret '{delete_secret_name}'. This action is irreversible.")
            if st.checkbox(f"Confirm deletion of {delete_secret_name}", key="confirm_delete_secret"):
                try:
                    # Recovery window is 30 days by default, can force immediate deletion
                    response = sm_client.delete_secret(SecretId=delete_secret_name, ForceDeleteWithoutRecovery=True)
                    display_aws_result(response)
                    st.success(f"Secret '{delete_secret_name}' scheduled for deletion.")
                except Exception as e:
                    display_aws_result(None, e)
        else: st.warning("Please provide a secret name to delete.")


def display_systems_manager_tasks():
    st.subheader("Systems Manager (SSM) Tasks")
    ssm_client = boto3.client('ssm')

    if st.button("List All Managed Instances"):
        try:
            response = ssm_client.describe_instance_information(
                Filters=[{'Key': 'PingStatus', 'Values': ['Online']}]
            )
            instances = [{'InstanceId': i['InstanceId'], 'PlatformName': i['PlatformName'], 'AgentVersion': i['AgentVersion'], 'PingStatus': i['PingStatus']} for i in response['InstanceInformationList']]
            if instances:
                st.dataframe(pd.DataFrame(instances))
            else:
                st.info("No SSM managed instances found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Run Commands on Instances")
    instance_id_run = st.text_input("Instance ID to Run Command", key="ssm_instance_id_run")
    command_to_run = st.text_input("Command (e.g., ipconfig /all or ls -la)", key="ssm_command_to_run")
    if st.button("Run Command on Instance"):
        if instance_id_run and command_to_run:
            try:
                response = ssm_client.send_command(
                    InstanceIds=[instance_id_run],
                    DocumentName="AWS-RunShellScript", # Or AWS-RunPowerShellScript for Windows
                    Parameters={'commands': [command_to_run]}
                )
                command_id = response['Command']['CommandId']
                st.success(f"Command sent. Command ID: {command_id}")
                st.info("Wait a few moments, then check command output using 'Get Command Output'.")
                display_aws_result(response)
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide instance ID and command.")

    command_id_output = st.text_input("Command ID to Get Output", key="ssm_command_id_output")
    instance_id_output = st.text_input("Instance ID for Command Output", key="ssm_instance_id_output") # Need instance ID to get output
    if st.button("Get Command Output"):
        if command_id_output and instance_id_output:
            try:
                # Use list_command_invocations to get basic info, then get_command_invocation for detailed output
                response = ssm_client.get_command_invocation(
                    CommandId=command_id_output,
                    InstanceId=instance_id_output
                )
                st.write(f"Status: {response['Status']}")
                if 'StandardOutputContent' in response:
                    st.write("Standard Output:")
                    st.code(response['StandardOutputContent'])
                if 'StandardErrorContent' in response:
                    st.write("Standard Error:")
                    st.code(response['StandardErrorContent'])
                display_aws_result(response)
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a Command ID and Instance ID.")


def display_cost_explorer_tasks():
    st.subheader("Cost Explorer Tasks")
    ce_client = boto3.client('ce')

    time_period_start = st.date_input("Start Date (YYYY-MM-DD)", pd.Timestamp.now() - pd.Timedelta(days=30), key="ce_start_date")
    time_period_end = st.date_input("End Date (YYYY-MM-DD)", pd.Timestamp.now(), key="ce_end_date")

    if st.button("Get Cost and Usage (Daily, last 30 days)"):
        start_date_str = time_period_start.strftime('%Y-%m-%d')
        end_date_str = time_period_end.strftime('%Y-%m-%d')
        try:
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date_str,
                    'End': end_date_str
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost']
            )
            results = []
            for result_by_time in response['ResultsByTime']:
                date = result_by_time['TimePeriod']['Start']
                cost = result_by_time['Total']['UnblendedCost']['Amount']
                unit = result_by_time['Total']['UnblendedCost']['Unit']
                results.append({'Date': date, 'Cost': float(cost), 'Unit': unit})

            if results:
                st.dataframe(pd.DataFrame(results))
            else:
                st.info("No cost data found for the selected period.")
        except Exception as e:
            display_aws_result(None, e)
    
    st.markdown("---")
    if st.button("Get Cost by Service (Monthly, last 3 months)"):
        start_date_str = (pd.Timestamp.now() - pd.Timedelta(days=90)).strftime('%Y-%m-%d')
        end_date_str = pd.Timestamp.now().strftime('%Y-%m-%d')
        try:
            response = ce_client.get_cost_and_usage(
                TimePeriod={'Start': start_date_str, 'End': end_date_str},
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )
            results = []
            for result_by_time in response['ResultsByTime']:
                time_period = f"{result_by_time['TimePeriod']['Start']} to {result_by_time['TimePeriod']['End']}"
                for group in result_by_time['Groups']:
                    service_name = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    unit = group['Metrics']['UnblendedCost']['Unit']
                    results.append({'Time Period': time_period, 'Service': service_name, 'Cost': cost, 'Unit': unit})
            
            if results:
                st.dataframe(pd.DataFrame(results).sort_values(by='Cost', ascending=False))
            else:
                st.info("No cost by service data found for the selected period.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    if st.button("Get Forecast (Next 30 days)"):
        start_date_str = pd.Timestamp.now().strftime('%Y-%m-%d')
        end_date_str = (pd.Timestamp.now() + pd.Timedelta(days=30)).strftime('%Y-%m-%d')
        try:
            response = ce_client.get_cost_forecast(
                TimePeriod={
                    'Start': start_date_str,
                    'End': end_date_str
                },
                Metric='UNBLENDED_COST',
                Granularity='MONTHLY'
            )
            forecast = response.get('ForecastResultsByTime', [])
            if forecast:
                st.write("Monthly Cost Forecast:")
                for f in forecast:
                    st.write(f"Period: {f['TimePeriod']['Start']} - {f['TimePeriod']['End']}")
                    st.write(f"Mean Value: {float(f['MeanValue']):.2f} {f['PredictionIntervalLowerBound']['Unit']}")
                    st.write(f"Lower Bound: {float(f['PredictionIntervalLowerBound']['Value']):.2f}")
                    st.write(f"Upper Bound: {float(f['PredictionIntervalUpperBound']['Value']):.2f}")
            else:
                st.info("No cost forecast available.")
        except Exception as e:
            display_aws_result(None, e)

def display_athena_tasks():
    st.subheader("Athena (Interactive Query Service) Tasks")
    athena_client = boto3.client('athena')
    s3_client = boto3.client('s3')

    if st.button("List Workgroups"):
        try:
            response = athena_client.list_work_groups()
            workgroups = [{'Name': wg['Name'], 'State': wg['State']} for wg in response['WorkGroups']]
            if workgroups:
                st.dataframe(pd.DataFrame(workgroups))
            else:
                st.info("No Athena workgroups found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Execute Queries")
    database_name = st.text_input("Athena Database Name", key="athena_db_name")
    query_string = st.text_area("SQL Query", "SELECT 1", key="athena_sql_query")
    output_location = st.text_input("S3 Output Location (e.g., s3://my-athena-results/)", key="athena_output_loc")
    workgroup_name = st.text_input("Workgroup Name (optional, default 'primary')", "primary", key="athena_workgroup_name")

    if st.button("Execute Query"):
        if database_name and query_string and output_location:
            try:
                response = athena_client.start_query_execution(
                    QueryString=query_string,
                    QueryExecutionContext={'Database': database_name},
                    ResultConfiguration={'OutputLocation': output_location},
                    WorkGroup=workgroup_name
                )
                query_execution_id = response['QueryExecutionId']
                st.success(f"Query started. Execution ID: {query_execution_id}")
                st.info("Check query status using 'Get Query Execution Status' below.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide database name, SQL query, and S3 output location.")

    query_exec_id = st.text_input("Query Execution ID", key="athena_query_exec_id")
    if st.button("Get Query Execution Status"):
        if query_exec_id:
            try:
                response = athena_client.get_query_execution(QueryExecutionId=query_exec_id)
                status = response['QueryExecution']['Status']['State']
                st.write(f"Query Status: {status}")
                if status == 'SUCCEEDED':
                    st.success("Query succeeded! You can find results in the specified S3 location.")
                elif status == 'FAILED':
                    st.error(f"Query failed: {response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown reason')}")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a Query Execution ID.")

    if st.button("Get Query Results (for SUCCEEDED queries)"):
        if query_exec_id:
            try:
                # This fetches results, but for large datasets, downloading the file is better
                response = athena_client.get_query_results(QueryExecutionId=query_exec_id)
                # Parse results for display (basic example, complex results need more robust parsing)
                if response['ResultSet']['Rows']:
                    header = [h['VarCharValue'] for h in response['ResultSet']['Rows'][0]['Data']]
                    data = []
                    for row in response['ResultSet']['Rows'][1:]: # Skip header row
                        data.append([col.get('VarCharValue', '') for col in row['Data']])
                    st.dataframe(pd.DataFrame(data, columns=header))
                else:
                    st.info("No results or query did not return data.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a Query Execution ID.")


def display_glue_tasks():
    st.subheader("Glue (ETL Service) Tasks")
    glue_client = boto3.client('glue')

    if st.button("List All Glue Databases"):
        try:
            response = glue_client.get_databases()
            databases = [{'Name': db['Name'], 'Description': db.get('Description', 'N/A')} for db in response['DatabaseList']]
            if databases:
                st.dataframe(pd.DataFrame(databases))
            else:
                st.info("No Glue databases found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Manage Tables/Jobs")
    db_name_glue = st.text_input("Glue Database Name", key="glue_db_name")
    if st.button("List Tables in Database"):
        if db_name_glue:
            try:
                response = glue_client.get_tables(DatabaseName=db_name_glue)
                tables = [{'Name': t['Name'], 'Retention': t.get('Retention', 'N/A')} for t in response['TableList']]
                if tables:
                    st.dataframe(pd.DataFrame(tables))
                else:
                    st.info(f"No tables found in database '{db_name_glue}'.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a Glue Database Name.")

    if st.button("List All Glue Jobs"):
        try:
            response = glue_client.get_jobs()
            jobs = [{'Name': j['Name'], 'GlueVersion': j['GlueVersion'], 'MaxCapacity': j.get('MaxCapacity', 'N/A')} for j in response['Jobs']]
            if jobs:
                st.dataframe(pd.DataFrame(jobs))
            else:
                st.info("No Glue jobs found.")
        except Exception as e:
            display_aws_result(None, e)
    
    st.markdown("---")
    st.write("### Create Glue Job")
    glue_job_name = st.text_input("New Glue Job Name", key="glue_new_job_name")
    glue_job_role_arn = st.text_input("Glue Job IAM Role ARN", key="glue_job_role_arn")
    glue_job_script_location = st.text_input("Glue Job Script S3 Path (e.g., s3://my-bucket/scripts/my_script.py)", key="glue_job_script_loc")
    glue_job_runtime = st.selectbox("Glue Version", ["Glue 4.0", "Glue 3.0", "Glue 2.0"], key="glue_job_version")

    if st.button("Create Glue Job"):
        if glue_job_name and glue_job_role_arn and glue_job_script_location and glue_job_runtime:
            try:
                response = glue_client.create_job(
                    Name=glue_job_name,
                    Role=glue_job_role_arn,
                    Command={
                        'Name': 'glueetl',
                        'ScriptLocation': glue_job_script_location,
                        'PythonVersion': '3' # Default for newer Glue versions
                    },
                    GlueVersion=glue_job_runtime.replace(" ", ""), # e.g., "Glue4.0"
                    NumberOfWorkers=2, # Example default
                    WorkerType='Standard' # Example default
                )
                display_aws_result(response)
                st.success(f"Glue Job '{glue_job_name}' created!")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide all required fields for Glue Job creation.")


def display_ecs_tasks():
    st.subheader("ECS (Elastic Container Service) Tasks")
    ecs_client = boto3.client('ecs')

    if st.button("List All Clusters"):
        try:
            response = ecs_client.list_clusters()
            cluster_arns = response['clusterArns']
            clusters = [{'ClusterName': arn.split('/')[-1]} for arn in cluster_arns]
            if clusters:
                st.dataframe(pd.DataFrame(clusters))
            else:
                st.info("No ECS clusters found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Manage Clusters")
    cluster_name = st.text_input("ECS Cluster Name", key="ecs_cluster_name")
    if st.button("List Services in Cluster"):
        if cluster_name:
            try:
                response = ecs_client.list_services(cluster=cluster_name)
                service_arns = response['serviceArns']
                services = [{'ServiceName': arn.split('/')[-1]} for arn in service_arns]
                if services:
                    st.dataframe(pd.DataFrame(services))
                else:
                    st.info(f"No ECS services found in cluster '{cluster_name}'.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide an ECS Cluster Name.")

    if st.button("List Tasks in Cluster"):
        if cluster_name:
            try:
                response = ecs_client.list_tasks(cluster=cluster_name)
                task_arns = response['taskArns']
                tasks = [{'TaskArn': arn} for arn in task_arns] # Task ARNs are long, maybe describe tasks?
                if tasks:
                    st.dataframe(pd.DataFrame(tasks))
                else:
                    st.info(f"No ECS tasks found in cluster '{cluster_name}'.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide an ECS Cluster Name.")
    
    new_ecs_cluster_name = st.text_input("New ECS Cluster Name", key="ecs_new_cluster_name")
    if st.button("Create ECS Cluster"):
        if new_ecs_cluster_name:
            try:
                response = ecs_client.create_cluster(clusterName=new_ecs_cluster_name)
                display_aws_result(response)
                st.success(f"ECS Cluster '{new_ecs_cluster_name}' created!")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide a new cluster name.")

    delete_ecs_cluster_name = st.text_input("ECS Cluster Name to Delete", key="ecs_delete_cluster_name")
    if st.button("Delete ECS Cluster"):
        if delete_ecs_cluster_name:
            st.warning(f"This will DELETE ECS cluster '{delete_ecs_cluster_name}'. Ensure no services/tasks are running.")
            if st.checkbox(f"Confirm deletion of {delete_ecs_cluster_name}", key="confirm_delete_ecs_cluster"):
                try:
                    response = ecs_client.delete_cluster(cluster=delete_ecs_cluster_name)
                    display_aws_result(response)
                    st.success(f"ECS Cluster '{delete_ecs_cluster_name}' deleted.")
                except Exception as e:
                    display_aws_result(None, e)
        else: st.warning("Please provide a cluster name to delete.")


def display_eks_tasks():
    st.subheader("EKS (Elastic Kubernetes Service) Tasks")
    eks_client = boto3.client('eks')

    if st.button("List All EKS Clusters"):
        try:
            response = eks_client.list_clusters()
            clusters = [{'ClusterName': name} for name in response['clusters']]
            if clusters:
                st.dataframe(pd.DataFrame(clusters))
            else:
                st.info("No EKS clusters found.")
        except Exception as e:
            display_aws_result(None, e)

    st.markdown("---")
    st.write("### Manage EKS Clusters")
    eks_cluster_name = st.text_input("EKS Cluster Name", key="eks_cluster_name")
    if st.button("Describe EKS Cluster"):
        if eks_cluster_name:
            try:
                response = eks_client.describe_cluster(name=eks_cluster_name)
                display_aws_result(response['cluster'])
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide an EKS Cluster Name.")

    if st.button("List Fargate Profiles"):
        if eks_cluster_name:
            try:
                response = eks_client.list_fargate_profiles(clusterName=eks_cluster_name)
                profiles = [{'FargateProfileName': p} for p in response['fargateProfileNames']]
                if profiles:
                    st.dataframe(pd.DataFrame(profiles))
                else:
                    st.info(f"No Fargate profiles found for cluster '{eks_cluster_name}'.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide an EKS Cluster Name.")

    new_eks_cluster_name = st.text_input("New EKS Cluster Name", key="eks_new_cluster_name")
    eks_cluster_role_arn = st.text_input("EKS Cluster IAM Role ARN", key="eks_cluster_role_arn")
    eks_subnet_ids = st.text_input("Subnet IDs (comma-separated)", help="e.g., subnet-0abcdef1234567890,subnet-0fedcba9876543210")

    if st.button("Create EKS Cluster"):
        if new_eks_cluster_name and eks_cluster_role_arn and eks_subnet_ids:
            try:
                subnet_ids_list = [s.strip() for s in eks_subnet_ids.split(',')]
                response = eks_client.create_cluster(
                    name=new_eks_cluster_name,
                    roleArn=eks_cluster_role_arn,
                    resourcesVpcConfig={'subnetIds': subnet_ids_list},
                    version='1.28' # Specify a Kubernetes version
                )
                display_aws_result(response)
                st.success(f"EKS Cluster '{new_eks_cluster_name}' creation initiated. This can take several minutes.")
            except Exception as e:
                display_aws_result(None, e)
        else: st.warning("Please provide cluster name, role ARN, and subnet IDs.")

    delete_eks_cluster_name = st.text_input("EKS Cluster Name to Delete", key="eks_delete_cluster_name")
    if st.button("Delete EKS Cluster"):
        if delete_eks_cluster_name:
            st.warning(f"This will DELETE EKS cluster '{delete_eks_cluster_name}'. This action is irreversible and can take time.")
            if st.checkbox(f"Confirm deletion of {delete_eks_cluster_name}", key="confirm_delete_eks"):
                try:
                    response = eks_client.delete_cluster(name=delete_eks_cluster_name)
                    display_aws_result(response)
                    st.success(f"EKS Cluster '{delete_eks_cluster_name}' deletion initiated.")
                except Exception as e:
                    display_aws_result(None, e)
        else: st.warning("Please provide a cluster name to delete.")


# --- AWS Sub-Menu and Detail View Functions ---

def display_aws_sub_menu():
    st.title("AWS Tasks Sub-Categories")
    st.write("Select an AWS service to view available tasks.")
    st.info("Ensure your AWS CLI is configured with valid credentials (`aws configure`) as `boto3` will use them.")

    if st.button("⬅️ Back to Main Menu", key="back_to_main_aws"):
        st.session_state.current_view = "main_menu"
        st.session_state.selected_category = None
        st.session_state.selected_sub_category = None
        st.session_state.selected_ml_sub_category = None
        st.session_state.selected_k8s_sub_category = None
        st.session_state.selected_aws_sub_category = None # Clear AWS sub-category on return
        st.rerun()

    st.markdown("---")

    # List of AWS services with implemented functionalities
    aws_services = [
        "EC2", "S3", "Lambda", "IAM", "RDS", "DynamoDB", "VPC", "SQS", "SNS", "CloudWatch",
        "CloudFormation", "Route 53", "CloudFront", "Secrets Manager", "Systems Manager", "Cost Explorer",
        "Athena", "Glue", "ECS", "EKS"
    ]

    # Dynamically create buttons for each service in columns
    num_cols = 3
    cols = st.columns(num_cols)
    for i, service in enumerate(aws_services):
        with cols[i % num_cols]:
            if st.button(service, key=f"aws_service_{service}_btn"):
                st.session_state.current_view = "aws_tasks_detail"
                st.session_state.selected_aws_sub_category = service
                st.rerun()

def display_aws_tasks_detail():
    st.title(f"{st.session_state.selected_category} - {st.session_state.selected_aws_sub_category}")

    # Back button to AWS services sub-menu
    if st.button(f"⬅️ Back to AWS Service List", key="back_to_aws_sub_menu"):
        st.session_state.current_view = "aws_sub_menu"
        st.session_state.selected_aws_sub_category = None # Clear current service selection
        st.rerun()

    st.markdown("---")

    # Route to the specific service's task display function
    service_func_map = {
        "EC2": display_ec2_tasks,
        "S3": display_s3_tasks,
        "Lambda": display_lambda_tasks,
        "IAM": display_iam_tasks,
        "RDS": display_rds_tasks,
        "DynamoDB": display_dynamodb_tasks,
        "VPC": display_vpc_tasks,
        "SQS": display_sqs_tasks,
        "SNS": display_sns_tasks,
        "CloudWatch": display_cloudwatch_tasks,
        "CloudFormation": display_cloudformation_tasks,
        "Route 53": display_route53_tasks,
        "CloudFront": display_cloudfront_tasks,
        "Secrets Manager": display_secrets_manager_tasks,
        "Systems Manager": display_systems_manager_tasks,
        "Cost Explorer": display_cost_explorer_tasks,
        "Athena": display_athena_tasks,
        "Glue": display_glue_tasks,
        "ECS": display_ecs_tasks,
        "EKS": display_eks_tasks,
    }

    selected_service = st.session_state.get('selected_aws_sub_category')
    if selected_service and selected_service in service_func_map:
        service_func_map[selected_service]()
    else:
        st.error("Invalid AWS service selected. Please go back and choose another.")