import os
import boto3
import requests


def detect_issues():
    print("Detecting issues...")
    ec2 = boto3.client("ec2", region_name=os.getenv("AWS_REGION"))
    response = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["stopped"]}]
    )
    instance_ids = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_ids.append(instance["InstanceId"])

    if not instance_ids:
        print("No issues detected.")
        return

    # call create_github_issues for each instance
    for instance_id in instance_ids:
        create_github_issues(instance_id)


def create_github_issues(instance_id):
    repo = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {"Authorization": f"token {token}"}
    issue_title = f"EC2 Instance {instance_id} Stopped"
    issue_body = f"The EC2 instance {instance_id} is currently stopped. Remediation action is required."
    issue = {"title": issue_title, "body": issue_body}
    response = requests.post(url, headers=headers, json=issue)
    if response.status_code == 201:
        print(f"GitHub issue created for instance {instance_id}")
    else:
        print(
            f"Failed to create GitHub issue for instance {instance_id}: {response.text}"
        )


if __name__ == "__main__":
    detect_issues()
