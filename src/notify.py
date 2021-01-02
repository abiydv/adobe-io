import json
from src.helper import aws_ses_send, post_request
from src.config import EMOJI, COLOR, EMAIL_TEMPLATE


def teams(**kwargs):
    url = kwargs["url"]
    emoji = EMOJI.get(kwargs["status"].lower(), EMOJI["default"])
    color = COLOR.get(kwargs["status"].lower(), COLOR["default"])
    headers = {"Content-Type": "application/json"}

    activity_title = "{} **{}**".format(emoji, kwargs["subject"])
    payload = {
        "@type": "MessageCard",
        "summary": kwargs["subject"],
        "themeColor": color[1:],
        "sections": [{"activityTitle": activity_title, "text": kwargs["message"]}],
    }
    response = post_request(url=url, data=json.dumps(payload), headers=headers)
    if response is None:
        print("message not posted to teams {}".format(url))
        return False
    elif "200" in response.headers.get("X-BackEndHttpStatus"):
        print("message posted to teams {}".format(url))
        return True
    else:
        print("message not posted to teams {}".format(url))
        return False


def email(**kwargs):
    to = {"BccAddresses": [kwargs["to"]]}
    emoji = EMOJI.get(kwargs["status"].lower(), EMOJI["default"])
    color = COLOR.get(kwargs["status"].lower(), COLOR["default"])
    body = EMAIL_TEMPLATE.format(color, emoji, kwargs["subject"], kwargs["message"])

    response = aws_ses_send(to=to, sub=kwargs["subject"], body=body)
    if response is None:
        print("could not send email")
        return False
    else:
        print("email sent")
        return True
