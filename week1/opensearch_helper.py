from flask import g

from opensearch_client import get_opensearch


# Create an OpenSearch client instance and put it into Flask shared space for use by the application
def get_client():
    if 'opensearch' not in g:
        client = get_opensearch()
        return client