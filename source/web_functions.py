from .web_functions_engine import WebFunctionsEngine
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
import copy
import win32com.client
import datetime
import time
import re
import requests
import os
import shutil
import pythoncom
from pathlib import Path
import pandas as pd
import pathlib


class WebFunctions(WebFunctionsEngine):
    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def check(
        self,
        driver: WebDriver,
        element,
        true_action_commands: list = [],
        false_action_commands: list = [],
        visible: bool = False,
    ) -> None:
        """
        ### check
        Check if a element exist

        @param element: element to check;
        @param true_action_commands: action to run if the element exist;
        @param false_action_commands: action to run if the not element exist;
        @param visible: check if the element exist or is visible;
        """
        try:
            web_element = self._get_element(driver, element)
            if visible:
                if web_element.is_displayed():
                    web_element = True
                else:
                    web_element = False

        except Exception:
            web_element = False

        if web_element:
            if true_action_commands:
                driver.web_engine.execute_commands(driver, true_action_commands)
        else:
            if false_action_commands:
                driver.web_engine.execute_commands(driver, false_action_commands)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def print_screen(
        self, driver: WebDriver, file_name: str, datetime: bool = False
    ) -> None:
        """
        ### print_screen
        Take a screenshot;

        @param file_name: name to save the screenshot
        @param datetime: if true, put the datetime on the file_name (f"{file_name}_%d_%m_%Y_%H_%M.png")
        """
        if datetime:
            today = datetime.datetime.today()
            file_path = Path(
                os.path.join(
                    driver.download_folder,
                    today.strftime(f"{file_name}_%d_%m_%Y_%H_%M.png"),
                )
            )
        else:
            file_path = Path(os.path.join(driver.download_folder, f"{file_name}.png"))
        driver.save_screenshot(file_path)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def error_log(
        self, driver: WebDriver, status: bool = False, message: str = False
    ) -> None:
        """
        ### error_log
        Create a error log in a Excel file:
        @param status: Status message
        @param message: message to put in the error log
        #### Will probably be discontinued
        """
        today = datetime.datetime.today()
        file_name = Path(
            today.strftime(
                os.path.join(
                    pathlib.Path().resolve(), "..", "logs", "log_%d_%m_%Y.xlsx"
                )
            )
        )

        if not file_name.is_file():
            df = pd.DataFrame(dict(datetime=[], status=[], message=[]))
            df.to_excel(file_name, index=False)
        else:
            df = pd.read_excel(file_name)

        df_log = pd.DataFrame(
            dict(
                dict(
                    datetime=[datetime.datetime.now()],
                    status=[status],
                    message=[message],
                )
            )
        )
        pd.concat([df, df_log], ignore_index=True).to_excel(file_name, index=False)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def get(self, driver: WebDriver, url: str) -> None:
        """
        ### GET
        Access the url
        """
        driver.get(url)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def click(self, driver: WebDriver, element: str, check: bool = False) -> None:
        """
        ### click
        Click in Element;

        @param check:
            - False: Will click in the element and will return a error if it cant
            - True: Will click on element if that exists
        """
        if not check:
            self._get_element(driver, element).click()

        elif check:
            try:
                self._get_element(driver, element).click()
            except NoSuchElementException:
                ...
        else:
            message = "[WebFunctions>click: ERROR] select a valid value to 'check' (True, False)"
            self._error_message(message)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def wait(self, driver: WebDriver, type_wait: str, element: str = "*") -> None:
        """
        ### WAIT
        Wait something happen to continue;

        @param element: element to wait
        @param type_wait:
            - APPEAR: Wait some element appear
            - DISAPPEAR: Wait some element disappear
            - CLICKABLE: Wait some element to be clickable
            - PRESENCE: Wait the element exist
            - ALERT: Wait a alert appear
            - WINDOW: Wait a window appear
        """

        element_type, element_selection = self._get_element_prop(
            element, accept_web_element=False
        )
        element_params: tuple = (element_type, element_selection)

        type_wait = type_wait.upper()
        wait = WebDriverWait(driver, 3000)

        if type_wait == "APPEAR":
            wait.until(EC.visibility_of_element_located(element_params))

        elif type_wait == "DISAPPEAR":
            wait.until(EC.invisibility_of_element_located(element_params))

        elif type_wait == "CLICKABLE":
            wait.until(EC.element_to_be_clickable(element_params))

        elif type_wait == "PRESENCE":
            wait.until(EC.presence_of_element_located(element_params))

        elif type_wait == "ALERT":
            wait.until(EC.alert_is_present())

        elif type_wait == "WINDOW":
            wait.until(EC.new_window_is_opened(driver.window_handles))
        else:
            message = "[WebEngine>wait: ERROR] Select a valid appear value (APPEAR, DISAPPEAR, CLICKABLE, PRESENCE, ALERT, WINDOW)."
            self._error_message(message)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def execute_window_command(
        self, driver: WebDriver, action_commands: list, trigger_command: list = False
    ) -> None:
        """
        ### execute_window_command
        Execute a function in another window;

        @param action_commands: Commands to execute
        @param trigger_command: Trigger action to execute the action commands

        #### Will probably be discontinued or altered
        """
        if trigger_command:
            driver.web_engine.execute_commands(driver, trigger_command)
        current_window = driver.current_window_handle
        window_to_switch = driver.window_handles[-1]
        driver.switch_to.window(window_to_switch)
        driver.web_engine.execute_commands(driver, action_commands)
        driver.switch_to.window(current_window)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def insert(self, driver: WebDriver, element: str, value: str) -> None:
        """
        ### insert
        Insert a value:str in a input;

        @param element: Element to be insered
        @param value: value to be insert
        """
        web_element: WebElement = self._get_element(driver, element)
        web_element.send_keys(value)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def add_cookies(self, driver: WebDriver, cookies_str: str) -> None:
        """
        ### add_cookies
        Add cookies in the driver;
        @param cookies_str: Has to be in "key=value;key=value"
        """
        for cookie_str in re.split("'|;| ", cookies_str):
            cookie = {
                "name": cookie_str.split("=")[0],
                "value": cookie_str.split("=")[1],
            }
            driver.add_cookie(cookie)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def close(self, driver: WebDriver) -> None:
        """
        ### close
        Close the driver;
        """
        driver.close()

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def quit(self, driver: WebDriver) -> None:
        """
        ### quit
        cant be used
        #### Will probably be discontinued or altered
        """
        driver.quit()

    # @WebFunctionsEngine._validation
    # @WebFunctionsEngine._get_web_element_atributte
    # def remove_empty_download_folder(self, driver:WebDriver):
    #     os.rmdir(driver.download_temp_folder)
    #     os.rmdir(driver.download_folder)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def insert_mail_token(
        self,
        driver: WebDriver,
        element: str,
        token_location: str,
        wait_time: str | int,
        action_commands: list = False,
        subject: str = False,
        sender_mail: str = False,
    ) -> None:
        """
        ### insert_mail_token
        Insert a email token in a input;

        @param action_commands: Command to trigger "insert_mail_token" function
        @param element: Element to insert the email token
        @param sender_mail: Email that send token
        @param token_location: Token location (re pattern)
        @param wait_time: Time to wait the email

        #### Will probably be altered using "__get_web_element_atributte"
        """
        if action_commands:
            driver.web_engine.execute_commands(driver, action_commands)
        init_time = datetime.datetime.now()
        current_time = datetime.timedelta(0)
        token = None
        while current_time <= datetime.timedelta(minutes=int(wait_time)):
            outlook = win32com.client.Dispatch(
                "Outlook.Application", pythoncom.CoInitialize()
            ).GetNamespace("MAPI")
            # outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
            inbox = outlook.GetDefaultFolder(6)
            if sender_mail:
                filteredItems = inbox.Items.Restrict(
                    f"[SenderEmailAddress]='{sender_mail}'"
                )
            elif subject:
                filteredItems = inbox.Items.Restrict(f"[Subject] = '{subject}'")
            else:
                message = f'[WebFunctions>insert_mail_token: ERROR] Select a "sender_mail" or a "subject"'
                self._error_message(message)
            email_result = filteredItems.GetLast()
            if email_result is not None:
                email_received_time = datetime.datetime.strptime(
                    str(email_result.ReceivedTime).replace("+00:00", "").split(".")[0],
                    "%Y-%m-%d %H:%M:%S",
                )
                if email_received_time > init_time:
                    token = re.findall(token_location, filteredItems.GetLast().body)
                    if token:
                        token = token[0]
                        break
                    else:
                        message = f'[WebFunctions>insert_mail_token: ERROR] Token not found, check "token_location"!'
                        self._error_message(message)
            current_time = datetime.datetime.now() - init_time
            time.sleep(5)
        self.insert(driver, element, token)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def create_parquet_file(
        self,
        driver: WebDriver,
        columns: list,
        save_path: str,
        file_name: str,
        validate_columns=True,
        overwrite=False,
    ) -> None:
        """
        ### add_parquet_row
        #### Will probably be discontinued
        """
        columns.append("change_datetime")
        save_path = Path(save_path)
        df = pd.DataFrame({column: [] for column in columns})

        if not save_path.is_dir():
            save_path.mkdir(parents=True)

        save_path_file = Path(os.path.join(str(save_path), file_name))

        if save_path_file.is_file():
            if validate_columns:
                opened_df = pd.read_parquet(str(save_path_file))
                validated_columns = set(columns) - set(opened_df.columns.values)
                if validated_columns:
                    message = f"[WebFunctions>create_parquet_file: ERROR] the file awready exist, and has not the same columns!\nException Columns: {validated_columns}"
                    self._error_message(message)
            if overwrite:
                save_path_file.unlink()
                df.to_parquet(str(save_path_file), index=False)
        else:
            df.to_parquet(str(save_path_file), index=False)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def add_parquet_row(
        self,
        driver: WebDriver,
        file_name: str,
        file_path: str,
        column_to_value: dict[str:str],
        create_columns: bool = True,
    ) -> None:
        """
        ### add_parquet_row
        #### Will probably be discontinued
        """
        column_to_value["change_datetime"] = datetime.datetime.today().strftime(
            "%d/%m/%Y %H:%M:%S"
        )
        # validate_text
        for key, value in column_to_value.items():
            column_to_value[key] = self._validate_text(driver, value)

        file_path = Path(os.path.join(file_path, file_name))

        if not file_path.is_file():
            message = f"[WebFunctions>add_parquet_row: ERROR] file_path do not exist!"
            self._error_message(message)

        df = pd.read_parquet(str(file_path))
        df_val = pd.DataFrame([column_to_value])

        if create_columns:
            df_final = pd.concat([df, df_val], ignore_index=True)
            df_final.to_parquet(str(file_path), index=False)

        else:
            columns_validate = set(df_val.columns.values) - set(df.columns.values)
            if columns_validate:
                message = f"[WebFunctions>add_parquet_row: ERROR] columns do not exist!\n columns: {columns_validate}"
                self._error_message(message)

            df_final = pd.concat([df, df_val], ignore_index=True)
            df_final.to_parquet(str(file_path), index=False)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def execute_js(
        self,
        driver: WebDriver,
        code_js: str,
        element: str = False,
        script_timeout: int = 100,
    ) -> None:
        """
        ### execute_js
        Execute a JavaScript command;
        """
        web_element = False
        if element:
            web_element: WebElement = self._get_element(driver, element)
        driver.set_script_timeout(script_timeout)
        driver.execute_script(code_js, web_element)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def execute_py(
        self, driver: WebDriver, code_py: str = False, code_path: str = False
    ) -> None:
        if (not code_py and not code_path) or (code_path and code_py):
            message = f"[WebFunctions>execute_py: ERROR] set a code_path or a code_py"
            self._error_message(message)

        if code_path:
            os.system(f"python {code_path}")

        elif code_py:
            exec(code_py)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def print(self, driver: WebDriver, value=False) -> None:
        print(value)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def select(self, driver: WebDriver, element, value) -> None:
        select = Select(self._get_element(driver, element))
        select.select_by_value(value)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def sleep(self, driver: WebDriver, timesec: str) -> None:
        time.sleep(int(timesec))

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def confirm_alert(self, driver: WebDriver) -> None:
        driver.switch_to.alert.accept()

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def download_from_email_link(
        self,
        driver: WebDriver,
        action_commands: dict,
        sender_mail: str,
        url_location: str,
        wait_time: str | int,
        file_name: str,
    ) -> None:
        """
        :param action_commands: Command to trigger "download_from_email_link" function
        :param element: Element to insert the email token
        :param sender_mail: Email that send token
        :param url_location: url download location (re pattern)
        :param wait_time: Time to wait the email
        :param file_name: file save name
        """
        driver.web_engine.execute_commands(driver, action_commands)
        init_time = datetime.datetime.now()
        current_time = datetime.timedelta(0)
        while current_time <= datetime.timedelta(minutes=int(wait_time)):
            outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace(
                "MAPI"
            )
            inbox = outlook.GetDefaultFolder(6)
            filteredItems = inbox.Items.Restrict(
                f"[SenderEmailAddress]='{sender_mail}'"
            )
            email_result = filteredItems.GetLast()

            if email_result is not None:
                email_received_time = datetime.datetime.strptime(
                    str(email_result.ReceivedTime).replace("+00:00", "").split(".")[0],
                    "%Y-%m-%d %H:%M:%S",
                )
                if email_received_time > init_time:
                    url = re.search(url_location, email_result.Body).group("url")
                    request = requests.get(url, verify=False, allow_redirects=True)
                    open(os.path.join(driver.download_folder, file_name), "wb").write(
                        request.content
                    )
                    break
            current_time = datetime.datetime.now() - init_time
            time.sleep(5)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def download_action_general(
        self, driver: WebDriver,
        action_commands:list,
        wait_time: str | int,
        file_name: str,
        folder_name: str = False,
        folder_name_date_format: dict = False,
        file_extension=False,
        file_name_date_format=False,
        finish_action_commands: list = False,
    ) -> None:
        datetime_format_variable = lambda values, datetime_format: datetime.datetime \
            .strptime(values, datetime_format["input"]) \
            .strftime(file_name_date_format["output"])
            
        # file name
        if file_name_date_format:
            file_name = datetime_format_variable(file_name, file_name_date_format)

        # folder name
        if folder_name_date_format:
            folder_name = datetime_format_variable(folder_name, folder_name_date_format)

        folder_name_path = os.path.join(driver.download_folder, folder_name)
        
        if not os.path.isdir(folder_name_path):
            os.mkdir(folder_name_path)

        # download and save file
        driver.web_engine.execute_commands(driver, action_commands)
        init_time, current_time = datetime.datetime.now(), datetime.timedelta(0)

        # wait util the time has been done or the file has been downloaded
        move = False
        while current_time <= datetime.timedelta(minutes=int(wait_time)):
            all_files = [x.name for x in Path(driver.download_temp_folder).glob("*")]
            
            files_to_validate = [
                os.path.join(driver.download_temp_folder, file) \
                for file in all_files \
                if ".htm" in file or "download" in file or "tmp" in file 
            ]
            
            if files_to_validate:
                old_file_name = max([file for file in files_to_validate], key=os.path.getctime)

                if not file_extension:
                    _, file_extension = os.path.splitext(old_file_name)

                # check name file to save
                
                file_paths = list(filter(None,[driver.download_folder,folder_name,f"{file_name}{file_extension}"]))
                new_file_name = os.path.join(*file_paths)

                while count:=0 <= 30:
                    count += 1
                    try:
                        shutil.move(old_file_name, new_file_name)
                        move = True
                        break
                    except Exception as e:
                        if count >= 30:
                            self._error_message(
                                f"[WebFunctions>download_action: ERROR] Download Exception:\n" \
                                f"File: {old_file_name}\n" \
                                f"Move to: {new_file_name}\n" \
                                f"Exception: {e}"
                            )       
                        time.sleep(1)
                if move:
                    break

            current_time = datetime.datetime.now() - init_time
            time.sleep(5)
            
        if finish_action_commands:
            driver.web_engine.execute_commands(driver, finish_action_commands)
            
    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def download_action(
        self,
        driver: WebDriver,
        action_commands: list,
        wait_time: str | int,
        finish_action_commands: list = False,
        folder_element_name: str = False,
        folder_name: str = False,
        folder_name_date_format: dict = False,
        file_name: str = False,
        element_file_name=False,
        file_extension=False,
        file_name_date_format=False,
    ) -> None:
        """
        :param action_commands: Trigger Download Commmand
        :param check_folder: Default local download
        :param file_name: FileName
        :param wait_time: Time to wait the download
        :param folder_name: Folder to save inside download_folder
        :param folder_name_date_format: transform the folder name in datetime to set a format;
        Has to be a dict with {"input": "format", "output": "format"}, ex.:
            >>> {"input": "%d/%m/%Y", "output": "%m_%Y")

        :param file_name_date_format: Transform the file_name in datetime to set a format;
        Has to be a dict with {"input": "format", "output": "format"}, ex.:
            >>> {"input": "%d/%m/%Y", "output": "%m_%Y")

        :param element_file_name: Set file name with the element selection text
        :param folder_element_name: Set folder name with the element selection text
        """
        self._warning_message("'download_action' will be discontinued please use 'download_action_general'!")
        # file name
        if not file_name and element_file_name:
            web_element = self._get_element(driver, element_file_name)
            file_name = web_element.text

        if file_name and file_name_date_format:
            file_name_datetime = datetime.datetime.strptime(
                file_name, file_name_date_format["input"]
            )
            file_name = file_name_datetime.strftime(file_name_date_format["output"])

        # folder name
        if folder_element_name:
            web_element = self._get_element(driver, folder_element_name)
            folder_name = web_element.text

        if folder_name or folder_element_name:
            if folder_name_date_format:
                folder_name_datetime = datetime.datetime.strptime(
                    folder_name, folder_name_date_format["input"]
                )
                folder_name = folder_name_datetime.strftime(
                    folder_name_date_format["output"]
                )

            folder_name_path = os.path.join(*[driver.download_folder, folder_name])
            if not os.path.isdir(folder_name_path):
                os.mkdir(folder_name_path)

        # download and save file
        driver.web_engine.execute_commands(driver, action_commands)
        init_time = datetime.datetime.now()
        current_time = datetime.timedelta(0)

        # wait util the time has been done or the file has been downloaded
        while current_time <= datetime.timedelta(minutes=int(wait_time)):
            all_files = [x.name for x in Path(driver.download_temp_folder).glob("*")]
            files_to_validate = []
            for file in all_files:
                if ".htm" in file or "download" in file or "tmp" in file:
                    continue
                files_to_validate.append(file)
            if files_to_validate:
                old_file_name = max(
                    [
                        os.path.join(driver.download_temp_folder, file)
                        for file in files_to_validate
                    ],
                    key=os.path.getctime,
                )

                if not file_extension:
                    _, file_extension = os.path.splitext(old_file_name)

                # check name file to save
                if file_name:
                    file_paths = list(
                        filter(
                            None,
                            [
                                driver.download_folder,
                                folder_name,
                                f"{file_name}{file_extension}",
                            ],
                        )
                    )
                else:
                    file_paths = list(
                        filter(
                            None,
                            [
                                driver.download_folder,
                                folder_name,
                                os.path.basename(old_file_name),
                            ],
                        )
                    )

                new_file_name = os.path.join(*file_paths)
                
                self._validate_file(old_file_name) # TODO validate file
                
                count = 0
                while count <= 30:
                    move = False
                    try:
                        shutil.move(old_file_name, new_file_name)
                        move = True
                    except Exception as e:
                        move = False
                        time.sleep(1)
                    if move:
                        break
                    count = count + 1

                if count >= 30:
                    message = f"[WebFunctions>download_action: ERROR] Download Exception:\nFile: {old_file_name}\nMove to: {new_file_name}"
                    self._error_message(message)
                break

            current_time = datetime.datetime.now() - init_time
            time.sleep(5)
        if finish_action_commands:
            driver.web_engine.execute_commands(driver, finish_action_commands)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def for_each(
        self,
        driver: WebDriver,
        elements: str,
        action_commands: list,
        find_again: bool = False,
    ) -> None:
        def __replace_commands(command, value):
            if isinstance(command, str):
                return self._get_this_element(command, value)

            if isinstance(command, dict):
                for func, param in command.items():
                    command[func] = __replace_commands(param, value)
                return command

            if isinstance(command, list):
                commands = []
                for c in command:
                    commands.append(__replace_commands(c, value))
                return commands
            else:
                return command

        web_elements = self._get_elements(driver, elements)
        for index, web_element in enumerate(web_elements):
            if find_again:
                web_element = self._get_elements(driver, elements)[index]
            commands = __replace_commands(copy.deepcopy(action_commands), web_element)
            driver.web_engine.execute_commands(driver, commands)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def block_commands(
        self,
        driver,
        block_commands: list = [],
        initial_state: list = [],
        true_action_commands: list = [],
        false_action_commands: list = [],
    ) -> None:
        """
        Try to execute each command inside 'block_command'

        :param block_commands: multiples commands lists [list, list, ...]
        :param initial_state: Command to return the program to the initial state to execute the next command block, \
            will be runned to each command inside 'block_command'
        :param true_action_commands: if the block has execute correctly, execute this block
        :param false_action_commands: if the block has not execute correctly, execute this block
        """
        for commands in block_commands:
            if initial_state:
                driver.web_engine.execute_commands(driver, initial_state)
            try:
                driver.web_engine.execute_commands(driver, commands)
                error = False
            except Exception as e:
                message = f"[WebFunctions>execute_block_commands: WARNING] commands can't be execute:\n - command: {commands}\n - error: {e}"
                self._warning_message(message)
                error = True

        if not error:
            if true_action_commands:
                driver.web_engine.execute_commands(driver, true_action_commands)
        else:
            if false_action_commands:
                driver.web_engine.execute_commands(driver, false_action_commands)

    @WebFunctionsEngine._validation
    @WebFunctionsEngine._get_web_element_atributte
    def try_while(self, driver, action_command: list, wait_time: str | int = 2) -> None:
        init_time = datetime.datetime.now()
        current_time = datetime.timedelta(0)
        last_error = False
        while current_time <= datetime.timedelta(minutes=int(wait_time)):
            try:
                driver.web_engine.execute_commands(driver, action_command)
                last_error = False
                break
            except Exception as e:
                last_error = e
            current_time = datetime.datetime.now() - init_time
            time.sleep(5)
        if last_error:
            message = f"[WebFunctions>try_while: WARNING] {last_error}"
            self._warning_message(message)

if __name__ == "__main__":
    test = WebFunctions()
    print()