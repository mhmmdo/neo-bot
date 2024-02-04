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
    text = message.Message.conversation or message.Message.extendedTextMessage.text
    chat = message.Info.MessageSource.Chat
    args = message.__str__()
    log.info('Someone Sending Msg : ', text)
    log.info('Log Chat : ', chat)
    match text:
    	case "ping":
    		client.send_message(chat, args)


@client.event(PairStatusEv)
def PairStatusMessage(_: NewClient, message: PairStatusEv):
    log.info(f"logged as {message.ID.User}")

client.connect()