"""
Alert Service — Abandoned Object SOS Notifications
Sends email (admin) + SMS via Fast2SMS API when an object's abandonment
confidence stays above 0.80 for more than 10 seconds.

Does NOT modify any existing logic; called externally from app.py.
"""

import smtplib
import threading
import time
import urllib.request
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# ─── Configuration ────────────────────────────────────────────────────────────
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "shaamas38@gmail.com"
SENDER_PASSWORD = "vppubrublkianwyx"   # App Password (spaces removed)

ADMIN_EMAIL = "shaam2310914@ssn.edu.in"
ADMIN_PHONE = "9342708253"             # Airtel Tamil Nadu

# ─── Fast2SMS API (free at fast2sms.com) ─────────────────────────────────────
# Steps: Register at fast2sms.com → Dev API → copy the key below
FAST2SMS_API_KEY = "IzTmpoEA5wF4VWldc3BaYiRb6G7NPZg0LsjDextUuHh298JyKkAdOqp1NKEg2CUrTF3m0lzGbhBDcaVy"
FAST2SMS_URL = "https://www.fast2sms.com/dev/bulkV2"
# ─────────────────────────────────────────────────────────────────────────────

ALERT_CONFIDENCE_THRESHOLD = 0.80   # Must exceed this to qualify
ALERT_DURATION_SECONDS = 10         # Must be sustained for this long
# ─────────────────────────────────────────────────────────────────────────────


class AlertTracker:
    """
    Tracks per-object timestamps and sends alerts once the 10-second
    sustained threshold is met.  Thread-safe.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self.object_alert_times: dict = {}
        self.alerts_sent: set = set()

    # ── Public API ─────────────────────────────────────────────────────────

    def check_and_send(
        self,
        object_id: str,
        class_name: str,
        confidence: float,
        stationary_time: float,
        location_type: str = "UNKNOWN"
    ):
        """
        Call this every detection frame for high-confidence objects.
        Triggers exactly one alert per object per abandonment event.
        """
        with self._lock:
            if confidence >= ALERT_CONFIDENCE_THRESHOLD:
                if object_id not in self.object_alert_times:
                    self.object_alert_times[object_id] = time.time()
                    print(f"[ALERT_SERVICE] Tracking object {object_id} ({class_name}) — conf={confidence:.2f}")

                elapsed = time.time() - self.object_alert_times[object_id]

                if elapsed >= ALERT_DURATION_SECONDS and object_id not in self.alerts_sent:
                    self.alerts_sent.add(object_id)
                    threading.Thread(
                        target=self._send_alerts,
                        args=(object_id, class_name, confidence, stationary_time, location_type, elapsed),
                        daemon=True
                    ).start()
            else:
                self.object_alert_times.pop(object_id, None)
                self.alerts_sent.discard(object_id)

    def should_send(self, object_id: str) -> bool:
        """Unit-test helper — checks if the object would fire an alert."""
        first = self.object_alert_times.get(object_id)
        return (first is not None
                and object_id not in self.alerts_sent
                and (time.time() - first) >= ALERT_DURATION_SECONDS)

    # ── Internal ───────────────────────────────────────────────────────────

    def _send_alerts(self, object_id, class_name, confidence, stationary_time, location_type, elapsed):
        """Sends email to admin + SMS via Fast2SMS API."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"SOS ABANDONED OBJECT ALERT - {class_name.upper()}"
        body = (
            f"ABANDONED OBJECT DETECTED\n"
            f"{'=' * 40}\n"
            f"Object      : {class_name}\n"
            f"Confidence  : {confidence * 100:.1f}%\n"
            f"Duration    : {elapsed:.0f} seconds\n"
            f"Stationary  : {stationary_time:.0f} seconds\n"
            f"Location    : {location_type}\n"
            f"Object ID   : {object_id}\n"
            f"Time        : {timestamp}\n"
            f"{'=' * 40}\n"
            f"Please investigate immediately.\n"
            f"[Context-Aware Abandoned Object Detection System]"
        )
        sms_msg = (
            f"SOS ALERT: Abandoned {class_name} detected! "
            f"Conf: {confidence*100:.0f}%, Duration: {elapsed:.0f}s. "
            f"Investigate immediately. [{timestamp}]"
        )

        print(f"[ALERT_SERVICE] Sending SOS alert for {object_id} ({class_name}) — {elapsed:.0f}s elapsed")

        # ── 1. Send Email via SMTP ────────────────────────────────────────
        try:
            msg = MIMEMultipart()
            msg["From"] = SENDER_EMAIL
            msg["To"] = ADMIN_EMAIL
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, ADMIN_EMAIL, msg.as_string())
            print(f"[ALERT_SERVICE] Email sent to {ADMIN_EMAIL}")
        except Exception as e:
            print(f"[ALERT_SERVICE] Email failed: {e}")

        # ── 2. Send SMS via Fast2SMS API ──────────────────────────────────
        if FAST2SMS_API_KEY == "PASTE_YOUR_FAST2SMS_KEY_HERE":
            print("[ALERT_SERVICE] SMS skipped — set FAST2SMS_API_KEY in alert_service.py")
            return

        try:
            # Use route 'v3' (Quick Transactional) with default sender 'TXTIND'
            params = urllib.parse.urlencode({
                "authorization": FAST2SMS_API_KEY,
                "route": "v3",
                "sender_id": "TXTIND",
                "message": sms_msg,
                "language": "english",
                "flash": "0",
                "numbers": ADMIN_PHONE,
            })
            url = f"{FAST2SMS_URL}?{params}"
            req = urllib.request.Request(url, headers={"cache-control": "no-cache"})

            with urllib.request.urlopen(req, timeout=10) as resp:
                result = resp.read().decode()
            
            print(f"[ALERT_SERVICE] SMS response: {result}")
            if "true" in result.lower():
                print(f"[ALERT_SERVICE] ✅ SMS sent successfully to {ADMIN_PHONE}")
            else:
                print(f"[ALERT_SERVICE] ⚠️ SMS might not have been delivered: {result}")

        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            print(f"[ALERT_SERVICE] ❌ SMS API Error {e.code}: {error_body}")
            if "sender" in error_body.lower():
                print(f"{'=' * 60}")
                print("💡 [ACTION REQUIRED] FAST2SMS SENDER ID NOT ACTIVE")
                print("1. Login to https://www.fast2sms.com/dashboard/index")
                print("2. Go to 'Sender ID' (left menu) and ensure a default ID is 'ADED' or 'ACTIVE'.")
                print("3. For free accounts, you MUST activate 'TXTIND' or 'FSTSMS' before the API works.")
                print(f"{'=' * 60}")
        except Exception as e:
            print(f"[ALERT_SERVICE] ❌ SMS System Error: {e}")


# ── Module-level singleton ────────────────────────────────────────────────────
alert_tracker = AlertTracker()
