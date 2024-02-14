import itertools
from typing import List

import weaviate
import weaviate.classes.config as wvcc
import json
import re


def get_chunks_fixed_size_with_overlap(text: str, chunk_size: int, overlap_size: int) -> List[str]:
    source_text = re.sub(r"\s+", " ", text)  # Remove multiple whitespaces
    text_words = re.split(r"\s", source_text)  # Split text by single whitespace

    chunks = []
    for i in range(0, len(text_words), chunk_size):  # Iterate through & chunk data
        chunk = " ".join(text_words[max(i - overlap_size, 0): i + chunk_size])  # Join a set of words into a string
        chunks.append(chunk)
    return chunks

def get_chunks_by_delimiter_with_minimum_size(text: str, delimiter_regex: str = '\n{7,}', minimum_size=100) -> List[str]:
    delimiter_chunks = re.split(delimiter_regex, text)
    delimiter_chunks = [re.sub(r"\s+", " ", chunk) for chunk in delimiter_chunks]

    chunks = []
    current_chunk = ''
    for chunk in delimiter_chunks:
        if current_chunk != '':
            current_chunk += ' '
        current_chunk += chunk
        if len(current_chunk.split(' ')) >= minimum_size:
            chunks.append(current_chunk)
            current_chunk = ''

    if len(current_chunk) > 0:
        chunks.append(current_chunk)

    return chunks

def chunk(article):
    if len(article['sections']) > 1:
        return itertools.chain.from_iterable(get_chunks_by_delimiter_with_minimum_size(section) for section in article['sections'])

    return get_chunks_fixed_size_with_overlap(article['text'], 100, 20)

if __name__ == '__main__':
    client = weaviate.connect_to_custom(
        http_host="localhost",
        http_port="9999",
        http_secure=False,
        grpc_host="localhost",
        grpc_port="50051",
        grpc_secure=False,
    )

    client.collections.delete("Article")

    collection = client.collections.create(
        name="Article",
        vectorizer_config=wvcc.Configure.Vectorizer.text2vec_transformers(),
        generative_config=wvcc.Configure.Generative.cohere(),
        properties=[
            wvcc.Property(name="title", data_type=wvcc.DataType.TEXT),
            wvcc.Property(name="chunk", data_type=wvcc.DataType.TEXT),
            wvcc.Property(name="chunk_index", data_type=wvcc.DataType.INT, skip_vectorization=True)
        ]
    )

    with open('articles.json') as f:
        data = json.load(f)

    with collection.batch.dynamic() as batch:
        for i, article in enumerate(data):
            print(f'importing article: {i + 1}', article['title'])
            for chunk_i, text_chunk in enumerate(chunk(article)):
                properties = {
                    'title': article['title'],
                    'chunk': text_chunk,
                    'chunk_index': chunk_i
                }
                batch.add_object(
                    properties=properties,
                )
                print('=' * 30)
                print('Imported chunk:', text_chunk)

    print('Testing if data was imported correctly with a query: open job positions')
    response = collection.query.near_text(
        query="open job positions",
        limit = 2
    )

    for o in response.objects:
        print(o.properties)
