"""
Monitoring & Alerting Demo for DataLineagePy
Demonstrates performance monitoring and production-ready alerting integrations.
"""
import time
from datalineagepy.core.performance import PerformanceMonitor
from datalineagepy.alerting.integrations import send_slack_alert, send_email_alert
from datalineagepy.core.tracker import LineageTracker
import os

# Setup tracker and monitor
tracker = LineageTracker(name="alerting_demo")
monitor = PerformanceMonitor(tracker)

# Simulate a slow operation


def slow_op():
    time.sleep(2)
    return "done"


monitor.start_monitoring()
monitor.time_operation("slow_op", slow_op)
monitor.stop_monitoring()

summary = monitor.get_performance_summary()
print("Performance Summary:", summary)

# Send Slack alert if operation is slow
slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
if slack_webhook and summary['total_execution_time'] > 1.0:
    send_slack_alert(
        slack_webhook, f"[ALERT] Slow operation detected: {summary['total_execution_time']:.2f}s")

# Send Email alert if memory usage is high
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT", "465"))
sender = os.getenv("ALERT_EMAIL_SENDER")
password = os.getenv("ALERT_EMAIL_PASSWORD")
recipient = os.getenv("ALERT_EMAIL_RECIPIENT")
if sender and password and recipient and summary['current_memory_usage'] > 100:
    send_email_alert(smtp_server, smtp_port, sender, password, recipient,
                     "[ALERT] High Memory Usage",
                     f"Current memory usage: {summary['current_memory_usage']:.2f} MB")
