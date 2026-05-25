import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
from db import get_db_connection

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Sen tarafsız, clickbait'ten nefret eden kıdemli bir haber editörüsün.

İLGİLENİLEN: Teknoloji, Eğitim, Finans, Politika, Siyaset, Gündem.
İLGİLENİLMEYEN: Spor, Magazin, Yiyecek-İçecek → sadece "PAS" yaz.

Haber metnini 3 madde işaretiyle özetle. Kurallar:
- Reklam, tekrar ve clickbait içeriği çıkar.
- Her madde 5W1K'ya (Kim/Ne/Nerede/Ne Zaman/Nasıl/Neden) yanıt versin.
- Önemli bir isim ve doğrudan alıntısı varsa mutlaka ekle.
- Giriş cümlesi, başlık veya "İşte özet:" gibi ifadeler kullanma; doğrudan 3 maddeyi yaz.
- Dil: net, temiz, kurallı Türkçe.
- Yalnızca ilgilenilen konularda haber yaz. İlgilenilmeyen konularda -> "PAS"
"""


def summarize_single_article(title, raw_text):

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Haber Başlığı: {title}\n\nHaber Metni:\n{raw_text}"}
            ],
            temperature=0.3,  # Daha tutarlı ve net yanıtlar için düşürdük
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API Hatası ({title[:30]}): {e}")
        return None


def process_todays_summaries():
    conn = get_db_connection()
    if not conn:
        print("Veritabanı bağlantısı kurulamadı.")
        return

    try:
        with conn.cursor() as cur:
            # Sadece henüz AI analizi yapılmamış olan haberleri getir
            cur.execute("""
                        SELECT id, title, raw_text
                        FROM news
                        WHERE ai_analysis IS NULL
                          AND raw_text IS NOT NULL;
                        """)
            unprocessed_news = cur.fetchall()

            if not unprocessed_news:
                print("Özetlenecek yeni haber bulunmuyor. Her şey güncel!")
                return

            print(f"{len(unprocessed_news)} adet yeni haber OpenAI ile özetleniyor...")

            for num, (db_id, title, raw_text) in enumerate(unprocessed_news, 1):
                print(f"[{num}/{len(unprocessed_news)}] Özetleniyor: {title[:50]}...")

                summary_bullet_points = summarize_single_article(title, raw_text)

                if summary_bullet_points:
                    cur.execute("""
                                UPDATE news
                                SET ai_analysis = %s
                                WHERE id = %s;
                                """, (summary_bullet_points, db_id))
                    conn.commit()

            print("Tüm haberlerin AI özetleri veritabanına başarıyla işlendi!")

    except Exception as e:
        print(f"Özetleme sürecinde hata: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    process_todays_summaries()