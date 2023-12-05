
from functools import wraps
from pathlib import Path
import pandas as pd
import ast
import glob
import pyautogui
import pathlib
import os
import datetime
import time
import pywinauto
import warnings
import cv2
import logging

warnings.simplefilter('ignore', category=UserWarning)
pyautogui.FAILSAFE = False

class ActionsFunctions():
    def __init__(self) -> None:
        self._set_actions_functions()

    def _execute_action_commands(self, driver, action_commands: list):
        command_line: dict
        for command_line in action_commands:
            for command, param in command_line.items():
                result, message = self.functions[command](driver, **param)
                if not result:
                    self.close()
                    message = f'[ActionsFunctions>execute_commands: ERROR] {command} {param}\nMessage: {message}'
                    self._error_message(message)

    def _set_actions_functions(self) -> None:
        functions = {}
        for function_name in dir(self):
            if function_name[0] != "_":
                functions[function_name] = getattr(self, function_name)
                self.functions = functions
        functions.pop("get_actions_functions")
        self.functions = functions

    def get_actions_functions(self):
        return self.functions
    
    def _error_message(self, message):
        logging.error(message)
        raise Exception(message)
    
    def _warning_message(self, message):
        logging.warn(message)
        warnings.warn(message)
    
    def _image_locate(self, image_path:str, x:int=0, y:int=0, search_time:float=5.0):
        image_path = pathlib.Path(image_path)
        if not image_path.is_file():
            message = f"[ActionsFunctions:_image_locate: ERROR] Image does not exist:\nImage Path: {image_path}"
            self._error_message(message)
        img = cv2.imread(str(image_path)) 
        box = pyautogui.locateOnScreen(img, confidence=0.9, minSearchTime=search_time)

        if box:
            x, y = (
                box.left + (box.width/2) + x,
                box.top + (box.height/2) + y
            )
            return (x, y)
        else: 
            return False
    
    def _found_app(self, app_name:str):
        apps = pywinauto.Desktop().windows()
        app = False
        for p in [app.window_text() for app in apps]:
            if app_name in p:
                app = pywinauto.Application().connect(title=p, timeout=10)
                break
        if not app:
            message = f'[ActionsFunctions>_found_app: ERROR] app "{app_name}" not found!'
            self._error_message(message)
        return app

    def __validation(func):
        """
        Validate function and return if it executed corretly
        """
        @wraps(func)
        def _validation(*args, **kwargs):
            func(*args, **kwargs)
            return True, ''
            # try:
                # func(*args, **kwargs)
                # return True, ''
            # except Exception as e:
            #     return False, e
        return _validation

    @__validation
    def wait_window_open(self, driver, window_name: str, action_commands: list = [], wait_time: int = 2):
        self._execute_action_commands(driver, action_commands)
        init_time = datetime.datetime.now()
        current_time = datetime.timedelta(0)
        while current_time <= datetime.timedelta(minutes=int(wait_time)):
            windows = pywinauto.Desktop(backend="uia").windows()
            windows = [w.window_text() for w in windows]
            if window_name in windows:
                break
            current_time = datetime.datetime.now() - init_time
            time.sleep(5)

    @__validation
    def wait_number_of_windows(self, driver, app_name:str, window_names_contains:str, count_window:int|str, action_commands: list = [], wait_time:int|str=1):
        self._execute_action_commands(driver, action_commands)
        init_time = datetime.datetime.now()
        current_time = datetime.timedelta(0)
        while current_time <= datetime.timedelta(minutes=int(wait_time)):
            count = 0
            for w in self._found_app(app_name).windows():
                if window_names_contains in w.window_text():
                    count = count + 1 
            if count >= int(count_window):
                break
            current_time = datetime.datetime.now() - init_time
            time.sleep(5)

    @__validation
    def drag_drop(self, driver, init_image_path:str, finish_image_path:str, search_time:float=5.0):
        init_image_cords = self._image_locate(os.path.join(driver.images_folder, init_image_path), search_time=search_time)
        finish_image_cords = self._image_locate(os.path.join(driver.images_folder, finish_image_path), search_time=search_time)
        if init_image_cords and finish_image_cords:
            pyautogui.moveTo(*init_image_cords)
            pyautogui.mouseDown()
            pyautogui.moveTo(*finish_image_cords, duration=1)
            pyautogui.mouseUp()
            time.sleep(2)
        else:
            if init_image_cords:
                image_error = "finish_image_cords"
            else:
                image_error = "init_image_cords"
            message = f'[ActionsFunctions>drag_drop: ERROR] "{image_error}" not found!'
            self._error_message(message)


    @__validation
    def click_image(self, driver, image_path: str, check:bool=False, search_time:float=5.0, x: int = 0, y: int = 0):
        if check:
            try:
                cords = self._image_locate(os.path.join(driver.images_folder, image_path), x, y, search_time)
                pyautogui.click(*cords)

            except Exception as e:
                cords = False
        else:
            cords = self._image_locate(os.path.join(driver.images_folder, image_path), x, y, search_time)
            pyautogui.click(*cords)

    @__validation
    def wait_image(self, driver, image_path:str, type:str="APPEAR", wait_time:str|int=1, search_time:float=5.0):
        if type == "APPEAR":
            cords = self._image_locate(os.path.join(driver.images_folder, image_path), search_time=search_time)
            if not cords:
                message = f'[ActionsFunctions>wait_image: ERROR] "{image_path}" not found!'
                self._error_message(message)
            
        elif type == "DISAPPEAR":
            init_time = datetime.datetime.now()
            current_time = datetime.timedelta(0)
            while current_time <= datetime.timedelta(minutes=int(wait_time)):
                cords = self._image_locate(os.path.join(driver.images_folder, image_path), search_time=search_time)
                if not cords:
                    return
                current_time = datetime.datetime.now() - init_time
                time.sleep(5)
                message = f'[ActionsFunctions>wait_image: ERROR] "{image_path}" not disappear!'
            self._error_message(message)

    @__validation
    def write(self, driver, text: str, interval: bool = 0):
        pyautogui.write(text, interval=interval)

    @__validation
    def press_key(self, driver, keys: str, presses:int=1):
        pyautogui.press(keys, presses=presses)

    @__validation
    def focus_on_the_window(self, driver, app_name:str, window_names_contains:str):
        for w in self._found_app(app_name).windows():
            if window_names_contains in w.window_text():
                w.type_keys('{VK_RIGHT}')
                break
        
    @__validation
    def close_windows(self, driver, app_name:str, window_names_contains:str):
        for w in self._found_app(app_name).windows():
            if window_names_contains in w.window_text():
                w.close()

    @__validation
    def search_window(self, driver, app_name:str, window_names_contains:str, search_image:str, search_time:int|str=5):
        find = False
        for w in self._found_app(app_name).windows():
            if window_names_contains in w.window_text():
                w.type_keys('{VK_RIGHT}')
                cords = self._image_locate(os.path.join(driver.images_folder, search_image), search_time=search_time)
                if cords:
                    find = True
                    break
                else:
                    continue

        if not find:
            message = f'[ActionsFunctions>search_window: ERROR] Window not Found in the search!'
            self._error_message(message)
