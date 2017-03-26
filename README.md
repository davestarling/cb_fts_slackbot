# Couchbase Full-Text Search Slackbot

This is an example for building a Slackbot that can interface with Couchbase's FTS service, using the beer-sample bucket.

Will expand on this README shortly, but for now you can just:

    chmod a+x bot.py

then run:

    ./bot.py -e development -s "{your Slack Bot User's API token}"

You will also need to create the FTS indexes in Couchbase using the JSON definitions in `fts_indexes`

![alt text](http://d10g.io/wp-content/uploads/2017/03/beerbot.gif)