import threading
import time
from collections import defaultdict
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import configparser

import firebase_admin
from firebase_admin import firestore, credentials

config = configparser.ConfigParser()
config.read("config.ini")

line_bot_api = LineBotApi(config.get("line-bot", "channel_access_token"))
handler = WebhookHandler(config.get("line-bot", "channel_secret"))

# Used to save the authorized user
authorized_ID_dict = defaultdict(str)
reversed_authorized_ID_dict = defaultdict(list)
running = True


def reply_message(reply_token, msg):
    line_bot_api.reply_message(reply_token, TextSendMessage(text=msg))


def send_direct_message(user_id, msg):
    line_bot_api.push_message(user_id, TextSendMessage(text=msg))


def check_database_anomaly(firestore_client):
    global running
    collection = firestore_client.collection(u"anomaly")
    while running:
        # Obtain data first
        docs = collection.stream()

        for data in docs:
            # Check error and send message to user if necessary
            error = data.to_dict()["error"]
            if error:
                notify_id = reversed_authorized_ID_dict[data.id]
                for single_id in notify_id:
                    send_direct_message(single_id, "Error detected!🆘")
                    collection.document(data.id).set({"error": False})
        time.sleep(10)


def set_password(reply_token, password, user_id):
    reversed_authorized_ID_dict[password].append(user_id)
    authorized_ID_dict[user_id] = password
    reply_message(reply_token, "Token is successfully activated!")


def clear_user_information(reply_token, user_id):
    reversed_authorized_ID_dict[authorized_ID_dict[user_id]].remove(user_id)
    del authorized_ID_dict[user_id]
    message = [TextSendMessage(text="Password is reset. Please input your new password.")]
    line_bot_api.reply_message(reply_token, message)


def check_database_token(cur_message):
    if not firebase_admin._apps:
        cred = credentials.Certificate("service_account.json")
        firebase_admin.initialize_app(cred)

    docs = firestore.client().collection(u"machines").stream()
    for data in docs:
        if cur_message in data.to_dict()["id"]:
            return True
    return False


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    cur_user_id = event.source.user_id
    cur_message = event.message.text

    if cur_user_id not in authorized_ID_dict:
        # Add user if user enter the correct password/token
        if not check_database_token(cur_message):
            reply_message(event.reply_token, "Token not found. Please try again")
        else:
            set_password(event.reply_token, cur_message, cur_user_id)
    else:
        if cur_message == "set password":
            clear_user_information(event.reply_token, cur_user_id)


# Firebase authorization
cred = credentials.Certificate("service_account.json")
firebase_admin.initialize_app(cred)
firestore_client = firestore.client()

# Threading for check the database and send message to user if needed
check_database_thread = threading.Thread(
    target=check_database_anomaly, args=(firestore_client,), daemon=True)
check_database_thread.start()

app = Flask(__name__)


@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return "OK"


if __name__ == "__main__":
    app.run()
