import google.cloud
from google.cloud import storage

bucket_name = "user-ocr-files"
client = storage.Client()
file_hash = "abcdefx00"
filename = "CSCI5253ProjectProposal.pdf"
try:
    bucket = client.get_bucket(bucket_name)
except google.cloud.exceptions.NotFound:
    print("Sorry, that bucket does not exist!")
    bucket = storage.Bucket(client, name=bucket_name, user_project="scalableocr")
    bucket.location = "us"
    bucket.storage_class = "COLDLINE"
    bucket = client.create_bucket(bucket)

blob = storage.Blob(file_hash, bucket)
blob.upload_from_filename(filename)