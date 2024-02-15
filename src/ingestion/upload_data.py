import itertools
from typing import List

import weaviate
import weaviate.classes.config as wvcc
import json
import re


def get_chunks_fixed_size_with_overlap(text: str, chunk_size: int, overlap_size: int) -> List[str]:
    """
    Splits the text into chunks of a fixed word count with overlap.
    :param text: The text to be split into chunks.
    :param chunk_size: The size of the chunks.
    :param overlap_size: The size of the overlap.
    :return: A list of chunks.
    """
    source_text = re.sub(r"\s+", " ", text)  # Remove multiple whitespaces
    text_words = re.split(r"\s", source_text)  # Split text by single whitespace

    chunks = []
    for i in range(0, len(text_words), chunk_size):  # Iterate through & chunk data
        chunk = " ".join(text_words[max(i - overlap_size, 0): i + chunk_size])  # Join a set of words into a string
        chunks.append(chunk)
    return chunks

def get_chunks_by_delimiter_with_minimum_size(text: str, delimiter_regex: str = '\n{7,}', minimum_size=125) -> List[str]:
    """
    Splits the text into chunks of a minimum word count by a delimiter.
    :param text: The text to be split into chunks.
    :param delimiter_regex: The delimiter regex.
    :param minimum_size: The minimum size of the chunks.
    :return: A list of chunks.
    """
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

def chunk(article: dict) -> List[str]:
    """
    Chunks the article into smaller parts.
    :param article: The article to be chunked.
    :return: A list of chunks.
    """
    if len(article['sections']) > 1:
        return itertools.chain.from_iterable(get_chunks_by_delimiter_with_minimum_size(section) for section in article['sections'])

    return get_chunks_fixed_size_with_overlap(article['text'], 125, 25)

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

    chunked_articles = [
        {
            'title': article['title'],
            'chunk': text_chunk,
            'chunk_index': chunk_i
        }
        for article in data
        for chunk_i, text_chunk in enumerate(chunk(article))
    ]

    unique_chunks = []
    for chunk in chunked_articles:
        if chunk['chunk'] not in [c['chunk'] for c in unique_chunks]:
            unique_chunks.append(chunk)
        else:
            print('Duplicate chunk:', chunk['chunk'])

    with collection.batch.dynamic() as batch:
        for chunk in unique_chunks:
            batch.add_object(
                properties=chunk,
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
