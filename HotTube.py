import pandas as pd 
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import datetime
from get_yt_trending import get_trending_videos 
from get_yt_summary import get_summary
import os

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

### 데이터 처리 및 컴포넌트 섹션============================================================
## 앱 실행시 데이터 로드
df = get_trending_videos()

## [HotTube 분석]==========================================================================
fig_category = px.bar(
    df['category_id'].value_counts(), 
    orientation='h',
    width=600)
fig_category.update_layout(
    title='카테고리별 동영상 수',
    xaxis_title=None,
    yaxis_title=None,
    showlegend=False)

fig_runtime = px.histogram(
    df['duration'],
    title= '동영상 런타임 분포',
    nbins=10,
    text_auto=True)
fig_runtime.update(layout_showlegend=False)
fig_runtime.update_xaxes(title='런타임(분)')
fig_runtime.update_yaxes(title='동영상 수')
 
fig_published_date = px.pie(
    df['published_at'].dt.strftime('%m.%d').value_counts().reset_index().sort_values(by='published_at', axis=0),     
    names='published_at', 
    values='count',
    hole=0.3,
    title='날짜별 동영상 수',
    category_orders={'published_at': list('published_at')}) # series를 list로 변환해야 한다
fig_published_date.update_traces(textinfo='label+percent')
fig_published_date.update(layout_showlegend=False)

## [HotTube필터링] ==========================================================================
category_filter = dcc.Dropdown(
    id='category-dropdown',
    # options=[{'label': i, 'value': i} for i in df['category_id'].unique()],
    # value='All',    
    options=[{'label': i, 'value': i} for i in df['category_id'].unique()] + [{'label': '모두 선택', 'value': 'all_values'}],
    value = 'all_values',
    clearable=False,
)
duration_filter = dcc.RangeSlider(
    id='duration-slider',
    min=df['duration'].min(),
    max=df['duration'].max(),   
    value=[df['duration'].min(), df['duration'].max()]
)
published_at_filter = dcc.DatePickerRange(
    id='published-range',
    display_format='YYYY-MM-DD',
    month_format='YYYY-MM',
    min_date_allowed=df['published_at'].min(),
    max_date_allowed=df['published_at'].max(),
    start_date=df['published_at'].min(),
    end_date=df['published_at'].max()    
)

### 앱 레이아웃 섹션===================================================================
def serve_layout(): # 페이지 로드시마다 데이터를 업데이트하기 위한 함수
    global df
    df = get_trending_videos() # 페이지 로드시마다 데이터를 업데이트
    
    utc_time = datetime.datetime.now()
    kor_time = utc_time + datetime.timedelta(hours=9) # 한국 시간으로 변경
    kor_time = kor_time.strftime("%Y-%m-%d %H:%M:%S") 

    ### 앱 레이아웃 섹션===================================================================
    return dbc.Container([
        ## 콜백에서 필터링된 중간 데이터 저장--------------------------------------------------
        dcc.Store(id='intermediate-df'),

        ## 로고 및 데이터 추출 일시------------------------------------------------------------
        html.Div([
            html.A(
                html.Img(src='../assets/hot50.png', style={'width':'30%'}, className='mb-1'),
            href='/'), # 로고 클릭시 홈으로 이동
            html.H5(kor_time + ' 기준',  className='text-danger fst-italic'), # 페이지 로드시마다 현재 시간을 업데이트
        ], className='text-center mt-3 mb-5'),
        
        ## 순위 배지---------------------------------------------------------------------
        dbc.Row(
            dbc.Col(id ='badge')
        ),
        
        ## Top 영상---------------------------------------------------------------------
        dcc.Loading(
            id='loading-top',
            children=
                dbc.Row([
                        dbc.Col(id = 'top-video', lg=4),
                        dbc.Col(id = 'top-meta', lg=4),
                        dbc.Col(id = 'top-summary', lg=4)
                ],className='bg-light p-2 border border-danger rounded m'),
        ),

        ## [HotTube 분석]------------------------------------------------------------------    
        dbc.Row(html.H5('[HotTube 분석]', className='mt-5 mb-2')),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_category), lg=4),
            dbc.Col(dcc.Graph(figure=fig_runtime), lg=4),               
            dbc.Col(dcc.Graph(figure=fig_published_date), lg=4)
        ], className='bg-light p-2 mb-3 border border-secondary rounded m'),

        ## [HotTube필터링]-----------------------------------------------------------------
        dbc.Row(html.H5('[HotTube 필터링]', className='mt-5 mb-2')),
        dbc.Row([
            dbc.Col([html.H6('카테고리 선택'), category_filter], className='mt-4 mb-4' , lg=4),
            dbc.Col([html.H6('영상시간 선택'), duration_filter], className='mt-4 mb-4', lg=4),
            dbc.Col([html.H6('게시날짜 선택'), published_at_filter], className='mt-4 mb-4', lg=4)
        ], className='bg-light mb-3 border border-secondary rounded m'),    

        ## [HotTube 리스트 50]----------------------------------------------------------------
        dbc.Row(html.H5('[HotTube 리스트 50]', className='mt-5 mb-2')),
        dbc.Row(html.Div(id='table')),
    ])
app.layout = serve_layout # 페이지 로드시마다 데이터를 업데이트하기 위한 함수 호출

