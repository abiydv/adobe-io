import json
import mock
import moto
import boto3
import pytest
import unittest
import requests

from .context import src
from src.config import REGION, EMAIL_FROM

"""
reusable mock_response method

"""
def mock_response(status=200,content="CONTENT",text="TEXT",json_data=None,raise_for_status=None):
    mock_resp = mock.Mock()
    mock_resp.raise_for_status = mock.Mock()
    
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status

    mock_resp.status_code = status
    mock_resp.content = content
    mock_resp.text = text

    if json_data:
        mock_resp.json = mock.Mock(return_value=json_data)
    
    return mock_resp

def test_bad_request():
    mock_resp = { "statusCode": 400, "headers": {"content-type": "application/json"}, "body": "Bad Request" }
    assert src.helper.bad_request() == mock_resp

def test_accepted_request():
    mock_body = "valid_request"
    mock_resp = { "statusCode": 200, "headers": {"content-type": "application/json"}, "body": mock_body }
    assert src.helper.accepted_request(mock_body) == mock_resp

"""
aws_read_ssm tests

"""
# test if no parameter exists
@moto.mock_ssm
def test_aws_read_ssm_fail_no_parameter():
    parameter = "path/to/parameter"
    param_value = src.helper.aws_read_ssm(parameter)
    assert param_value is None

@moto.mock_ssm
def test_aws_read_ssm_success():
    parameter = "path/to/parameter"
    parameter_value = "store_safely"
    ssm = boto3.client("ssm", region_name=REGION)
    ssm.put_parameter(Name=parameter,Value=parameter_value,Type='SecureString',Overwrite=True,Tier='Standard')
    
    param_value = src.helper.aws_read_ssm(parameter)
    assert param_value == parameter_value


"""
aws_ses_send tests

"""
@moto.mock_ses
def test_aws_ses_send_unverified_email_fail():
    assert src.helper.aws_ses_send(to={"BccAddresses": ["to"]},sub="sub",body="text") is None

@moto.mock_ses
def test_aws_ses_send_parameter_error_fail():
    assert src.helper.aws_ses_send(to="to",sub="sub",body="text") is None

@moto.mock_ses
def test_aws_ses_send_success():
    ses = boto3.client("ses", region_name=REGION)
    ses.verify_email_identity(EmailAddress=EMAIL_FROM)
    assert src.helper.aws_ses_send(to={"BccAddresses": ["to@example.com"]},sub="test",body="test email body")


"""
post_request tests

"""
@mock.patch('src.helper.requests.post')
def test_post_request_fail_connection(mock_request):
    
    mock_request.return_value = mock_response(status=0, raise_for_status=requests.exceptions.ConnectionError("connection"))
    assert src.helper.post_request(url="someurl",body="",headers="") is None

@mock.patch('src.helper.requests.post')
def test_post_request_fail_timeout(mock_request):
    mock_request.return_value = mock_response(status=0, raise_for_status=requests.exceptions.Timeout("timeout"))
    assert src.helper.post_request(url="someurl",body="",headers="") is None

@mock.patch('src.helper.requests.post')
def test_post_request_fail_random(mock_request):
    mock_request.return_value = mock_response(status=0, raise_for_status=Exception("random"))
    assert src.helper.post_request(url="someurl",body="",headers="") is None

@mock.patch('src.helper.requests.post')
def test_post_request_fail_404(mock_request):
    mock_request.return_value = mock_response(status=404, raise_for_status=requests.exceptions.HTTPError("404"))
    assert src.helper.post_request(url="someurl",body="",headers="") is None
    
@mock.patch('src.helper.requests.post')
def test_post_request_fail_500(mock_request):
    mock_request.return_value = mock_response(status=500, raise_for_status=requests.exceptions.HTTPError("500"))
    assert src.helper.post_request(url="someurl",body="",headers="") is None

