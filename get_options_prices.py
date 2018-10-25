from datetime import datetime
import psycopg2

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

    try:
        cur.execute("""SELECT DISTINCT * FROM prices WHERE underlyingsymbol IS (%()s) """, ticker)
        result = cur.fetchall()
        print(result)
    # otherwise, nope, not found
    except ValueError:
        abort(
            404, "asset with name {ticker} not found".format(ticker=ticker)
        )
    cur.close()
    conn.close()
    return result

