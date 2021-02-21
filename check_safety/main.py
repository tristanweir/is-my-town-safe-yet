# gcloud functions deploy check_safety --entry-point check_safety --trigger-http --runtime python38
import urllib.request, json
from datetime import date, datetime
from google.cloud import firestore

database_name = "is-my-town-safe"

'''
Takes a dict and adds it to a document in a Firestore database called 'is-my-town-safe'
'''
def write_to_db(data):
    
    document_name = str(days_since_epoch()) # the document name is the number of days since 1970-01-01

    db = firestore.Client()
    db.collection(database_name).document(document_name).set(data)    

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
Returns the number of days since 1970-01-01, using the current time and local timezone
'''
def days_since_epoch():
    return int(int(datetime.now().timestamp()) / 60 / 60 / 24)    # may be a better way to calculate this


'''
Takes a URL, which hopefully points at a JSON document
Returns the parsed JSON that the URL returns
'''
def pull_data(address):
    with urllib.request.urlopen(address) as url:
        data = json.loads(url.read().decode())

    return data

''' 
Takes ArcGis data and a list of zip codes
Returns a dict containing only the data for those zips in the list of zip code (zip is the key)
'''
def filter_data(data, zip_codes_to_keep):

    filtered_data = dict()

    for entry in data:
        for zip in zip_codes_to_keep:
            if "attributes" in entry and "Zip_Number" in entry["attributes"] and entry["attributes"]["Zip_Number"] == zip:
                filtered_data.update({ zip : entry["attributes"] })

    return filtered_data

'''
data1 and data2 are dicts that look like
{ key : { some info about the key }}

In most cases the keys are the same in each dict, but they don't have to be
'''
def merge_data(data1, data2):
    for key in data2:
        if key in data1:
            data1[key].update(data2[key])
        else:
            data1.update({ key : data2[key]})   # merge unfound keypairs in data2 into data1
    return data1

'''
Take in a dict-of-dicts and a key on which we are aggregating
Returns the sum of ints within that key
'''
def aggregate(data, value_to_aggregate):
    running_total = 0

    for key in data:
        if value_to_aggregate in data[key]:
            running_total += data[key][value_to_aggregate]

    return running_total

'''
Takes an int, n, which is the number of days to calculate the average
data, a dict
key, a string which is the corresponding key in data to average
Returns an average of n ints. If n ints can't be found, return the average of however many ints were found up to n
'''
def n_day_average(n, data, key):
    sum = 0
    count = 0
    
    todays_value = data.get(key)
    if type(todays_value) == int or type(todays_value) == float:
        sum = sum + todays_value
        count = count + 1

    todays_date = days_since_epoch()

    for i in range(n):
        response = read_from_db(todays_date - i, key)
        if response is not None:
            sum = sum + response
            count = count + 1

    average = 0
    if count > 0: 
        average = sum / count
    else:
        average = sum

    return average

def check_safety(request):
# def main():
    zip_codes_to_keep = [94601, 94602, 94606, 94610, 94619]
    
    url1 = "https://services5.arcgis.com/ROBnTHSNjoZ2Wm1P/arcgis/rest/services/COVID_19_Statistics/FeatureServer/0/query?where=1%3D1&outFields=Zip_Number,Population,Cases,CaseRates&returnGeometry=false&outSR=4326&f=json"
    url2 = "https://services5.arcgis.com/ROBnTHSNjoZ2Wm1P/arcgis/rest/services/COVID_19_Statistics/FeatureServer/1/query?where=1%3D1&outFields=Zip_Number,Positives,NumberOfTests&returnGeometry=false&outSR=4326&f=json"
    
    data1 = pull_data(url1)
    filtered_data1 = filter_data(data1["features"], zip_codes_to_keep)
    
    data2 = pull_data(url2)
    filtered_data2 = filter_data(data2["features"], zip_codes_to_keep)

    merged = merge_data(filtered_data1, filtered_data2)
    today = str(date.today()    )

    results = dict()

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

     # calculate how case rate and percentage positive have changed in the past week   
    week_old_avg_case_rate = read_from_db(days_since_epoch()-7,"7_day_avg_case_rate")
    if week_old_avg_case_rate is not None:
        results["7_day_change_avg_case_rate"] = results["case_rate_per_100k"] - week_old_avg_case_rate
    else:
        results["7_day_change_avg_case_rate"] = None
    
    week_old_percentage_pos = read_from_db(days_since_epoch()-7,"percentage_positive_tests")   
    if week_old_percentage_pos is not None:
        results["7_day_change_avg_percentage_pos"] = results["percentage_positive_tests"] - week_old_percentage_pos
    else:
        results["7_day_change_avg_percentage_pos"] = None
    
    # calculate how case rate and percentage positive have changed in the past month
    month_old_avg_case_rate = read_from_db(days_since_epoch()-28,"7_day_avg_case_rate")
    if month_old_avg_case_rate is not None:
        results["28_day_change_avg_case_rate"] = results["case_rate_per_100k"] - month_old_avg_case_rate
    else:
        results["28_day_change_avg_case_rate"] = None
    

    month_old_percentage_pos = read_from_db(days_since_epoch()-28,"percentage_positive_tests")   
    if month_old_percentage_pos is not None:
        results["28_day_change_avg_percentage_pos"] = results["percentage_positive_tests"] - month_old_percentage_pos
    else:
        results["28_day_change_avg_percentage_pos"] = None


    for result in results:
        print(result,": ",results[result])

    write_to_db(results)
    
    response =  "Case Rate per 100k: " + str(results["case_rate_per_100k"])
    return response



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

# main()
