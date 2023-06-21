# From Dmitiriy Shvadskiy https://github.com/dshvadskiy/search_with_machine_learning_course/blob/main/index_queries.py
import configparser
from opensearchpy import OpenSearch

def get_opensearch():
    # Load the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Get properties from the file
    host = config.get('OpenSearch', 'host')
    port = config.getint('OpenSearch', 'port')
    username = config.get('OpenSearch', 'username')
    password = config.get('OpenSearch', 'password')
    use_ssl = config.getboolean('OpenSearch', 'use_ssl')
    verify_certs = config.getboolean('OpenSearch', 'verify_certs')
    ssl_assert_hostname = config.getboolean('OpenSearch', 'ssl_assert_hostname')
    ssl_show_warn = config.getboolean('OpenSearch', 'ssl_show_warn')
    http_compress = config.getboolean('OpenSearch', 'http_compress')

    # Check if properties exist and if not, set to None
    client_cert = config.get('OpenSearch', 'client_cert') if config.has_option('OpenSearch', 'client_cert') else None
    client_key = config.get('OpenSearch', 'client_key') if config.has_option('OpenSearch', 'client_key') else None
    ca_certs = config.get('OpenSearch', 'ca_certs') if config.has_option('OpenSearch', 'ca_certs') else None

    # Initialize the OpenSearch client
    return OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_auth=(username, password),
        use_ssl=use_ssl,
        verify_certs=verify_certs,
        ssl_assert_hostname=ssl_assert_hostname,
        ssl_show_warn=ssl_show_warn,
        http_compress=http_compress,  # enables gzip compression for request bodies
        client_cert=client_cert,
        client_key=client_key,
        ca_certs=ca_certs
    )