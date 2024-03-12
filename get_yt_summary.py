

from youtube_transcript_api import YouTubeTranscriptApi
from langchain import OpenAI, PromptTemplate
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.text_splitter import TokenTextSplitter
import tiktoken
from dotenv import load_dotenv

def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
        text = " ".join([line["text"] for line in transcript])  
    except:
        text = '해당 영상은 자막을 제공하지 않습니다.'
    return text

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def get_summary(video_id):
    ## 기본 설정
    model_name = "gpt-3.5-turbo" 
    temperature = 0.1
    model_max_tokens = 16385
    verbose = True  
    load_dotenv() # .env 파일로부터 api key(OPENAI_API_KEY)를 가져옴
    
    ## 비디오의 자막을 가져옴
    script = get_video_transcript(video_id)
    
    ## 스크립트를 청크 단위로 분리
    splitter = TokenTextSplitter(chunk_size=model_max_tokens)
    split_script = splitter.split_text(script)

    docs = [Document(page_content=t) for t in split_script] # text를 Document 객체로 변환

    ## 프롬프트 생성
    prompt_template = """ 다음을 3개의 간결한 문장으로 요약해주세요 :

    {text}

    각 문장은 불릿으로 구분하고, 한국어로 작성해 주세요"""

    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

    ## 토큰의 갯수에 따라 요약 모델을 선택
    llm = ChatOpenAI(temperature=temperature, model_name=model_name) # ChatOpenAI 객체 생성
    
    num_tokens = num_tokens_from_string(script, model_name)

    if num_tokens < model_max_tokens:
        chain = load_summarize_chain(llm, chain_type='stuff', prompt=prompt, verbose=verbose)
    else:
        chain = load_summarize_chain(llm, chain_type='map_reduce', combine_prompt=prompt, verbose=verbose)

    ## 요약 실행 및 결과를 path에 video_id.txt로 저장      
    summary = chain.run(docs)
    path = './assets/scripts/'
    path += video_id + '.txt'
    with open(path, 'w') as f:
        f.write(summary)
        



