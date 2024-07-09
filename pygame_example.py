import cv2
import urllib.request
import numpy as np
import time
import os
import pandas as pd
import easyocr
import pprint
from gtts import gTTS
import pygame
from http.client import IncompleteRead
import tempfile

# Initialize pygame mixer
pygame.mixer.init()

# Replace the URL with the IP camera's stream URL
url = 'http://192.168.0.104/cam-hi.jpg'
print('Opening Window')
cv2.namedWindow("live Cam Testing", cv2.WINDOW_AUTOSIZE)

reader = easyocr.Reader(['en'])  # this needs to run only once to load the model into memory

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
            img_resp = urllib.request.urlopen(url)
            print(img_resp)
            imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            im = cv2.imdecode(imgnp, -1)
            result = reader.readtext(im)
            pprint.pprint(result)

            if len(result) > 0:
                # Create a DataFrame for easier sorting
                df = pd.DataFrame(result, columns=["box", "text", "confidence"])
                df["area"] = df["box"].apply(calculate_area)

                # Sort by area in descending order
                df_sorted = df.sort_values(by="area", ascending=False).reset_index(drop=True)
                text = df_sorted.iloc[0]['text']
                if len(df_sorted) > 1:
                    if df_sorted.iloc[1]['area'] >= df_sorted.iloc[0]['area'] * 0.75:
                        text += ' ' + df_sorted.iloc[1]['text']

                print(text)

                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                    temp_audio_path = temp_audio.name
                    tts = gTTS(text=text, lang='id')
                    tts.save(temp_audio_path)

                try:
                    time.sleep(0.2)
                    pygame.mixer.music.load(temp_audio_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.2)
                except pygame.error as e:
                    print(f"Error playing sound: {e}")

                try:
                    os.remove(temp_audio_path)
                except Exception as e:
                    print(f"Error deleting sound: {e}")


            cv2.imshow('live Cam Testing', im)
        except IncompleteRead:
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            continue
        
        key = cv2.waitKey(5)
        if key == ord('q'):
            break
        
    cv2.destroyAllWindows()

if __name__ == '__main__':
    print("started")
    main()