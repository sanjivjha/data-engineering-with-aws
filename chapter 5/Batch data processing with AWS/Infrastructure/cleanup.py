import boto3
import time
import json

# Configuration - should match your app.py configuration
PROJECT_NAME = "retail-etl"
REGION = "ap-south-1"
ACCOUNT_ID = "359373501475"  # Replace with your AWS account ID

# Initialize AWS clients
s3_client = boto3.client('s3')
glue_client = boto3.client('glue')
sns_client = boto3.client('sns')
sfn_client = boto3.client('stepfunctions')
iam_client = boto3.client('iam')

def cleanup_resources():
    """Delete all resources created by the infrastructure script"""
    print("=== Starting Cleanup of Retail ETL Resources ===")
    
    # 1. Find and empty S3 buckets (must empty before deleting)
    print("\n== Cleaning up S3 buckets ==")
    try:
        response = s3_client.list_buckets()
        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            # Check if this is one of our project buckets
            if bucket_name.startswith(f"{PROJECT_NAME}-"):
                print(f"  - Found bucket: {bucket_name}")
                
                # Empty the bucket first
                try:
                    print(f"    Emptying bucket...")
                    # List objects and delete them
                    paginator = s3_client.get_paginator('list_objects_v2')
                    for page in paginator.paginate(Bucket=bucket_name):
                        if 'Contents' in page:
                            objects = [{'Key': obj['Key']} for obj in page['Contents']]
                            s3_client.delete_objects(
                                Bucket=bucket_name,
                                Delete={'Objects': objects}
                            )
                    
                    # Delete versioned objects if any
                    versions_paginator = s3_client.get_paginator('list_object_versions')
                    for page in versions_paginator.paginate(Bucket=bucket_name):
                        delete_keys = []
                        if 'Versions' in page:
                            delete_keys.extend([{'Key': obj['Key'], 'VersionId': obj['VersionId']} for obj in page['Versions']])
                        if 'DeleteMarkers' in page:
                            delete_keys.extend([{'Key': obj['Key'], 'VersionId': obj['VersionId']} for obj in page['DeleteMarkers']])
                        
                        if delete_keys:
                            s3_client.delete_objects(
                                Bucket=bucket_name,
                                Delete={'Objects': delete_keys}
                            )
                    
                    # Delete the bucket
                    print(f"    Deleting bucket...")
                    s3_client.delete_bucket(Bucket=bucket_name)
                    print(f"    Successfully deleted bucket: {bucket_name}")
                    
                except Exception as e:
                    print(f"    Error while emptying/deleting bucket {bucket_name}: {str(e)}")
    except Exception as e:
        print(f"  Error listing S3 buckets: {str(e)}")
    
    # 2. Delete SNS topics
    print("\n== Cleaning up SNS topics ==")
    try:
        topics = sns_client.list_topics()
        for topic in topics['Topics']:
            if f"{PROJECT_NAME}-notifications" in topic['TopicArn']:
                print(f"  - Deleting SNS topic: {topic['TopicArn']}")
                sns_client.delete_topic(TopicArn=topic['TopicArn'])
                print(f"    Successfully deleted topic")
    except Exception as e:
        print(f"  Error during SNS cleanup: {str(e)}")
    
    # 3. Delete Glue resources
    # 3.1 Delete Glue jobs
    print("\n== Cleaning up Glue jobs ==")
    job_names = ['validate_sales', 'transform_sales', 'generate_analytics']
    for job_name in job_names:
        try:
            print(f"  - Deleting Glue job: {job_name}")
            glue_client.delete_job(JobName=job_name)
            print(f"    Successfully deleted job")
        except glue_client.exceptions.EntityNotFoundException:
            print(f"    Job does not exist: {job_name}")
        except Exception as e:
            print(f"    Error deleting job {job_name}: {str(e)}")
    
    # 3.2 Delete Glue crawlers
    print("\n== Cleaning up Glue crawlers ==")
    crawler_name = f"{PROJECT_NAME}-reference-crawler"
    try:
        print(f"  - Deleting Glue crawler: {crawler_name}")
        glue_client.delete_crawler(Name=crawler_name)
        print(f"    Successfully deleted crawler")
    except glue_client.exceptions.EntityNotFoundException:
        print(f"    Crawler does not exist: {crawler_name}")
    except Exception as e:
        print(f"    Error deleting crawler {crawler_name}: {str(e)}")
    
    # 3.3 Delete Glue database
    print("\n== Cleaning up Glue database ==")
    database_name = PROJECT_NAME.replace('-', '_')
    try:
        print(f"  - Deleting Glue database: {database_name}")
        # First get all tables in the database
        try:
            tables = glue_client.get_tables(DatabaseName=database_name)
            for table in tables.get('TableList', []):
                print(f"    Deleting table: {table['Name']}")
                glue_client.delete_table(DatabaseName=database_name, Name=table['Name'])
        except Exception as e:
            print(f"    Error listing/deleting tables: {str(e)}")
            
        # Then delete the database
        glue_client.delete_database(Name=database_name)
        print(f"    Successfully deleted database")
    except glue_client.exceptions.EntityNotFoundException:
        print(f"    Database does not exist: {database_name}")
    except Exception as e:
        print(f"    Error deleting database {database_name}: {str(e)}")
    
    # 4. Delete Step Functions resources
    print("\n== Cleaning up Step Functions ==")
    state_machine_name = f"{PROJECT_NAME}-workflow"
    try:
        state_machines = sfn_client.list_state_machines()
        for machine in state_machines['stateMachines']:
            if machine['name'] == state_machine_name:
                print(f"  - Deleting state machine: {machine['name']}")
                # Stop any running executions
                executions = sfn_client.list_executions(
                    stateMachineArn=machine['stateMachineArn'],
                    statusFilter='RUNNING'
                )
                for execution in executions.get('executions', []):
                    print(f"    Stopping execution: {execution['executionArn']}")
                    try:
                        sfn_client.stop_execution(executionArn=execution['executionArn'])
                    except Exception as e:
                        print(f"    Error stopping execution: {str(e)}")
                
                # Delete the state machine
                sfn_client.delete_state_machine(stateMachineArn=machine['stateMachineArn'])
                print(f"    Successfully deleted state machine")
    except Exception as e:
        print(f"  Error during Step Functions cleanup: {str(e)}")
    
    # 5. Delete IAM roles
    print("\n== Cleaning up IAM roles ==")
    
    # 5.1 Delete Glue role
    role_name = f"{PROJECT_NAME}-glue-role"
    try:
        # First detach all managed policies
        policies = iam_client.list_attached_role_policies(RoleName=role_name)
        for policy in policies['AttachedPolicies']:
            print(f"  - Detaching policy from {role_name}: {policy['PolicyName']}")
            iam_client.detach_role_policy(
                RoleName=role_name,
                PolicyArn=policy['PolicyArn']
            )
            
        # Delete inline policies
        policy_names = iam_client.list_role_policies(RoleName=role_name)['PolicyNames']
        for policy_name in policy_names:
            print(f"  - Deleting inline policy from {role_name}: {policy_name}")
            iam_client.delete_role_policy(
                RoleName=role_name,
                PolicyName=policy_name
            )
            
        # Delete the role
        print(f"  - Deleting IAM role: {role_name}")
        iam_client.delete_role(RoleName=role_name)
        print(f"    Successfully deleted role")
    except iam_client.exceptions.NoSuchEntityException:
        print(f"    Role does not exist: {role_name}")
    except Exception as e:
        print(f"    Error cleaning up role {role_name}: {str(e)}")
    
    # 5.2 Delete Step Functions role
    sfn_role_name = f"{PROJECT_NAME}-sfn-role"
    try:
        # First detach all managed policies
        policies = iam_client.list_attached_role_policies(RoleName=sfn_role_name)
        for policy in policies['AttachedPolicies']:
            print(f"  - Detaching policy from {sfn_role_name}: {policy['PolicyName']}")
            iam_client.detach_role_policy(
                RoleName=sfn_role_name,
                PolicyArn=policy['PolicyArn']
            )
            
        # Delete inline policies
        policy_names = iam_client.list_role_policies(RoleName=sfn_role_name)['PolicyNames']
        for policy_name in policy_names:
            print(f"  - Deleting inline policy from {sfn_role_name}: {policy_name}")
            iam_client.delete_role_policy(
                RoleName=sfn_role_name,
                PolicyName=policy_name
            )
            
        # Delete the role
        print(f"  - Deleting IAM role: {sfn_role_name}")
        iam_client.delete_role(RoleName=sfn_role_name)
        print(f"    Successfully deleted role")
    except iam_client.exceptions.NoSuchEntityException:
        print(f"    Role does not exist: {sfn_role_name}")
    except Exception as e:
        print(f"    Error cleaning up role {sfn_role_name}: {str(e)}")
    
    print("\n=== Cleanup Complete ===")
    print("You can now run app.py to recreate the infrastructure from scratch.")

if __name__ == "__main__":
    cleanup_resources()