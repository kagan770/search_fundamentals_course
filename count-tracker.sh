# A simple loop that can be run to check on counts for our two indices as you are indexing.  Ctrl-c to get out.

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

while [ true ];
do
  queries_count=$(curl -s -k -XGET -u admin:admin  "$OPENSEARCH_HOST:$OPENSEARCH_PORT/_cat/count/bbuy_queries" | awk '{print $3}')
  products_count=$(curl -s -k -XGET -u admin:admin  "$OPENSEARCH_HOST:$OPENSEARCH_PORT/_cat/count/bbuy_products" | awk '{print $3}')
  echo "Queries:"$queries_count
  echo "Products:"$products_count
  echo ""
  sleep 5;
done