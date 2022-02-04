from flask import Flask
from flask_restful import Api, reqparse
import json
import datetime
import firebase_admin
from firebase_admin import db
import dont_commit as dc

firebase_admin.initialize_app()
    # Get a database reference 
ref = db.reference(url=dc.DB_URL)

app = Flask(__name__)
api = Api(app)

DATE_FORMAT = "%b%d%y-%H%M%S"

auction_history = []
current_largest_bid = 0.0

@app.route(dc.BID_ENDPOINT)
def get():
    # get arguments of !bid command from bot
    parser = reqparse.RequestParser()
    parser.add_argument(dc.SENDER)
    parser.add_argument(dc.BID, required = True)
    args = parser.parse_args()

    # validate the arguments
    try:
        bid = float(args[dc.BID])
    except:
        return "@"+args[dc.SENDER]+" 's bid of "+args[dc.BID]+" was not a number", 200

    # store sender bid in history
    #auction_history.append({args[SENDER]: bid, "time":datetime.datetime.now().strftime(DATE_FORMAT)})
    ref.child(dc.BIDS).update({args[dc.SENDER]: bid, "time":datetime.datetime.now().strftime(DATE_FORMAT)})

    # compare the bid argument with the current bid to see which is larger
    global current_largest_bid 
    current_largest_bid = bid if bid > current_largest_bid else current_largest_bid
# return success or fail message
    return "The current winning bid is: "+str(current_largest_bid)+" pounds", 200

@app.route(dc.RESET_ENDPOINT)
def reset():
    AUTH = "auth"
    #authorize
    parser = reqparse.RequestParser()
    parser.add_argument(AUTH)
    args = parser.parse_args()
    token = args[AUTH]

    if token != dc.TOKEN:
        return "unauthorized", 401

    save_history()
    global current_largest_bid
    current_largest_bid = 0.0
    s = "The auction has been reset."
    print(s)
    return s, 200

def save_history():
   # with open("history_"+datetime.datetime.now().strftime(DATE_FORMAT)+".json", 'w') as f:
    #    json.dump(auction_history, f)
    bids = ref.child(dc.BIDS).get()
    ref.child(dc.HISTORY).push(bids)
    ref.child(dc.BIDS).delete()

if(__name__=="__main__"):
    app.run()
