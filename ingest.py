import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# 환경 변수 로드 (.env 파일에서 API 키 등)
load_dotenv()

def ingest_docs():
    # 1. 문서 로드
    loader = TextLoader("./sample_data.txt", encoding="utf-8")
    documents = loader.load()
    
    # 2. 문서 분할 (Chunking)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    print(f"문서를 {len(chunks)}개의 청크로 분할했습니다.")

    # 3. 임베딩 및 벡터 DB 저장
    # API 키는 환경 변수 OPENAI_API_KEY에서 자동으로 로드됩니다.
    embeddings = OpenAIEmbeddings()
    
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db",  # 데이터 저장 경로
        collection_name="mindful_collection"
    )
    
    print("임베딩 및 벡터 DB 저장이 완료되었습니다. (./chroma_db)")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("오류: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("로컬 실행: .env 파일에 OPENAI_API_KEY를 설정하세요.")
        print("Streamlit Cloud: Settings > Secrets에 OPENAI_API_KEY를 추가하세요.")
    else:
        ingest_docs()

