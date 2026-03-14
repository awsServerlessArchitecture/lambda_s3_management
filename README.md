---

# Automated S3 Bucket Cleanup Using AWS Lambda and Boto3

## 📌 Objective
This project demonstrates how to use **AWS Lambda** with **Boto3** to automatically delete files older than a specified threshold (10 minutes for testing, AS testign for 30 days is not possible coz s3 works on modified date not created date. an other bucket with old files can be used for 30 days testing) from an **Amazon S3 bucket**. It also integrates with **CloudWatch Logs** for monitoring and auditing.

---

## ⚙️ Setup Instructions

### 1. S3 Bucket
- Navigate to the **S3 dashboard**.
- Create a new bucket named:  
  **`heroviredb1`**
- Upload multiple files for testing.


---

### 2. IAM Role for Lambda
- Go to the **IAM dashboard**.
- Create a new role for **Lambda**.
- Attach the following policies:
  - `AmazonS3FullAccess` (for assignment simplicity).
  - `CloudWatchLogsFullAccess` (to allow Lambda to write logs).
- For production, replace with least‑privilege permissions:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": ["s3:ListBucket"],
        "Resource": "arn:aws:s3:::heroviredb1"
      },
      {
        "Effect": "Allow",
        "Action": ["s3:DeleteObject"],
        "Resource": "arn:aws:s3:::heroviredb1/*"
      },
      {
        "Effect": "Allow",
        "Action": [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource": "*"
      }
    ]
  }
  ```

---

### 3. Lambda Function (Python 3.x)

```python
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
```

---

### 4. Practical Testing Method
Since newly uploaded files always get a **current timestamp**, testing with a 30‑day threshold won’t work.  
Instead:
1. Upload a file to `heroviredb1`.
2. Wait at least **10 minutes**.
3. Invoke the Lambda function.
4. The file should be deleted, and its name will appear in the logs.

This simulates the cleanup logic without needing genuinely old files.

---

### 5. CloudWatch Logs View
- Lambda automatically streams logs to **CloudWatch**.
- Navigate to **CloudWatch → Logs → Log groups**.
- Find the log group:  
  `/aws/lambda/<your-function-name>`
- Each invocation creates a log stream containing:
  - Deleted file names (with bucket name included)  
  - Status messages  
  - Errors (if any)  

Example log entries:
```
Deleted file 'test1.txt' from bucket 'heroviredb1'
Deleted file 'report.pdf' from bucket 'heroviredb1'
Cleanup complete for bucket 'heroviredb1'
```

This ensures visibility into which files were removed and when.


