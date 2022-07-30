from flask import Flask, flash, request, redirect, url_for, render_template, Blueprint
# from werkzeug.utils import secure_filename, os

# from keras.applications.mobilenet_v2 import MobileNetV2
# from keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
# from tensorflow.keras.preprocessing import image

# import numpy as np
# import pandas as pd



from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from azure.storage.blob import BlobClient

from array import array
import os
from PIL import Image
import sys
import time

## Define static variables and paths
UPLOAD_FOLDER = 'website/static/'

## Define the blueprint
views = Blueprint('views', __name__)

## Load the model.
#model = MobileNetV2(weights='imagenet')


## Define the allowed file extensions
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'pdf', 'tif'])
def allowed_filename(name):
    return '.' in name and name.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


## Define the route for the home page
@views.route('/', methods=['GET'])
def home():
    return render_template("index.html")


@views.route('/', methods=['POST'])
def main_function():
    
    '''
    Authenticate
    Authenticates your credentials and creates a client.
    '''
    subscription_key = "961fcfae50984882891cbdc0241d6db4"
    endpoint = "https://kbcvforocr.cognitiveservices.azure.com/"

    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))



    '''
    END - Authenticate
    '''

    '''
    OCR: Read File using the Read API, extract text - remote
    This example will extract text in an image, then print results, line by line.
    This API call can also extract handwriting style text (not shown).
    '''
    #print("===== Read File - remote =====")
    # Get an image with text

    # if 'file' not in request.files:
    #     flash('No file was uploaded.')
    #     return redirect(request.url) 
   
    # file = request.files['file']

    # if file.filename == '':
    #     flash('No image selected for uploading')
    #     return redirect(request.url)

    # if file and allowed_filename(file.filename):
    #     filename = secure_filename(file.filename)
    #     file.save(os.path.join(UPLOAD_FOLDER, filename))

    #blob = BlobClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=kbfilesforocr;AccountKey=zh7tNwc6b7Wyrj6xdyCDKXtKs101qJ19F6lw5gxg+QsWGVr73+Zi+/jIxThPMMTuJPAmkv0jIbpr+ASt0Seiow==;EndpointSuffix=core.windows.net", container_name="drawings", blob_name=filename) 


    # with open(UPLOAD_FOLDER + filename, "rb") as data:
    #     blob.upload_blob(data)

    filename = "b92001.pdf"
    read_image_url = "https://kbfilesforocr.blob.core.windows.net/drawings/" + filename
    print(read_image_url)

    # Call API with URL and raw response (allows you to get the operation location)
    read_response = computervision_client.read(read_image_url,  raw=True)

    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results 
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Print the detected text, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                flash(line.text)
                flash(line.bounding_box)
                return render_template('index.html')

    flash()
    '''
    END - Read File - remote
    '''

    flash("End of Computer Vision quickstart.")
    return render_template('index.html')


# def upload_image():

    # if 'file' not in request.files:
    #     flash('No file was uploaded.')
    #     return redirect(request.url) 
   
    # file = request.files['file']

    # if file.filename == '':
    #     flash('No image selected for uploading')
    #     return redirect(request.url)

    # if file and allowed_filename(file.filename):

    #     filename = secure_filename(file.filename)
    #     file.save(os.path.join(UPLOAD_FOLDER, filename))

#         img = image.load_img(os.path.join(UPLOAD_FOLDER, filename), target_size=(224, 224))
#         img = image.img_to_array(img)
#         img = np.expand_dims(img, axis=0)
#         img = preprocess_input(img)

#         preds = model.predict(img)
#         predictions = decode_predictions(preds, top=5)[0]
#         predictions_filtered = pd.DataFrame.from_records(predictions, columns =['class_name', 'class_description', 'score']).query("class_description in ('bullet_train', 'electric_locomotive','freight_car', 'steam_locomotive')")
        
#         if predictions_filtered.size == 0:
#             flash('This is not a train 😒')
#             return render_template('index.html', filename=filename)
#             #return str(predictions)
#         else:
#             score = predictions_filtered['score'].iloc[0]
#             flash('It is a train! 😍')
#             return render_template('index.html', filename=filename)

#     else:
#         flash('Not an allowed file type, please use png, jpg, jpeg, gif.')
#         return redirect(request.url)


@views.route('/display/<filename>', methods=['GET'])
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

