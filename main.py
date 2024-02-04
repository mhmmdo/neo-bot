# Neo Python Bot WhatsApp

# Use lib Neonize
# https://github.com/krypton-byte/neonize

# Thanks to :
# https://github.com/krypton-byte

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
    msg = message.Message  # Access the 'Message' attribute
    chat = message.Info.MessageSource.Chat
    prefix = "!"
    # log.info(message__str__()) debug msg
    # Check the type of the message
    if msg.conversation:
        chats = msg.conversation
    elif msg.imageMessage and msg.imageMessage.caption:
        chats = msg.imageMessage.caption
    elif msg.documentMessage and msg.documentMessage.caption:
        chats = msg.documentMessage.caption
    elif msg.videoMessage and msg.videoMessage.caption:
        chats = msg.videoMessage.caption
    elif msg.extendedTextMessage and msg.extendedTextMessage.text:
        chats = msg.extendedTextMessage.text
    else:
        chats = ""

    if chats.startswith(prefix):
        args = chats[len(prefix):].split(' ')
        command = args[0].lower() if args else ''

        # is_group = message.isGroup
        log.info(message.__str__())
        log.info(chats)
        match command:
            case "menu":
                txt = "Neo Bot WhatsApp\n\n"
                txt += "</ Command >\n"
                txt += "!menu\n"
                txt += "!ping\n"
                txt += "!sticker < media img/vid/gif to sticker >"
                client.send_message(chat, txt)
            case "ping":
                client.send_message(chat, "Pong")
            case "sticker":
                if message.Info.Type == "media":
                    client.send_sticker(
                        chat,
                        client.download_any(message.Message),
                        quoted=message,
                        name="@Neo Bot WhatsApp",
                        packname="@mhmmdoo_",
                    )
                else:
                    client.reply_message("Tolong kirimkan media gambar/video/gif dengan caption !sticker", quoted=message)

            # for more example visit "https://github.com/krypton-byte/neonize/blob/master/examples/basic.py"


@client.event(PairStatusEv)
def PairStatusMessage(_: NewClient, message: PairStatusEv):
    log.info(f"logged as {message.ID.User}")

client.connect()
