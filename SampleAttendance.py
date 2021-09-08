from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.prediction.models import (
    ImageUrl,
    ImagePrediction,
)
from msrest.authentication import ApiKeyCredentials
import os


projectid = "75f5bd51-949f-4616-8376-4a82a51b162a"
publish_iteration_name = "Iteration3"
ENDPOINT = "https://deiface.cognitiveservices.azure.com/"
prediction_key = "7bb53499bc494fa09b32fb0c79188d49"


prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)



prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)


with open(os.path.join(f"assets/img/users/maxim.jpg"), "rb") as image_contents:
    results = predictor.classify_image(
        projectid, publish_iteration_name, image_contents.read())

    # Display the results.
    #for prediction in results.predictions:
      #  print("\t" + prediction.tag_name +
           #   ": {0:.2f}%".format(prediction.probability * 100))
    print(results.predictions[0].tag_name)
