from flask import Flask, jsonify, render_template
from google.cloud import storage
import random
import os
import subprocess

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\ANNE CREMONA\Downloads\gifted-pulsar-422809-q0-b4d9cc90c98c.json"

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

# Initialize the Google Cloud Storage client
storage_client = storage.Client()
bucket_name = 'random-numbers1'
bucket = storage_client.get_bucket(bucket_name)

def fetch_random_numbers_from_bucket():
    """
    Fetches all random numbers stored in the Cloud Storage bucket.
    """
    numbers = []
    blobs = bucket.list_blobs(prefix='random_numbers/')
    
    try:
        for blob in blobs:
            data = blob.download_as_string().decode('utf-8')
            numbers.append(int(data))
        print(f"Fetched random numbers from bucket: {numbers}")
    except Exception as e:
        print(f"Error fetching random numbers from bucket: {e}")
    
    return numbers

# Define the endpoints
@app.route('/')
def home():
    print("Rendering home page")
    return render_template('index3.html')

#added delete button 
@app.route('/delete_bucket_contents', methods=['POST'])
def delete_bucket_contents():
    try:
        # Use subprocess to execute gsutil command to delete all objects in the bucket
        subprocess.run(['gsutil', '-m', 'rm', '-r', f'gs://{bucket_name}/*'])

        return jsonify({'message': 'Bucket contents deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/generate', methods=['GET'])
def generate_random_number():
    """
    Generates a single random number and stores it in the Cloud Storage bucket.
    """
    random_number = random.randint(0, 100000)
    
    # Store the random number in the Cloud Storage bucket
    blob = bucket.blob(f'random_numbers/{random_number}.txt')
    try:
        blob.upload_from_string(str(random_number))
        print(f"Stored random number {random_number} in bucket")
    except Exception as e:
        print(f"Error storing random number {random_number} in bucket: {e}")
    
    print(f"Generated and stored random number: {random_number}")
    return jsonify({'randomNumber': random_number})

@app.route('/results', methods=['GET'])
def get_results():
    """
    Retrieves the minimum, maximum, and distinct instances of the generated random numbers.
    """
    print("Request received for results")
    
    # Fetch the random numbers from the Cloud Storage bucket
    random_numbers = fetch_random_numbers_from_bucket()
    
    min_number = min(random_numbers)
    max_number = max(random_numbers)
    #  instances = len(set(random_numbers))  # Count distinct instances
    
     # print(f"Calculated results: Min={min_number}, Max={max_number}, Instances={instances}")
    print(f"Calculated results: Min={min_number}, Max={max_number}")
    
    return jsonify({
        'min': min_number,
        'max': max_number,
         # 'instances': instances
    })

if __name__ == '__main__':
    app.run()
