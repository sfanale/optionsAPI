from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import flask
import json
# 3rd party modules
from flask import make_response, abort
import time


def connect_to_db():
    conn = psycopg2.connect(host="options-prices.cetjnpk7rvcs.us-east-1.rds.amazonaws.com", database="options_prices",
                            user="Stephen", password="password69")
    cur = conn.cursor(cursor_factory=RealDictCursor)
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
    values = ticker.split(':')
    try:
        cur.execute("""SELECT DISTINCT pricedate FROM QOUTES ORDER BY pricedate DESC""")
        last_date = str(int(cur.fetchall()[0]['pricedate']))
        print(last_date)
        if values[1] == '' and values[2] == '':
            cur.execute(
                """SELECT DISTINCT contractsymbol, expiration, strike, optiontype, lastprice FROM prices WHERE 
                underlyingsymbol = %s and pricedate = %s ORDER BY expiration;""",(values[0].upper(), last_date))
        elif values[1] == '':
            cur.execute(
                """SELECT DISTINCT contractsymbol, expiration, strike, optiontype, lastprice FROM prices WHERE 
              underlyingsymbol = %s  AND expiration > %s AND pricedate = %s ORDER BY expiration;""", (values[0].upper(), values[2], last_date))
        elif values [2] == '':
            cur.execute(
                """SELECT DISTINCT contractsymbol, expiration, strike, optiontype, lastprice FROM prices WHERE
                underlyingsymbol = %s AND strike = %s AND pricedate= %s ORDER BY expiration;""",
                (values[0].upper(), values[1], last_date))
        else:
            cur.execute(
                """SELECT DISTINCT contractsymbol, expiration, strike, optiontype, lastprice FROM prices WHERE
                underlyingsymbol = %s AND strike = %s AND expiration> %s AND pricedate = %s ORDER BY expiration;""",
                (values[0].upper(), values[1], values[2], last_date))

        result = cur.fetchall()

        # otherwise, nope, not found
    except ValueError:
        abort(
            404, "asset with name {ticker} not found".format(ticker=ticker)
        )
    cur.close()
    conn.close()

    return result


def read_one_all(ticker):
    """
    This function responds to a request for /api/options/all{ticker}
    with  matching assset from options database
    :param ticker:   symbol of asset to find
    :return:        assets matching symbol
    """
    # Does the person exist in people?
    cur, conn = connect_to_db()
    result = []

    try:
        if ticker == "*":
            cur.execute("""SELECT * FROM prices """,)
        else:
            cur.execute("""SELECT * FROM prices WHERE underlyingsymbol = %s;""", (ticker.upper(),))
        result = cur.fetchall()

    except ValueError:
        abort(
            404, "asset with name {ticker} not found".format(ticker=ticker)
        )
    cur.close()
    conn.close()
    return result


def read_one_symbol(contractsymbol, pricetype):
    """
        This function responds to a request for /api/options/detail/{contractsymbol}
        with  matching assset from options database
        :param ticker:   symbol of asset to find
        :return:        assets matching symbol
        """
    # Does the person exist in people?
    cur, conn = connect_to_db()
    result = []
    try:
        cur.execute("""SELECT * FROM prices WHERE contractsymbol = %s and pricetype= %s ORDER BY pricedate;""",
                    (contractsymbol.upper(), pricetype))
        result = cur.fetchall()

    except ValueError:
        abort(
            404, "asset with name {sym} not found".format(sym=contractsymbol)
        )
    cur.close()
    conn.close()
    return result

def getAllTickers():
    """
        This function responds to a request for /api/options/getAllTickers
        with all tickers that have options
        :param
        :return:  all tickers
        """
    cur, conn = connect_to_db()
    result = []
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

    # otherwise, nope, not found
    except ValueError:
        abort(
            404, "not found"
        )
    cur.close()
    conn.close()
    return result

def getAllContracts():
    """
        This function responds to a request for /api/options/getAllTickers
        with all tickers that have options
        :param
        :return:  all tickers
        """
    cur, conn = connect_to_db()
    result = []
    try:
        cur.execute("""WITH RECURSIVE t AS (
   (SELECT contractsymbol FROM prices ORDER BY contractsymbol LIMIT 1)  -- parentheses required
   UNION ALL
   SELECT (SELECT contractsymbol FROM prices WHERE contractsymbol > t.contractsymbol ORDER BY contractsymbol LIMIT 1)
   FROM t
   WHERE t.contractsymbol IS NOT NULL
   )
SELECT contractsymbol FROM t WHERE contractsymbol IS NOT NULL;""")
        result = cur.fetchall()

    # otherwise, nope, not found
    except ValueError:
        abort(
            404, "not found"
        )
    cur.close()
    conn.close()
    return result


def getByIndustry(industry):
    """

    :param industry:
    :return:
    """
    cur, conn = connect_to_db()
    result = []
    try:
        cur.execute("""SELECT * FROM prices WHERE industry = %s;""", (industry,))
        result = cur.fetchall()

    # otherwise, nope, not found
    except ValueError:
        abort(
            404, "not found"
        )
    cur.close()
    conn.close()
    return result


def getBySector(sector):
    """

    :param industry:
    :return:
    """
    cur, conn = connect_to_db()
    result = []
    try:
        cur.execute("""SELECT * FROM prices WHERE sector = %s;""", (sector,))
        result = cur.fetchall()

    # otherwise, nope, not found
    except ValueError:
        abort(
            404, "not found"
        )
    cur.close()
    conn.close()
    return result


def lambda_handler(event, context):
    op = event["queryStringParameters"]['operation']
    ticker = event["queryStringParameters"]['operand1']
    info = event["queryStringParameters"]['operand2']
    result = []
    if op == "read_list":
        result = read_list(ticker)
    elif op == "get_all_by_ticker":
        result = read_one_all(ticker)
    elif op == "get_one_contract":
        result = read_one_symbol(ticker, info)
    elif op == "get_all_tickers":
        result = getAllTickers()
    elif op == "get_all_contracts":
        result = getAllContracts()
    elif op == "get_by_industry":
        result = getByIndustry(ticker)
    elif op == "get_by_sector":
        result = getBySector(ticker)
    else:
        return {
            'statusCode': 500,
            'body': json.dumps(op)
        }
    return {
        'statusCode': 200,
        'body': json.dumps(result),
        'headers': {"Access-Control-Allow-Origin": "*"}
    }

