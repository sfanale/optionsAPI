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
    This function responds to a request for /api/options/{ticker}
    with  a list of known contracts for that symbol
    :param ticker:   symbol of asset to find
    :return:        list of known contracts matching symbol
    """
    # Does the person exist in people?
    cur, conn = connect_to_db()
    resultDict = []
    try:
        cur.execute("""SELECT DISTINCT contractsymbol FROM prices WHERE underlyingsymbol = %s ORDER BY contractsymbol;""", (ticker.upper(),))
        result = cur.fetchall()
        print(result)
        print(len(result))
        print(cur.rowcount)
        for row in result:
            resultDict.append({'symbol': ticker, 'contractsymbol':row[0]})
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


def read_one_all(ticker):
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
        cur.execute("""SELECT pricedate, contractsymbol, expiration, strike, lastprice, optiontype, bid, ask FROM prices WHERE underlyingsymbol = %s;""", (ticker.upper(),))
        result = cur.fetchall()
        print(result)
        print(len(result))
        print(cur.rowcount)

        for row in result:
            resultDict.append({'symbol': ticker, 'contractsymbol':row[1],'expiry': row[2], 'strike': row[3], 'lastprice': row[4],
                               'pricedate': row[0], 'optiontype':row[5], 'bid':row[6], 'ask' :row[7], 'timestamp': get_timestamp()})
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


def read_one_symbol(contractsymbol):
    """
        This function responds to a request for /api/options/detail/{contractsymbol}
        with  matching assset from options database
        :param ticker:   symbol of asset to find
        :return:        assets matching symbol
        """
    # Does the person exist in people?
    cur, conn = connect_to_db()
    resultDict = []
    try:
        cur.execute("""SELECT pricedate, expiration, strike, lastprice, underlyingsymbol, optiontype FROM prices WHERE contractsymbol = %s ORDER BY pricedate;""",
                    (contractsymbol.upper(),))
        result = cur.fetchall()
        print(result)
        print(len(result))
        print(cur.rowcount)
        for row in result:
            resultDict.append({'expiry': row[1], 'strike': row[2], 'lastprice': row[3],
                               'pricedate': row[0], 'symbol': row[4], 'timestamp': get_timestamp(), 'optiontype': row[5]})
    # otherwise, nope, not found
    except ValueError:
        abort(
            404, "asset with name {sym} not found".format(sym=contractsymbol)
        )
    cur.close()
    conn.close()
    print(resultDict)
    print(len(resultDict))
    return flask.jsonify(resultDict)

