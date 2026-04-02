`langchain`: RAG 파이프라인 전체를 좀 편하게 다루기 위한 기본 프레임워크다.
- 문서 처리
- 체인 구성
- retriever 연결
- prompt 연결

`langchain-community`: LangChain에서 외부 연동 기능들을 모아둔 패키지다. 문서로더나 벡터스토어 쪽에서 자주 필요하다.
`langchain-ollama`: 로컬 Ollama 모델 연결용이다.

---
`faiss-cpu`: 벡터 검색 DB이다. 문서 chunk를 임베딩한 뒤 저장하고, 질문과 유사한 chunk를 찾을 때 쓴다.
`sentence-transformers`: 임베딩 모델용이다. 문서를 벡터로 바꾸는 역할을 한다.
`transformers`: 임베딩 모델이나 Hugging Face 계열 모델을 다룰 때 내부적으로 자주 필요하다.
`torch`: `sentence-transformers`가 내부적으로 많이 사용한다. 설치 환경에 따라 자동으로 잡히기도 하지만, 명시해두는 편이 안전하다.

---
`pypdf`: PDF문서 읽기용이다. `data/raw/`에 PDF 넣고 불러올 떄 사용한다.
`python-dotenv`: `.env`파일에서 환경변수를 읽기 위해 쓴다.
- 모델명
- 데이터 경로
- chunk size
- top-k 설정

`tqdm`: 문서가 많을 때 진행률 표시용이다. 임베딩 생성할 때 꽤 유용하다.

---
`pytest`: 테스트 코드 실행용이다.
`ipykernel`: `notebooks/experiments.ipynb` 사용할 거면 넣는게 편하다.