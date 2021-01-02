# provides helper functions

import boto3
import botocore
import requests
from src.config import REGION, EMAIL_FROM


def aws_read_ssm(name):
    try:
        ssm = boto3.client("ssm", region_name=REGION)
        parameter = ssm.get_parameter(Name=name, WithDecryption=True)
    except botocore.exceptions.ClientError as cerr:
        print("error_message: {}".format(cerr))
        return None
    else:
        return parameter["Parameter"]["Value"]


def aws_ses_send(to="", sub="", body=""):
    message = {
        "Subject": {"Data": sub, "Charset": "utf-8"},
        "Body": {"Html": {"Data": body, "Charset": "utf-8"}},
    }
    try:
        ses = boto3.client("ses", region_name=REGION)
        response = ses.send_email(
            Source=EMAIL_FROM,
            Destination=to,
            Message=message,
            ReplyToAddresses=[EMAIL_FROM],
        )
    except botocore.exceptions.ClientError as cerr:
        print("error_message: {}".format(cerr))
        return None
    except botocore.exceptions.ParamValidationError as p:
        print("error_message: {}".format(p))
        return None
    else:
        print(
            "{} - {}".format(
                response["ResponseMetadata"]["HTTPStatusCode"], response["MessageId"]
            )
        )
        return True


def bad_request():
    return {
        "statusCode": 400,
        "headers": {"content-type": "application/json"},
        "body": "Bad Request",
    }


def accepted_request(body):
    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": body,
    }


def post_request(url, **kwargs):
    try:
        r = requests.post(url, **kwargs, timeout=10)
        r.raise_for_status()
    except requests.exceptions.HTTPError as h:
        print("post_http_error: {}".format(h))
    except requests.exceptions.ConnectionError as c:
        print("post_connection_error: {}".format(c))
    except requests.exceptions.Timeout as t:
        print("post_timeout_error: {}".format(t))
    except Exception as err:
        print("post_unknown_error: {}".format(err))
    else:
        return r
    return None


def get_request(url, **kwargs):
    try:
        r = requests.get(url, **kwargs, timeout=10)
        r.raise_for_status()
    except requests.exceptions.HTTPError as h:
        print("get_http_error: {}".format(h))
    except requests.exceptions.ConnectionError as c:
        print("get_connection_error: {}".format(c))
    except requests.exceptions.Timeout as t:
        print("get_timeout_error: {}".format(t))
    except Exception as err:
        print("get_unknown_error: {}".format(err))
    else:
        return r
    return None


def head_request(url, headers):
    try:
        r = requests.head(url, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.exceptions.HTTPError as h:
        print("head_http_error: {}".format(h))
    except requests.exceptions.ConnectionError as c:
        print("head_connection_error: {}".format(c))
    except requests.exceptions.Timeout as t:
        print("head_timeout_error: {}".format(t))
    except Exception as err:
        print("head_unknown_error: {}".format(err))
    else:
        return r
    return None
