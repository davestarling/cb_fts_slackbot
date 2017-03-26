#!/usr/bin/env python

from lib.options import Options

import logging.config
import lib
import os
import daemon.pidfile
import argparse
import importlib


def start_bot():
    """Starts the Slack Bot"""
    from slackbot.bot import Bot

    bot = Bot()
    bot.run()


if __name__ == "__main__":

    environments = [
        'development'
    ]

    parser = argparse.ArgumentParser(description="Runs the Couchbase FTS Slackbot")
    parser.add_argument("-e", "--environment", help="The environment in which the slackbot is run (" + ', '.join(environments) + ")")
    parser.add_argument("-s", "--slackapikey", help="The Slack API key")
    parser.add_argument("-p", "--pidfile", help="PID file for daemonisation")

    args = parser.parse_args()

    # validate environment
    if args.environment not in environments:
        exit('Environment is mandatory, and must be one of: ' + ', '.join(environments))

    # validate num workers (< cpu count)

    lib.config_path = os.path.dirname(os.path.realpath(__file__)) + "/conf/" + args.environment + ".cfg"
    lib.options = Options(lib.config_path, args.environment)

    if args.slackapikey:
        lib.options.set('slackbot', 'api_token', args.slackapikey)

    c = importlib.import_module('conf.logging.' + args.environment)
    logging.config.dictConfig(c.LOG_CONF)

    if args.pidfile is not None:
        with daemon.DaemonContext(umask=0o002,
                                  pidfile=daemon.pidfile.PIDLockFile(args.pidfile)):
            start_bot()
    else:
        start_bot()
