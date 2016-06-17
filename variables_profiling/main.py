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
        outputdir = os.path.join("/tmp/mip-scripts-vp/",
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

        url = 'http://%s:%s/mining/query/WP_LIST_VARIABLES' % (host, port)
        logging.info("Listing variables %s ..." % url)
        response = requests.post(url, stream=True)
        if response.status_code != 200:
            raise Exception("Interval error")

        variables = response.json()['variables']
        logging.info("'#Variables : %d" % len(variables))
        logging.debug(variables)
        try:
            variablesfp = open(os.path.join(outputdir, "variables.json"), 'a+')
            json.dump(variables, variablesfp)
        except Exception, ex:
            logging.error("Unable to store variables", ex)
        finally:
            try:
                if variablesfp:
                    variablesfp.close()
            except:
                logging.error("Unable to close variables.json", ex)

        for variable in variables:

            var = variable[0]
            profile = []
            payload = [{"name": "variable", "value": var}, {"name": "format", "value": "True"}]
            logging.debug(payload)
            url = 'http://%s:%s/mining/query/WP_VARIABLE_SUMMARY' % (host, port)
            logging.info(" Summary Statistics %s variable %s ..." % (var, url))
            response = requests.post(url, json=payload, stream=True)
            if response.status_code != 200:
                raise Exception("Interval error")
            profile.append(response.json())

            if variable[1] != "text":

                payload = [{"name": "column1", "value": var}, {"name": "nobuckets", "value": "10"}, {"name": "format", "value": "True"}]
                logging.info(payload)
                url = 'http://%s:%s/mining/query/WP_VARIABLE_HISTOGRAM' % (host, port)
                logging.info(" Dataset Statistics %s variable %s ..." % (var, url))
                response = requests.post(url, json=payload, stream=True)
                if response.status_code != 200:
                    raise Exception("Interval error")
                profile.append(response.json())

                byvars = ["DX_bl", "AGE", "PTGENDER", "APOE"]
                for byvar in byvars:

                    logging.info(" Dataset Statistics %s - %s variable ..." % (var, byvar))
                    payload = [
                        {"name": "column1", "value": var},
                        {"name": "column2", "value": byvar},
                        {"name": "nobuckets", "value": "10"},
                        {"name": "format", "value": "True"}
                    ]
                    logging.info(payload)
                    url = 'http://%s:%s/mining/query/WP_VARIABLES_HISTOGRAM' % (host, port)
                    response = requests.post(url, json=payload, stream=True)
                    logging.info(" Dataset Statistics %s - %s variable %s ..." % (var, byvar, url))
                    if response.status_code != 200:
                        raise Exception("Interval error")
                    profile.append(response.json())

            # logging.info(profile)
            # # original
            resultpath = os.path.join(outputdir, var)
            os.makedirs(resultpath)
            # oresultfp = open(os.path.join(resultpath, "response.original.json"), 'a+')
            # try:
            #
            #     oresultfp.write(json.dumps(profile, sort_keys=True, indent=4, separators=(',', ': ')))
            # finally:
            #     if oresultfp:
            #         oresultfp.close()

            # specs
            resultfp = open(os.path.join(resultpath, "response.json"), 'a+')
            try:
                resultfp.write(json.dumps(profile, sort_keys=True, indent=4, separators=(',', ': ')))
                logging.info("Response stored.")
            finally:
                if resultfp:
                    resultfp.close()

    except Exception, e:
        import traceback

        traceback.print_exc()
        # os.removedirs(outputdir)
        logging.error(e)
