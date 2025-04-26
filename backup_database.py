import os
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import schedule
import time
from dotenv import load_dotenv 

load_dotenv()

SOURCE_FOLDER = r'E:\auto\database'
BACKUP_FOLDER = r'E:\auto\DB_BackUp'
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
APP_PASSWORD = os.getenv('APP_PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

def send_email(subject, body_html):
    """Gửi email kiểu HTML"""
    try:
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = RECEIVER_EMAIL
        message["Subject"] = subject

        message.attach(MIMEText(body_html, "html"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())
        server.quit()
        print(f"✅ Đã gửi email thông báo đến {RECEIVER_EMAIL}")
    except Exception as e:
        print(f"❌ Lỗi gửi email: {e}")

def backup_database():
    """Backup file database và gửi mail"""
    try:
        if not os.path.exists(BACKUP_FOLDER):
            os.makedirs(BACKUP_FOLDER)
        
        files_copied = []
        for filename in os.listdir(SOURCE_FOLDER):
            if filename.endswith('.sql') or filename.endswith('.sqlite3'):
                src_file = os.path.join(SOURCE_FOLDER, filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_filename = f"{timestamp}_{filename}"
                backup_file = os.path.join(BACKUP_FOLDER, backup_filename)
                shutil.copy2(src_file, backup_file)
                files_copied.append(backup_filename)

        if files_copied:
            subject = "🎯 Backup Database Thành Công"
            body_html = "<h2>Danh sách file đã backup:</h2><ul>"
            for file in files_copied:
                body_html += f"<li>{file}</li>"
            body_html += "</ul>"
        else:
            subject = "⚠️ Backup Database - Không tìm thấy file"
            body_html = "<p>Không có file .sql hoặc .sqlite3 nào để backup.</p>"

        send_email(subject, body_html)
    except Exception as e:
        subject = "❌ Backup Database Thất Bại"
        body_html = f"<p>Đã xảy ra lỗi trong quá trình backup:</p><pre>{str(e)}</pre>"
        send_email(subject, body_html)

# Lên lịch chạy mỗi ngày lúc 00:00
schedule.every().day.at("00:00").do(backup_database)
print("🚀 Hệ thống backup đã khởi động, chờ tới 00:00 mỗi ngày...")
while True:
    schedule.run_pending()
    time.sleep(60)
