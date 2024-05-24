# trying waynes code to see if it works 
# the differences are: 
# I need to test without the GAE INSTANCE
# I am adding the app route to this code as well 

#WITH GAE INSTANCE


from flask import Flask, jsonify, render_template
from google.cloud import storage
import random
import os


# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\ANNE CREMONA\Downloads\gifted-pulsar-422809-q0-b4d9cc90c98c.json"


app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

# Initialize the Google Cloud Storage client
storage_client = storage.Client()
#bucket_name = os.environ.get('CLOUD_STORAGE_BUCKET', 'random-numbers1')
#bucket = storage_client.bucket(bucket_name)

bucket_name = 'random-numbers1'
bucket = storage_client.get_bucket(bucket_name)



def store_random_number_in_bucket(random_number, instance):
    """
    Stores the generated random number in the Cloud Storage bucket.
    """
    blob = bucket.blob(f'random_numbers/{instance}.txt')
    if blob.exists():
        data = blob.download_as_string().decode('utf-8')
        numbers = list(map(int, data.split(',')))
    else:
        numbers = []
    
    numbers.append(random_number)
    blob.upload_from_string(','.join(map(str, numbers)))

def fetch_random_numbers_from_bucket():
    """
    Fetches all random numbers stored in the Cloud Storage bucket.
    """
    numbers = []
    blobs = bucket.list_blobs(prefix='random_numbers/')
    
    for blob in blobs:
        data = blob.download_as_string().decode('utf-8')
        numbers.extend(map(int, data.split(',')))
    
    return numbers

# Define the endpoints


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/generate', methods=['GET'])
def generate_random_number():
    """
    Generates a single random number and stores it in the Cloud Storage bucket.
    """
    random_number = random.randint(0, 100000)
    instance = f'GAE_INSTANCE_{random.randint(1, 10000)}'
    
    # Store the random number in the Cloud Storage bucket
    store_random_number_in_bucket(random_number, instance)
    
    return jsonify({'randomNumber': random_number, 'instance': instance})

@app.route('/results', methods=['GET'])
def get_results():
    """
    Retrieves the minimum, maximum, and distinct instances of the generated random numbers.
    """
    # Fetch the random numbers from the Cloud Storage bucket
    random_numbers = fetch_random_numbers_from_bucket()
    
    min_number = min(random_numbers)
    max_number = max(random_numbers)
    instances = set(random_numbers)  # This should probably be modified to accurately reflect distinct instances if needed
    
    return jsonify({
        'min': min_number,
        'max': max_number,
        'instances': list(instances)
    })

if __name__ == '__main__':
    app.run(debug=True)
