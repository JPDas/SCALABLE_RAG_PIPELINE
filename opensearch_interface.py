from loguru import logger
from opensearchpy import OpenSearch, helpers

import os
import sys

logger.remove()
logger.add(sys.stdout, level=os.getenv("LOG_LEVEL", "INFO"))


def get_opensearch_cluster_client(index_name, host, port, user_id, password):
    opensearch_endpoint = host
    opensearch_client = OpenSearch(
        hosts=[{
            'host': opensearch_endpoint,
            'port': port
            }],
        http_auth=(user_id, password),
        verify_certs=False,
        index_name = index_name,
        )
    return opensearch_client
def check_opensearch_index(opensearch_client, index_name):
    return opensearch_client.indices.exists(index=index_name)

def create_index(opensearch_client, index_name):
    settings = {
        "settings": {
            "index": {
                "knn": True
                }
            }
        }
    response = opensearch_client.indices.create(index=index_name, body=settings)
    return bool(response['acknowledged'])

def create_index_mapping(opensearch_client, index_name):
    response = opensearch_client.indices.put_mapping(
        index=index_name,
        body={
            "properties": {
                "vector_field": {
                    "type": "knn_vector",
                    "dimension": 768,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "engine": "faiss",
                        "parameters": {
                            "ef_construction": 128,
                            "m": 24
                        }
                    }
                },
                "text": {
                    "type": "text",
                    "store": True
                },
                "metadata": {
                    "properties": {
                        "version" : {
                            "type" : "text",
                            "store": True
                        },
                        "document_name": {
                            "type" : "text",
                            "store": True
                        },
                        "page_number": {
                            "type" : "integer",
                            "store": True
                        },
                        "chunk_number": {
                            "type" : "integer",
                            "store": True
                        }
                    }                   
                }
            }
        }
    )
    return bool(response['acknowledged'])

def create_index_with_mapping(opensearch_client, index_name):
    """
    Creates the index with k-NN settings and full schema mappings 
    in a single atomic request to prevent 400 RequestErrors.
    """
    body = {
        "settings": {
            "index": {
                "knn": True  # Enables k-NN plugin for this index
            }
        },
        "mappings": {
            "properties": {
                "vector_field": {
                    "type": "knn_vector",
                    "dimension": 768,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "engine": "faiss",
                        "parameters": {
                            "ef_construction": 128,
                            "m": 24
                        }
                    }
                },
                "text": {
                    "type": "text",
                    "store": True
                },
                "metadata": {
                    "properties": {
                        "version" : {
                            "type" : "text",
                            "store": True
                        },
                        "document_name": {
                            "type" : "text",
                            "store": True
                        },
                        "page_number": {
                            "type" : "integer",
                            "store": True
                        },
                        "chunk_number": {
                            "type" : "integer",
                            "store": True
                        }
                    }                   
                }
            }
        }
    }
            
    response = opensearch_client.indices.create(index=index_name, body=body)
    return bool(response['acknowledged'])


def delete_opensearch_index(opensearch_client, index_name):
    logger.info(f"Trying to delete index {index_name}")
    try:
        response = opensearch_client.indices.delete(index=index_name)
        logger.info(f"Index {index_name} deleted")
        return response['acknowledged']
    except Exception as e:
        logger.info(f"Index {index_name} not found, nothing to delete")
        return True

def insert_doc(opensearch_client, index_name, docs, meta_datas, embeddings):

    chunk_count, success_count, failure_count = 0, 0, 0
    for doc, meta, vector in zip(docs, meta_datas, embeddings):

        
        # Add a document to the index.
        
        document = {
            'vector_field': vector,
            'metadata': meta,
            'text': doc
        }
        id = str(meta['document_name']) + "_" + str(meta['page_number']) + "_" + str(meta['chunk_number'])

        response = opensearch_client.index(
            index = index_name,
            body = document,
            id = id,
            refresh = True
        )
        
        chunk_count += 1
        
        logger.info(response)

        if response['result'] == 'created':
            success_count +=1
        else:
            failure_count +=1
    return success_count, failure_count

def insert_docs_bulk(opensearch_client, actions):
    actions = []
    
    success, failed = helpers.bulk(opensearch_client, actions)

    return success, failed