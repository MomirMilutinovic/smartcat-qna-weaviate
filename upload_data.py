import weaviate
import os
import json

if __name__ == '__main__':
    auth_config = weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY"))

    client = weaviate.Client(
        url="https://smartcat-qna-demo-cluster-ecr5j21k.weaviate.network",
        auth_client_secret=auth_config,
        additional_headers={
            "X-HuggingFace-Api-Key": os.getenv("HUGGING_FACE_API_KEY")
        }
    )

    client.schema.delete_all()

    class_obj = {
        'class': 'Article',
        'vectorizer': 'text2vec-huggingface',
        'module-config': {
            'text2vec-huggingface': {
                'model': 'sentence-transformers/all-MiniLM-L6-v2',
                "options": {
                    "waitForModel": "true"
                }
            }
        }
    }

    client.schema.create_class(class_obj)

    with open('articles.json') as f:
        data = json.load(f)


    client.batch.configure(batch_size=10)
    with client.batch as batch:  # Initialize a batch process
        for i, d in enumerate(data):  # Batch import data
            print(f'importing article: {i + 1}')
            properties = {
                'title': d['title'],
                'text': d['text'],
            }
            batch.add_data_object(
                data_object=properties,
                class_name='Article'
            )

    response = (
        client.query
        .get('Article', ['title', 'text'])
        .with_near_text({"concepts": 'open job positions'})
        .with_limit(2)
        .do()
    )

    print(json.dumps(response, indent=4))