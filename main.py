import time
import schedule
from scraper import fetch_and_save_news
from summarizer import process_todays_summaries
from mailer import send_daily_newspaper


def daytime_scraper_task():
    """Gün içinde belirli aralıklarla haberleri toplayan görev."""
    print(f"\n[{time.strftime('%X')}] Gün içi RSS taraması başlatılıyor...")
    fetch_and_save_news()


def midnight_digest_task():
    """Gece yarısı tetiklenen yapay zeka özetleme ve mail gönderim görevi."""
    print(f"\n [{time.strftime('%X')}] bülten operasyonu başladı!")

    print("OpenAI özetleme motoru tetikleniyor...")
    process_todays_summaries()

    print("Gazete derleniyor ve SMTP ile gönderiliyor...")
    send_daily_newspaper()

    print(f"[{time.strftime('%X')}] operasyonu başarıyla bitti.")


schedule.every().day.at("08:00").do(daytime_scraper_task)
schedule.every().day.at("14:00").do(daytime_scraper_task)
schedule.every().day.at("18:50").do(daytime_scraper_task)
schedule.every().day.at("23:30").do(daytime_scraper_task)

schedule.every().day.at("19:00").do(midnight_digest_task)

if __name__ == "__main__":
    print("Yapay Zeka Destekli Gazete Otomasyonu Başlatıldı!")
    print("Sistem arka planda zamanlanan saatleri bekliyor...")


    while True:
        schedule.run_pending()
        time.sleep(60)