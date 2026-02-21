import sys
import os
import re
from datetime import datetime
from google.cloud import storage

# Patterns that indicate a successful run (final outcome)
SUCCESS_MARKERS = re.compile(
    r"Apply complete!|Destroy complete!|No changes\."
)
# Patterns that indicate a failed run
ERROR_MARKERS = re.compile(r"Error:|Error \d+:|\bError\b", re.IGNORECASE)


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


def is_failed_run(log_text):
    """Treat as failure if we see error markers or never see success markers."""
    has_error = bool(ERROR_MARKERS.search(log_text))
    has_success = bool(SUCCESS_MARKERS.search(log_text))
    return has_error or not has_success


def upload_to_gcs(bucket_name, content, action_type, failed=False):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    now = datetime.utcnow()
    date_folder = now.strftime("%d-%m-%Y")
    timestamp = now.strftime("%d-%m-%Y_%H-%M-%S")

    # Use "Failed" subfolder under the same date when the run failed
    subfolder = "Failed" if failed else action_type
    blob_name = f"{date_folder}/{subfolder}/{timestamp}_tf_audit.txt"

    blob = bucket.blob(blob_name)
    blob.upload_from_string(content, content_type="text/plain")
    label = "failure/error" if failed else "parsed audit"
    print(f"✅ Successfully uploaded {label} log to gs://{bucket_name}/{blob_name}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python audit_parser.py <log_file_path> <gcs_bucket_name> <action_type>")
        sys.exit(1)

    log_file = sys.argv[1]
    bucket_name = sys.argv[2]
    action_type = sys.argv[3]  # E.g., "Plan-and-Apply" or "Destroy"

    if not os.path.isfile(log_file):
        # Previous step failed before writing any output; still upload to Failed/
        content = (
            f"[No log file produced]\n"
            f"The Terraform step may have failed before writing output.\n"
            f"Action type: {action_type}\n"
        )
        upload_to_gcs(bucket_name, content, action_type, failed=True)
        sys.exit(0)

    with open(log_file, "r") as f:
        raw_log = f.read()

    if is_failed_run(raw_log):
        # Upload full log to Failed/ so dashboard can show errors
        upload_to_gcs(bucket_name, raw_log, action_type, failed=True)
        sys.exit(0)

    parsed_content = parse_terraform_log(raw_log)

    if parsed_content.strip():
        upload_to_gcs(bucket_name, parsed_content, action_type, failed=False)
    else:
        # No plan/summary found but no clear error either; upload raw to Failed/ for visibility
        upload_to_gcs(bucket_name, raw_log, action_type, failed=True)