from google.cloud import storage
import googleAuth
import os
import glob

def uploadFromDirectory(directoryPath: str, bucketName, destBlobName: str):
    relPaths = glob.glob(directoryPath + '/**', recursive=True)
    storageClient = storage.Client()
    bucket = storageClient.bucket(bucketName)
    for localFile in relPaths:
        remotePath = f'{destBlobName}/{"/".join(localFile.split(os.sep)[1:])}'
        if os.path.isfile(localFile):
            blob = bucket.blob(remotePath)
            blob.upload_from_filename(localFile)
            print('Uploading '+remotePath)

uploadFromDirectory('angels', 'maps.digitalcurator.art', 'angels')

