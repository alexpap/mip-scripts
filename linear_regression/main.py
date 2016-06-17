#!/usr/bin/env python

import argparse
import datetime
import json
import logging
import os
import requests

LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR
}

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
            prog="variables_profiling",
            description="Variables Profiling",
            version="0.1"
    )
    parser.add_argument('--host', action='store', dest='host')
    parser.add_argument('--port', action='store', dest='port')
    parser.add_argument('--log', action='store', dest='level')
    parser.add_argument('--dir', action='store', dest='dir')

    try:
        args = parser.parse_args()
    except IOError, msg:
        parser.error(msg)

    level = LEVELS.get(args.level, logging.INFO)
    logging.basicConfig(level=level)

    if args.host:
        host = args.host
    else:
        host = "0.0.0.0"
    logging.debug("Host : %s" % host)

    if args.port:
        port = args.port
    else:
        port = "9090"
    logging.debug("PORT : %s" % port)

    if args.dir:
        outputdir = args.dir
    else:
        dt = datetime.datetime.now()
        outputdir = os.path.join("/tmp/mip-scripts-lr/",
                                 datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    logging.debug("OUTPUT DIR : %s" % outputdir)

    try:
        url = 'http://%s:%s/mining/algorithms.json' % (host, port)
        logging.info("Listing algorithms %s ..." % url)
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Interval error")
        logging.info("#Algorithms : %d" % len(response.json()))

        payload = [
            {"name":"groupings","desc":"","value":"DX_bl,APOE4_bl"},
            {"name":"covariables","desc":"","value":"AGE,PTEDUCAT,PTGENDER"},
            {"name":"variable","desc":"","value":"AV45_bl"}
        ]
        payload = []
        logging.debug(payload)
        url = 'http://%s:%s/mining/query/WP_LINEAR_REGRESSION' % (host, port)
        logging.info(" Linear Regression %s ..." % (url))
        response = requests.post(url, json=payload, stream=True)
        if response.status_code != 200:
            raise Exception("Interval error")

        # # original
        # oresultfp = open(os.path.join(resultpath, "response.original.json"), 'a+')
        # try:
        #
        #     oresultfp.write(json.dumps(profile, sort_keys=True, indent=4, separators=(',', ': ')))
        # finally:
        #     if oresultfp:
        #         oresultfp.close()

        # specs
        resultfp = open(os.path.join(outputdir, "response.json"), 'a+')
        try:
            resultfp.write(json.dumps(response.json(), sort_keys=True, indent=4, separators=(',', ': ')))
            logging.info("Response stored.")
        finally:
            if resultfp:
                resultfp.close()

    except Exception, e:
        import traceback

        traceback.print_exc()
        # os.removedirs(outputdir)
        logging.error(e)
