import datetime
import sys
import os
import pathlib
sys.path.insert(0, os.path.join(pathlib.Path().resolve(), pathlib.Path('../')))
from source.web_multithread import WebMultithread
import copy
import datetime
import sys
import pathlib
import os
import copy
import pytesseract
import re
import requests
import string
import cv2 as cv
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def get_captcha_text(image_element):
    # download image
    # id_instance_element = id(image_element)
    # response = requests.get(image_element.get_attribute("src"))
    # image_path = f"{id_instance_element}.jpg"
    # with open(image_path, "wb") as f:
    #     f.write(response.content) 
    
    # image path        
    image_path = "./python_logo.png"
    
    # getting text
    img = cv.imread(image_path)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    rgb_to_hsv = lambda rgb: cv.cvtColor(np.uint8([[rgb]]), cv.COLOR_RGB2HSV)[0][0]
    lower_orange = np.array(rgb_to_hsv([98,98,98]))
    upper_orange = np.array(rgb_to_hsv([101,101,101]))
    binary_image = cv.inRange(hsv, lower_orange, upper_orange)
    config = f'--psm 6 ' \
        f'-c tessedit_char_whitelist={string.ascii_uppercase+string.ascii_lowercase}'
    texto = pytesseract.image_to_string(binary_image, lang="por", config=config)
    return re.sub(r'[\n\s]+', '', texto)

commands = [
    {"get": {"url": rf"{os.path.join(pathlib.Path(__file__).parent, 'index.html')}"}},
    {"insert": {"element": "@teste_input", "value": "{get_captcha_text(@text_image)}"}},
    {"print": {"value": "$teste"}},
    {"print": {"value": "{text(%/html/body/table/tbody/tr[3]/td)} - {text(%/html/body/table/tbody/tr[2]/td)}"}},
    {"for_each": {
        "elements": "%/html/body/table/tbody/tr",
        "action_commands": [
            {"print": {"value": "{text(this %//td[1])} - {text(this %./td[2])} - {text(this %./td[3])}"}},
        ]
    }},
    {"print": {"value": 1}},
    {"print": {"value": {"print": {"value": {"teste"}}}}},
    {"print": {"value": "(\d\{6\})"}},
    {"sleep":{"timesec": 10}}
]

contents = [
    {
        'content_variables':{
            '$teste': '12345678910',
        },
        'error_log_name': os.path.join('./logs', datetime.datetime.today().strftime("teste_%d_%m_%Y.log")),
        'commands': copy.deepcopy(commands),
        'show_webdriver': True,
        'more_functions': [get_captcha_text]
    }
]

web_automation = WebMultithread(contents)
web_automation.execute_all_contents()
