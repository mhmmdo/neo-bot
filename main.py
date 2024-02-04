import logging
import os
import signal
import sys
from datetime import timedelta

import magic

from neonize.client import NewClient

from neonize.events import (
    ConnectedEv,
    MessageEv,
    PairStatusEv,
    event,
    ReceiptEv,
    CallOfferEv,
)
from neonize.proto.def_pb2 import ImageMessage
from neonize.types import MessageServerID
from neonize.utils import log
from neonize.utils.enum import ReceiptType
from neonize.utils.jid import JIDToNonAD

sys.path.insert(0, os.getcwd())


def interrupted(*_):
    event.set()


log.setLevel(logging.DEBUG)
signal.signal(signal.SIGINT, interrupted)


client = NewClient("db.sqlite3")


@client.event(ConnectedEv)
def on_connected(_: NewClient, __: ConnectedEv):
    log.info("⚡ Connected")


@client.event(ReceiptEv)
def on_receipt(_: NewClient, receipt: ReceiptEv):
    log.debug(receipt)


@client.event(CallOfferEv)
def on_call(_: NewClient, call: CallOfferEv):
    log.debug(call)


@client.event(MessageEv)
def on_message(client: NewClient, message: MessageEv):
    handler(client, message)

def handler(client: NewClient, message: MessageEv):
	msg = message.Info # .__str__()
    # text = msg.Message.conversation or message.Message.extendedTextMessage.text
    from = msg.MessageSource.Chat
    msg_message_keys = list(msg['message'].keys())
    type = msg_message_keys[0]
    chats = ""
	if type == 'conversation' and 'conversation' in msg['Message']:
	    chats = msg['message']['conversation']
	elif type == 'imageMessage' and 'imageMessage' in msg['Message'] and 'caption' in msg['Message']['imageMessage']:
	    chats = msg['Message']['imageMessage']['caption']
	elif type == 'documentMessage' and 'documentMessage' in msg['Message'] and 'caption' in msg['Message']['documentMessage']:
	    chats = msg['Message']['documentMessage']['caption']
	elif type == 'videoMessage' and 'videoMessage' in msg['Message'] and 'caption' in msg['Message']['videoMessage']:
	    chats = msg['Message']['videoMessage']['caption']
	elif type == 'extendedTextMessage' and 'extendedTextMessage' in msg['Message'] and 'text' in msg['Message']['extendedTextMessage']:
	    chats = msg['Message']['extendedTextMessage']['text']
    isGroup = msg.isGroup
    log.info(msg.Chat.User)
    log.info(chats)
    # log.info("")
    match text:
    	case "ping":
    		client.send_message(from, "Pong")


@client.event(PairStatusEv)
def PairStatusMessage(_: NewClient, message: PairStatusEv):
    log.info(f"logged as {message.ID.User}")

client.connect()