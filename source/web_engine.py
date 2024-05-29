import jstyleson
from selenium import webdriver
import datetime
import warnings
from webdriver_manager.chrome import ChromeDriverManager
from source.web_functions import WebFunctions
from source.actions_functions import ActionsFunctions
import os
import urllib3
import random
import json
from glob import glob
import logging
from selenium.webdriver.chrome.webdriver import WebDriver
import secrets
import pathlib
import shutil
from selenium.webdriver.chrome.service import Service


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning) 

class WebEngine():
    def __init__(self, error_log_name:bool=False, download_temp_path:str=False, download_path:str=False, commands_path:str=False, commands:list=False, content_variables:dict=False, more_functions:list={}, show_webdriver:bool=False, random_window_size:bool=False, web_functions:bool=True, actions_functions:bool=False, images_folder:str=False, random_agent:bool=False) -> None:
        self.random_agent = random_agent
        self.show_webdriver = show_webdriver
        self.content_variables = content_variables
        self._set_more_functions(more_functions)
        self._set_functions(web_functions, actions_functions)
        self.images_folder = images_folder
        self.commands_path = commands_path
        self.random_window_size = random_window_size
        self.commands = self._get_commands(commands=commands, commands_path=commands_path)
        self._set_download_temp_folder(download_temp_path)
        self._set_download_folder(download_path)
        self._set_drive()
        self._set_error_log(error_log_name)

    def _set_more_functions(self, more_functions):
        """
        Function to use in "WebFunctionsEngine._set_web_element_functions"; Use "{function_name()}" to use function.
        
        !!! "_set_more_functions" functions no accept params yet;
        
        Args:
            more_functions (list[function]): list with functions
        """
        self.more_functions = {
            mfunction.__name__: mfunction
            for mfunction in more_functions
        }
        
    def _set_error_log(self, error_log_name:bool):
        self.error_log_name = error_log_name
        
        if error_log_name:
            logging.basicConfig(filename=self.error_log_name, encoding='utf-8', level=logging.ERROR, filemode='w')

    def _set_functions(self, web_functions=True, actions_functions=False):
        if web_functions:
            self.web_functions = WebFunctions(more_functions=self.more_functions)
            self.functions = self.web_functions.get_web_functions()
            
            self.has_web_functions = True
        if actions_functions:
            self.actions_functions = ActionsFunctions()
            self.functions.update(self.actions_functions.get_actions_functions())
            self.has_actions_functions = True

    def _get_random_window_size(self):
        sizes = list(range(0, 1000, 100))
        return (random.choice(sizes), random.choice(sizes))
    
    def _get_random_agent(self):
        agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17720",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931",
            "Mozilla/5.0 (X11) AppleWebKit/62.41 (KHTML, like Gecko) Edge/17.10859 Safari/452.6",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
            "Chrome (AppleWebKit/537.1; Chrome50.0; Windows NT 6.3) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19577",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
            "Mozilla/5.0 (X11; CrOS i686 4319.74.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.8810.3391 Safari/537.36 Edge/18.14383"
        ]
        return random.choice(agents)
    
    def _set_download_folder(self, download_path:str=False) -> None:
        if not download_path:
            self.download_folder = self.download_temp_folder
            return
            
        if not os.path.exists(download_path):
            os.makedirs(download_path)
            
        if download_path[-1] != "\\":
            self.download_folder = f"{download_path}\\"
        else:
            self.download_folder = download_path
    
    def _set_download_temp_folder(self, download_temp_path:str=False):
        if not download_temp_path:
            download_temp_path = os.path.join(pathlib.Path().resolve(), 'download_temp', secrets.token_hex(15))
        if os.path.exists(download_temp_path):
            shutil.rmtree(download_temp_path)
        os.makedirs(download_temp_path)
        
        if download_temp_path[-1] != "\\":
            self.download_temp_folder = f"{download_temp_path}\\"
        else:
            self.download_temp_folder = download_temp_path
        
    def _get_webdrive_options(self):
        options = webdriver.ChromeOptions()
        
        if not self.show_webdriver:
            options.add_argument("--headless")
        
        if self.random_agent:
            options.add_argument(f"user-agent={self._get_random_agent()}")
            
        options.add_argument("--disable-default-apps")
        
        settings_kiosk = {
            "recentDestinations": [{
                "id": "Save as PDF",
                "origin": "local",
                "account": "",
            }],
            "selectedDestinationId": "Save as PDF",
            "version": 2,
        }
        prefs = {
            "plugins.always_open_pdf_externally": True,
            "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
            "download.extensions_to_open": "applications/pdf",
            "download.default_directory": rf'{self.download_temp_folder}',
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "savefile.default_directory": rf'{self.download_temp_folder}',
            'printing.print_preview_sticky_settings.appState' : json.dumps(settings_kiosk),
        }

        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])   
        options.add_argument("--disable-blink-features")
        options.add_argument('--kiosk-printing')
        options.add_argument("--disable-blink-features=AutomationControlled")
        return options   
     
    def _set_drive(self):
        # service = Service(
        #     executable_path=r"C:\Users\u1280820\MMC\Marsh Brasil Data Analytics - Python\WebEngine\chrome-win64\chrome.exe"
        # )
        
        driver = webdriver.Chrome(
            self._get_webdrive_options(),
            # service
        )
        if self.random_window_size:
            driver.set_window_size(*self._get_random_window_size())

        params = {'behavior': 'allow', 'downloadPath': self.download_temp_folder}
        driver.execute_cdp_cmd('Page.setDownloadBehavior', params)
        
        # adictional variables
        driver.download_folder = self.download_folder
        driver.download_temp_folder = self.download_temp_folder
        driver.images_folder = self.images_folder if getattr(self, 'has_actions_functions', False) else ''
        
        driver.web_engine = self

        self.driver = driver
    
    def _get_commands(self, commands:list=False, commands_path:str=False):
        """
        ### _set_commands_txt
        Transform 'py' files with json in commands.
        """
        def __replace_commands(command, comparison, value):
            if isinstance(command, str):
                if comparison in command:
                    return command.replace(comparison, value)
                else:
                    return command

            elif isinstance(command, dict):
                for func, param in command.items():
                    command[func] = __replace_commands(param, comparison, value)
                return command

            elif isinstance(command, list):
                commands = []
                for c in command:
                    commands.append(__replace_commands(c, comparison, value))
                return commands 
            
            else:
                return command

                
        if commands_path:
            with open(commands_path) as user_file:
                commands_str = user_file.read()
                commands:dict = jstyleson.loads(commands_str)

                for content_key, content_value in self.content_variables.items():               
                    commands = __replace_commands(commands, content_key, content_value)
            return commands

        elif commands:  
            for content_key, content_value in self.content_variables.items():               
                commands = __replace_commands(commands, content_key, content_value)
            return commands
        else:
            raise Exception("[WebEngine>_set_commands: ERROR] select a commands path or a dict command")
    
    def _error_message(self, message:str):
        current_time = datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S")
        message = f"{current_time}\n{message}"
        logging.error(message)
        print(message)
        
    def _check_to_quit(self, driver:WebDriver):
        if driver.service.is_connectable():
            self.web_functions.quit(driver)
        if os.path.exists(self.download_temp_folder):
            shutil.rmtree(self.download_temp_folder)

    def execute_commands(self, driver=False, commands=False):
        """
        Execute self.commands based on self.functions
        """
        driver = self.driver if not driver else driver
        commands = self.commands if not commands else commands
        message_error = False
        try:
            for command_line in commands:
                command_line:dict      
                for command, param in command_line.items():
                    result, message = self.functions[command](driver, **param)
                    if not result:
                        self._check_to_quit(driver)
                        message_error = \
                            f"[{self.functions[command].__qualname__.split('.')[0]}>{self.functions[command].__name__}: ERROR]\n" \
                            f"command: {command_line}\n error: {message}" 
                        break
                if message_error:
                    break

        except Exception as e:
            message_error = \
                f"[{self.functions[command].__qualname__.split('.')[0]}>{self.functions[command].__name__}: ERROR]\n" \
                f"command: {command_line}\n error: {e}\n" \
                f"content_variables: {self.content_variables}" 
            
        self._check_to_quit(driver)
        if message_error:
            self._error_message(message_error)
            raise Exception(message_error)


