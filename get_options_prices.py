from datetime import datetime
import psycopg2
import flask


# 3rd party modules
from flask import make_response, abort


def connect_to_db():
    conn = psycopg2.connect(host="localhost", database="options_prices", user="postgres", password="mypassword")
    cur = conn.cursor()
    return cur, conn


def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))


def read_one(ticker):
    """
    This function responds to a request for /api/options/{ticker}
    with  matching assset from options database
    :param ticker:   symbol of asset to find
    :return:        assets matching symbol
    """
    # Does the person exist in people?
    cur, conn = connect_to_db()
    resultDict = []
    try:
        cur.execute("""SELECT pricedate, expiration, strike, lastprice FROM prices WHERE underlyingsymbol = 'AAPL';""")
        result = cur.fetchall()
        print(result)
        print(len(result))
        print(cur.rowcount)
        for row in result:
            resultDict.append({'symbol': ticker, 'expiry': row[1], 'strike': row[2], 'lastprice': row[3],
                               'pricedate': row[0], 'timestamp': get_timestamp()})
    # otherwise, nope, not found
    except ValueError:
        abort(
            404, "asset with name {ticker} not found".format(ticker=ticker)
        )
    cur.close()
    conn.close()
    print(resultDict)
    print(len(resultDict))
    return flask.jsonify(resultDict)
    #print(flask.jsonify(resultDict[0:3]))
    #return resultDict[0:3]

