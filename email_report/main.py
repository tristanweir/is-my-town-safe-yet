from datetime import date, datetime
from google.cloud import firestore

database_name = "is-my-town-safe"

'''
Takes a document_name in a firestore db, a key that corresponds to a value in a firestore db
Returns the value of the key, or None if neither the document or the key can be found
'''
def read_from_db(document_name, key):
    db = firestore.Client()
    doc = db.collection(database_name).document(str(document_name)).get()
    if doc.exists:
        doc_dict = doc.to_dict()
        return doc_dict.get(key)
    else:
        return None

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



def main():
    todays_data = read_from_db(days_since_epoch())
    body = ""

    '''
    results["date"] = today    # add the date to the database record
    results["zips"] = zip_codes_to_keep
    results["total_cases"] = aggregate(merged,"Cases")
    results["total_population"] = aggregate(merged, "Population")
    results["case_rate_per_100k"] = results["total_cases"] / results["total_population"] * 100000
    results["positive_tests"] = aggregate(merged,"Positives")
    results["total_tests"] = aggregate(merged,"NumberOfTests")
    results["percentage_positive_tests"] = results["positive_tests"] / results["total_tests"]
    results["7_day_avg_case_rate"] = n_day_average(7, results, "case_rate_per_100k")
    results["7_day_avg_percentage_pos"] = n_day_average(7, results, "percentage_positive_tests")
    '''
    if todays_data is not None:
        body += "<h2>COVID-19 data for {}</h2>\n".format(todays_data["date"])
        body += "<p>Total Cases: {:,}</p>\n".format(todays_data["total_cases"])
        body += "<p>Case Rate per 100,000 population: {:,.1f}</p>\n".format(todays_data["case_rate_per_100k"])


    print(body)    

main()
