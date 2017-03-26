from slackbot.bot import respond_to
from slackbot.bot import listen_to
from lib.couchbase.cb import CB, CB_Connection_Exception
from couchbase.fulltext import MatchQuery, MatchPhraseQuery, TermQuery, \
    DisjunctionQuery, BooleanQuery, PrefixQuery, TermFacet
import json
import re
import time


@respond_to('test my couchbase connection', re.IGNORECASE)
def cb_test(message):
    """ Tests the configuration Couchbase connection """

    try:
        cb = CB()
        cb.create_connection()

        message.reply('I can connect to Couchbase!')
        # react with thumbs up emoji
        message.react('+1')
    except CB_Connection_Exception:
        message.reply('I cannot connect to Couchbase')
        # react with thumbs down emoji
        message.react('-1')
    except:
        raise
