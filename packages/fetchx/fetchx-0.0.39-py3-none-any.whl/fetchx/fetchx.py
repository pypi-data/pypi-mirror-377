"""
fetchx
===================================

Implementation of the ultra universal fetch function similar to the 
fetch function in the Chrome, Firefox, Edge, Opera browser.
Open the browser developer tools, go to the network tab, right click on any
http request and select "copy as fetch". Paste the copied fetch command
into the python script and call the fetch function.

"""

from .generaltypes import HttpBody
from .common import DictX, DataType, repeat_letter, timestamp, get_uid
from ._call import ResponseX, _sync_call, _async_call, raise_exception


def _get_example_str() -> str:
    return "https://pypi.org/project/fetchx/"


def _is_valid_method(method: str) -> bool:
    method = method.upper()
    methods = ["GET", "POST", "OPTIONS", "HEAD", "PUT", "DELETE", "PATCH"]
    if method in methods:
        return True
    return False


def _fetch_prepare_params(url: str, fetch_body: HttpBody = None, 
                          setup: DictX | dict | None = None) -> tuple[str, str, str | DictX | None, DictX]:
    """
    Returns url, method, body and setup from chrome fetch
    :return:
    """
    # check url
    if url is None or not isinstance(url, str):
        raise Exception(f'url must be string')

    # get setup
    if setup is None:
        setup = fetch_setup(duplicate=True)
    elif isinstance(setup, DictX):
        pass
    else:
        setup = DictX(setup)

    # solve the case when only url is specified
    if fetch_body is None:
        return url, "GET", None, setup

    # solve the case when only url is specified
    if isinstance(fetch_body, str):
        return url, "GET", fetch_body, setup

    if isinstance(fetch_body, dict):
        request = DictX(fetch_body)
        body = request.case_insensitive_get_value("body")
        if body is not None and not isinstance(body, str) and not isinstance(body, dict):
            raise Exception(f'Invalid body type: {type(body)}. Expected None or str or dict.')
        # process body from chrome fetch
        if body is not None:
            temp_body = DictX(body)
            temp_body_data_type = temp_body.data_type
            # if body is json then set body as dict
            if temp_body_data_type == DataType.DICT:
                body = temp_body
            elif temp_body_data_type == DataType.LIST:
                pass
            # otherwise if body is not a str then raise exception
            elif temp_body_data_type != DataType.TEXT:
                raise Exception(f'Unknown data type of "body" element in "request_body" parameter.')
        # get method
        if request.case_insensitive_get_key("method") is None:
            raise Exception(f'Parameter "method" must exist in the request_body but it is not.\n{str(request)}. '
                            f'If the first argument of the "fetch" fuction is a string (which is the case) '
                            f'the second argument must be either null or a dictionary containing "method" element '
                            f'for example "method": "GET", or "method": "POST".\n\nIt is assumed the "fetch" function was copied'
                            f'from chrome browser using "copy as fetch" item in the network popup menu. See {_get_example_str()}')
        method = str(request.case_insensitive_get_value("method")).strip().upper()
        if not _is_valid_method(method):
            raise_exception(f'Method "{method}" is not a valid http method. Try to use "GET" or "POST".', setup=setup)
        # switch headers
        if request.case_insensitive_get_key("headers") is not None:
            setup["headers"] = request.case_insensitive_get_value("headers")
        return url, method, body, setup # type: ignore
    raise Exception(f"fetch was called using invalid combination of arguments. See {_get_example_str()}")


def _init_fetch_setup():    
    setup = DictX({
        # Will raise exception if error occurs. Default value is True. Default value can be modified using fetch_global_setup(...)
        "fail_strategy": "try_to_compensate",
        # timeout: How long to wait for the http, https response. Default value is 120. Default value can be modified using fetch_global_setup(...)
        "timeout": 120,
        # if verbose is true then fetch will automatically print out result into the console output
        "verbose_level": 0,
        # http version to use possible options "1.1", "2.0"
        "http_version": "2.0",
        "thread": 0,
        # following http headers will be sent during fetch request
        "headers": {
            "accept": "*/*;q=0.9",
            "accept-language": "*;q=0.9",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=1",
            "sec-ch-ua-mobile": "?0"
        }
    })
    setup.indentation = 4
    setup["verbose_level"] = 3 if __debug__ else 0
    # make fetchx_setup_global_vars available globally
    globals()["fetchx_setup_global_vars"] = setup

# Initialize fetch setup
_init_fetch_setup()


