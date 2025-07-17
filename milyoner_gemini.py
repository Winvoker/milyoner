import re
import os
import pandas as pd
import csv
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize clients with environment variables
google_ai_api_key = os.getenv("GOOGLE_AI_API_KEY")
if not google_ai_api_key:
    raise ValueError("GOOGLE_AI_API_KEY environment variable is required")

client = genai.Client(api_key=google_ai_api_key)

# Extract playlist ID from environment variables
playlist_id = "PLsD-lH1jaVRP--NiDw0ekIYNcwA1D1q_g"

api_key = os.getenv("YOUTUBE_API_KEY")
if not api_key:
    raise ValueError("YOUTUBE_API_KEY environment variable is required")


def fetch_transcript(video_id: str, lang="tr") -> str:
    try:
        transcript_path = os.path.join("transcripts", f"{video_id}.txt")
        if os.path.exists(transcript_path):
            print(f"Transcript already exists: {transcript_path}")
            with open(transcript_path, "r", encoding="utf-8") as f:
                return f.read()

        data = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang, "en"])
        transcript = " ".join([d["text"] for d in data])

        os.makedirs("transcripts", exist_ok=True)
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"Transcript saved to {transcript_path}")
        return transcript
    except Exception as e:
        print(f"[Transcript hata] {video_id}: {e}")
        return ""


PROMPT = """
Aşağıdaki \"Kim Milyoner Olmak İster\" transkript parçasını analiz et. Her yarışmacı için aşağıdaki alanları çıkar ve sadece geçerli bir JSON listesi döndür:

ÖNEMLİ: Oktay Kaynarca programın sunucusudur, yarışmacı DEĞİLDİR. Onu yarışmacı olarak kaydetme!

Alanlar:
- \"contestant\": Yarışmacının adı (Oktay Kaynarca sunucudur, yarışmacı değil!)
- \"question\": Sorulan sorunun metni
- \"options\": Şıklar (A, B, C, D şeklinde liste)
- \"correct_answer\": Doğru cevap (A, B, C, D)
- \"contestant_answer\": Yarışmacının verdiği cevap (A, B, C, D, veya boş bırakılabilir)
- \"category\": Sorunun kategorisi (Tarih, Coğrafya, Bilim, Sanat, Edebiyat, Spor, Müzik, Genel Kültür, Matematik, Teknoloji, bilinmiyor)
- \"level\": Soru seviyesi (1-15 arası, bilinmiyorsa 0)
- \"amount\": Soru değeri (1000, 2000, 3000, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000 TL)
- \"joker_used\": Kullanılan joker türü (yok, yarı_yarıya, telefon, seyirci, değiştir)
- \"is_correct\": Yarışmacının cevabının doğru olup olmadığı (true/false)
- \"eliminated\": Yarışmacının elendi mi (true/false)

Sorularda \"A)\", \"B)\", \"C)\", \"D)\" şeklinde şıkları ayır. Joker kullanımını ve doğru/yanlış cevapları bağlamdan anlamaya çalış. Yarışmacı ismini doğru çıkar. Sadece geçerli JSON döndür.

- Çıktı sadece geçerli JSON olsun, başka açıklama veya metin olmasın.
- Soru metni tam olarak çıkarılsın.
"""


def parse_chunk(chunk: str):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=PROMPT + "\n\n" + chunk,
    )
    return response.text.strip()


