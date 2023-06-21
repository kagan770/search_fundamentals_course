# WARNING: this will silently delete both of your indexes

# Specify the opensearch host and port
OPENSEARCH_HOST="https://localhost"
OPENSEARCH_PORT="9200"

# Send a GET request to Opensearch
curl -s -k -XGET -u admin:admin "$OPENSEARCH_HOST:$OPENSEARCH_PORT" > /dev/null

# Check the status code returned by curl
if [ $? -ne 0 ]; then
    echo "Opensearch Server is not running."
    exit 1
fi

echo "Deleting products"
curl -k -X DELETE -u admin:admin  "$OPENSEARCH_HOST:$OPENSEARCH_PORT/bbuy_products"
echo ""
echo "Deleting queries"
curl -k -X DELETE -u admin:admin  "$OPENSEARCH_HOST:$OPENSEARCH_PORT/bbuy_queries"

