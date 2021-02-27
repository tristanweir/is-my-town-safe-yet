import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import date, datetime
from google.cloud import firestore

database_name = "is-my-town-safe"

'''
Takes a document_name in a firestore db
Returns a dict of the document or None if the document cannot be found
'''
def read_from_db(document_name):
    db = firestore.Client()
    doc = db.collection(database_name).document(str(document_name)).get()
    if doc.exists:
        doc_dict = doc.to_dict()
        return doc_dict
    else:
        return None

'''
Returns the number of days since 1970-01-01, using the current time and local timezone
'''
def days_since_epoch():
    return int(int(datetime.now().timestamp()) / 60 / 60 / 24)    # may be a better way to calculate this

'''
Takes a value, the amount that value changed from a previous value, and the number of days we are looking at
Returns an HTML formatted string that is the percentage change between today's value and the previous value
HTML color is red if there is an increase (bad outcome), green if there is a decrease (good outcome)
'''
def calc_percentage(todays_data, amt_changed, num_days):
    snippet = ""

    if amt_changed is not None:
        percent_change = amt_changed / (todays_data - amt_changed)
        if percent_change <= 0:
            color = "<span style=\"color:green\">"   # negative numbers mean improvement (green)
        else:
            color = "<span style=\"color:red\">"     # positive numbers mean worsening (red)
        snippet += " {0}({1:+.1%} from {2} days ago)</span>".format(color, percent_change, num_days)

    return snippet



def create_body():
    todays_data = read_from_db(days_since_epoch())
    body = ""
    hstyle = "style=\"font-family: sans-serif; font-size: 24px; font-weight: normal; margin: 0; Margin-bottom: 15px;\""
    pstyle = "style=\"font-family: sans-serif; font-size: 14px; font-weight: normal; margin: 0; Margin-bottom: 15px;\""

    if todays_data is not None:
        body += "<p {0}>COVID-19 data for {1}</p>\n".format(hstyle, todays_data.get("date"))

        zips = ""
        for zip in todays_data.get("zips"):
            zips += str(zip) + ", "
        zips = zips[:-2]        # trim the final comma and space from the list

        body += "<p {0}><span style=\"color:gray\">Zip Codes Included: [{1}]</span></p>".format(pstyle, zips)


        body += "<p {0}>Total Cases: {1:,}<br>\n".format(pstyle, todays_data.get("total_cases"))
        body += "Case Rate per 100,000 population: {0:,.1f}<br>\n".format(todays_data.get("case_rate_per_100k"))
        body += "Percentage of positive tests: {0:.1%}<br></p>\n".format(todays_data.get("percentage_positive_tests"))
        body += "\n"

        body += "<p {0}>7-day average case rate per 100,000: {1:,.1f}".format(pstyle, todays_data.get("7_day_avg_case_rate"))
        body += calc_percentage(todays_data.get("7_day_avg_case_rate"),todays_data.get("7_day_change_avg_case_rate"),7)
        body += calc_percentage(todays_data.get("7_day_avg_case_rate"),todays_data.get("28_day_change_avg_case_rate"),28)
        body += "</p>\n"

        body += "<p {0}>7-day average percentage positive: {1:.1%}".format(pstyle, todays_data.get("7_day_avg_percentage_pos"))
        body += calc_percentage(todays_data.get("7_day_avg_percentage_pos"),todays_data.get("7_day_change_avg_percentage_pos"),7)
        body += calc_percentage(todays_data.get("7_day_avg_percentage_pos"),todays_data.get("28_day_change_avg_percentage_pos"),28)
        body += "</p>\n\n"



    body = get_pretty_email_header() + body + get_pretty_email_footer()
    return body

# TODO: Convert to GCP Cloud Function
def main():

    # TODO: Parse email addresses from inbound HTTP request object
    from_temp = ""
    send_to = ""
    subject = "COVID-19 Report for " + str(date.today())
    body = create_body()
    '''
    message = Mail(
        from_email=from_temp,
        to_emails=send_to,
        subject=subject,
        html_content=body)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print("Error: ", e)
    '''
    print(body)    






# reference for processing inbound flask requests
'''
def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    if request.args and 'message' in request.args:
        return request.args.get('message')
    elif request_json and 'message' in request_json:
        return request_json['message']
    else:
        return f'Hello World!'
'''

