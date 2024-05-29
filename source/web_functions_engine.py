from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import datetime
import re
from functools import wraps
import warnings
import logging
import pathlib


class WebFunctionsEngine():
    def __init__(self, more_functions:dict={}) -> None:
        self.more_functions = more_functions
        self._set_web_functions()
        self._set_web_element_functions()
        
    def _set_web_functions(self) -> None:
        """
            ### _set_web_functions
            Get all functions from the web, filtered functions with initial name in "_" are not used, they are system functions;
        """
        functions = {}
        for function_name in dir(self):
            if function_name[0] != "_":
                functions[function_name] = getattr(self, function_name)
                self.functions = functions
        
        # remove because that is a external function to get all web functions
        functions.pop("get_web_functions")
        self.functions = functions
    
    def _set_web_element_functions(self):
        """
            ### _set_web_element_functions
            Functions used in "_get_web_element_atributte";
        """
        
        self.web_element_functions = {
            "text": lambda web_element: web_element.text,
            "text_": lambda web_element: re.sub(r'[ /-]', '_', str(web_element.text).lower()),
            "value": lambda web_element: web_element.get_attribute('value'),
        }
        self.web_element_functions.update(self.more_functions)
        
    def get_web_functions(self):
        """
            ### get_web_functions
            Get all web Functions;
        """
        return self.functions
    
    def _error_message(self, message):
        """
            ### _error_message
            Generate a error mensage and stop the system;
        """
        logging.error(message)
        raise Exception(message)
    
    def _warning_message(self, message):
        """
            ### _warning_message
            Generate a error warning;
        """
        logging.warn(message)
        warnings.warn(message)

    def _get_element_prop(self, element: str, accept_web_element:bool=True) -> None|str|WebElement:
        """
        ### _get_element_prop
        Return the element type and the selection
        element_types = {
            '#': By.ID,
            '.': By.CLASS_NAME,
            '%':  By.XPATH,
            '*': By.TAG_NAME,
            '@': By.NAME
        }
        """
        element_types = {
            '#': By.ID,
            '.': By.CLASS_NAME,
            '%':  By.XPATH,
            '*': By.TAG_NAME,
            '@': By.NAME
        }
        if element == '.':
            return None, element
        
        if isinstance(element, WebElement) and accept_web_element:
            return element
        
        elif isinstance(element, WebElement) and not accept_web_element:
            message = f"[WebFunctions>_get_element_prop: ERROR] this function does't accept object 'WebElement' in 'element' parameter."
            self._error_message(message)
        
        if element[0] not in element_types:
            message = f"[WebFunctions>_get_element_prop: ERROR] '{element[0]}' not in dict element types."
            self._error_message(message)
        
        return element_types[element[0]], element[1:]

    def _get_element(self, driver:WebDriver, element:str|WebElement) -> WebElement:
        """
        ### _get_element
        Pass parameter 'element' in:
            >>> element_type, element_selection = self._get_element_prop(element)
            >>> element = driver.find_element(element_type, element_selection)
        And return that correspondent WebElement.
        """
        if isinstance(element, WebElement):
            return element
        
        elif isinstance(element, str):
            element_type, element_selection = self._get_element_prop(element)
            element = driver.find_element(element_type, element_selection)
            return element
    
    def _get_elements(self, driver:WebDriver, element:list[WebElement]):
        """
        ### _get_elements
        Pass parameter 'element' in:
            >>> element_type, element_selection = self._get_element_prop(element)
            >>> element = driver.find_elements(element_type, element_selection)
        And return all correspondents WebElements. 
        """
        if isinstance(element, list): 
            return element
        elif isinstance(element, str):
            element_type, element_selection = self._get_element_prop(element)
            elements = driver.find_elements(element_type, element_selection)
            return elements
    
    def _validation(func):
        """
        ### __validation
        Validate function and return if it executed corretly;
        """
        @wraps(func)
        def _validation(*args, **kwargs):
            try:
                func(*args, **kwargs)
                return True, ''
            except Exception as e:
                return False, e
        return _validation
    
    # def _internal_validation(func):
    #     """
    #     ### __validation
    #     Validate function and return if it executed corretly;
    #     """
    #     @wraps(func)
    #     def _internal_validation(*args, **kwargs):
    #         try:
    #             return func(*args, **kwargs)
    #         except Exception as e:
    #             raise e
    #     return _internal_validation
       
    def _get_this_element(self, this_element:str, web_element:WebElement):
        """
        ### _get_this_element
        return corresponding elementelement:
            -   this <element selection [example '*a' will return all children (tags'a')]>
        
        #### This functions work some like "_get_web_element_tag_result", rather that, this replace "this" element in the param
        """
        if not 'this' in this_element:
            return this_element
        if 'this' == this_element:
            return web_element
        
        web_element_tag_result = self._get_web_element_tag_result(web_element, this_element)
                
        if web_element_tag_result != this_element:
            return web_element_tag_result
        else:
            this_element_parameters = this_element.replace("this", "").split()
            for element in  this_element_parameters:
                web_element = self._get_element(web_element, element)
            return web_element
    
    def _get_location_tags(self, param:str, tag_open:str="\{", tag_close:str="\}") -> list[tuple]:
        """
            ### _get_location_tags
            Separe and check if a parameter have a tag to be validate using "_get_web_element_atributte";
            #### That function is a complement of "_get_web_element_atributte".
        """
        param = re.sub('\\\{', "&|+", param)
        param = re.sub('\\\}', "&|-", param)
        
        open_tags = [m.start(0) for m in re.finditer(tag_open, param)]
        close_tags = [m.start(0) for m in re.finditer(tag_close, param)]
        
        # validation
        if len(open_tags) != len(close_tags):
            message = f"[WebFunctions>_get_location_tags: ERROR] invalid element param! check \"{param}\""
            self._error_message(message)

        for i in range(len(open_tags)):
            if open_tags[i] > close_tags[i]:
                message = f"[WebFunctions>_get_location_tags: ERROR] invalid element param! check \"{param}\""
                self._error_message(message)

            if i + 1 <= len(open_tags) -1:
                if close_tags[i] >= open_tags[i+1]:
                    message = f"[WebFunctions>_get_location_tags: ERROR] invalid element param! check \"{param}\""
                    self._error_message(message)
        
        # getting information
        location_tags = [(open_tags[i], close_tags[i])for i in range(len(open_tags))] 

        param = re.sub("\&\|\+", "{", param)
        param = re.sub("\&\|\-", "}", param)
        return param, location_tags
    
    def _get_element_tags(self, param:str):
        """
        ### _get_element_tags
        Separates the parameter into tags defined by {} returning its string pattern along with its functions;
            -   Example:\n
            >>> "Nome do Usuário - {text(#nome_usuario)}" = "Nome do Usuário - Lucas Borges"
        #### That function is a complement of "_get_web_element_atributte".
        """
        param, location_tags = self._get_location_tags(param=param, tag_open="\{", tag_close="\}")
        content_tags = []
        cont_adjust = 0
        for open_tags, close_tags in location_tags:
            content_tags.append(
                re.sub("[{}]", "", param[open_tags - cont_adjust: close_tags - cont_adjust + 1])
            )
            
            param = list(param)
            to_remove = param[open_tags - cont_adjust: close_tags - cont_adjust + 1]
            param[open_tags - cont_adjust: close_tags - cont_adjust + 1] = ["{", "}"]
            
            param = "".join(param)
            cont_adjust += len(to_remove) - 2
        return param, content_tags
    
    def _get_function_result_tag(self, content_tags:str):
        """
        ### _get_function_result_tag
        "content_tags" is a tuple (Function, Parameter)
        Run the Function using its Parameter.
        
        #### That function is a complement of "_get_web_element_atributte".
        """
        
        # only to validation, checking if follow the parameters rules
        self._get_location_tags(param=content_tags, tag_open="\(", tag_close="\)")
        
        result = re.findall(r'(\w+)\((.*)\)', content_tags)
        if result == []:
            message = f"[WebFunctions>get_function_result_tag: ERROR] content_tags do not have function! check {content_tags}"
            self._error_message(message)
            
        func, param = result[0]
        return func, param
    
    def _get_element_text(self, driver, element, file_name_date_format:dict[str:str]=False) -> str:
        """
        ### _get_element_text
        use "get_element_text" in value
        :param file_name_date_format: Transform the "web_element_text" in datetime to set a format: \n
        Has to be a dict with {"input": "format", "output": "format"}, ex.:
        >>> {"input": "%d/%m/%Y", "output": "%m_%Y")
        #### Will probably be discontinued
        """
        web_element = self._get_element(driver, element)
        web_element_text = web_element.text

        if file_name_date_format: 
            web_element_text = datetime.datetime.strptime(web_element_text, file_name_date_format['input'])
            web_element_text = web_element_text.strftime(file_name_date_format['output'])

        return web_element_text
    
    def _validate_text(self, driver, text_props):
        """
        ### _validate_text
        #### Will probably be discontinued
        """
        if isinstance(text_props, dict) and "get_element_text" in text_props:
            result = self._get_element_text(driver, **text_props["get_element_text"])
        else:
            result = text_props
        return result
    
    def _get_web_element_tag_result(self, driver:WebDriver, param):
        if not isinstance(param, str):
            return param
        
        string_tag, param_tags = self._get_element_tags(param=param)
        if param_tags:
            result_tag = []
            for param_tag in param_tags:
                
                func, param = self._get_function_result_tag(param_tag)
                
                if 'this' in param:
                    this_element_parameters = param.replace("this", "").split()
                    
                    web_element_consult = driver # this instance WebElement
                    
                    for element in this_element_parameters:
                        web_element_consult = self._get_element(web_element_consult, element)
                        
                    result_tag.append(self.web_element_functions[func](web_element_consult))
                    
                else:
                    func, param = self._get_function_result_tag(param_tag)
                    if param:
                        web_element_consult = self._get_element(driver, param)
                        result_tag.append(self.web_element_functions[func](web_element_consult))
                    else:
                        result_tag.append(self.web_element_functions[func]())
                    
            return string_tag.format(*result_tag) 
        else:
            return string_tag

    def _validate_file(self, file_path:str=False, file_request_content=False):
        if file_path:
            file = pathlib.Path(file_path)
            if file.stat().st_size <= 0:
                self._error_message(
                   f"[WebFunctions>_validate_file: ERROR] File size errorn, check the download function:\n    - File: {str(file)}"
                )
        elif file_request_content:... # TODO download from email
        
        
        
    def _get_web_element_atributte(func):
        @wraps(func)
        def _get_web_element_atributte(self, driver, *args, **kwargs):
            new_args = []
            new_kwargs = {}
            for value in args:
                new_args.append(self._get_web_element_tag_result(driver, value))
                
            for key, value in kwargs.items():
                new_kwargs[key] = self._get_web_element_tag_result(driver, value)
                             
            return func(self, driver, *new_args, **new_kwargs)
        return _get_web_element_atributte