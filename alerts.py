import smtplib

class AlertManager:

    def send_alert(self, threat):
        print(f"ALERT: {threat} detected! Notification sent to {self.email}.")
        self.send_email_notification(threat)

    def send_email_notification(self, threat):
        print(f"Simulating email: Subject: Security Alert - {threat}")
