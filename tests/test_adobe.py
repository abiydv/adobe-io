import jwt
import mock
import json
import pytest
import unittest

from .context import src


"""
main tests

"""

# test function returns bad request if proper headers are not received
@mock.patch('src.adobe.bad_request')
@mock.patch('src.adobe.adobe_incoming_headers')
def test_main_fail_invalid_headers(mock_request,mock_bad_req):
    mock_request.return_value = False
    src.adobe.main("","")
    assert mock_request.called
    assert mock_bad_req.called

# test function returns value as returned by accepted_request function if it is a challenge event
@mock.patch('src.adobe.accepted_request')
@mock.patch('src.adobe.adobe_challenge_request')
@mock.patch('src.adobe.adobe_incoming_headers')
def test_main_success_challenge_request(mock_header_req,mock_challenge_req,mock_accepted_req):
    mock_header_req.return_value = True
    mock_challenge_req.return_value = True
    mock_accepted_req.return_value = "challenge_accepted"
    main_resp = src.adobe.main({"queryStringParameters":"random"},"")
    assert mock_header_req.called
    assert mock_challenge_req.called
    assert main_resp == mock_accepted_req.return_value
    assert mock_accepted_req.called

# test function does not invoke accepted_request function if it is not a challenge event
@mock.patch('src.adobe.accepted_request')
@mock.patch('src.adobe.adobe_challenge_request')
@mock.patch('src.adobe.adobe_incoming_headers')
def test_main_fail_not_challenge_request(mock_header_req,mock_challenge_req,mock_accepted_req):
    mock_header_req.return_value = True
    mock_challenge_req.return_value = False
    mock_accepted_req.return_value = "challenge_accepted"
    main_resp = src.adobe.main("","")
    assert mock_header_req.called
    assert mock_challenge_req.called
    assert main_resp != mock_accepted_req.return_value
    assert not mock_accepted_req.called

# test function returns bad request if proper signature not received
@mock.patch('src.adobe.bad_request')
@mock.patch('src.adobe.adobe_signature')
@mock.patch('src.adobe.adobe_challenge_request')
@mock.patch('src.adobe.adobe_incoming_headers')
def test_main_fail_invalid_signature(mock_header_req,mock_challenge_req,mock_sig_req,mock_bad_req):
    mock_header_req.return_value = True
    mock_challenge_req.return_value = False
    mock_sig_req.return_value = False
    src.adobe.main("","")
    assert mock_header_req.called
    assert mock_challenge_req.called
    assert mock_sig_req.called
    assert mock_bad_req.called

# test function invokes process method and returns response
@mock.patch('src.adobe.process')
@mock.patch('src.adobe.adobe_signature')
@mock.patch('src.adobe.adobe_challenge_request')
@mock.patch('src.adobe.adobe_incoming_headers')
def test_main_success_invoke_process(mock_header_req,mock_challenge_req,mock_sig_req,mock_process_req):
    mock_header_req.return_value = True
    mock_challenge_req.return_value = False
    mock_sig_req.return_value = True
    mock_process_req.return_value = "accepted"
    assert src.adobe.main("","") == mock_process_req.return_value
    assert mock_header_req.called
    assert mock_challenge_req.called
    assert mock_sig_req.called
    assert mock_process_req.called

"""
values tests

"""

def test_values_success_valid_values():
    event = {"headers":{"x-adobe-event-id":"evid","x-adobe-event-code":"code"},"body":"{\"event\":{\"activitystreams:object\":{\"@id\":\"0/1/2/3/4/5/6/7/8/9\"}}}"}
    
    output = {"evid":event['headers'].get("x-adobe-event-id"),"code":event['headers'].get('x-adobe-event-code'),"body":json.loads(event['body']),"link":json.loads(event['body']).get('event').get('activitystreams:object').get('@id'),"exid":json.loads(event['body']).get('event').get('activitystreams:object').get('@id').split("/")[9]}

    assert src.adobe.values(event) == output

def test_values_fail_invalid_json():
    event = {"body":"random"}
    assert src.adobe.values(event) is None

def test_values_fail_missing_headers():
    event = {"body":"{\"event\":{\"activitystreams:object\":{\"@id\":\"0/1/2/3/4/5/6/7/8/9\"}}}"}
    assert src.adobe.values(event) is None

def test_values_fail_missing_index():
    event = {"headers":{"x-adobe-event-id":"evid","x-adobe-event-code":"code"},"body":"{\"event\":{\"activitystreams:object\":{\"@id\":\"0\"}}}"}
    assert src.adobe.values(event) is None

"""  
aio_cm_status tests 

"""

@mock.patch('src.adobe.get_request')
@mock.patch('src.adobe.aio_generate_access_token')
def test_aio_cm_status_success(mock_aio_generate_access_token, mock_get_request):
    mock_aio_generate_access_token.return_value = "token"
    mock_get_request.return_value.status_code = 200
    mock_get_request.return_value.text = "{\"json\":\"updated\"}"
    assert src.adobe.aio_cm_status("url") == json.loads("{\"json\":\"updated\"}")

@mock.patch('src.adobe.get_request')
@mock.patch('src.adobe.aio_generate_access_token')
def test_aio_cm_status_fail_none_response(mock_aio_generate_access_token, mock_get_request):
    mock_aio_generate_access_token.return_value = "token"
    mock_get_request.return_value = None
    assert src.adobe.aio_cm_status("url") is None


