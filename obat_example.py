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
from fuzzywuzzy import process

# Initialize pygame mixer
pygame.mixer.init()

# Load medicine data
med_df = pd.read_csv('obat.csv')

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
    while True:
        time.sleep(2)
        try:
            img_resp = urllib.request.urlopen(url)
            imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            im = cv2.imdecode(imgnp, -1)
            result = reader.readtext(im)
            pprint.pprint(result)

            if len(result) > 0:
                df = pd.DataFrame(result, columns=["box", "text", "confidence"])
                df["area"] = df["box"].apply(calculate_area)
                df_sorted = df.sort_values(by="area", ascending=False).reset_index(drop=True)
                text = df_sorted.iloc[0]['text']
                if len(df_sorted) > 1 and df_sorted.iloc[1]['area'] >= df_sorted.iloc[0]['area'] * 0.75:
                    text += ' ' + df_sorted.iloc[1]['text']

                # Fuzzy matching to find the closest medicine name
                best_match = process.extractOne(text, med_df['NAMA'], score_cutoff=70)
                if best_match:
                    matched_data = med_df[med_df['NAMA'] == best_match[0]].iloc[0]
                    details = f"Nama obat: {matched_data['NAMA']}, Jenis Takaran: {matched_data['Jenis/Takaran']}, Instruksi Pemakaian: {matched_data['Instruksi Pemakaian']}, Efek Samping: {matched_data['Efek Samping']}, Indikasi: {matched_data['Indikasi']}"
                    tts = gTTS(text=details, lang='id')
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                        temp_audio_path = temp_audio.name
                        tts.save(temp_audio_path)

                    pygame.mixer.music.load(temp_audio_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.2)
                    os.remove(temp_audio_path)

            cv2.imshow('live Cam Testing', im)
        except IncompleteRead:
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
        
        key = cv2.waitKey(5)
        if key == ord('q'):
            break
        
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
