import mock

from .context import src

"""
adobe_challenge_request tests

"""


def test_adobe_challenge_request_true():
    challenge_event = {
        "headers": {"x-adobe-event-code": "challenge"},
        "queryStringParameters": "challenge=9634ec44-83a0-4cfa-a975-a8c913104596",
    }
    assert src.validate.adobe_challenge_request(challenge_event)


def test_adobe_challenge_request_false():
    not_challenge_event = {
        "headers": {"x-adobe-event-code": "random"},
        "queryStringParameters": "",
    }
    assert not src.validate.adobe_challenge_request(not_challenge_event)


"""
adobe_incoming_headers tests

"""


def test_no_adobe_incoming_headers():
    no_header = {"body": "content"}
    assert not src.validate.adobe_incoming_headers(no_header)


def test_invalid_adobe_incoming_headers():
    invalid_headers = {
        "headers": {"x-adobe-event-code": "random", "x-adobe-event-id": "step_start"}
    }
    assert not src.validate.adobe_incoming_headers(invalid_headers)


def test_valid_adobe_incoming_headers():
    valid_headers = {
        "headers": {
            "x-adobe-event-code": "pipeline_execution_start",
            "x-adobe-event-id": "917c7241",
            "x-adobe-provider": "adobe-io",
            "x-adobe-signature": "s1wg5Ja6k/1a7vC6Iu6mE",
        }
    }
    assert src.validate.adobe_incoming_headers(valid_headers)


"""
adobe_signature tests

"""


@mock.patch("src.validate.aws_read_ssm")
@mock.patch("src.validate.comparehmac")
def test_adobe_signature_valid(mock_comparehmac, mock_aws_read_ssm):
    mock_event = {
        "headers": {"x-adobe-signature": "valid_signature_string"},
        "body": "body",
    }
    mock_comparehmac.return_value = True
    mock_aws_read_ssm.return_value = "valid_signature_string"
    assert src.validate.adobe_signature(mock_event)


@mock.patch("src.validate.aws_read_ssm")
@mock.patch("src.validate.comparehmac")
def test_adobe_signature_invalid_hmac(mock_comparehmac, mock_aws_read_ssm):
    mock_event = {
        "headers": {"x-adobe-signature": "valid_signature_string"},
        "body": "body",
    }
    mock_comparehmac.return_value = False
    mock_aws_read_ssm.return_value = "valid_signature_string"
    assert not src.validate.adobe_signature(mock_event)


def test_adobe_signature_invalid_body():
    mock_event = {"headers": {"x-adobe-signature": "valid_signature_string"}}
    assert not src.validate.adobe_signature(mock_event)


"""
comparehmac tests

"""


def test_comparehmac_success():
    assert src.validate.comparehmac(
        "DmnMCtjpsHgz6vZAah8+EzUVnoECjM1nZ1zw34jJX4o=", "valid-string", "confidential"
    )


def test_comparehmac_fail():
    assert not src.validate.comparehmac(
        "randomstringtofailtest", "valid-string", "confidential"
    )
