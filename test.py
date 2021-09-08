from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
import os, time, uuid

ENDPOINT = "https://deiface.cognitiveservices.azure.com/"
training_key = "211b7c76494b4054a2a24fb559d86c8f"
prediction_key = '211b7c76494b4054a2a24fb559d86c8f'
prediction_resource_id = "75f5bd51-949f-4616-8376-4a82a51b162a"
ProjectID= '75f5bd51-949f-4616-8376-4a82a51b162a'
ProjectName= "DEIFace"
iteration= "classifyModel"


# Now there is a trained endpoint that can be used to make a prediction
prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)

with open(os.path.join(f"assets/img/users/res.jpg"), "rb") as image_contents:
    results = predictor.classify_image(
        ProjectID, iteration, image_contents.read())

    # Display the results.
    for prediction in results.predictions:
        print("\t" + prediction.tag_name +
              ": {0:.2f}%".format(prediction.probability * 100))