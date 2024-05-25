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
try:
    GAE_INSTANCE = os.environ.get('GAE_INSTANCE')
    if GAE_INSTANCE is None:
        GAE_INSTANCE = 'Unknown'
    logging.info(f"GAE_INSTANCE: {GAE_INSTANCE}")
except Exception as e:
    logging.error(f"Error fetching GAE_INSTANCE: {e}")
    GAE_INSTANCE = 'Unknown'

def fetch_random_numbers_from_bucket():
    """
    Fetches all random numbers stored in the Cloud Storage bucket.
    """
    numbers = []
    blobs = bucket.list_blobs(prefix='random_numbers/')
    for blob in blobs:
        try:
            data = blob.download_as_string().decode('utf-8')
            numbers.append(int(data))
        except Exception as e:
            logging.error(f"Error decoding random number from blob {blob.name}: {e}")
    return numbers

def store_random_number(random_number):
    """
    Stores a random number in the Cloud Storage bucket.
    """
    blob = bucket.blob(f'random_numbers/{random_number}.txt')
    try:
        blob.upload_from_string(str(random_number))
        logging.info(f"Instance {GAE_INSTANCE} stored random number {random_number}")
    except Exception as e:
        logging.error(f"Instance {GAE_INSTANCE} error storing random number {random_number}: {e}")

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
    store_random_number(random_number)
    return jsonify({'randomNumber': random_number})

@app.route('/results', methods=['GET'])
def get_results():
    random_numbers = fetch_random_numbers_from_bucket()
    if not random_numbers:
        return jsonify({'error': 'No random numbers found'}), 404
    min_number = min(random_numbers)
    max_number = max(random_numbers)
    return jsonify({'min': min_number, 'max': max_number})

if __name__ == '__main__':
    app.run(host='127.0.0.0', port=8080)
