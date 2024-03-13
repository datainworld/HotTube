이 코드는 사용자가 유튜브 트렌딩 데이터를 다양한 기준으로 필터링하고 분석할 수 있는 대시보드를 제공합니다. 또한, 사용자 상호작용에 따라 동적으로 업데이트되는 인터랙티브한 웹 애플리케이션을 구현하기 위해 Dash의 기능을 광범위하게 활용합니다.

- HotTube.py : 핫튜브 50의 메인 코드로, Dash와 Plotly, 그리고 Dash Bootstrap Components를 사용하여 유튜브 트렌딩 동영상에 대한 정보를 시각화하고 분석하는 대시보드 웹 애플리케이션을 구현합니다.
- HotTube.ipynb : HotTube.py의 주피터노트북 버전입니다.
- get_yt_trending.py : YouTube API를 사용하여 유튜브에서 인기 동영상 데이터를 가져옵니다
- get_yt_summary.py : YouTube 동영상의 자막을 가져와서 openAI의 API와 langchain을 이용하여 요약하는 기능을 수행합니다.
- get_yt_summary_openai.py : langchain을 사용하지 않습니다. 따라서 gpt-3.5-turbo모델의 한계인 16,385 토큰을 초과하면 요약이 이루어지지 않습니다.
- youtube_trending_videos.csv : get_yt_trending.py를 이용하여 추출한 샘플 데이터 파일입니다.
- assets
  - hot50.png : 로고 이미지
  - scripts : 3줄로 요약된 스크립트 파일이 담긴 디렉토리

https://hottube-datagongjak.pythonanywhere.com 은 이 Dash 애플리케이션을 호스팅하는 실제 웹 사이트로, 여기서 실시간으로 유튜브 트렌딩 데이터의 시각화 및 분석 결과를 볼 수 있습니다.
