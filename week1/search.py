#
# The main search hooks for the Search Flask application.
#
import json
from flask import (
    Blueprint, redirect, render_template, request, url_for
)

from opensearch_helper import get_client

bp = Blueprint('search', __name__, url_prefix='/search')


# Process the filters requested by the user and return a tuple that is appropriate for use in: the query, URLs displaying the filter and the display of the applied filters
# filters -- convert the URL GET structure into an OpenSearch filter query
# display_filters -- return an array of filters that are applied that is appropriate for display
# applied_filters -- return a String that is appropriate for inclusion in a URL as part of a query string.  This is basically the same as the input query string
def process_filters(filters_input):
    # Filters look like: &filter.name=regularPrice&regularPrice.key={{ agg.key }}&regularPrice.from={{ agg.from }}&regularPrice.to={{ agg.to }}
    filters = []
    display_filters = []  # Also create the text we will use to display the filters that are applied
    applied_filters = ""
    for filter in filters_input:
        type = request.args.get(filter + ".type")
        display_name = request.args.get(filter + ".displayName", filter)
        applied_filters += "&filter.name={}&{}.type={}&{}.displayName={}".format(filter, filter, type, filter,
                                                                                 display_name)
        if type == "range":
            from_val = request.args.get(filter + ".from", None)
            to_val = request.args.get(filter + ".to", None)
            print("from: {}, to: {}".format(from_val, to_val))
            # we need to turn the "to-from" syntax of aggregations to the "gte,lte" syntax of range filters.
            to_from = {}
            if from_val and from_val != "*":
                to_from["gte"] = from_val
            else:
                from_val = "*"  # set it to * for display purposes, but don't use it in the query
            if to_val and to_val != "*":
                to_from["lt"] = to_val
            else:
                to_val = "*"  # set it to * for display purposes, but don't use it in the query
            the_filter = {"range": {filter: to_from}}
            filters.append(the_filter)
            display_filters.append("{}: {} TO {}".format(display_name, from_val, to_val))
            applied_filters += "&{}.from={}&{}.to={}".format(filter, from_val, filter, to_val)
        elif type == "terms":
            field = request.args.get(filter + ".fieldName", filter)
            key = request.args.get(filter + ".key", None)
            the_filter = {"term": {field: key}}
            filters.append(the_filter)
            display_filters.append("{}: {}".format(display_name, key))
            applied_filters += "&{}.fieldName={}&{}.key={}".format(filter, field, filter, key)
    print("Filters: {}".format(filters))
    return filters, display_filters, applied_filters


# Our main query route.  Accepts POST (via the Search box) and GETs via the clicks on aggregations/facets
@bp.route('/query', methods=['GET', 'POST'])
def query():
    opensearch = get_client() # Load up our OpenSearch client from the opensearch_helper.py file.
    # Put in your code to query opensearch.  Set error as appropriate.
    error = None
    user_query = None
    query_obj = None
    display_filters = None
    applied_filters = ""
    filters = None
    sort = "_score"
    sortDir = "desc"
    if request.method == 'PUT':
        redirect(url_for("index"))
    if request.method == 'DELETE':
        redirect(url_for("index"))
    if request.method == 'POST':  # a query has been submitted
        user_query = request.form['query']
        if not user_query:
            user_query = "*"
        sort = request.form["sort"]
        if not sort:
            sort = "_score"
        sortDir = request.form["sortDir"]
        if not sortDir:
            sortDir = "desc"
        query_obj = create_query(user_query, [], sort, sortDir)
    elif request.method == 'GET':  # Handle the case where there is no query or just loading the page
        user_query = request.args.get("query", "*")
        filters_input = request.args.getlist("filter.name")
        sort = request.args.get("sort", sort)
        sortDir = request.args.get("sortDir", sortDir)
        if filters_input:
            (filters, display_filters, applied_filters) = process_filters(filters_input)
        query_obj = create_query(user_query, filters, sort, sortDir)
    else:
        query_obj = create_query("*", [], sort, sortDir)
    print("query: {}".format(str(query_obj)).replace("\'", "\"").replace(" ",""))

    try:
        response = opensearch.search(index='bbuy_products', body=query_obj)
        json_response = json.dumps(response)  # indent for pretty printing
        print("response: {}".format(json_response.replace("\n","").replace(" ","")))
    except Exception as e:
        error = str(e)
        print(error)
        response = None

    if error is None:
        return render_template("search_results.jinja2", query=user_query, search_response=response,
                               display_filters=display_filters, applied_filters=applied_filters,
                               sort=sort, sortDir=sortDir)
    else:
        redirect(url_for("index"))


def create_query(user_query, filters, sort="_score", sortDir="desc"):
    print("Query: {} Filters: {} Sort: {}".format(user_query, filters, sort))
    # fixme: research the regular price data
    # fixme: research the unknown images.
    query_obj = {
        'size': 10,
        "query": {
            "bool": {
                "must": {
                    "query_string": {
                        "query": user_query,
                        "fields": ["name", "shortDescription", "longDescription"],
                        "phrase_slop": 3},
                }
                # ,"filter": filters
            },
        },
        "aggs": {
            "regularPrice": {"range": {
                    "field": "regularPrice",
                             "ranges": [
                                {"to": 20.0},
                                 {"from": 20.0, "to": 300.0},
                                 {"from": 30.0, "to": 40.0},
                                 {"from": 40.0, "to": 50.0},
                                 {"from": 50.0, "to": 60.0},
                                 {"from": 60.0, "to": 70.0},
                                 {"from": 70.0, "to": 80.0},
                                 {"from": 80.0, "to": 90.0},
                                 {"from": 90.0, "to": 100.0},
                                 {"from": 100.0, "to": 200.0},
                                {"from": 200.0, "to": 300.0},
                                {"from": 300.0, "to": 400.0},
                                {"from": 400.0, "to": 500.0},
                                {"from": 500.0}
                            ]
                }},
            "department": {
                "terms": {
                    "field": "department.keyword"
                }},
            "missing_images": {
                "missing": {
                    "field": "image.keyword"
                }}},
        "highlight": {
            "fields": {"name": {},"shortDescription": {},"longDescription": {}
            }
        },
        "sort": [{sort: {"order": sortDir}},{"name.keyword": {"order": sortDir}}]
    }
    return query_obj
