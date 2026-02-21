import sys
import re
from datetime import datetime
from google.cloud import storage

def parse_terraform_log(log_text):
    output = []
    is_capturing_diff = False

    start_diff_pattern = re.compile(r"Terraform will perform the following actions:|Terraform used the selected providers to generate the following execution plan\.")
    summary_pattern = re.compile(r"^(Plan:|Apply complete!|Destroy complete!|No changes\.)")

    for line in log_text.splitlines():
        if start_diff_pattern.search(line):
            is_capturing_diff = True
            output.append(line)
            continue

        if summary_pattern.search(line):
            output.append(line)
            is_capturing_diff = False 
            continue

        if is_capturing_diff:
            output.append(line)

    return "\n".join(output)

def upload_to_gcs(bucket_name, content, action_type):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # NEW HIERARCHY: DD-MM-YYYY / Action_Type / DD-MM-YYYY_HH-MM-SS_tf_audit.txt
    now = datetime.utcnow()
    
    date_folder = now.strftime("%d-%m-%Y") 
    timestamp = now.strftime("%d-%m-%Y_%H-%M-%S")
    
    blob_name = f"{date_folder}/{action_type}/{timestamp}_tf_audit.txt"

    blob = bucket.blob(blob_name)
    blob.upload_from_string(content, content_type="text/plain")
    print(f"✅ Successfully uploaded parsed audit log to gs://{bucket_name}/{blob_name}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python audit_parser.py <log_file_path> <gcs_bucket_name> <action_type>")
        sys.exit(1)

    log_file = sys.argv[1]
    bucket_name = sys.argv[2]
    action_type = sys.argv[3] # E.g., "Plan-and-Apply" or "Destroy"

    with open(log_file, "r") as f:
        raw_log = f.read()

    parsed_content = parse_terraform_log(raw_log)

    if parsed_content.strip():
        upload_to_gcs(bucket_name, parsed_content, action_type)
    else:
        print("No Terraform changes or summaries found in log to upload.")