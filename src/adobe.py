import json
import datetime
import jwt

from src.notify import teams, email
from src.helper import aws_read_ssm, bad_request, accepted_request, post_request, get_request
from src.validate import adobe_challenge_request, adobe_incoming_headers, adobe_signature
from src.config import JWT_ALGO, JWT_DURATION, JWT_URL, PRIVATE_KEY, TEAMS_WH, \
AIO_CLIENT_ID, AIO_CLIENT_SECRET, AIO_ORG_ID, TECHNICAL_ACCOUNT_ID, CLDMGR_URL, AUD_URL, EMAIL_TO

def main(event, context):
    print(json.dumps(event))

    if not adobe_incoming_headers(event):
        return bad_request()

    if adobe_challenge_request(event):
        return accepted_request(json.dumps(event['queryStringParameters']))

    if not adobe_signature(event):
        return bad_request()

    resp = process(event)
    return resp

def process(event):
    e = values(event)
    print("event_id: {} | event_code: {}".format(e["evid"], e["code"]))

    if e["code"] in ["pipeline_execution_start", "pipeline_execution_end", "pipeline_execution_step_waiting", "pipeline_execution_step_end"]:
        status = aio_cm_status("/".join(e["link"].split("/")[0:10]))
    elif e["code"] == "pipeline_execution_step_start":
        status = aio_cm_status(e["link"])
        if status['action'] == "deploy":
            status = aio_cm_status("/".join(e["link"].split("/")[0:10]))
        else:
            print("info: ignoring {} | {}".format(e["code"], status['action']))
            return accepted_request("Accepted. Ignored")
    else:
        print("unknown event_code {}".format(e["code"]))
        return accepted_request("Unknown Event")

    if not e["exid"] == status["id"]:
        return accepted_request("error: not latest execution")

    title = "ACM Pipeline | #{} | {}".format(e["exid"], status['status'])
    msg = "{} - {}\n\n".format(status['trigger'], status['artifactsVersion'])
    for i in status['_embedded']['stepStates']:
        if i['status'] != "NOT_STARTED":
            msg = msg + "\t{} - {} - {}\t- {} \n".format(i['stepId'], str(i.get('environment')).ljust(30), i['action'].ljust(20), i['status'])

    email(to=EMAIL_TO, subject=title, message=msg.replace("\n", "<br>"), status=status['status'])
    teams(url=TEAMS_WH, subject=title, message=msg, status=status['status'])
    return accepted_request("Accepted")

def values(event):
    try:
        body = json.loads(event['body'])
        link = body.get('event').get('activitystreams:object').get('@id')
        e = {
            "evid":event['headers'].get("x-adobe-event-id"),
            "code":event['headers'].get('x-adobe-event-code'),
            "body":body,
            "link":link,
            "exid":link.split("/")[9]
        }
    except json.decoder.JSONDecodeError as jerr:
        print("Json Error ", jerr)
        return None
    except KeyError as kerr:
        print("Key Error ", kerr)
        return None
    except IndexError as ierr:
        print("Index Error ", ierr)
        return None
    else:
        return e

def aio_generate_jwt(payload=None):
    if payload is None:
        payload = {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_DURATION),
            "iss": AIO_ORG_ID,
            "sub": TECHNICAL_ACCOUNT_ID,
            CLDMGR_URL: True,
            "aud": AUD_URL
        }

    try:
        private_key = str.encode(aws_read_ssm(PRIVATE_KEY))
        encoded = jwt.encode(payload, private_key, algorithm=JWT_ALGO)
    except ValueError as verr:
        print("Value Error ", verr)
        return None
    except TypeError as terr:
        print("Type Error ", terr)
        return None
    else:
        return encoded

def aio_generate_access_token():
    jwtencoded = aio_generate_jwt()
    url = JWT_URL
    data = {
        "client_id": AIO_CLIENT_ID,
        "client_secret": str.encode(aws_read_ssm(AIO_CLIENT_SECRET)),
        "jwt_token": str(jwtencoded, 'utf-8')
    }

    r = post_request(url=url, data=data)

    if r is None:
        print("could not connect, cannot continue")
        return None

    try:
        token = json.loads(r.text)['access_token']
    except json.decoder.JSONDecodeError as jerr:
        print("Json Error ", jerr)
        return None
    except KeyError as kerr:
        print("Key Error ", kerr)
        return None
    else:
        return token

def aio_cm_status(url):
    token = aio_generate_access_token()
    headers = {
        "x-gw-ims-org-id": AIO_ORG_ID,
        "x-api-key": AIO_CLIENT_ID,
        "Authorization": "Bearer {}".format(token)
    }
    r = get_request(url=url, headers=headers)

    if r is None:
        print("could not connect, cannot continue")
        return None
    else:
        return json.loads(r.text)

if __name__ == "__main__":
    event = {"test": "local"}
    resp = main(event, "")
    print(resp)
