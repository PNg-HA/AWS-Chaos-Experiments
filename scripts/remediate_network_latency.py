import os
import boto3
import requests
import re
import base64


def run_ssm_document(instance_id):
    ssm = boto3.client("ssm", region_name=os.getenv("AWS_REGION"))
    script = "echo Hello"
    encoded_script = base64.b64encode(script.encode("utf-8")).decode("utf-8")
    response = ssm.start_automation_execution(
        DocumentName="AWSSupport-StartEC2RescueWorkflow",
        Parameters={
            "InstanceId": [instance_id],
            "AllowEncryptedVolume": ["True"],
            "OfflineScript": [encoded_script],
        },
    )
    execution_id = response["AutomationExecutionId"]
    print(f"Started SSM document on instance {instance_id}: {execution_id}")


def parse_body(issue_body):
    match = re.search(r"EC2 instance (\bi-\w+\b)", issue_body)
    if match:
        return match.group(1)
    else:
        raise ValueError("Instance ID not found in issue body")


def remediate():
    issue_body = os.getenv("ISSUE_BODY")
    try:
        instance_id = parse_body(issue_body)
        print(f"Instance ID to remediate: {instance_id}")
        run_ssm_document(instance_id)
    except Exception as e:
        print(f"Error during remediation: {e}")
        reopen_issue()


def reopen_issue():
    issue_number = os.getenv("ISSUE_NUMBER")
    repo = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    headers = {"Authorization": f"token {token}"}
    data = {"state": "open"}
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Reopened issue {issue_number}")
    else:
        print(f"Failed to reopen issue {issue_number}: {response.content}")


if __name__ == "__main__":
    remediate()