# def fetch_setup:
def fetch_setup(duplicate: bool = False) -> DictX:
    """
    Gets a copy or a reference to fetch setup dictionary
    If "duplicate" is True, a copy will be returned, otherwise a reference will be returned.
    :param duplicate: If True, return a copy of the setup dictionary, otherwise return a reference.
    :return: A copy or a reference to the fetch setup dictionary.
    """
    result: DictX = globals()["fetchx_setup_global_vars"]
    if duplicate:
        return result.duplicate()
    else:
        return result


# __SYNC_SECTION_BEGIN__
# async def acall(url: str, method: str | None = None, body: HttpBody = None, setup: DictX | dict | None = None) -> ResponseX: #__ASYNC__
def call(url: str, method: str | None = None, body: HttpBody = None, setup: DictX | dict | None = None) -> ResponseX: #__SYNC__
    """"
    Calls a REST API endpoint and returns the response.
    """
    # determine method
    method = str(method).strip().upper()
    if method is None and body is None:
        method = "GET"
    if method is None and body is not None:
        method = "POST"
    if not isinstance(method, str):
        raise Exception(f'argument "method" must be a string but it is type of "{str(type(method))}"')
    
    # check if body is valid
    if body is not None and not isinstance(body, dict) and not isinstance(body, str):
        raise Exception(f'argument "body" must be a dict or str or None but it is type of "{str(type(body))}"')
    
    # check if setup is valid
    if setup is None:
        setup = fetch_setup()
    # setup must be an instance of dict
    if not isinstance(setup, dict):
        raise Exception(f'argument "setup" must be a dict but it is type of "{str(type(body))}"')
    # if setup is a dict but not DictX then transform it
    if isinstance(setup, DictX):
        setup = setup.duplicate()
    elif isinstance(setup, dict):
        setup = DictX(setup)
    # set uid of the fetch or call
    setup["uid"] = get_uid()
    
    # if verbose then print header
    if setup["verbose_level"] >= 1:
        print(repeat_letter(value=f' call ').rstrip()) #__SYNC__
        # print(repeat_letter(value=f' acall ').rstrip()) #__ASYNC__
    if setup["verbose_level"] >= 3:
        verbose_message = ""
        verbose_message += repeat_letter(value=f' INPUTS ', letter='-')
        verbose_message += repeat_letter(value=f' {timestamp()}(CALLID_{setup["uid"]}) ', letter='-')
        arguments = {"url": url, "method": method, "body": body, "setup": setup}
        verbose_message += DictX(arguments).to_str() + "\n"
        print(verbose_message)
    # call command
    result = _sync_call(url=url, method=method, body=body, setup=setup) #__SYNC__
    # result = await _async_call(url=url, method=method, body=body, setup=setup) #__ASYNC__
    return result
# __SYNC_SECTION_END__
# __ASYNC_SECTION_BEGIN__
async def acall(url: str, method: str | None = None, body: HttpBody = None, setup: DictX | dict | None = None) -> ResponseX: #__ASYNC__
# def call(url: str, method: str | None = None, body: HttpBody = None, setup: DictX | dict | None = None) -> ResponseX: #__SYNC__
    """"
    Calls a REST API endpoint and returns the response.
    """
    # determine method
    method = str(method).strip().upper()
    if method is None and body is None:
        method = "GET"
    if method is None and body is not None:
        method = "POST"
    if not isinstance(method, str):
        raise Exception(f'argument "method" must be a string but it is type of "{str(type(method))}"')
    
    # check if body is valid
    if body is not None and not isinstance(body, dict) and not isinstance(body, str):
        raise Exception(f'argument "body" must be a dict or str or None but it is type of "{str(type(body))}"')
    
    # check if setup is valid
    if setup is None:
        setup = fetch_setup()
    # setup must be an instance of dict
    if not isinstance(setup, dict):
        raise Exception(f'argument "setup" must be a dict but it is type of "{str(type(body))}"')
    # if setup is a dict but not DictX then transform it
    if isinstance(setup, DictX):
        setup = setup.duplicate()
    elif isinstance(setup, dict):
        setup = DictX(setup)
    # set uid of the fetch or call
    setup["uid"] = get_uid()
    
    # if verbose then print header
    if setup["verbose_level"] >= 1:
        # print(repeat_letter(value=f' call ').rstrip()) #__SYNC__
        print(repeat_letter(value=f' acall ').rstrip()) #__ASYNC__
    if setup["verbose_level"] >= 3:
        verbose_message = ""
        verbose_message += repeat_letter(value=f' INPUTS ', letter='-')
        verbose_message += repeat_letter(value=f' {timestamp()}(CALLID_{setup["uid"]}) ', letter='-')
        arguments = {"url": url, "method": method, "body": body, "setup": setup}
        verbose_message += DictX(arguments).to_str() + "\n"
        print(verbose_message)
    # call command
    # result = _sync_call(url=url, method=method, body=body, setup=setup) #__SYNC__
    result = await _async_call(url=url, method=method, body=body, setup=setup) #__ASYNC__
    return result
