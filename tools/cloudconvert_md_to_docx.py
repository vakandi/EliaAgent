#!/usr/bin/env python3
"""
CloudConvert API - MD to DOCX Converter
Uses CloudConvert API v2 to convert markdown files to DOCX
"""

import os
import json
import time
import requests
from pathlib import Path

# Configuration
API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiYmE3YmM1YWU3NjZlMGEyZTMwMTg2ZTU4YzA0ZDA3ZGE3MzgwNjJkOTEzOWJiNjI1YTdkYWEzYzQ3N2EzNTk2OGQwMDgwMzJiZDVlZmI4YmQiLCJpYXQiOjE3NzQyMjM5MDMuMjA3NzU1LCJuYmYiOjE3NzQyMjM5MDMuMjA3NzU2LCJleHAiOjQ5Mjk4OTc1MDMuMjAwMzkxLCJzdWIiOiI3NDgwOTY4MSIsInNjb3BlcyI6WyJ1c2VyLnJlYWQiLCJ1c2VyLndyaXRlIiwidGFzay5yZWFkIiwidGFzay53cml0ZSIsIndlYmhvb2sucmVhZCIsIndlYmhvb2sud3JpdGUiLCJwcmVzZXQucmVhZCIsInByZXNldC53cml0ZSJdfQ.gVv0wk-Srr4ao87Mfg_Y7uiXitTYKRXCRaEFiz04CF6aSOcdvAHrAQBg_obDeRGw04CBx_E2-s6xus2AciLCYbMo_vx_rGGuFJ_U49COxslHS8bEP909bI3Zx84ARy4Wt8MWf8zSUm3goPVDLr8fzvtCtRQUH9ST3aDzJNUr7s6Ff7VbVAEBgjiVRIEXTVvpUuzIKOGiz1YBe6c4VHneVHCAPR9DYaqOVL53I_zrx5djSebD6ykIka_ohUJ0wYFnATD05SE_4yvxU2qWQopxOIf6865h8sh-WGShs-4cz9trPqNuoYcWETiBAccBV1GDDrUBmjT-HtiyFltwG-O3zQ3UHVJ1L4u7WDcMEqiAwrS-BEfeB8qB8n8YMpwq9td9QuvD2k2AEt3olgyY6pMqpeNGoYwmKVN2O_3wshW5ud12anqgo0ZejjWmqsRWdZcQtGcAduhTSLc8vRf58bGP_-6kxCF9gdbMuDQ1S_iBH0aHZ2GAdtlOYCAgbNJR6aH_zMSQ3Ir5yCOEUrXZIeL68fWDJ_E8BrsH_7bXiyy3kjK4a4MhpCfMQeTT8fsprEx7hXH8aAgEJhjuA0Xlvqj5qlh7K8b__GrLvWVeBrjP9WSpDccv1FVsViWUCLEjDxGI6RLqT-yxB8rHQfBDYYLH0zKjkxgCP2JpTL3c_sX4D0U"
BASE_URL = "https://api.cloudconvert.com/v2"


def create_job_with_upload(input_file_path, output_format="docx"):
    """
    Create a job that uploads a local file, converts it, and returns a download URL.
    Uses the import/upload task to handle local files.
    """
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    filename = os.path.basename(input_file_path)

    # Step 1: Create job with import/upload, convert, and export tasks
    job_payload = {
        "tasks": {
            "import-file": {"operation": "import/upload", "filename": filename},
            "convert-file": {
                "operation": "convert",
                "input": "import-file",
                "output_format": output_format,
            },
            "export-file": {"operation": "export/url", "input": "convert-file"},
        }
    }

    response = requests.post(f"{BASE_URL}/jobs", headers=headers, json=job_payload)

    if response.status_code < 200 or response.status_code >= 300:
        print(f"Error creating job: {response.text}")
        return None

    job = response.json()["data"]
    print(f"Job created: {job['id']}")

    # Find the upload task
    import_task = None
    for task in job["tasks"]:
        if task["name"] == "import-file":
            import_task = task
            break

    if not import_task or "result" not in import_task:
        print("Error: No upload URL in response")
        return None

    # Upload URL is in result.form.url
    upload_url = import_task["result"]["form"]["url"]
    upload_params = import_task["result"]["form"]["parameters"]
    print(f"Upload URL: {upload_url}")

    # Step 2: Upload the file with all form parameters
    with open(input_file_path, "rb") as f:
        files = {"file": (filename, f)}
        upload_response = requests.post(upload_url, data=upload_params, files=files)

    if upload_response.status_code not in [200, 201]:
        print(f"Error uploading file: {upload_response.text}")
        return None

    print("File uploaded successfully")

    return job["id"]


def wait_for_job(job_id, max_wait=120):
    """Wait for job to complete"""
    headers = {"Authorization": f"Bearer {API_KEY}"}

    start_time = time.time()
    while time.time() - start_time < max_wait:
        response = requests.get(f"{BASE_URL}/jobs/{job_id}", headers=headers)

        if response.status_code != 200:
            print(f"Error checking job: {response.text}")
            return None

        job = response.json()["data"]
        status = job["status"]

        print(f"Job status: {status}")

        if status == "finished":
            # Find export task to get download URL
            for task in job["tasks"]:
                if task["name"] == "export-file" and "result" in task:
                    # Export result might have url or files
                    result = task["result"]
                    if "url" in result:
                        return result["url"]
                    elif "files" in result and result["files"]:
                        return result["files"][0]["url"]
            return None
        elif status == "error":
            for task in job["tasks"]:
                if task["status"] == "error":
                    print(f"Error: {task.get('message', 'Unknown error')}")
            return None

        time.sleep(2)

    print("Job timed out")
    return None


def convert_md_to_docx(input_file, output_file=None):
    """
    Convert a markdown file to DOCX using CloudConvert API.

    Args:
        input_file: Path to the input markdown file
        output_file: Path for the output DOCX file (optional)

    Returns:
        Path to the downloaded DOCX file, or None on failure
    """
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_file}")
        return None

    if output_file is None:
        output_file = input_path.with_suffix(".docx")

    print(f"Converting {input_file} to DOCX...")

    # Create job and upload file
    job_id = create_job_with_upload(str(input_path))
    if not job_id:
        return None

    # Wait for conversion to complete
    download_url = wait_for_job(job_id)
    if not download_url:
        print("Conversion failed")
        return None

    print(f"Download URL: {download_url}")

    # Download the converted file
    response = requests.get(download_url)
    if response.status_code != 200:
        print(f"Error downloading file: {response.text}")
        return None

    with open(output_file, "wb") as f:
        f.write(response.content)

    print(f"✓ Converted file saved to: {output_file}")
    return str(output_file)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert MD to DOCX using CloudConvert API"
    )
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument(
        "-o", "--output", help="Output DOCX file (default: same name with .docx)"
    )

    args = parser.parse_args()

    result = convert_md_to_docx(args.input, args.output)

    if result:
        print(f"\n✅ Success! File saved to: {result}")
    else:
        print("\n❌ Conversion failed")


if __name__ == "__main__":
    main()
