from clarifai.rest import ClarifaiApp

app=ClarifaiApp (api_key='ba18384f19dc4e6b95bd1c76f356d308')
model = app.models.get('color')
response = model.predict_by_url(url='https://samples.clarifai.com/metro-north.jpg')
print response