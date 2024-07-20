import easyocr
import pprint
reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory
result = reader.readtext('easyocr_framework.jpeg')

pprint.pprint(result)