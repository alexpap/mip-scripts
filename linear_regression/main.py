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

    payload = [{"name": "x", "value": "DX_bl*APOE4_bl+AGE+PTEDUCAT+PTGENDER"}, {"name": "y", "value": "AV45_bl"}, {"name": "showtable", "desc":"", "value": "TotalResults"}, {"name": "format", "desc": "", "value": "false"}]
    logging.info(payload)
    url = 'http://%s:%s/mining/query/WP_LINEAR_REGRESSION' % (host, port)
    logging.info("Submit LR %s ..." % url)
    response = requests.post(url, stream=True)
    if response.status_code != 200:
        raise Exception("Interval error")
    lines = response.iter_lines()
    schema = json.loads(next(lines))
    result = json.loads(next(lines))
    logging.debug(result)
    lr = json.loads(result[0])

    try:
        resultfp = open(os.path.join(outputdir, "response.json"), 'a+')
        resultfp.write(json.dump(lr, sort_keys=True, indent=4, separators=(',', ': ')))
    except Exception, ex:
        logging.error("Unable to store variables", ex)
    finally:
        try:
            if resultfp:
                resultfp.close()
        except:
            logging.error("Unable to close response.json", ex)

except Exception, e:
    import traceback

    traceback.print_exc()
    # os.removedirs(outputdir)
    logging.error(e)
