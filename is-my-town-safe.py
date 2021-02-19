import urllib.request, json
from datetime import date, datetime
from google.cloud import firestore


'''
Takes a dict and adds it to a document in a Firestore database called 'is-my-town-safe'
'''
def write_to_db(data):
    
    days_since_epoch = int(int(datetime.now().timestamp()) / 60 / 60 / 24)
    data["date"] = str(date.today())

    db = firestore.Client()
    db.collection(u'is-my-town-safe').document(str(days_since_epoch)).set(data)


def pull_data(address):
    #print("Collecting data...")
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


def aggregate(data, value_to_aggregate):
    running_total = 0

    for key in data:
        if value_to_aggregate in data[key]:
            running_total += data[key][value_to_aggregate]

    return running_total


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

    results["total_cases"] = aggregate(merged,"Cases")
    results["total_population"] = aggregate(merged, "Population")
    results["case_rate"] = results["total_cases"] / results["total_population"] * 100000
    results["positives"] = aggregate(merged,"Positives")
    results["total_tests"] = aggregate(merged,"NumberOfTests")
    results["percentage_positive_tests"] = results["positives"] / results["total_tests"]

    write_to_db(results)

    print("Total Cases:", format(results["total_cases"], ',d'))
    print("Total Population:", format(results["total_population"], ',d'))
    print("Case Rate per 100,000:", format(results["case_rate"], ',.1f'))  # format to 1 decimal place
    print("Percentage of Positive Tests:", format(results["percentage_positive_tests"], ',.1%'))

main()
