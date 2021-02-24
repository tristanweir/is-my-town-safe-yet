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

def calc_percentage(todays_data, amt_changed, num_days):
    snippet = ""

    if amt_changed is not None:
        percent_change = amt_changed / (todays_data - amt_changed)
        if percent_change <= 0:
            color = "<div style=\"color:green\">"   # negative numbers mean improvement (green)
        else:
            color = "<div style=\"color:red\">"     # positive numbers mean worsening (red)
        snippet += " {}({:+.1%} from {} days ago)</div>".format(color, percent_change,num_days)

    return snippet



def create_body():
    todays_data = read_from_db(days_since_epoch())
    body = ""

    if todays_data is not None:
        body += "<h2>COVID-19 data for {}</h2>\n".format(todays_data.get("date"))
        body += "<p>Total Cases: {:,}</p>\n".format(todays_data.get("total_cases"))
        body += "<p>Case Rate per 100,000 population: {:,.1f}</p>\n".format(todays_data.get("case_rate_per_100k"))
        body += "<p>Percentage of positive tests: {:.1%}</p>\n".format(todays_data.get("percentage_positive_tests"))
        body += "\n"

        body += "<p>7-day average case rate per 100,000: {:,.1f}".format(todays_data.get("7_day_avg_case_rate"))
        body += calc_percentage(todays_data.get("7_day_avg_case_rate"),todays_data.get("7_day_change_avg_case_rate"),7)
        body += calc_percentage(todays_data.get("7_day_avg_case_rate"),todays_data.get("28_day_change_avg_case_rate"),28)
        body += "</p>\n"

        body += "<p>7-day average percentage positive: {:.1%}".format(todays_data.get("7_day_avg_percentage_pos"))
        body += calc_percentage(todays_data.get("7_day_avg_percentage_pos"),todays_data.get("7_day_change_avg_percentage_pos"),7)
        body += calc_percentage(todays_data.get("7_day_avg_percentage_pos"),todays_data.get("28_day_change_avg_percentage_pos"),28)
        body += "</p>\n"
    return body

def main():
    body = create_body()

    print(body)    

main()
