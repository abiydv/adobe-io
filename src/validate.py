import json
import hmac
import base64
import hashlib

from src.helper import aws_read_ssm
from src.config import AIO_CLIENT_SECRET

def adobe_challenge_request(event):
    return bool('queryStringParameters' in event.keys() \
        and event['headers'].get('x-adobe-event-code') == 'challenge')

def adobe_incoming_headers(event):
    if not event.get('headers'):
        print(json.dumps(event))
        print("error: missing headers")
        return False
    elif not event['headers'].get("x-adobe-event-code")  \
      or not event['headers'].get("x-adobe-event-id")    \
      or not event['headers'].get("x-adobe-provider")    \
      or not event['headers'].get("x-adobe-signature"):
        print(json.dumps(event.get('headers')))
        print("error: missing headers")
        return False
    else:
        return True

def adobe_signature(event):
    if "body" not in event or "headers" not in event:
        print("missing header or body. cannot continue")
        return False
    else:
        actual = event['headers'].get("x-adobe-signature")
        body = event['body']
        key = aws_read_ssm(AIO_CLIENT_SECRET)
        if not comparehmac(actual, body, key):
            print("error: mismatch adobe signature")
            return False
        return True

def comparehmac(actual, body, key):
    generated = base64.b64encode(hmac.new(bytes(key, encoding='ascii'), bytes(body, encoding='ascii'), hashlib.sha256).digest()).decode()
    print("info: \n generated {} \n actual {} \n match? : {}".format(generated, actual, hmac.compare_digest(actual, generated)))
    return hmac.compare_digest(actual, generated)
