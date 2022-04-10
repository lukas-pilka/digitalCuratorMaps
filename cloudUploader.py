from google.cloud import storage
import googleAuth
import os
import glob

def uploadFromDirectory(directoryPath: str, bucketName, destBlobName: str):
    relPaths = glob.glob(directoryPath + '/**', recursive=True)
    storageClient = storage.Client()
    bucket = storageClient.bucket(bucketName)
    for localFile in relPaths:
        # [2:] in remotePath means that first two parts in paths will be cut for Google Bucket deployment
        remotePath = f'{destBlobName}/{"/".join(localFile.split(os.sep)[2:])}'
        if os.path.isfile(localFile):
            blob = bucket.blob(remotePath)
            blob.upload_from_filename(localFile)
            print('Uploading '+remotePath)

uploadFromDirectory('atlases/landesmuseum', 'maps.digitalcurator.art', 'landesmuseum')

