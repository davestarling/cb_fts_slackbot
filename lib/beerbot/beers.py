from slackbot.bot import respond_to
from slackbot.bot import listen_to
from lib.couchbase.cb import CB
from couchbase.fulltext import MatchQuery, MatchPhraseQuery, DisjunctionQuery
import json
import re
import time


@respond_to('Find beers called (.*)', re.IGNORECASE)
def find_beers_called(message, terms):
    """ Finds beers by their name """

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

    search = cb.fts_search('fts_idx_beers', query)
    results = cb.process_fts_result(search)

    out = format_beer_results(results, terms)

    message.send_webapi('', json.dumps(out))


def format_beer_results(results, term):
    """
    Formats beers results for Slack

    :param results:
    :param term:
    :return:
    """

    out = [{
        "color": "#36a64f",
        "author_name": "BeerBot",
        "title": "There are {length} beer results for {term}".format(length=results['total_hits'],
                                                                     term=term),
        "footer": "BeerBot",
        "ts": time.time()
    }]

    if len(results['rows']) > 0:

        out[0]['text'] = "Here are the first {row_count}:".format(row_count=len(results['rows']))

        for key, row in results['rows'].iteritems():
            doc = row['doc']

            fields = []
            if doc.get('category'):
                fields.append({
                        "title": "Category",
                        "value": doc.get('category'),
                        "short": True
                })

            if doc.get('style'):
                fields.append({
                        "title": "Style",
                        "value": doc.get('style'),
                        "short": True
                })

            out.append({
                "color": "#36a64f",
                "title": doc.get("name"),
                "fields": fields
            })

    return out
