


https://github.com/MomirMilutinovic/smartcat-qna-weaviate/assets/40830508/fc7b0b52-d174-418e-848c-bade5c06abe0



# smartcat-qna-weaviate
A RAG chatbot that answers questions about [SmartCat](https://smartcat.io).

The chatbot bases its answers on the articles on the company's website. The pages are scraped, chunked and stored in a [Weaviate](https://github.com/weaviate/weaviate) vector database beforehand. The pages are fed to a [Cohere](https://cohere.com) LLM to generate the answers to the questions.

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
1. Start up Weaviate: `docker compose up -d`. Once completed, Weaviate is running on [`http://localhost:9999`]().
2. Download the pages from  [SmartCat](https://smartcat.io)'s website:
```
scrapy runspider src/ingestion/smartcat_spider.py -O articles.json
```
3. Upload the pages into Weaviate: `python src/ingestion/upload_data.py`
4. Start the Streamlit app: `streamlit run src/streamlit/app.py`. The app should be running on [`http://localhost:8501`]() once it starts up.

## Limitations
- Even though the chatbot queries the Weaviate database before it generates its answer, it may include inaccurate information in its answers.
- The chatbot may disregard instructions in its system prompt in longer conversations

These problems likely stem from the way pages are stored in the database and presented to the LLM. The LLM receives chunks of possibly disparate pages. Firstly, these chunks may contain insufficient information. Secondly, they could also confuse the LLM as they are not cohesive.

Fetching entire pages may improve the chatbot's performance.

## Disclaimer
This project is not affiliated with SmartCat in any way. It should not be used as a source of truth for any information about SmartCat.
