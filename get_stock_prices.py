from datetime import datetime
import psycopg2
import flask


# 3rd party modules
from flask import make_response, abort


def connect_to_db():
    conn = psycopg2.connect(host="options-prices.cetjnpk7rvcs.us-east-1.rds.amazonaws.com", database="options_prices",
                            user="Stephen", password="password69")
    cur = conn.cursor()
    return cur, conn


def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))


def read_list(ticker):
    """
    This function responds to a request for /api/quotes/{ticker}
    with  a list of known contracts for that symbol
    :param ticker:   symbol of asset to find
    :return:       price data for that asset
    """
    # Does the person exist in people?
    cur, conn = connect_to_db()
    resultDict = []
    try:
        cur.execute("""SELECT pricedate, regularmarkettime, regularmarketprice  FROM qoutes WHERE symbol = %s ORDER BY pricedate;""",
                    (ticker.upper(),))
        result = cur.fetchall()
        print(result)
        print(len(result))
        print(cur.rowcount)
        for row in result:
            resultDict.append({'symbol': ticker, 'pricedate': row[0], 'regulardate': row[1], 'close': row[2],
                               'timestamp': get_timestamp()})
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
