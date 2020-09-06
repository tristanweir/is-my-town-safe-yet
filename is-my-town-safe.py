import urllib.request, json


def pullData(address):
    #print("Collecting data...")
    with urllib.request.urlopen(address) as url:
        data = json.loads(url.read().decode())

    return data

''' 
Takes ArcGis data and a list of zip codes
Returns a dict containing only the data for those zips in the list of zip code (zip is the key)
'''
def filterData(data, zipCodesToKeep):

    filteredData = dict()

    for entry in data:
        for zip in zipCodesToKeep:
            if "attributes" in entry and "Zip_Number" in entry["attributes"] and entry["attributes"]["Zip_Number"] == zip:
                #print(entry["attributes"])
                filteredData.update({ zip : entry["attributes"] })

    return filteredData

'''
data1 and data2 are dicts that look like
{ zip : { some info about the zip }}
'''
def mergeData(data1, data2):


def main():
    zipCodesToKeep = [94601, 94602]
    url1 = "https://services5.arcgis.com/ROBnTHSNjoZ2Wm1P/arcgis/rest/services/COVID_19_Statistics/FeatureServer/0/query?where=1%3D1&outFields=Zip_Number,Population,Cases,CaseRates&returnGeometry=false&outSR=4326&f=json"
    url2 = "https://services5.arcgis.com/ROBnTHSNjoZ2Wm1P/arcgis/rest/services/COVID_19_Statistics/FeatureServer/1/query?where=1%3D1&outFields=Zip_Number,PercentagePositiveTests&returnGeometry=false&outSR=4326&f=json"

    data1 = pullData(url1)
    filteredData1 = filterData(data1["features"], zipCodesToKeep)
    
    data2 = pullData(url2)
    filteredData2 = filterData(data2["features"], zipCodesToKeep)
    
    
    print(filteredData1)
    print(filteredData2)

main()