import boto3
from datetime import datetime, timezone, timedelta

# Initialize S3 client
s3 = boto3.client('s3')

# Configuration
BUCKET_NAME = "heroviredb1"
MINUTES = 10   # threshold in minutes

def lambda_handler(event, context):
    deleted_files = []

    # List objects in the bucket
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    if 'Contents' not in response:
        print(f"Bucket '{BUCKET_NAME}' is empty")
        return {
            "status": "No objects found",
            "deleted_files": []
        }

    for obj in response['Contents']:
        file_name = obj['Key']
        last_modified = obj['LastModified']

        # Calculate file age
        file_age = datetime.now(timezone.utc) - last_modified

        # Delete if older than threshold
        if file_age > timedelta(minutes=MINUTES):
            s3.delete_object(
                Bucket=BUCKET_NAME,
                Key=file_name
            )
            print(f"Deleted file '{file_name}' from bucket '{BUCKET_NAME}'")
            deleted_files.append(file_name)

    return {
        "status": f"Cleanup complete for bucket '{BUCKET_NAME}'",
        "deleted_files": deleted_files
    }