# __ASYNC_SECTION_END__


# __SYNC_SECTION_BEGIN__
# async def afetch(url: str, body: HttpBody = None, setup: DictX | None = None) -> ResponseX: #__ASYNC__
def fetch(url: str, body: HttpBody = None, setup: DictX | None = None) -> ResponseX: #__SYNC__
    """
    Calls rest api url and returns response.
    Fetch command is typically copied directly from the Chrome browser
    :param url: Contains url string or dictionary (json) containing url, method and optionally a token for example {"url": "...", "method": "POST", "token": "..."}
    :param method: "GET" or "POST"
    :param body:
    :param setup:
    :return:
    """
    new_url, new_method, new_body, new_setup = _fetch_prepare_params(url=url, fetch_body=body, setup=setup)
    # if verbose then print info
    if new_setup["verbose_level"] >= 3:
        verbose_message = ""
        arguments = {"url": url, "body": body, "setup": setup}
        verbose_message += repeat_letter(value=f' fetch ') #__SYNC__
        # verbose_message += repeat_letter(value=f' afetch ') #__ASYNC__
        verbose_message += repeat_letter(value=f' INPUTS ', letter='-')
        verbose_message += repeat_letter(value=f' {timestamp()} ', letter='-')
        verbose_message += DictX(arguments).to_str() + "\n"
        verbose_message += repeat_letter(value=' TRIGGERING CALL(...) ', letter='-') #__SYNC__
        verbose_message += f"Triggering \"call\" function. fetch() is always translated to call()\n" #__SYNC__
        # verbose_message += repeat_letter(value=' TRIGGERING ACALL(...) ', letter='-') #__ASYNC__
        # verbose_message += f"Triggering \"acall\" function. afetch() is always translated to acall()\n" #__ASYNC__
        print(verbose_message)
    result = call(url=new_url, method=new_method, body=new_body, setup=new_setup) #__SYNC__
    # result = await acall(url=new_url, method=new_method, body=new_body, setup=new_setup) #__ASYNC__
    return result
# __SYNC_SECTION_END__
# __ASYNC_SECTION_BEGIN__
async def afetch(url: str, body: HttpBody = None, setup: DictX | None = None) -> ResponseX: #__ASYNC__
# def fetch(url: str, body: HttpBody = None, setup: DictX | None = None) -> ResponseX: #__SYNC__
    """
    Calls rest api url and returns response.
    Fetch command is typically copied directly from the Chrome browser
    :param url: Contains url string or dictionary (json) containing url, method and optionally a token for example {"url": "...", "method": "POST", "token": "..."}
    :param method: "GET" or "POST"
    :param body:
    :param setup:
    :return:
    """
    new_url, new_method, new_body, new_setup = _fetch_prepare_params(url=url, fetch_body=body, setup=setup)
    # if verbose then print info
    if new_setup["verbose_level"] >= 3:
        verbose_message = ""
        arguments = {"url": url, "body": body, "setup": setup}
        # verbose_message += repeat_letter(value=f' fetch ') #__SYNC__
        verbose_message += repeat_letter(value=f' afetch ') #__ASYNC__
        verbose_message += repeat_letter(value=f' INPUTS ', letter='-')
        verbose_message += repeat_letter(value=f' {timestamp()} ', letter='-')
        verbose_message += DictX(arguments).to_str() + "\n"
        # verbose_message += repeat_letter(value=' TRIGGERING CALL(...) ', letter='-') #__SYNC__
        # verbose_message += f"Triggering \"call\" function. fetch() is always translated to call()\n" #__SYNC__
        verbose_message += repeat_letter(value=' TRIGGERING ACALL(...) ', letter='-') #__ASYNC__
        verbose_message += f"Triggering \"acall\" function. afetch() is always translated to acall()\n" #__ASYNC__
        print(verbose_message)
    # result = call(url=new_url, method=new_method, body=new_body, setup=new_setup) #__SYNC__
    result = await acall(url=new_url, method=new_method, body=new_body, setup=new_setup) #__ASYNC__
    return result