def process_video(video_url: str):
    import json

    vid = re.search(r"v=([\w\-]+)", video_url).group(1)

    # Check if raw output already exists
    raw_output_path = f"raw_output/debug_raw_output_{vid}.txt"
    if os.path.exists(raw_output_path):
        print(f"Raw output already exists for video {vid}, loading from file...")
        with open(raw_output_path, "r", encoding="utf-8") as f:
            out = f.read()
    else:
        text = fetch_transcript(vid)

        # Skip if transcript is empty
        if not text:
            return []

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=PROMPT + "\n\n" + text,
        )

        out = response.text.strip()

        # Save raw output for future use
        os.makedirs("raw_output", exist_ok=True)
        with open(raw_output_path, "w", encoding="utf-8") as f:
            f.write(out)

    try:
        # Attempt to parse the JSON output
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]

        rows = []
        for entry in data:
            contestant_name = entry.get("contestant", "").strip()

            # Oktay Kaynarca sunucudur, yarışmacı olarak kaydetme
            if (
                "oktay kaynarca" in contestant_name.lower()
                or "oktay" in contestant_name.lower()
            ):
                continue

            # Check if this is the nested format with questions_answered
            if "questions_answered" in entry:
                # Handle nested format
                for question_data in entry.get("questions_answered", []):
                    question_row = {
                        "video_id": vid,
                        "contestant": contestant_name,
                        "question": question_data.get("question", ""),
                        "options": question_data.get("options", []),
                        "correct_answer": question_data.get("correct_answer", ""),
                        "contestant_answer": question_data.get("contestant_answer", ""),
                        "category": question_data.get("category", "Genel Kültür"),
                        "level": question_data.get("level", 0),
                        "amount": question_data.get("amount", 0),
                        "joker_used": question_data.get("joker_used", "yok"),
                        "is_correct": question_data.get("is_correct", False),
                        "eliminated": question_data.get("eliminated", False),
                    }
                    rows.append(question_row)
            else:
                # Handle flat format (original expected format)
                if not entry.get("contestant") or not entry.get("question"):
                    continue

                entry["video_id"] = vid
                rows.append(entry)

        print(f"Extracted {len(rows)} entries from video {vid}")
        return rows

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}\nRaw output: {out}")

        # Attempt to recover partial JSON
        try:
            start_index = out.find("[")
            end_index = out.rfind("]") + 1
            if start_index != -1 and end_index != -1:
                partial_data = json.loads(out[start_index:end_index])
                print(f"Recovered partial JSON data: {partial_data}")
                return partial_data
        except Exception as recovery_error:
            print(f"Failed to recover partial JSON: {recovery_error}")

        return []
    except Exception as e:
        print(f"Error processing video: {e}")
        return []


def clean_with(df):
    # Basic cleaning without LLM for better performance
    print("Performing basic cleaning...")

    # Remove obvious duplicates
    df = df.drop_duplicates(subset=["video_id", "contestant", "question"], keep="first")

    # Clean contestant names
    df["contestant"] = df["contestant"].str.strip().str.title()

    # Remove entries with Oktay Kaynarca as contestant
    # df = df[~df["contestant"].str.lower().str.contains("oktay", na=False)]

    # Fill missing values with defaults
    df["category"] = df["category"].fillna("Genel Kültür")
    df["level"] = df["level"].fillna(0)
    df["joker_used"] = df["joker_used"].fillna("yok")
    df["is_correct"] = df["is_correct"].fillna(False)
    df["eliminated"] = df["eliminated"].fillna(False)

    print(f"Basic cleaning completed. {len(df)} entries remaining.")
    return df


def get_video_ids_from_playlist(playlist_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults=50&key={api_key}"
    video_ids = []
    while url:
        response = requests.get(url).json()
        for item in response.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])
        next_page_token = response.get("nextPageToken")
        if next_page_token:
            url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults=50&pageToken={next_page_token}&key={api_key}"
        else:
            url = None
    return video_ids