"""  
aio_generate_access_token tests 

"""

@mock.patch('src.adobe.post_request')
@mock.patch('src.adobe.aws_read_ssm')
@mock.patch('src.adobe.aio_generate_jwt')
def test_aio_generate_access_token_fail_no_return(mock_aio_generate_jwt,mock_aws_read_ssm,mock_post_request):
    mock_aio_generate_jwt.return_value = b'jwt_token'
    mock_aws_read_ssm.return_value = "parameter"
    mock_post_request.return_value = None
    assert src.adobe.aio_generate_access_token() is None

@mock.patch('src.adobe.post_request')
@mock.patch('src.adobe.aws_read_ssm')
@mock.patch('src.adobe.aio_generate_jwt')
def test_aio_generate_access_token_fail_no_token(mock_aio_generate_jwt,mock_aws_read_ssm,mock_post_request):
    mock_aio_generate_jwt.return_value = b'jwt_token'
    mock_aws_read_ssm.return_value = "parameter"
    mock_post_request.return_value.text = "{\"random\":\"json response\"}" 
    assert src.adobe.aio_generate_access_token() is None

@mock.patch('src.adobe.post_request')
@mock.patch('src.adobe.aws_read_ssm')
@mock.patch('src.adobe.aio_generate_jwt')
def test_aio_generate_access_token_fail_invalid_json(mock_aio_generate_jwt,mock_aws_read_ssm,mock_post_request):
    mock_aio_generate_jwt.return_value = b'jwt_token'
    mock_aws_read_ssm.return_value = "parameter"
    mock_post_request.return_value.text = "not a json response" 
    assert src.adobe.aio_generate_access_token() is None

@mock.patch('src.adobe.post_request')
@mock.patch('src.adobe.aws_read_ssm')
@mock.patch('src.adobe.aio_generate_jwt')
def test_aio_generate_access_token_success(mock_aio_generate_jwt,mock_aws_read_ssm,mock_post_request):
    mock_aio_generate_jwt.return_value = b'jwt_token'
    mock_aws_read_ssm.return_value = "parameter"
    mock_post_request.return_value.text = "{\"access_token\":\"access_token\"}" 
    assert src.adobe.aio_generate_access_token() == "access_token"


"""  
aio_generate_jwt tests 

"""

@mock.patch('src.adobe.aws_read_ssm')
def test_aio_generate_jwt_fail_invalid_key(mock_aws_read_ssm):
    demo_key = "invalid_key"
    demo_payload = {"random":"payload"}
    mock_aws_read_ssm.return_value = demo_key
    assert src.adobe.aio_generate_jwt(demo_payload) is None

@mock.patch('src.adobe.aws_read_ssm')
def test_aio_generate_jwt_fail_invalid_payload(mock_aws_read_ssm):
    demo_key = "invalid_key"
    demo_payload = "random_payload"
    mock_aws_read_ssm.return_value = demo_key
    assert src.adobe.aio_generate_jwt(demo_payload) is None


@mock.patch('src.adobe.aws_read_ssm')
def test_aio_generate_jwt_fail_none_payload(mock_aws_read_ssm):
    demo_key = "invalid_key"
    mock_aws_read_ssm.return_value = demo_key
    assert src.adobe.aio_generate_jwt() is None


"""  
process tests 

"""

@mock.patch('src.adobe.values')
def test_process_fail_unknown_event(mock_values):
    mock_values.return_value = {"evid":"123","code":"random"}
    assert src.adobe.process("event")['body'] == "Unknown Event"

@mock.patch('src.adobe.aio_cm_status')
@mock.patch('src.adobe.values')
def test_process_fail_not_latest_event(mock_values,mock_aio_cm_status):
    mock_values.return_value = {"evid":"123","code":"pipeline_execution_start","exid":"099","link":"0/1/2/3/4/5/6/7/8/9"}
    mock_aio_cm_status.return_value = {"id":"100"}
    assert src.adobe.process("event")['body'] == "error: not latest execution"

@mock.patch('src.adobe.aio_cm_status')
@mock.patch('src.adobe.values')
def test_process_success_ignore_non_deploy_start(mock_values,mock_aio_cm_status):
    mock_values.return_value = {"evid":"123","code":"pipeline_execution_step_start","exid":"099","link":"0/1/2/3/4/5/6/7/8/9"}
    mock_aio_cm_status.return_value = {"id":"099","action":"build"}
    assert src.adobe.process("event")['body'] == "Accepted. Ignored"

@mock.patch('src.adobe.teams')
@mock.patch('src.adobe.email')
@mock.patch('src.adobe.aio_cm_status')
@mock.patch('src.adobe.values')
def test_process_success_deploy_start(mock_values,mock_aio_cm_status,mock_email,mock_teams):
    mock_values.return_value = {"evid":"123","code":"pipeline_execution_step_start","exid":"099","link":"0/1/2/3/4/5/6/7/8/9"}
    mock_aio_cm_status.return_value = {"id":"099","action":"deploy","status":"RUNNING","trigger":"MANUAL","artifactsVersion":"001","_embedded":{"stepStates":[{"stepId":"4000","environment":"dev","action":"deploy","status":"RUNNING"},{"stepId":"4001","environment":"dev","action":"test","status":"NOT_STARTED"}]}}
    mock_email.return_value = True
    mock_teams.return_value = True

    assert src.adobe.process("event")['body'] == "Accepted"
    assert mock_email.called
    assert mock_teams.called