# __ASYNC_SECTION_END__


def translate_fetch(url: str, body: HttpBody = None) -> str:
    """
    Translate fetch command into call command and print generated source code
    :param url:
    :param body:
    :return:
    """
    url, method, body, setup = _fetch_prepare_params(url=url, fetch_body=body)
    result = ""
    # generate code
    # setup url and method
    result += f'url = "{url}"\n'
    result += f'method = "{method}"\n'
    # setup body
    if body is None:
        result += f'body = None\n'
    elif isinstance(body, str):
        new_body = body.replace("\"", "\\\"")
        result += f'body = """{new_body}"""\n'
    elif isinstance(body, DictX):
        result += f'body = {body.to_str()}\n'
    elif isinstance(body, dict):
        result += f'body = {DictX(body).to_str()}\n'
    else:
        result += f'{DataType.ERROR.value: "Unknown type of body"}\n'
    custom_setup = DictX(setup).to_str()
    # create call command
    result += f'custom_setup = {custom_setup}\n'
    result += f'response = call(url=url, method=method, body=body, setup=custom_setup)\n'
    # if verbose then print result
    if setup["verbose_level"] >= 1:
        print(result)
    return result


def smart_translate_fetch(url: str, request_body: HttpBody = None) -> str:
    url, method, body, setup = _fetch_prepare_params(url=url, fetch_body=request_body)
    # setup body_str
    body_str = None
    if body is not None:
        if isinstance(body, DictX):
            body_str = f'"{body.to_str()}"'
        elif isinstance(body, str):
            body_str = f'"{DictX(body, dict_indent=4).to_str()}"'
        elif isinstance(body, dict):
            body_str = f'{DictX(body, dict_indent=4).to_str()}'
        else:
            raise Exception(f'Unknown type of body in smart translate fetch command. Body must be either str or dict but it is {str(type(body))}')
    # setup authorization if the authorization header exists
    authorization = DictX(setup["headers"]).case_insensitive_get_value("authorization")
    if authorization is not None:
        if not isinstance(authorization, str):
            raise Exception(f'Authorization header must be a string but it is {str(type(authorization))}')
    # generate code
    result = ""
    # if the input is like fetch("http://example.com") then translate to call(url="http://example.com")
    if body_str is None and method == "GET" and authorization is None:
        result += f'response = call(url="{url}")\n'
    # if the input is like fetch("http://example.com", setup={..."Authorization": "Bearer or Token ..."})
    # then translate to call with custom setup containing authorization header
    elif body_str is None and method == "GET" and authorization is not None:
        result += f'custom_setup = fetch_setup(duplicate=True)\n'
        result += f'custom_setup["headers"]["authorization"] = "{authorization}"\n'
        result += f'response = call(url="{url}", method="GET", setup=custom_setup)\n'
    # if the input is like fetch("http://example.com", "POST") then translate to call(url="http://example.com", method="POST")
    elif body_str is None and method != "GET" and authorization is None:
        result += f'response = call(url="{url}", method="{method}")'
    # if the input is like fetch("http://example.com", setup={..."Authorization": "Bearer or Token ..."})
    # then translate to call with method post and custom setup containing authorization header
    elif body_str is None and method != "GET" and authorization is not None:
        result += f'custom_setup = fetch_setup(duplicate=True)\n'
        result += f'custom_setup["headers"]["authorization"] = "{authorization}"\n'
        result += f'response = call(url="{url}", method="{method}", setup=custom_setup)\n'
    # if the input contains body then translate to call with body
    elif body_str is not None and authorization is None:
        result += f'body = {body_str}\n'
        result += f'response = call(url="{url}", method="{method}", payload=payload)\n'
    # if the input contains body and authorization 
    # then translate to call with body and custom setup containing authorization header
    elif body_str is not None and authorization is not None:
        result += f'custom_setup = fetch_setup(duplicate=True)\n'
        result += f'custom_setup["headers"]["authorization"] = "{authorization}"\n'
        result += f'body = {body_str}\n'
        result += f'response = call(url="{url}", method="{method}", body=body, setup=custom_setup)\n'
    # otherwise return None
    else:
        result = None
    # result is not None and the verbose level is at least 1 then print the generated code
    if result is not None and setup["verbose_level"] >= 1:
        print(result)
    # if result is None then fallback to translate fetch
    else:   
        result = translate_fetch(url=url, body=request_body)
    return result
