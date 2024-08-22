import os
import boto3
import requests


def detect_alarm_state():
    print("Detecting NetworkIn alarm state...")
    cloudwatch = boto3.client("cloudwatch", region_name=os.getenv("AWS_REGION"))

    alarm_name = os.getenv("CLOUDWATCH_ALARM_NAME")
    response = cloudwatch.describe_alarms(AlarmNames=[alarm_name])
    alarms = response["MetricAlarms"]

    if not alarms:
        print("No alarms found with the specified name.")
        return

    alarm_state = alarms[0]["StateValue"]

    if alarm_state == "ALARM":
        instance_id = alarms[0]["Dimensions"][0]["Value"]
        create_github_issue(instance_id)
    else:
        print("No NetworkIn alarm issues detected.")


def create_github_issue(instance_id):
    repo = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {"Authorization": f"token {token}"}
    issue_title = f"EC2 Instance {instance_id} NetworkIn Alarm Triggered"
    issue_body = f"The NetworkIn alarm for EC2 instance {instance_id} has been triggered. Remediation action is required."
    issue = {"title": issue_title, "body": issue_body}
    response = requests.post(url, headers=headers, json=issue)
    if response.status_code == 201:
        print(f"GitHub issue created for instance {instance_id}")
    else:
        print(
            f"Failed to create GitHub issue for instance {instance_id}: {response.content}"
        )


if __name__ == "__main__":
    detect_alarm_state()
