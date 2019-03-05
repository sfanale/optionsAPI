from datetime import datetime
import psycopg2
import json
from psycopg2.extras import RealDictCursor


# 3rd party modules
from flask import make_response, abort


def connect_to_db():
    conn = psycopg2.connect(host="options-prices.cetjnpk7rvcs.us-east-1.rds.amazonaws.com", database="options_prices",
                            user="Stephen", password="password69")
    cur = conn.cursor(cursor_factory=RealDictCursor)
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
    result = []
    try:
        cur.execute("""SELECT * FROM qoutes WHERE symbol = %s ORDER BY pricedate;""",
                    (ticker.upper(),))
        result = cur.fetchall()

    # otherwise, nope, not found
    except ValueError:
        abort(
            404, "asset with name {ticker} not found".format(ticker=ticker)
        )
    cur.close()
    conn.close()
    return result


def getMovers(direction):
    cur, conn = connect_to_db()
    cur.execute("""SELECT DISTINCT pricedate FROM QOUTES ORDER BY pricedate DESC""")
    last_date = str(int(cur.fetchall()[0]['pricedate']))
    if direction =='up':
        cur.execute("""SELECT * FROM qoutes WHERE regularmarketchangepercent!=0 AND marketcap > 10 AND pricedate= %s 
        ORDER BY regularmarketchangepercent DESC LIMIT 10;""", (last_date,))
    elif direction =='down':
        cur.execute("""SELECT * FROM qoutes WHERE regularmarketchangepercent!=0 AND marketcap > 10 AND pricedate = %s
                      ORDER BY regularmarketchangepercent ASC LIMIT 10; """, (last_date,))
    else:
        return direction
    return cur.fetchall()


def getIndustries():
    cur, conn = connect_to_db()
    cur.execute("""SELECT DISTINCT industry FROM assetinfo """)
    info = cur.fetchall()
    result = [i['industry'] for i in info]
    return result


def getSector():
    cur, conn = connect_to_db()
    cur.execute("""SELECT DISTINCT sector FROM assetinfo """)
    info = cur.fetchall()
    result = [i['sector'] for i in info]
    return result


def lambda_handler(event, context):
    op = event["queryStringParameters"]['operation']
    query = event["queryStringParameters"]['operand1']
    result = []
    if op == "read_list":
        result = read_list(query)
    elif op == "movers":
        result = getMovers(query)
    elif op == "industries":
        result = getIndustries()
    elif op == 'sectors':
        result = getSector()

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