'''
Wrap the text we care about in a lot of inlined HTML
Sourced from: https://github.com/leemunroe/responsive-html-email-template
'''
def get_pretty_email_header():
    html_header = """
    <!doctype html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>COVID-19 Report for Oakland</title>
        <style>
        /* -------------------------------------
            INLINED WITH htmlemail.io/inline
        ------------------------------------- */
        /* -------------------------------------
            RESPONSIVE AND MOBILE FRIENDLY STYLES
        ------------------------------------- */
        @media only screen and (max-width: 620px) {
        table[class=body] h1 {
            font-size: 28px !important;
            margin-bottom: 10px !important;
        }
        table[class=body] p,
                table[class=body] ul,
                table[class=body] ol,
                table[class=body] td,
                table[class=body] span,
                table[class=body] a {
            font-size: 16px !important;
        }
        table[class=body] .wrapper,
                table[class=body] .article {
            padding: 10px !important;
        }
        table[class=body] .content {
            padding: 0 !important;
        }
        table[class=body] .container {
            padding: 0 !important;
            width: 100% !important;
        }
        table[class=body] .main {
            border-left-width: 0 !important;
            border-radius: 0 !important;
            border-right-width: 0 !important;
        }
        table[class=body] .btn table {
            width: 100% !important;
        }
        table[class=body] .btn a {
            width: 100% !important;
        }
        table[class=body] .img-responsive {
            height: auto !important;
            max-width: 100% !important;
            width: auto !important;
        }
        }

        /* -------------------------------------
            PRESERVE THESE STYLES IN THE HEAD
        ------------------------------------- */
        @media all {
        .ExternalClass {
            width: 100%;
        }
        .ExternalClass,
                .ExternalClass p,
                .ExternalClass span,
                .ExternalClass font,
                .ExternalClass td,
                .ExternalClass div {
            line-height: 100%;
        }
        .apple-link a {
            color: inherit !important;
            font-family: inherit !important;
            font-size: inherit !important;
            font-weight: inherit !important;
            line-height: inherit !important;
            text-decoration: none !important;
        }
        #MessageViewBody a {
            color: inherit;
            text-decoration: none;
            font-size: inherit;
            font-family: inherit;
            font-weight: inherit;
            line-height: inherit;
        }
        .btn-primary table td:hover {
            background-color: #34495e !important;
        }
        .btn-primary a:hover {
            background-color: #34495e !important;
            border-color: #34495e !important;
        }
        }
        </style>
    </head>
    <body class="" style="background-color: #f6f6f6; font-family: sans-serif; -webkit-font-smoothing: antialiased; font-size: 14px; line-height: 1.4; margin: 0; padding: 0; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%;">
        <!-- <span class="preheader" style="color: transparent; display: none; height: 0; max-height: 0; max-width: 0; opacity: 0; overflow: hidden; mso-hide: all; visibility: hidden; width: 0;">This is preheader text. Some clients will show this text as a preview.</span> -->
        <table border="0" cellpadding="0" cellspacing="0" class="body" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%; background-color: #f6f6f6;">
        <tr>
            <td style="font-family: sans-serif; font-size: 14px; vertical-align: top;">&nbsp;</td>
            <td class="container" style="font-family: sans-serif; font-size: 14px; vertical-align: top; display: block; Margin: 0 auto; max-width: 580px; padding: 10px; width: 580px;">
            <div class="content" style="box-sizing: border-box; display: block; Margin: 0 auto; max-width: 580px; padding: 10px;">

                <!-- START CENTERED WHITE CONTAINER -->
                <table class="main" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%; background: #ffffff; border-radius: 3px;">
                
                <!-- START MAIN CONTENT AREA -->
                <tr>
                    <td class="wrapper" style="font-family: sans-serif; font-size: 14px; vertical-align: top; box-sizing: border-box; padding: 20px;">
                    <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%;">
                        <tr>
                        <td style="font-family: sans-serif; font-size: 14px; vertical-align: top;">
    """
    return html_header

def get_pretty_email_footer():
    html_footer = """
                        </td>
                        </tr>
                    </table>
                    </td>
                </tr>
                <!-- END MAIN CONTENT AREA -->
                </table>

                <!-- START FOOTER -->
                <div class="footer" style="clear: both; Margin-top: 10px; text-align: center; width: 100%;">
                <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%;">
                    <tr>
                    <td class="content-block" style="font-family: sans-serif; vertical-align: top; padding-bottom: 10px; padding-top: 10px; font-size: 12px; color: #999999; text-align: center;">
                        <br> Data sourced from <a href="https://covid-19.acgov.org/data" style="text-decoration: underline; color: #999999; font-size: 12px; text-align: center;">Alameda County Public Health Department</a>
                        <br> Don't like these emails? Ask Tristan to stop sending them to you.
                    </td>
                    </tr>
                    <tr>
                    <td class="content-block powered-by" style="font-family: sans-serif; vertical-align: top; padding-bottom: 10px; padding-top: 10px; font-size: 12px; color: #999999; text-align: center;">
                        Powered by <a href="http://htmlemail.io" style="color: #999999; font-size: 12px; text-align: center; text-decoration: none;">HTMLemail</a>.
                    </td>
                    </tr>
                </table>
                </div>
                <!-- END FOOTER -->

            <!-- END CENTERED WHITE CONTAINER -->
            </div>
            </td>
            <td style="font-family: sans-serif; font-size: 14px; vertical-align: top;">&nbsp;</td>
        </tr>
        </table>
    </body>
    </html>
    """
    return html_footer

main()