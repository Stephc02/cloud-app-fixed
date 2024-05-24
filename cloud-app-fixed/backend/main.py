import os
from flask import Flask, jsonify, render_template
import random
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\ANNE CREMONA\Downloads\gifted-pulsar-422809-q0-b4d9cc90c98c.json"

# app = Flask(__name__)
# do things with the gae instance 
# see if theres a delete button
# Initialize Storage client

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

@app.route('/')
def home():
    return render_template('index.html')


storage_client = storage.Client()
# bucket_name = os.environ.get('CLOUD_STORAGE_BUCKET', 'random-numbers1')
# bucket = storage_client.bucket(bucket_name)

bucket_name = 'random-numbers1'
bucket = storage_client.get_bucket(bucket_name)

# @app.route('/')   #change the route
# def home():
   # return "Backend Service"

@app.route('/generate_and_store', methods=['POST'])   #seems like 1 number is generated and is stored 
def generate_and_store():
    random_number = random.randint(0, 100000)
    
    blob = bucket.blob('random_numbers/numbers.txt')
    if blob.exists():
        data = blob.download_as_string().decode('utf-8')
        numbers = list(map(int, data.split(',')))
    else:
        numbers = []
    
    numbers.append(random_number)
    blob.upload_from_string(','.join(map(str, numbers)))



#This line is attempting to upload the generated random numbers
#to the Google Cloud Storage bucket using the upload_from_string method 
#of the blob object. However, the upload is 
#failing due to a rate limit exceeded error 
#(HTTP status code 429).



    
    return jsonify({"message": "Random number generated and stored successfully."})

@app.route('/get_results', methods=['GET'])
def get_results():
    blob = bucket.blob('random_numbers/numbers.txt')
    if blob.exists():
        data = blob.download_as_string().decode('utf-8')
        numbers = list(map(int, data.split(',')))
        
        smallest_number = min(numbers)
        largest_number = max(numbers)
        
        return jsonify({'smallest_number': smallest_number, 'largest_number': largest_number})
    else:
        return jsonify({'smallest_number': None, 'largest_number': None})

if __name__ == '__main__':
    app.run()
