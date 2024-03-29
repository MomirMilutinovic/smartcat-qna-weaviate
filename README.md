

https://github.com/MomirMilutinovic/smartcat-qna-weaviate/assets/40830508/197121dc-15fa-4232-9af9-a9a20387509d


# smartcat-qna-weaviate
A RAG chatbot that answers questions about [SmartCat](https://smartcat.io), an AI company based in Novi Sad, Serbia.

The chatbot bases its answers on articles scraped from SmartCat's website. The web pages are chunked and stored in a [Weaviate](https://github.com/weaviate/weaviate) vector database. Pages relevant to the user's question are fetched based on a hybrid search over chunks and entire pages. The resulting pages are fed to a [Cohere](https://cohere.com) LLM to generate an answer to the user's question.

## Prerequisites
- Docker 
- Docker Compose
- Python

## Setup instructions

1. **Install virtualenv** (if not already installed):
```
pip install virtualenv
```
2. **Create a virtual environment**:
```
virtualenv <name_of_environment>
```
3. **Activate the virtual environment**:
```
source <name_of_virtualenv>/bin/activate
```
4. **Install the necessary Python packages**:
```
pip install -r requirements.txt
```
5. **Export Cohere API Key**:
```
export COHERE_API_KEY=<your_cohere_api_key>
```
## Usage instructions
1. Start up Weaviate: `docker compose up -d`. Once completed, Weaviate will run on [`http://localhost:9999`]().
2. Download the pages from  [SmartCat](https://smartcat.io)'s website:
```
scrapy runspider src/ingestion/smartcat_spider.py -O articles.json
```
3. Upload the pages into Weaviate: `python src/ingestion/upload_data.py`
4. Start the Streamlit app: `streamlit run src/streamlit/app.py`. The app should be running on [`http://localhost:8501`]() once it starts up.

## Limitations
Parts of the chatbot's answers may be inaccurate.

## Disclaimer
This project is not affiliated with SmartCat in any way. It should not be used as a source of truth for any information about SmartCat.
