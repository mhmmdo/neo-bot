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

import json

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

# Read File 

with open('./config.json') as json_file:
    config = json.load(json_file)


@client.event(MessageEv)
def on_message(client: NewClient, message: MessageEv):
    handler(client, message)

def handler(client: NewClient, message: MessageEv):
    text = message.Message.conversation or message.Message.extendedTextMessage.text
    msg = message.Message  # Access the 'Message' attribute
    msg_info = message.Info.MessageSource
    chat = message.Info.MessageSource.Chat
    prefix = config['prefix']
    log.info(message.__str__()) # debug msg
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

    isGroup = msg_info.IsGroup
    is_image = (message.Info.MediaType == "image")
    is_sticker = (message.Info.MediaType == "sticker")
    is_text = (message.Info.Type == "text")
    quoted_image = msg.extendedTextMessage.contextInfo.quotedMessage
    is_quoted_image = msg.extendedTextMessage.contextInfo.quotedMessage.imageMessage.mimetype == "image/jpeg"

    def reply(msg):
        client.reply_message(msg, quoted=message)

    if chats.startswith(prefix):
        args = chats[len(prefix):].split(' ')
        command = args[0].lower() if args else ''
        q = chats[len(command) + 1:]
        sender = msg_info.Sender.User
        is_owner = sender in config['ownerNumber']
        # log.info(is_QuotedMsg)

        author = config['waterMark']['author']
        pack_name = config['waterMark']['packName']

        match command:
            case "menu":
                txt = "Neo Bot WhatsApp\n\n"
                txt += "</ Command >\n"
                txt += "!menu <display menu>\n"
                txt += "!ping <check respon>\n"
                txt += "!sticker < media img/vid/gif to sticker >"
                client.send_message(chat, txt)

            case "ping":
                if len(args) < 2:
                    reply(f"Masukan Query\nContoh: {command} hai")
                else:
                    client.send_message(chat, q)

            case "cek":
                if isGroup:
                    if len(args) < 2:
                        reply(f"Masukan Query\nContoh: !{command} hai")
                    else:
                        client.send_message(chat, q)
                else:
                    reply("Command hanya bisa dilakukan di group")

            case "sticker":
                if is_image:
                    client.send_sticker(
                        chat,
                        client.download_any(message.Message, quoted_image),
                        quoted=message,
                        name=author,
                        packname=pack_name,
                    )
                elif is_quoted_image:
                    client.send_sticker(
                        chat,
                        client.download_any(quoted_image),
                        quoted=message,
                        name=author,
                        packname=pack_name,
                        )
                else:
                    reply("Tolong kirimkan atau reply media gambar/video/gif dengan caption !sticker")

            case "eval": #eval message
                if is_owner:
                    try:
                        evaled = eval(q)
                        if not isinstance(evaled, str):
                            evaled = str(evaled)
                        reply(f"{evaled}")
                    except Exception as e:
                        error_message = f'Error: {str(e)}'
                        reply(error_message)


            # for more example visit "https://github.com/krypton-byte/neonize/blob/master/examples/basic.py"


@client.event(PairStatusEv)
def PairStatusMessage(_: NewClient, message: PairStatusEv):
    log.info(f"logged as {message.ID.User}")

client.PairPhone(config['phone'], show_push_notification=True)