### 콜백 섹션 ===================================================================
## 테이블 생성===================================================================
@app.callback(
    Output('table', 'children'),
    Output('intermediate-df', 'data'),
    Input('category-dropdown', 'value'),
    Input('duration-slider', 'value'),
    Input('published-range', 'start_date'),
    Input('published-range', 'end_date'))
def update_table(category, duration, published_at_start, published_at_end):
    df_filtered = df.copy()
    if category == 'all_values':
        df_filtered = df_filtered
    else:
        df_filtered = df_filtered[df_filtered['category_id'] == category]
    df_filtered = df_filtered[(df_filtered['duration'] >= duration[0]) & (df_filtered['duration'] <= duration[1])]
    df_filtered = df_filtered[(df_filtered['published_at'] >= published_at_start) & (df_filtered['published_at'] <= published_at_end)]
    
    df_tbl = df_filtered[['ranking','title', 'video_id', 'thumbnail_link', 'channel_title', 'category_id', 'duration', 'published_at', 'view_count']]
    df_tbl['published_at'] = df_tbl['published_at'].dt.strftime('%Y-%m-%d') # 날짜 형식 변경
    df_tbl['view_count'] = df_tbl['view_count'].apply(lambda x: "{:,}".format(x)) # 조회수 3자리마다 콤마 찍기

    intermediate_df = df_tbl.to_dict('records') # 필터링된 중간 데이터를 dcc.Store에 저장

    table = dash_table.DataTable(
        id='inner-table',
        data=df_tbl.to_dict('records'),
        columns=[
            {"id": "ranking", "name": "순위"},
            {"id": "title", "name": "제목"},
            {"id": "thumbnail_link", "name": "썸네일", "presentation": "markdown"}, # presentation: 셀에 이미지 삽입
            {"id": "category_id", "name": "카테고리"},
            {"id": "duration", "name": "영상시간(분)"},
            {"id": "published_at", "name": "게시일"},
            {"id": "view_count", "name": "조회수"},
        ],
        row_selectable='single', # 단일행 선택 가능
        selected_rows=[], 
        style_table={'height': '800px'},
        style_data={'whiteSpace': 'normal', 'height': 'auto'}, # 긴 텍스트 줄 바꿈
        style_cell_conditional=[
            {'if': {'column_id': 'title'}, 'width': '20%'},
            {'if': {'column_id': 'Thumbnail Link'}, 'width': '10%'},
        ],
        style_as_list_view=True, # 테이블 테두리 없애기
        style_cell={'textAlign': 'left'}, # 테이블 셀 텍스트 왼쪽 정렬
        sort_action='native', # 정렬 옵션
    )
    return table, intermediate_df

## top 콘텐츠 생성 ================================================================
@app.callback(
    Output('top-video', 'children'),
    Output('top-meta', 'children'),
    Output('top-summary', 'children'),
    Input('inner-table', 'selected_rows'),
    Input('intermediate-df', 'data'))
def update_top(row, data):
    row = 0 if not row else row[0] # row가 없으면 0, 있으면 row의 첫번째 값
    df = pd.DataFrame(data) # 필터링된 중간 데이터를 데이터프레임으로 변환해서 사용
    video = html.Iframe(
        width="100%", height="100%",
        src="https://www.youtube.com/embed/" + df.loc[row, 'video_id'], 
        allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
    )
    meta = html.Div([
        html.P(df.loc[row, 'title'], className='fs-5 fw-bold'),
        html.P('⊙ 채   널 : ' + df.loc[row, 'channel_title'], className='fs-6 mb-1'),
        html.P('⊙ 카테고리 : ' + df.loc[row, 'category_id'], className='fs-6 mb-1'),
        html.P('⊙ 재생시간 : ' + str(df.loc[row, 'duration']) + '분', className='fs-6 mb-1'),    
        html.P('⊙ 조 회 수 : ' + df.loc[row, 'view_count'] + '회', className='fs-6 mb-1'),
        html.P('⊙ 게 시 일 : ' + df.loc[row, 'published_at'][:10], className='fs-6 mb-2')
    ])

    path = './assets/scripts/'
    script = df.loc[row, 'video_id'] + '.txt'

    if script in os.listdir(path):
        with open(path+script, 'r') as f:
            script_summary = f.read()
    else:
        get_summary(df.loc[row, 'video_id'])
        with open(path+script, 'r') as f:
            script_summary = f.read()

    summary = html.Div([
        html.Span('3줄 요약', className='fs-5 fw-bold'),
        html.Span(' by chatGPT+langchain', className='fs-5'),
        dcc.Markdown(script_summary, className='mt-3'),
    ])
    return video, meta, summary

## 순위 배지
@app.callback(
    Output('badge', 'children'),
    Input('inner-table', 'selected_rows'),
    Input('intermediate-df', 'data'))
def update_badge(row, data):
    df = pd.DataFrame(data) # 필터링된 중간 데이터를 데이터프레임으로 변환해서 사용
    row = 0 if not row else row[0] # row가 없으면 0, 있으면 row의 첫번째 값
    ranking = df.loc[row, 'ranking']
    button = dbc.Button(['HotTube ', dbc.Badge(ranking, color='light', text_color='danger', 
                                      className='ms-1 fw-bold'),' 위'], color='danger', className='mb-1', style={'width':'150px'})
    return button

### 앱 실행 섹션=====================================================================
if __name__ == '__main__':
    app.run_server()