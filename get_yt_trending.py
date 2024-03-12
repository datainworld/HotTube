from googleapiclient.discovery import build  # pip install google-api-python-client
import pandas as pd
import isodate
from dotenv import load_dotenv, find_dotenv  # pip install python-dotenv
import os
dotenv_path = find_dotenv()  # 상위 폴더에 있는 .env 파일을 찾는다.
load_dotenv(dotenv_path)  # .env 파일을 로드한다.
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")  # YOUTUBE_API_KEY라는 이름의 환경변수 값을 가져온다.

def get_trending_videos():
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)  # 유튜브 API 클라이언트를 생성한다.
    ## 유튜브 API를 사용하여 인기 급상승 동영상 50개를 가져온다.
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        chart="mostPopular",
        regionCode="KR",
        maxResults=50
    )
    response = request.execute()

    ## Response에서 필요한 데이터를 추출하여 리스트에 저장
    data = []
    for item in response['items']:
        video_id = item['id']
        title = item['snippet']['title']
        description = item['snippet']['description']
        thumbnail_link_default = item['snippet']['thumbnails']['default']['url']
        thumbnail_link_medium = item['snippet']['thumbnails']['medium']['url']
        channel_id = item['snippet']['channelId']
        channel_title = item['snippet']['channelTitle']
        category_id = item['snippet']['categoryId']
        duration = isodate.parse_duration(item['contentDetails']['duration'])
        published_at = item['snippet']['publishedAt']
        view_count = item['statistics']['viewCount']
        data.append([video_id, title, description, thumbnail_link_default, thumbnail_link_medium, 
                    channel_id, channel_title, category_id, duration, published_at, view_count])

    ## 이해하기 쉬운 컬럼을 사용하면서 데이터프레임으로 변환
    df = pd.DataFrame(data, columns=['video_id', 'title', 'description', 'thumbnail_link_default', 
        'thumbnail_link_medium', 'channel_id', 'channel_title', 'category_id', 'duration', 'published_at', 'view_count'])

    ## 숫자로 되어있는 카테고리 ID를 알아보기 쉽게 카테고리 명칭으로 변환
    category_ids = df['category_id'].unique().tolist()
    category_dict = {}
    for category_id in category_ids:
        category_request = youtube.videoCategories().list(part='snippet', id=category_id)
        category_response = category_request.execute()
        category_name = category_response['items'][0]['snippet']['title']
        category_dict[category_id] = category_name
    df['category_id'] = df['category_id'].map(category_dict)

    ## 데이터 전처리
    df['duration'] = round(df.duration.dt.seconds/60, 1).astype(float) # 동영상 길이를 분 단위로 변환
    df['published_at'] = pd.to_datetime(df['published_at']) # 발행일을 날짜 형식으로 변환
    df['view_count'] = df['view_count'].astype(int) # 조회수를 정수형으로 변환
    # 썸네일 이미지를 클릭하면 해당 동영상으로 이동할 수 있도록 하이퍼링크 생성
    df['thumbnail_link'] = df.apply(lambda x: '[![Image](' + x['thumbnail_link_default'] + ')](https://www.youtube.com/watch?v=' + x['video_id'] + ')', axis=1) 
    df['ranking'] = df.index + 1 # 데이터 행 순서대로 순위 컬럼 추가

    return df 