import os
import smtplib
from email.message import EmailMessage

import requests


def send_rule_failure_alert(table_name: str, failed_rules: list[dict]) -> dict[str, bool]:
    subject = f"[DataGate] Rule validation failed for {table_name}"
    lines = [f"Applied rule validation failed for {table_name}."]
    for rule in failed_rules[:10]:
        lines.append(
            f"- {rule.get('column_name', '--')} / {rule.get('rule_type', '--')}: "
            f"{rule.get('constraint_message', 'Validation failed')}"
        )
    body = "\n".join(lines)

    return {
        "slack": _send_slack(subject, body),
        "email": _send_email(subject, body),
    }


def _send_slack(subject: str, body: str) -> bool:
    webhook_url = os.getenv("DATAGATE_SLACK_WEBHOOK_URL")
    if not webhook_url:
        return False
    try:
        response = requests.post(
            webhook_url,
            json={"text": f"*{subject}*\n{body}"},
            timeout=10,
        )
        response.raise_for_status()
        return True
    except Exception:
        return False


def _send_email(subject: str, body: str) -> bool:
    smtp_host = os.getenv("DATAGATE_SMTP_HOST")
    smtp_port = os.getenv("DATAGATE_SMTP_PORT")
    smtp_user = os.getenv("DATAGATE_SMTP_USER")
    smtp_pass = os.getenv("DATAGATE_SMTP_PASS")
    smtp_to = os.getenv("DATAGATE_ALERT_EMAIL_TO")
    smtp_from = os.getenv("DATAGATE_ALERT_EMAIL_FROM", smtp_user or "datagate@localhost")

    if not smtp_host or not smtp_port or not smtp_to:
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = smtp_from
    message["To"] = smtp_to
    message.set_content(body)

    try:
        with smtplib.SMTP(smtp_host, int(smtp_port), timeout=10) as server:
            server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(message)
        return True
    except Exception:
        return False
