import logging
from flask import Flask, jsonify, request
from google.cloud import storage
import random
import os
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Initialize the Google Cloud Storage client
storage_client = storage.Client()
bucket_name = os.environ.get('CLOUD_STORAGE_BUCKET', 'random-numbers1')
bucket = storage_client.bucket(bucket_name)

# Fetch GAE instance ID if available
GAE_INSTANCE = os.environ.get('GAE_INSTANCE', 'Unknown')
logging.info(f"GAE_INSTANCE: {GAE_INSTANCE}")

@app.route('/')
def home():
    logging.info(f"Instance {GAE_INSTANCE} handling the request")
    return jsonify({'message': 'Backend is running'}), 200

@app.route('/delete_bucket_contents', methods=['POST'])
def delete_bucket_contents():
    try:
        subprocess.run(['gsutil', '-m', 'rm', '-r', f'gs://{bucket_name}/*'], check=True)
        logging.info(f"Instance {GAE_INSTANCE} deleted bucket contents")
        return jsonify({'message': 'Bucket contents deleted successfully'}), 200
    except subprocess.CalledProcessError as e:
        logging.error(f"Instance {GAE_INSTANCE} error deleting bucket contents: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['GET'])
def generate_random_number():
    random_number = random.randint(0, 100000)
    blob = bucket.blob(f'random_numbers/{random_number}.txt')
    try:
        blob.upload_from_string(str(random_number))
        logging.info(f"Instance {GAE_INSTANCE} generated and stored random number {random_number}")
        return jsonify({'randomNumber': random_number})
    except Exception as e:
        logging.error(f"Instance {GAE_INSTANCE} error storing random number {random_number}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/results', methods=['GET'])
def get_results():
    try:
        blobs = bucket.list_blobs(prefix='random_numbers/')
        random_numbers = [int(blob.download_as_string()) for blob in blobs]
        min_number = min(random_numbers)
        max_number = max(random_numbers)
        logging.info(f"Instance {GAE_INSTANCE} fetched results: min {min_number}, max {max_number}")
        return jsonify({'min': min_number, 'max': max_number})
    except Exception as e:
        logging.error(f"Instance {GAE_INSTANCE} error fetching results: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.0', port=8080)

  

