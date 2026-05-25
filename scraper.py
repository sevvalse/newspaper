import feedparser
from newspaper import Article
import psycopg2
from db import get_db_connection

NEWS_FEEDS = {
    "BBC Türkçe": "https://feeds.bbci.co.uk/turkce/rss.xml",
    "NTV Gündem": "https://www.ntv.com.tr/gundem.rss",
    "Sözcü": "https://www.sozcu.com.tr/rss/son-dakika.xml"
}


def scrape_full_article(url):
    try:
        article = Article(url, language='tr')
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"İçerik kazınırken hata oluştu ({url}): {e}")
        return None


def fetch_and_save_news():
    conn = get_db_connection()
    if not conn:
        print("Veritabanı bağlantısı kurulamadığı için tarama iptal edildi.")
        return

    try:
        with conn.cursor() as cur:
            for source_name, feed_url in NEWS_FEEDS.items():
                print(f"{source_name} RSS akışı taranıyor...")
                feed = feedparser.parse(feed_url)

                saved_count = 0
                for entry in feed.entries:
                    title = entry.title
                    link = entry.link
                    # RSS içinde kısa özet varsa al, yoksa boş bırak
                    summary = entry.get("summary", "")

                    # ON CONFLICT (link) DO NOTHING: Eğer link DB'de varsa hata verme, pas geç.
                    # Bu sayede gün içinde mükerrer kayıt oluşmaz ve kod çökmez.
                    check_query = "SELECT 1 FROM news WHERE link = %s;"
                    cur.execute(check_query, (link,))

                    if cur.fetchone():
                        continue

                    print(f"Yeni haber bulundu: {title[:50]}...")
                    raw_text = scrape_full_article(link)

                    if not raw_text or len(raw_text.strip()) < 100:
                        continue

                    insert_query = """
                                   INSERT INTO news (source, title, link, summary, raw_text)
                                   VALUES (%s, %s, %s, %s, %s); \
                                   """
                    cur.execute(insert_query, (source_name, title, link, summary, raw_text))
                    saved_count += 1

                conn.commit()
                print(f"{source_name}: {saved_count} yeni haber başarıyla kaydedildi.\n")

    except Exception as e:
        print(f"Tarama sürecinde bir hata meydana geldi: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    print("Gün içi haber tarama sistemi başlatıldı...")
    fetch_and_save_news()