from http.client import IncompleteRead
import cv2
import urllib.request
import numpy as np
import time, os
import pandas as pd

import easyocr
import pprint

from gtts import gTTS
from playsound import playsound, PlaysoundException

# Replace the URL with the IP camera's stream URL
url = 'http://192.168.0.104/cam-hi.jpg'
print('Opening Window')
cv2.namedWindow("live Cam Testing", cv2.WINDOW_AUTOSIZE)

reader = easyocr.Reader(['en']) # this needs t`o run only once to load the model into memory

if os.path.exists("output.mp3"):
    os.remove("output.mp3")

print('Displaying...')

def calculate_area(box):
    height = box[2][1] - box[0][1]
    return height


def main():
# Read and display video frames
    while True:
        # Read a frame from the video stream
        time.sleep(0.1)
        try: 
            print('Requesting..')
            img_resp=urllib.request.urlopen(url)
            print(img_resp)
            imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
            #ret, frame = cap.read()
            im = cv2.imdecode(imgnp,-1)
            result = reader.readtext(im)
            pprint.pprint(result)


            if len(result) > 0:
                # Create a DataFrame for easier sorting
                df = pd.DataFrame(result, columns=["box", "text", "confidence"])
                df["area"] = df["box"].apply(calculate_area)

                # Sort by area in descending order
                df_sorted = df.sort_values(by="area", ascending=False).reset_index(drop=True)
                text = df_sorted.iloc[0]['text']
                if len(df_sorted)>1:
                    if df_sorted.iloc[1]['area'] >= df_sorted.iloc[0]['area'] * 0.8:
                        text += ' ' + df_sorted.iloc[1]['text']

                print(text)


                tts = gTTS(text=text, lang='id')
                tts.save("output.mp3")

                
                try:
                    time.sleep(0.2)
                    playsound('output.mp3')
                except PlaysoundException as e:
                    print(f"Error playing sound: {e}")

                if os.path.exists("output.mp3"):
                    os.remove("output.mp3")




            cv2.imshow('live Cam Testing',im)
        except IncompleteRead:
            continue
        key=cv2.waitKey(5)
        if key==ord('q'):
            break
        
    cv2.destroyAllWindows()

if __name__ == '__main__':
    print("started")
    main()