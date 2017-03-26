from slackbot.bot import respond_to
from slackbot.bot import listen_to
from lib.couchbase.cb import CB, CB_Connection_Exception
from couchbase.fulltext import MatchQuery, MatchPhraseQuery, TermQuery, \
    DisjunctionQuery, BooleanQuery, PrefixQuery, TermFacet
import json
import re
import time


@respond_to('Find breweries in (.*)', re.IGNORECASE)
def find_breweries_in(message, location):
    """ Finds breweries in a specific location - searches city and state """

    cb = CB()

    match_queries = [
        MatchQuery(location, field="city"),
        MatchQuery(location, field="state")
    ]

    query = DisjunctionQuery(*match_queries)

    search = cb.fts_search('fts_idx_brewery_by_location', query)
    results = cb.process_fts_result(search)

    out = format_brewery_results(results, location)

    message.send_webapi('', json.dumps(out))


@respond_to('Find breweries with (.*)', re.IGNORECASE)
def find_breweries(message, terms):
    """ Finds breweries based on their description and name """

    cb = CB()

    match_queries = []

    # If there is more than one word in the terms then create match phrase queries and boost them
    if len(terms.split()) > 1:
        match_queries += [
            MatchPhraseQuery(terms, field="name", boost=3),
            MatchPhraseQuery(terms, field="description", boost=3)
        ]

    # Create match queries for all terms
    for q in terms.split():
        match_queries += [
            MatchQuery(q, field="description"),
            MatchQuery(q, field="name")
        ]

    query = DisjunctionQuery(*match_queries)

    search = cb.fts_search('fts_idx_breweries', query)
    results = cb.process_fts_result(search)

    out = format_brewery_results(results, terms)

    message.send_webapi('', json.dumps(out))


@respond_to('Find breweries called (.*)', re.IGNORECASE)
def find_breweries_called(message, terms):
    """ Finds breweries by their name """

    cb = CB()

    match_queries = []

    # If there is more than one word in the terms then create match phrase queries and boost them
    if len(terms.split()) > 1:
        match_queries += [
            MatchPhraseQuery(terms, field="name", boost=3),
        ]

    # Create match queries for all terms
    for q in terms.split():
        match_queries += [
            MatchQuery(q, field="name")
        ]

    query = DisjunctionQuery(*match_queries)

    search = cb.fts_search('fts_idx_breweries', query)
    results = cb.process_fts_result(search)

    out = format_brewery_results(results, terms)

    message.send_webapi('', json.dumps(out))


def format_brewery_results(results, term):
    """
    Formats brewery results for Slack

    :param results:
    :param term:
    :return:
    """

    out = [{
        "color": "#36a64f",
        "author_name": "BeerBot",
        "title": "There are {length} brewery results for {term}".format(length=results['total_hits'],
                                                                        term=term),
        "text": "Here are the first {row_count}".format(row_count=len(results['rows'])),
        "footer": "BeerBot",
        "ts": time.time()
    }]

    for key, row in results['rows'].iteritems():
        out.append({
            "color": "#36a64f",
            "title": row['doc'].get("name"),
            "text": row['doc'].get("description")
        })

    return out
