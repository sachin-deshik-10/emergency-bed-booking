import firebase_admin
from firebase_admin import credentials
from google.cloud import storage

# Initialize Firebase Admin SDK
cred = credentials.Certificate('emergencybooking-31043-firebase-adminsdk-l69k0-98c85bc3f2.json')
firebase_admin.initialize_app(cred)

# Initialize Google Cloud Storage client
storage_client = storage.Client.from_service_account_json('emergencybooking-31043-firebase-adminsdk-l69k0-98c85bc3f2.json')


def download_pdf_from_storage(bucket_name, file_name, destination_path):
    try:
        # Get the bucket
        bucket = storage_client.bucket(bucket_name)

        # Get the blob (file) from the bucket
        blob = bucket.blob(file_name)

        # Download the PDF file
        blob.download_to_filename(destination_path)

        print(f"PDF file downloaded successfully to: {destination_path}")
    except Exception as e:
        print(f"Error downloading PDF file: {e}")


# Specify the Firebase Storage bucket name, PDF file name, and destination path to save the file
bucket_name = 'emergencybooking-31043'
pdf_file_name = '6th Maths Unit 9 Lesson Plan.pdf'
destination_path = 'filepth'

# Call the function to download the PDF file
download_pdf_from_storage(bucket_name, pdf_file_name, destination_path)