def main(video_urls):
    import time

    os.makedirs("csv", exist_ok=True)

    print(f"Starting processing of {len(video_urls)} video(s)...")
    start_time = time.time()

    all_rows = []
    for i, url in enumerate(video_urls, 1):
        print(f"\nProcessing video {i}/{len(video_urls)}: {url}")
        video_start = time.time()

        try:
            vid = re.search(r"v=([\w\-]+)", url).group(1)
            csv_path = os.path.join("csv", f"{vid}.csv")
            stats_path = os.path.join("csv", f"{vid}_stats.csv")

            if os.path.exists(csv_path) and os.path.exists(stats_path):
                print(f"CSV files already exist for video {vid}")
                continue

            rows = process_video(url)
            all_rows.extend(rows)

            if not rows:
                print(f"No data extracted from video {vid}!")
                continue  # Create DataFrame for this video
            df_video = pd.DataFrame(rows)
            print(f"DEBUG: DataFrame created with {len(df_video)} rows")
            if len(df_video) > 0:
                print(
                    f"DEBUG: Video ID column sample: {df_video['video_id'].head().tolist()}"
                )

            # Kolonları yeniden sırala
            expected_columns = [
                "video_id",
                "contestant",
                "question",
                "options",
                "correct_answer",
                "contestant_answer",
                "category",
                "level",
                "amount",
                "joker_used",
                "is_correct",
                "eliminated",
            ]

            # Add missing columns
            for col in expected_columns:
                if col not in df_video.columns:
                    df_video[col] = None
                    print(f"DEBUG: Added missing column: {col}")

            df_video = df_video[expected_columns]
            print(
                f"DEBUG: After column reordering, video_id sample: {df_video['video_id'].head().tolist()}"
            )

            # Veri temizleme for this video
            df_video = clean_with(df_video)
            print(
                f"DEBUG: After cleaning, video_id sample: {df_video['video_id'].head().tolist()}"
            )

            # Save detailed data for this video
            df_video.to_csv(csv_path, index=False, quoting=csv.QUOTE_NONNUMERIC)
            print(f"Video CSV saved: {csv_path}")

            # Generate contestant stats for this video
            if len(df_video) > 0:
                contestant_stats_video = (
                    df_video.groupby(["video_id", "contestant"], as_index=False)
                    .agg(
                        {
                            "question": "count",  # Toplam soru sayısı
                            "is_correct": "sum",  # Doğru cevap sayısı
                            "amount": "max",  # Ulaştığı en yüksek miktar
                            "eliminated": "max",  # Elendi mi
                            "level": "max",  # Ulaştığı en yüksek seviye
                        }
                    )
                    .rename(
                        columns={
                            "question": "total_questions",
                            "is_correct": "correct_answers",
                            "amount": "max_amount",
                            "level": "max_level",
                        }
                    )
                )

                # Save contestant stats for this video
                contestant_stats_video.to_csv(
                    stats_path,
                    index=False,
                    quoting=csv.QUOTE_NONNUMERIC,
                )
                print(f"Video stats CSV saved: {stats_path}")

            video_duration = time.time() - video_start
            print(
                f"Video {i} completed in {video_duration:.1f}s, extracted {len(rows)} entries"
            )

        except Exception as e:
            print(f"Error processing video {i}: {e}")
            continue

    if not all_rows:
        print("No data extracted from any video!")
        return

    # Create combined DataFrames for all videos
    df_all = pd.DataFrame(all_rows)
    print(f"\nTotal entries extracted: {len(df_all)}")

    # Kolonları yeniden sırala
    expected_columns = [
        "video_id",
        "contestant",
        "question",
        "options",
        "correct_answer",
        "contestant_answer",
        "category",
        "level",
        "amount",
        "joker_used",
        "is_correct",
        "eliminated",
    ]

    # Add missing columns
    for col in expected_columns:
        if col not in df_all.columns:
            df_all[col] = None

    df_all = df_all[expected_columns]

    # Veri temizleme for combined data
    df_all = clean_with(df_all)

    # Her yarışmacı için özet istatistikleri (combined)
    if len(df_all) > 0:
        contestant_stats_all = (
            df_all.groupby(["video_id", "contestant"], as_index=False)
            .agg(
                {
                    "question": "count",  # Toplam soru sayısı
                    "is_correct": "sum",  # Doğru cevap sayısı
                    "amount": "max",  # Ulaştığı en yüksek miktar
                    "eliminated": "max",  # Elendi mi
                    "level": "max",  # Ulaştığı en yüksek seviye
                }
            )
            .rename(
                columns={
                    "question": "total_questions",
                    "is_correct": "correct_answers",
                    "amount": "max_amount",
                    "level": "max_level",
                }
            )
        )

        # Ana veriyi kaydet (combined)
        df_all.to_csv(
            "csv/milyoner_data_all.csv", index=False, quoting=csv.QUOTE_NONNUMERIC
        )
        print(f"Combined CSV oluşturuldu: {len(df_all)} satır.")

        # Yarışmacı özetini kaydet (combined)
        contestant_stats_all.to_csv(
            "csv/milyoner_contestant_stats_all.csv",
            index=False,
            quoting=csv.QUOTE_NONNUMERIC,
        )
        print(f"Combined stats CSV oluşturuldu: {len(contestant_stats_all)} satır.")

    total_duration = time.time() - start_time
    print(f"\nTotal processing time: {total_duration:.1f}s")


if __name__ == "__main__":
    # Fetch video IDs from the playlist
    video_ids = get_video_ids_from_playlist(playlist_id, api_key)

    # Generate video URLs
    video_urls = [
        f"https://www.youtube.com/watch?v={video_id}" for video_id in video_ids
    ]
    main(video_urls)
