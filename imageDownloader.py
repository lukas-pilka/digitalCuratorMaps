from google.cloud import storage
import requests
from requests.auth import HTTPBasicAuth
import config
import json
import csv

#LIST OF ITEMS FOR DOWNLOAD
elasticIdsList = []

# CONNECTION TO ELASTIC SEARCH
def load10kFromElastic(afterId):
    query = {
        "size":10000,
        "query": {
        "bool": {
            "must": [
                {
                    "range": {
                        "date_earliest": {
                            "gte": 1350,
                            "lt": 1850
                        }
                    }
                },
                {
                    "nested": {
                        "path": "detected_objects",
                        "query": {
                            "bool": {
                                "should": [
                                    {"bool": {
                                        "must": [
                                            {"match": {"detected_objects.object": "Angel"}},
                                            {"range": {"detected_objects.score": {"gt": 0.75}}}
                                        ]
                                    }
                                    },
                                    {"bool": {
                                        "must": [
                                            {"match": {"detected_objects.object": "Putto"}},
                                            {"range": {"detected_objects.score": {"gt": 0.8}}}
                                        ]
                                    }
                                    }
                                ]
                            }
                        }
                    }
                },
                {
                    "bool": {
                        "should": config.supportedWorkTypes
                    }
                }
            ]
        }
    },
        "search_after": [afterId],
        "sort": [
            {"_id": "asc"}
        ]
    }

    rawData = requests.get('https://66f07727639d4755971f5173fb60e420.europe-west3.gcp.cloud.es.io:9243/artworks/_search',
                           auth=HTTPBasicAuth(config.userDcElastic, config.passDcElastic), json=query)
    rawData.encoding = 'utf-8'
    dataDict = json.loads(rawData.text)
    artworks = dataDict['hits']['hits']
    csvHeader = ['filename', 'category', 'tags', 'description','permalink','year']

    # preparing CSV

    with open('metadataSources/downloadedItems.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csvHeader)

        # Iterating through artworks

        for artwork in artworks:
            elasticIdsList.append(artwork['_id'])
            fileName = artwork['_id']+'.jpg'
            dating = str(artwork['_source']['date_earliest'])
            if 'author' in artwork['_source'].keys():
                author = artwork['_source']['author'][0]
            else:
                author = ''
            description = author + ', '+ artwork['_source']['title'] + ', ' + dating + ', ' + artwork['_source']['gallery']
            year = artwork['_source']['date_earliest']
            if 'gallery_url' in artwork['_source'].keys():
                galleryUrl = artwork['_source']['gallery_url']
            else:
                galleryUrl = ''
            csvRow = [fileName,'','',description,galleryUrl,year]
            writer.writerow(csvRow)
            print(csvRow)
        print(len(artworks))

def loadAllFromElastic():
    for request in range(1):
        print('Loading IDs...')
        if len(elasticIdsList) >= 1:
            load10kFromElastic(elasticIdsList[-1])
        else:
            load10kFromElastic('')
        print('IDs loaded: ' + str(len(elasticIdsList)) + ', Last one: ' + elasticIdsList[-1])

# CONNECTING TO BUCKET
def download_blob(source_blob_name, destination_file_name):

    storageClient = storage.Client()
    bucket = storageClient.bucket('tfcurator-artworks')
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )


loadAllFromElastic()
counter = 0
for id in elasticIdsList:
    sourceFileName = 'artworks-all/'+id+'.jpg'
    destinationFileName = 'angelsImg/'+id+'.jpg'
    download_blob(sourceFileName,destinationFileName)
    counter += 1
    print(counter)
