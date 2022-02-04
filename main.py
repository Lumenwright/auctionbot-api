from flask import Flask
from flask_restful import Api, reqparse
import json
import datetime
import firebase_admin
from firebase_admin import db

firebase_admin.initialize_app()
    # Get a database reference 
ref = db.reference(url=dc.DB_URL)

app = Flask(__name__)
api = Api(app)

DATE_FORMAT = "%b%d%y-%H%M%S"

"""
Arguments
Structure of bot command: !bid 10
https://basic-auction-bot.oa.r.appspot.com/bid?sender=$(sender)&bid=${1}
"""
SENDER = "sender"
BID = "bid"

"""
Endpoints
"""
BID_ENDPOINT = "/bid"
RESET_ENDPOINT = "/resetbid"

auction_history = []
current_largest_bid = 0.0

@app.route(BID_ENDPOINT)
def get():
    # get arguments of !bid command from bot
    parser = reqparse.RequestParser()
    parser.add_argument(SENDER)
    parser.add_argument(BID, required = True)
    args = parser.parse_args()

    # validate the arguments
    try:
        bid = float(args[BID])
    except:
        return "@"+args[SENDER]+" 's bid of "+args[BID]+" was not a number", 200

    # store sender bid in history
    auction_history.append({args[SENDER]: bid, "time":datetime.datetime.now().strftime(DATE_FORMAT)})

    # compare the bid argument with the current bid to see which is larger
    global current_largest_bid 
    current_largest_bid = bid if bid > current_largest_bid else current_largest_bid
# return success or fail message
    return "The current winning bid is: "+str(current_largest_bid)+" pounds", 200

@app.route(RESET_ENDPOINT)
def reset():
    save_history()
    global current_largest_bid
    current_largest_bid = 0.0
    s = "The auction has been reset."
    print(s)
    return s, 200

def save_history():
    with open("history_"+datetime.datetime.now().strftime(DATE_FORMAT)+".json", 'w') as f:
        json.dump(auction_history, f)

if(__name__=="__main__"):
    app.run()