@mock.patch('src.helper.requests.post')
def test_post_request_success_201(mock_request):
    mock_request.return_value = mock_response(status=201,content="updated")
    r = src.helper.post_request(url="someurl",body="",headers="")
    assert r.status_code == 201
    assert r.content == "updated"

"""
get_request tests

"""
@mock.patch('src.helper.requests.get')
def test_get_request_fail_connection(mock_request):
    
    mock_request.return_value = mock_response(status=0, raise_for_status=requests.exceptions.ConnectionError("connection"))
    assert src.helper.get_request(url="someurl",body="",headers="") is None

@mock.patch('src.helper.requests.get')
def test_get_request_fail_timeout(mock_request):
    mock_request.return_value = mock_response(status=0, raise_for_status=requests.exceptions.Timeout("timeout"))
    assert src.helper.get_request(url="someurl",body="",headers="") is None

@mock.patch('src.helper.requests.get')
def test_get_request_fail_random(mock_request):
    mock_request.return_value = mock_response(status=0, raise_for_status=Exception("random"))
    assert src.helper.get_request(url="someurl",body="",headers="") is None

@mock.patch('src.helper.requests.get')
def test_get_request_fail_404(mock_request):
    mock_request.return_value = mock_response(status=404, raise_for_status=requests.exceptions.HTTPError("404"))
    assert src.helper.get_request(url="someurl",body="",headers="") is None
    
@mock.patch('src.helper.requests.get')
def test_get_request_fail_500(mock_request):
    mock_request.return_value = mock_response(status=500, raise_for_status=requests.exceptions.HTTPError("500"))
    assert src.helper.get_request(url="someurl",body="",headers="") is None

@mock.patch('src.helper.requests.get')
def test_get_request_success_201(mock_request):
    mock_request.return_value = mock_response(status=201,content="updated")
    r = src.helper.get_request(url="someurl",body="",headers="")
    assert r.status_code == 201
    assert r.content == "updated"

@mock.patch('src.helper.requests.get')
def test_get_request_success_200_json(mock_request):
    mock_request.return_value = mock_response(status=200,text="{\"json\":\"updated\"}")
    r = src.helper.get_request(url="someurl",body="",headers="")
    assert r.status_code == 200
    assert r.text == "{\"json\":\"updated\"}"

"""
head_request tests

"""
@mock.patch('src.helper.requests.head')
def test_head_request_fail_connection(mock_request):
    
    mock_request.return_value = mock_response(status=0, raise_for_status=requests.exceptions.ConnectionError("connection"))
    assert src.helper.head_request(url="someurl",headers="") is None

@mock.patch('src.helper.requests.head')
def test_head_request_fail_timeout(mock_request):
    mock_request.return_value = mock_response(status=0, raise_for_status=requests.exceptions.Timeout("timeout"))
    assert src.helper.head_request(url="someurl",headers="") is None

@mock.patch('src.helper.requests.head')
def test_head_request_fail_random(mock_request):
    mock_request.return_value = mock_response(status=0, raise_for_status=Exception("random"))
    assert src.helper.head_request(url="someurl",headers="") is None

@mock.patch('src.helper.requests.head')
def test_head_request_fail_404(mock_request):
    mock_request.return_value = mock_response(status=404, raise_for_status=requests.exceptions.HTTPError("404"))
    assert src.helper.head_request(url="someurl",headers="") is None
    
@mock.patch('src.helper.requests.head')
def test_head_request_fail_500(mock_request):
    mock_request.return_value = mock_response(status=500, raise_for_status=requests.exceptions.HTTPError("500"))
    assert src.helper.head_request(url="someurl",headers="") is None

@mock.patch('src.helper.requests.head')
def test_head_request_success_201(mock_request):
    mock_request.return_value = mock_response(status=200,content="exists!")
    r = src.helper.head_request(url="someurl",headers="")
    assert r.status_code == 200
    assert r.content == "exists!"
