from datetime import datetime
import psycopg2
import pandas as pd
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
    values = ticker.split('&')
    try:
        if values[1] == '' and values[2] == '':
            cur.execute(
                """SELECT DISTINCT contractsymbol, expiration, strike FROM prices WHERE underlyingsymbol = %s ORDER BY expiration;""",
                (values[0].upper(),))
        elif values[1] == '':
            cur.execute(
                """SELECT DISTINCT contractsymbol, expiration, strike FROM prices WHERE underlyingsymbol = %s  AND expiration > %s ORDER BY expiration;""",
                (values[0].upper(), values[2]))
        elif values [2] == '':
            cur.execute(
                """SELECT DISTINCT contractsymbol, expiration, strike FROM prices WHERE underlyingsymbol = %s AND strike = %s ORDER BY expiration;""",
                (values[0].upper(), values[1],))
        else:
            cur.execute(
                """SELECT DISTINCT contractsymbol, expiration, strike FROM prices WHERE underlyingsymbol = %s AND strike = %s AND expiration> %s ORDER BY expiration;""",
                (values[0].upper(), values[1], values[2]))

        result = cur.fetchall()
        for row in result:
            resultDict.append({'symbol': ticker, 'contractsymbol':row[0], 'expiry': row[1], 'strike': row[2]})
    # otherwise, nope, not found
    except ValueError:
        abort(
            404, "asset with name {ticker} not found".format(ticker=ticker)
        )
    cur.close()
    conn.close()

    return flask.jsonify(resultDict)


def read_one_all(ticker):
    """
    This function responds to a request for /api/options/all{ticker}
    with  matching assset from options database
    :param ticker:   symbol of asset to find
    :return:        assets matching symbol
    """
    # Does the person exist in people?
    print(get_timestamp())
    cur, conn = connect_to_db()
    resultDict = []
    print(get_timestamp())

    try:
        if ticker == "*":
            cur.execute("""SELECT pricedate, contractsymbol, expiration, strike, lastprice, optiontype,
          bid, ask, openinterest, volume, industry, sector FROM prices """,)
        else:
            cur.execute("""SELECT pricedate, contractsymbol, expiration, strike, lastprice, optiontype,
          bid, ask, openinterest, volume, industry, sector FROM prices WHERE underlyingsymbol = %s;""", (ticker.upper(),))
        result = cur.fetchall()
        for row in result:
            resultDict.append({'symbol': ticker, 'contractsymbol':row[1],'expiry': row[2], 'strike': row[3],
                               'lastprice': row[4], 'pricedate': row[0], 'optiontype':row[5], 'bid':row[6],
                               'ask' :row[7], 'openinterest':row[8], 'volume':row[9], 'industry':row[10], 'sector':row[11], 'timestamp': get_timestamp()})
    except ValueError:
        abort(
            404, "asset with name {ticker} not found".format(ticker=ticker)
        )
    cur.close()
    conn.close()
    return flask.jsonify(resultDict)


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
        cur.execute("""SELECT pricedate, expiration, strike, lastprice, underlyingsymbol, optiontype, bid, ask,
          openinterest, volume, industry, sector FROM prices WHERE contractsymbol = %s ORDER BY pricedate;""",
                    (contractsymbol.upper(),))
        result = cur.fetchall()
        for row in result:
            resultDict.append({'expiry': row[1], 'strike': row[2], 'lastprice': row[3],
                               'pricedate': row[0], 'symbol': row[4],  'bid': row[6],
                               'ask':row[7], 'openinterest': row[8], 'volume': row[9],
                               'industry': row[10], 'sectr': row[11],
                               'timestamp': get_timestamp(), 'optiontype': row[5]})
    # otherwise, nope, not found
    except ValueError:
        abort(
            404, "asset with name {sym} not found".format(sym=contractsymbol)
        )
    cur.close()
    conn.close()
    return flask.jsonify(resultDict)

def getAllTickers():
    """
        This function responds to a request for /api/options/getAllTickers
        with all tickers that have options
        :param
        :return:  all tickers
        """
    # Does the person exist in people?
    cur, conn = connect_to_db()
    resultDict = []
    try:
        cur.execute("""WITH RECURSIVE t AS (
   (SELECT underlyingsymbol FROM prices ORDER BY underlyingsymbol LIMIT 1)  -- parentheses required
   UNION ALL
   SELECT (SELECT underlyingsymbol FROM prices WHERE underlyingsymbol > t.underlyingsymbol ORDER BY underlyingsymbol LIMIT 1)
   FROM t
   WHERE t.underlyingsymbol IS NOT NULL
   )
SELECT underlyingsymbol FROM t WHERE underlyingsymbol IS NOT NULL;""")
        result = cur.fetchall()
        for row in result:
            resultDict.append(row[0])
    # otherwise, nope, not found
    except ValueError:
        abort(
            404, "not found"
        )
    cur.close()
    conn.close()
    return flask.jsonify(resultDict)
