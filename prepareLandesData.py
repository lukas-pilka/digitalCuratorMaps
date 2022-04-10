import json
import os
import datetime
import csv
now = datetime.datetime.now()

# Opening JSON file
jsonFile = open('metadataSources/blm_codingDaVinci_20220328.json')
artifactsData = json.load(jsonFile)

# Reading image names
path, dirs, imageNames = next(os.walk("imageSources/landesImg"))
matchCounts = 0
csvRows = []
for imageName in imageNames:
    successMatch = False
    for artifact in artifactsData:
        if 'medium' in artifact.keys():
            for medium in artifact['medium']:

                # Matching image file name with medium field value in json data
                if medium['name'] == imageName:

                    matchCounts += 1
                    successMatch = True

                    # Filename
                    filename = medium['name']

                    # Category
                    if 'indigenebez' in artifact.keys():
                        category = artifact['indigenebez'].strip("»«").capitalize()
                    else:
                        category = ''

                    # Tags
                    tags = ''
                    if 'technik' in artifact.keys():
                        for technique in artifact['technik']:
                            if 'term' in technique.keys():
                                tags += technique['term'] + '|'

                    # Year
                    for dating in artifact["datierung"]:
                        if 'beginn' in dating.keys():
                            yearFrom = int(dating['beginn'])
                            yearTo = int(dating['ende'])
                            if yearTo > now.year:
                                yearTo = now.year
                            year = round((yearFrom + yearTo) / 2)
                            datingDescription = dating['term']
                        else:
                            year = ''

                    # Description
                    description = artifact['titel'] + ', ' + datingDescription + ', ' + artifact['invnr']

                    newRow = [filename, category, tags, description, '', year]

                    # Check if doesn't exist the item with same filename
                    currentlyAdded = False
                    for item in csvRows:
                        if item[0] == newRow[0]:
                            currentlyAdded = True

                    if currentlyAdded == False:
                        csvRows.append(newRow)

    if successMatch == False:
        os.remove('landesImg/' + imageName)

# Preparing CSV
with open('metadataSources/landesMetadata.csv', 'w', newline='') as csvfile:
    collectionWriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    collectionWriter.writerow(['filename','category','tags','description','permalink','year'])
    for row in csvRows:
        collectionWriter.writerow(row)

print('–––––')
print('Count of images: ' + str(len(imageNames)))
print('Count of matches with collection metadata: ' + str(matchCounts))
print('Count of items in csv: ' + str(len(csvRows)))


# Closing JSON file
jsonFile.close()