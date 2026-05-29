import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from generator import build_html_newsletter
from db import clear_yesterdays_data

load_dotenv()


def send_daily_newspaper():
    """Oluşturulan HTML gazeteyi e-posta ile gönderir ve ardından DB'yi temizler."""

    print("Gazete içeriği hazırlanıyor...")
    html_content = build_html_newsletter()

    if not html_content:
        print("Gönderilecek içerik bulunamadı veya bir hata oluştu. İşlem iptal edildi.")
        return False

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")

    if not smtp_server:
        print("HATA: .env dosyasında 'SMTP_SERVER' tanımlanmamış!")
        return False
    if not sender_email:
        print("HATA: .env dosyasında 'SMTP_EMAIL' tanımlanmamış!")
        return False
    if not sender_password:
        print("HATA: .env dosyasında 'SMTP_PASSWORD' tanımlanmamış!")
        return False

    receiver_emails_raw = os.getenv("RECEIVER_EMAIL", "")
    receiver_list = [email.strip() for email in receiver_emails_raw.split(",") if email.strip()]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Günlük Kişisel Gazeteniz Hazır!"
    msg["From"] = f"Dijital Gazete"
    msg["To"] = ", ".join(receiver_list)

    part = MIMEText(html_content, "html", "utf-8")
    msg.attach(part)

    try:
        print(f"SMTP Sunucusuna bağlanılıyor ({smtp_server})...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Bağlantıyı şifrele (Güvenlik için zorunlu)

        server.login(sender_email, sender_password)
        print("Giriş başarılı. E-posta postalanıyor...")

        server.sendmail(sender_email, receiver_list, msg.as_string())
        server.quit()
        print(f"Gazete başarıyla gönderildi -> {', '.join(receiver_list)}")

        print("Gün sonu veritabanı temizliği başlatılıyor...")
        clear_yesterdays_data()
        print("Tüm süreç başarıyla tamamlandı. Yarın yeni haberlerde görüşmek üzere!")
        return True

    except Exception as e:
        print(f"E-posta gönderilirken bir hata oluştu: {e}")
        print("Güvenlik nedeniyle veritabanı temizliği İPTAL EDİLDİ. Verileriniz güvende.")
        return False


if __name__ == "__main__":
    send_daily_newspaper()