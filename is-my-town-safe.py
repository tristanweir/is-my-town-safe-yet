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
TO DO: write this up
'''
def read_from_db(document_name, key):
    db = firestore.Client()
    doc = db.collection(database_name).document(str(document_name)).get()
    if doc.exists:
        doc_dict = doc.to_dict()
        return doc_dict[key]
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
                #print(entry["attributes"])
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
    
    todays_value = data[key]
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

def main():
    zip_codes_to_keep = [94601, 94602, 94606, 94610, 94619]
    # zip_codes_to_keep = [94602]
    
    url1 = "https://services5.arcgis.com/ROBnTHSNjoZ2Wm1P/arcgis/rest/services/COVID_19_Statistics/FeatureServer/0/query?where=1%3D1&outFields=Zip_Number,Population,Cases,CaseRates&returnGeometry=false&outSR=4326&f=json"
    url2 = "https://services5.arcgis.com/ROBnTHSNjoZ2Wm1P/arcgis/rest/services/COVID_19_Statistics/FeatureServer/1/query?where=1%3D1&outFields=Zip_Number,Positives,NumberOfTests&returnGeometry=false&outSR=4326&f=json"

    
    data1 = pull_data(url1)
    filtered_data1 = filter_data(data1["features"], zip_codes_to_keep)
    
    data2 = pull_data(url2)
    filtered_data2 = filter_data(data2["features"], zip_codes_to_keep)
    
    
    print(filtered_data1, "\n\n")
    print(filtered_data2, "\n\n")
    merged = merge_data(filtered_data1, filtered_data2)
    today = date.today()
    print("Live Data as of", today, "\n", merged)
    
    # for testing, statically load the merged dataset so we are not constantly calling the API
    # merged = {94606: {'Zip_Number': 94606, 'Population': 38169, 'Cases': 639, 'CaseRates': 1674.13345909, 'PercentagePositiveTests': 5.964795194794}, 94610: {'Zip_Number': 94610, 'Population': 30014, 'Cases': 154, 'CaseRates': 513.09388952, 'PercentagePositiveTests': 1.581609195402}, 94619: {'Zip_Number': 94619, 'Population': 25119, 'Cases': 348, 'CaseRates': 1385.40546996, 'PercentagePositiveTests': 5.819360293081}, 94601: {'Zip_Number': 94601, 'Population': 55840, 'Cases': 2035, 'CaseRates': 3644.34097421, 'PercentagePositiveTests': 15.088161209068}, 94602: {'Zip_Number': 94602, 'Population': 30831, 'Cases': 311, 'CaseRates': 1008.72498459, 'PercentagePositiveTests': 3.97580916116}}
    # print("Statically loaded data: ", merged)

    results = dict()

    results["date"] = str(today)    # add the date to the database record
    results["zips"] = zip_codes_to_keep
    results["total_cases"] = aggregate(merged,"Cases")
    results["total_population"] = aggregate(merged, "Population")
    results["case_rate_per_100k"] = results["total_cases"] / results["total_population"] * 100000
    results["positive_tests"] = aggregate(merged,"Positives")
    results["total_tests"] = aggregate(merged,"NumberOfTests")
    results["percentage_positive_tests"] = results["positive_tests"] / results["total_tests"]

    results["7_day_avg_case_rate"] = n_day_average(7, results, "case_rate_per_100k")
    
    write_to_db(results)

    print("Total Cases:", format(results["total_cases"], ',d'))
    print("Total Population:", format(results["total_population"], ',d'))
    print("Case Rate per 100,000:", format(results["case_rate_per_100k"], ',.1f'))  # format to 1 decimal place
    print("Percentage of Positive Tests:", format(results["percentage_positive_tests"], ',.1%'))

main()
