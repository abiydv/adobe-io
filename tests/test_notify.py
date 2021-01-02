import mock

from .context import src

"""
teams tests

"""


@mock.patch("src.notify.post_request")
def test_teams_fail_none(mock_request):
    mock_request.return_value = None
    assert not src.notify.teams(
        url="url", subject="subject", message="msg", status="status"
    )


@mock.patch("src.notify.post_request")
def test_teams_fail_401(mock_request):
    mock_request.return_value.headers = {"X-BackEndHttpStatus": "401"}
    assert not src.notify.teams(
        url="url", subject="subject", message="msg", status="status"
    )


@mock.patch("src.notify.post_request")
def test_teams_success(mock_request):
    mock_request.return_value.headers = {"X-BackEndHttpStatus": "200"}
    assert src.notify.teams(
        url="url", subject="subject", message="msg", status="status"
    )


"""
email tests

"""


@mock.patch("src.notify.aws_ses_send")
def test_email_fail_none(mock_request):
    mock_request.return_value = None
    assert not src.notify.email(
        to="mailto", subject="subject", message="msg", status="status"
    )


@mock.patch("src.notify.aws_ses_send")
def test_email_success(mock_request):
    mock_request.return_value = True
    assert src.notify.email(
        to="mailto", subject="subject", message="msg", status="status"
    )
