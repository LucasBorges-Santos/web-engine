"""
https://blog.devgenius.io/multi-threaded-web-scraping-with-selenium-dbcfb0635e83
"""

from .web_engine import WebEngine
from .web_functions import WebFunctions
from threading import Thread
from threading import Semaphore
import threading
from multiprocessing.pool import ThreadPool
import logging
from selenium.webdriver.chrome.webdriver import WebDriver
import numpy as np

class WebEngineMultithread(WebEngine):
    def __init__(self, semaphores_limit:threading.BoundedSemaphore, semaphores:dict[str:Semaphore], *args, **kwargs) -> None:
        self.semaphores_limit = semaphores_limit
        self.semaphores_limit.acquire()
        self.semaphores = semaphores
        super().__init__(*args, **kwargs)

    def _execute_command_function(self, driver, command, param):
        if command in self.semaphores:
            with self.semaphores[command]:
                result, message = self.functions[command](driver, **param)
        else:
            result, message = self.functions[command](driver, **param)
        return result, message

    def execute_commands(self, driver=False, commands=False, is_multithread_command:bool=False):
        driver = driver if driver else self.driver
        commands = commands if commands else self.commands

        message_error = False
        try:
            for command_line in self._get_commands(commands):
                command_line:dict 
                     
                if not driver.service.is_connectable():
                    message_error = f'[WebEngine>execute_commands: ERROR] driver is not connectable!'
                    break

                for command, param in command_line.items():
                    result, message = self._execute_command_function(driver, command, param)

                    if not result:
                        self._check_to_quit(driver)
                        message_error = f'[WebEngine>execute_commands: ERROR] {command} {param}\nMessage: {message}'
                        break 
                    
                if message_error:
                    break

        except Exception as e:
            message_error = f'[WebEngine>execute_commands: ERROR] {command} {param}\nMessage: {e}'
                
        if is_multithread_command:
            self._check_to_quit(driver)
            self.semaphores_limit.release()

        if message_error:
            self._error_message(message_error)
            raise Exception(message_error)
        

class WebMultithread():
    def __init__(self, contents, limit=10) -> None:
        self.set_contents(contents)
        self.semaphore_limit = threading.BoundedSemaphore(limit)
        self.semaphores = self.get_semaphores()
        
    def set_contents(self, contents:list):
        self.contents = contents
        self.initial_contents = contents
    
    def get_error_content_result(self, results:list, contents:list):
        for x in results:
            false_index = np.where(np.invert(np.array(x).astype(bool)))[0]
            contents = [contents[x] for x in false_index]
            
        return contents

    def get_error_results(self, result:list):
        return list(filter(None, np.where(np.invert(np.array(result).astype(bool)), self.contents, False)))
        
    def get_semaphores(self):
        return {
            WebFunctions.download_from_email_link.__name__: Semaphore(1),
            WebFunctions.download_action.__name__: Semaphore(1),
            WebFunctions.insert_mail_token.__name__: Semaphore(1),
            WebFunctions.error_log.__name__: Semaphore(1),
        }

    def execute_content_commands(self, web_engine:WebEngineMultithread, index:int, result:list) -> None:
        try:
            web_engine.execute_commands(is_multithread_command=True)
            result[index] = True
        except: 
            result[index] = False
    
    def execute_all_contents_util_no_errors(self, attempts:int=2) -> list:
        initial_attempts = attempts
        all_results = []
        
        while attempts != 0:
            running_result = self.execute_all_contents()
            all_results.append(running_result)
            error_results = self.get_error_results(running_result)
            if error_results == []:
                break
            else:
                self.set_contents(error_results)
            attempts -= 1
            
        if attempts == 0:
            print(f"[WebMultithread>execute_all_contents_util_no_errors: WARNING] cannot be execute with {initial_attempts} attempts!") ### TODO cannot be here, use error_log functions    
        return all_results
    
    def execute_all_contents(self):
        result = [None] * len(self.contents)
        web_driver_objects = []
        for index, content in enumerate(self.contents):
            t = Thread(
                target=self.execute_content_commands, 
                args=(WebEngineMultithread(semaphores_limit=self.semaphore_limit, semaphores=self.semaphores, **content), index, result)
            ) 
            web_driver_objects.append(t)
            t.start()
        for t in web_driver_objects:
            t.join()
        return result
