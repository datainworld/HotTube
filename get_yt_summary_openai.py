from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv  # pip install python-dotenv
import os

dotenv_path = find_dotenv()  # 상위 폴더에 있는 .env 파일을 찾는다.
load_dotenv(dotenv_path)  # .env 파일을 로드한다.
api_key = os.environ.get("OPENAI_API_KEY")  # YOUTUBE_API_KEY라는 이름의 환경변수 값을 가져온다.

def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
        text = " ".join([line["text"] for line in transcript])  
    except:
        text = '해당 영상은 자막을 제공하지 않습니다.'
    return text

def get_video_summary(script):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",        
        messages=[
            {"role": "system", "content": "콘텐츠를 한국어 3줄로 요약해 줘, 각 줄은 숫자로 시작하고 문단의 끝에는 줄바꿈 표시를 넣어 줘"},
            {"role": "user", "content": script}
        ],
        temperature=0.2,
        max_tokens=256
    )
    return response.choices[0].message.content  # 응답에서 원본 소스 코드만 반환

def get_summary(video_id):
    script = get_video_transcript(video_id)
    summary = get_video_summary(script)
    return summary