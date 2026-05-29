import datetime
import holidays
from jinja2 import Template
from db import get_db_connection


def prepare_newsletter_data():
    """Veritabanından filtrelenmiş haberleri çeker ve şablona uygun formata getirir."""
    conn = get_db_connection()
    if not conn:
        return []

    formatted_news = []
    try:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT source, title, link, ai_analysis
                        FROM news
                        WHERE ai_analysis IS NOT NULL
                          AND ai_analysis != 'PAS'
                        ORDER BY source, id DESC;
                        """)
            rows = cur.fetchall()

            for source, title, link, ai_analysis in rows:
                # OpenAI'dan gelen satırları (-) işaretine göre bölüp listeye çeviriyoruz
                # Böylece HTML içinde <li> olarak dönmek çok kolay olacak
                lines = [line.strip("- ").strip() for line in ai_analysis.split("\n") if line.strip()]

                formatted_news.append({
                    "source": source,
                    "title": title,
                    "link": link,
                    "bullets": lines
                })
    except Exception as e:
        print(f"Veri toplanırken hata oluştu: {e}")
    finally:
        conn.close()

    return formatted_news


def build_html_newsletter():
    news_list = prepare_newsletter_data()

    try:
        with open("template.html", "r", encoding="utf-8") as f:
            template_content = f.read()
    except FileNotFoundError:
        print("'template.html' dosyası bulunamadı!")
        return None

    template = Template(template_content)

    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    tomorrow_day_of_week = tomorrow.weekday()
    tr_holidays = holidays.Turkey(years=tomorrow.year)

    if tomorrow_day_of_week in [5, 6]:  # Cumartesi veya Pazar
        borsa_durumu = "KAPALI (Hafta Sonu)"
    elif tomorrow.strftime('%Y-%m-%d') in tr_holidays:
        tatil_adi = tr_holidays.get(tomorrow.strftime('%Y-%m-%d'))
        borsa_durumu = f"KAPALI (Resmi Tatil: {tatil_adi})"
    else:
        borsa_durumu = "AÇIK (İş Günü)"

    today_str = datetime.datetime.now().strftime("%d %B %Y - %A")

    final_html = template.render(
        date=today_str,
        news_list=news_list,
        borsa_durumu=borsa_durumu
    )

    return final_html


if __name__ == "__main__":
    print("Gazete tasarımı oluşturuluyor...")
    html_output = build_html_newsletter()

    if html_output:
        with open("daily_newspaper_test.html", "w", encoding="utf-8") as f:
            f.write(html_output)
        print(
            "Test gazetesi başarıyla 'daily_newspaper_test.html' adıyla oluşturuldu! Çift tıklayarak tarayıcıda inceleyebilirsin.")