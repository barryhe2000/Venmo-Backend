import json
import sqlite3
from flask import Flask, request
import db

DB = db.DatabaseDriver()
app = Flask(__name__)

def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code

@app.route("/api/users/")
def get_users():
    return success_response(DB.get_all_users())

@app.route("/api/users/", methods=["POST"])
def create_user():
    body = json.loads(request.data)
    name = body.get("name")
    username = body.get("username")
    balance = body.get("balance")
    if balance is None:
        balance = 0
    user_id = DB.insert_users_table(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is not None:
        return success_response(user, 201)
    return failure_response("failed to create user")

@app.route("/api/user/<int:user_id>/")
def get_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("user not found")
    user["transactions"] = DB.get_txns_of_user(user_id)
    return success_response(user)

@app.route("/api/transactions/", methods=["POST"])
def create_transaction():
    body = json.loads(request.data)
    sender = body.get("sender_id")
    receiver = body.get("receiver_id")
    amount = body.get("amount")
    message = body.get("message")
    accepted = body.get("accepted")
    sender_money = DB.get_user_by_id(sender).get("balance")-amount
    if accepted == True and sender_money < 0:
        return failure_response("can't overdraw balance")
    receiver_money = DB.get_user_by_id(receiver).get("balance")+amount
    try:
        txn_id = DB.insert_txn_table(sender, receiver, amount, message, accepted)
        txn = DB.get_txn(txn_id)
        if accepted == True:
            DB.update_user_by_id(sender, sender_money)
            DB.update_user_by_id(receiver, receiver_money)
        if txn is not None:
            return success_response(txn, 201)
        return failure_response("transaction not found")
    except sqlite3.IntegrityError:
        return json.dumps({'success': False, 'error': "id not found!"}), 404

@app.route("/api/transaction/<int:txn_id>/", methods=["POST"])
def payment_req(txn_id):
    body = json.loads(request.data)
    accepted = body.get("accepted")
    t = DB.get_txn(txn_id)
    sender = t.get("sender_id")
    receiver = t.get("receiver_id")
    amount = t.get("amount")
    if t.get("accepted") == None:
        DB.update_txn_by_id(txn_id, accepted)
        DB.update_time(txn_id)
        if accepted == True:
            sender_money = DB.get_user_by_id(sender).get("balance")-amount
            receiver_money = DB.get_user_by_id(receiver).get("balance")+amount
            DB.update_user_by_id(sender, sender_money)
            DB.update_user_by_id(receiver, receiver_money)
    else:
        return failure_response("transaction already acted on")
    return success_response(DB.get_txn(txn_id),201)

@app.route("/api/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user is not None:
        DB.delete_user_by_id(user_id)
        return success_response(user)
    return failure_response("user not found")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
