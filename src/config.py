# Configurations

REGION = 'us-west-1'

JWT_DURATION = 30
JWT_ALGO = "RS256"

AIO_ORG_ID = "__alpha_numeric_string__"      # available in your adobe i/o console
AIO_CLIENT_ID = "__alpha_numeric_string__"   # available in your adobe i/o console
AIO_CLIENT_SECRET = "/adobeio/client_secret" # this maps to aws ssm parameter store
PRIVATE_KEY = "/adobeio/cert/privatekey"     # this maps to aws ssm parameter store

TECHNICAL_ACCOUNT_ID = "__alpha_numeric_string__" # available in your adobe i/o console

AIO_BASE_URL = "https://ims-na1.adobelogin.com"
CLDMGR_URL = "{}/s/ent_cloudmgr_sdk".format(AIO_BASE_URL)
CLOUDMANAGER_URL = "{}/s/ent_cloudmgr_sdk".format(AIO_BASE_URL)
AUD_URL = "{}/c/{}".format(AIO_BASE_URL, AIO_CLIENT_ID)
AUDIENCE = "{}/c/{}".format(AIO_BASE_URL, AIO_CLIENT_ID)
JWT_URL = "{}/ims/exchange/jwt/".format(AIO_BASE_URL)


EMAIL_TO = "notify@example.com"       # replace
EMAIL_FROM = "no-reply@example.com"   # replace

TEAMS_WH = "https://outlook.office.com/webhook/__teams_incoming_webhook__"  # replace

COLOR = {
    "default": "#0078D7",
    "info": "#0078D7",
    "in_progress": "#0078D7",
    "ok": "#008000",
    "success": "#008000",
    "succeeded": "#008000",
    "finished": "#008000",
    "error": "#ff0000",
    "stopped": "#ff0000",
    "failed": "#ff0000",
    "alarm": "#ff0000",
    "alert": "#ff0000"
}

EMOJI = {
    "default": "&#x1F449;",
    "info": "&#x1F449;",
    "in_progress": "&#x1F449;",
    "ok": "&#x1F44D;",
    "success": "&#x1F44D;",
    "succeeded": "&#x1F44D;",
    "finished": "&#x1F44D;",
    "error": "&#x1F44E;",
    "stopped": "&#x1F44E;",
    "failed": "&#x1F44E;",
    "alarm": "&#x1F44E;",
    "alert": "&#x1F44E;"
}

EMAIL_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns = "http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv = "Content-Type" content = "text/html; charset = utf-8" />
  <title>Notification</title>
  <style type = "text/css">
  body {{margin: 0; padding: 0; min-width: 100%!important;}}
  img {{height: auto;}}
  .content {{width: 100%; max-width: 1200px;}}
  .header {{padding: 15px 15px 15px 15px;}}
  .innerpadding {{padding: 30px 30px 30px 30px;}}
  .h1, .h2, .h3, .bodycopy {{color: #153643; font-family: sans-serif;}}
  .h1 {{font-size: 33px; line-height: 38px; font-weight: bold;}}
  .h2 {{padding: 0 0 15px 0; font-size: 24px; line-height: 28px; font-weight: bold;}}
  .h3 {{padding: 0 0 15px 0; font-size: 18px; line-height: 22px; font-weight: bold;}}
  .bodycopy {{font-size: 14px; line-height: 20px; white-space: pre-wrap; }}

  @media only screen and (max-width: 550px), screen and (max-device-width: 550px) {{
  body[yahoo] .hide {{display: none!important;}}
  }}

  </style>
</head>

<body yahoo bgcolor = "#ffffff">
<table width = "100%" bgcolor = "#ffffff" border = "0" cellpadding = "0" cellspacing = "0">
<tr>
  <td bgcolor = "{}" class = "header" width = "100%"></td>
</tr>
<tr>
  <td>
    <table bgcolor = "#ffffff" class = "content" align = "left" cellpadding = "0" cellspacing = "0" border = "0">
      <tr>
        <td class = "innerpadding">
          <table width = "100%" border = "0" cellspacing = "0" cellpadding = "0">
            <tr>
              <td class = "h3"> {} {} </td>
            </tr>
            <tr>
              <td class = "bodycopy">
              {}
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </td>
  </tr>
</table>
</body>
</html>
"""
