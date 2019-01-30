from datetime import datetime
import psycopg2
import json
import flask
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
    resultDict = []
    try:
        cur.execute("""SELECT ask, asksize, averagedailyvolume10day, averagedailyvolume3month, bid,
      bidsize, bookvalue, currency, dividenddate, earningstimestamp, earningstimestampend, 
      earningstimestampstart, epsforward, epstrailing12months, esgpopulated, exchange, exchangedatadelayedby,
      exchangetimezonename, exchangetimezoneshortname, fiftydayaverage, fiftydayaveragechange, 
      fiftydayaveragechangepercent, fiftytwoweekhigh, fiftytwoweekhighchange, fiftytwoweekhighchangepercent,
      fiftytwoweeklow, fiftytwoweeklowchange, fiftytwoweeklowchangepercent, fiftytwoweekrange, 
      financialcurrency, forwardpe, fullexchangename, gmtoffsetmilliseconds, language, longname, 
      market, marketcap, marketstate, messageboardid, postmarketchange, postmarketchangepercent, 
      postmarketprice, postmarkettime, pricehint, pricetobook, quotesourcename, quotetype, region,
      regularmarketchange, regularmarketchangepercent, regularmarketdayhigh, regularmarketdaylow, 
      regularmarketdayrange, regularmarketopen, regularmarketpreviousclose, regularmarketprice, 
      regularmarkettime, regularmarketvolume, sharesoutstanding, shortname, sourceinterval, symbol, 
      tradeable, trailingannualdividendrate, trailingannualdividendyield, trailingpe, twohundreddayaverage, 
      twohundreddayaveragechange, twohundreddayaveragechangepercent, pricedate FROM qoutes WHERE symbol = %s ORDER BY pricedate;""",
                    (ticker.upper(),))
        result = cur.fetchall()
        print(json.dumps(result, indent=2))

        #for row in result:
           # resultDict.append({'ask': ticker, 'pricedate': row[0], 'volume': row[1], 'close': row[2],
                              # 'timestamp': get_timestamp()})
    # otherwise, nope, not found
    except ValueError:
        abort(
            404, "asset with name {ticker} not found".format(ticker=ticker)
        )
    cur.close()
    conn.close()
    return flask.jsonify(result)
