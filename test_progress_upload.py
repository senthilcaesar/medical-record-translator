import requests
import time
import json

# Test file upload and progress tracking
def test_upload_progress():
    # Use the sample PDF file
    file_path = "sample_lab_report.pdf"
    
    # Upload the file
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'application/pdf')}
        response = requests.post('http://localhost:8000/api/v1/translate/upload', files=files)
    
    if response.status_code != 200:
        print(f"Upload failed: {response.text}")
        return
    
    upload_data = response.json()
    job_id = upload_data['job_id']
    print(f"Upload successful. Job ID: {job_id}")
    
    # Poll for status
    while True:
        status_response = requests.get(f'http://localhost:8000/api/v1/translate/status/{job_id}')
        if status_response.status_code != 200:
            print(f"Status check failed: {status_response.text}")
            break
        
        status_data = status_response.json()
        print(f"Status: {status_data['status']}, Progress: {status_data['progress']}%")
        
        if status_data['status'] in ['completed', 'failed']:
            print(f"Final status: {status_data['status']}")
            break
        
        time.sleep(0.2)  # Poll every 200ms to catch all progress updates

if __name__ == "__main__":
    test_upload_progress()