"""
    TODO IDEIAS
    CRIAR UM NOME ESPECIFICO PARA CADA TIPO DE RELARÓRIO ASSIM NÃO PRECISAMOS DEFINIR TODAS AS VEZES OS PARAMETROS DE 
    LOG

    CRIAR MAIS VALIDAÇÕES DE LOG POIS ALGUMAS VEZES O NAVEGADOR SÓ TRAVA OU SÓ NÃO AVANÇA

    OUTRO PROBLEMA QUE ESTA ACONTECENDO É Q QUANDO ABRE UMA NOVA PAGINA ELE NÃO FUNCIONA O METODO CLOSE, ASSIM DA
    PROBLEMA COM OS SEMAPHOROS

    EXISTE A POSSIBILIDADE DE O DOWNLOAD_ACTIONS_NÃO ESTAR TERMINANDO DE MOVER OS ARQUIVOS ANTES DE EXECUTAR O CLOSE
    
    EXISTE A POSSIBILIDADE DE RENOVARMOS A FORMA DE PROCESSO DE DESENVOLVIMENTO DA FUNÇÃO DE DOWNLOAD, SEPARANDO EM 2 ETAPAS
    
    1 - FAZENDO O DOWNLOAD E JOGANDO NA PASTA TEMP
    2 - MOVENDO DA PASTA TEMP PARA A PASTA FINAL
    
    ASSIM REMOVEMOS A NECESSIDADE DE TERMOS 3 FUNÇÕES DIFERENTES PARA REALIZARMOS AS MESMAS TAREFAS, COMO FAZER DOWNLOAD DO EMAIL,
    DOWNLOAD_ACTION E DOWNLOAD_FROM_ANOTHER_WINDOW, APENAS CRIAMOS UM TEMPLADE DE DOWNLOAD E REAPROVEITAMOS A PARTE DE CRIAÇÃO 
    DE PASTAS;
    
    O COMEÇO DISSO É O "DOWNLOAD_ACTION_GENERAL";
"""
