"""

_call
===================================

Implementation of the call functions used to download data from the server

"""

from .generaltypes import __itemList__, HttpBody
from .common import (RestMethod, DataType, DictX, ListX, get_allowed_letters,
                     repeat_letter, timestamp, shorten_text)
from .ioutils import save_json, save_textfile, save_binary

import math
import base64
import httpx
import json
import threading
import asyncio
import concurrent.futures
import contextlib
from pathlib import Path
from io import BufferedReader
import random


class ResponseX:
    def __init__(self, response: httpx.Response) -> None:
        self.httpx_response = response
        self._content_type = response.headers.get("content-type", "")
        self._status_code = response.status_code
        self._encoding = response.encoding
        self._content = DictX(response.content, encoding=self._encoding if self._encoding is not None else "utf-8")
        self._content.indentation = 4
        self._data_type = get_data_type(self._content)

    @property
    def content_type(self) -> str:
        return self._content_type

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def encoding(self) -> str | None:
        return self._encoding

    @property
    def content(self) -> DictX:
        return self._content

    @property
    def data_type(self) -> str:
        return self._data_type
    
    @property
    def json(self) -> DictX | ListX | None:
        result = self._content
        if result is None:
            return None
        if self.data_type == DataType.DICT.value:
            result = self._content
        elif self.data_type == DataType.LIST.value:
            result = self._content[DataType.LIST.value]
        else:
            raise Exception(f'Cannot convert response to JSON. Response data type must be '
                            f'either {DataType.DICT.value} or {DataType.LIST.value}, but it is {str(self.data_type)}.')
        return result
    
    @property
    def dict(self) -> dict:
        data_type = self.data_type
        if data_type == DataType.DICT.value:
            return self._content
        raise Exception(f'Response data type is not {DataType.DICT.value}, it is {str(data_type)}. '
                        f'Please check "data_type" property')
    
    @property
    def list(self) -> list:
        data_type = self.data_type
        if data_type == DataType.LIST.value:
            return self._content[DataType.LIST.value]
        raise Exception(f'Response data type is not {DataType.LIST.value}, it is {str(data_type)}. '
                        f'Please check "data_type" property')

    @property
    def text(self) -> str:
        data_type = self.data_type
        if data_type == DataType.TEXT.value:
            return self._content[DataType.TEXT.value]
        raise Exception(f'Response data type is not {DataType.TEXT.value}, it is {str(data_type)}. '
                        f'Please check "data_type" property')

    @property
    def binary(self) -> bytes:
        data_type = self.data_type
        if data_type == DataType.BINARY.value and self._content.binary is not None:
            return self._content.binary
        if data_type != DataType.BINARY.value:
            raise Exception(f'Response data type is not {str(DataType.BINARY.value)}, it is {str(data_type)}. '
                            f'Please check "data_type" property')
        raise Exception(f'Response data type is {str(data_type)} but binary content is None.')


    def save_json(self, filename: str, encoding="utf-8"):
        save_json(filename=filename, value=self.json, encoding=encoding)

    def save_text(self, filename: str, encoding="utf-8"):
        save_textfile(filename=filename, value=self.text, encoding=encoding)

    def save_binary(self, filename: str):
        save_binary(value=self.binary, filename=filename)

    def __str__(self) -> str:
        return str(self._content)


def raise_exception(message: str | dict, setup: DictX) -> httpx.Response:
    if setup["fail_strategy"] == "fail_fast":
        raise Exception(str(message))
    if isinstance(message, str):
        message = {DataType.ERROR.value: message}
    return httpx.Response(504, content=json.dumps(message).encode(), 
                          headers={"Content-Type": "application/json; charset=utf-8"})


def _parse_charset_from_content_type(content_type_value: str) -> str | None:
    content_type_value_lower = content_type_value.lower()
    charset_position = content_type_value_lower.find(f'charset=')
    if charset_position > -1:
        charset_value = content_type_value_lower[charset_position + 8:]
        charset_value += " "
        charset_value = charset_value.split(";")[0]
        charset_value = charset_value.split(",")[0]
        charset_value = charset_value.split(" ")[0]
        return charset_value
    return None


def _get_content_type_of_file(filename: Path) -> str:
    result = 'application/octet-stream'
    extension = filename.resolve().suffix.lower().strip()
    if extension == ".zip":
        result = 'application/zip'
    if extension == ".pdf":
        result = 'application/pdf'
    if extension == ".json":
        result = 'application/json'
    if extension == ".xml":
        result = 'application/xml'
    if extension == ".png":
        result = 'image/png'
    if extension == ".jpg" or extension == ".jpeg":
        result = 'image/jpg'
    return result


def get_server_name_and_port(url: str) -> tuple[str, int | None]:
    """
    Parses the server name and port from the given URL.
    """
    parsed_url = httpx.URL(url)
    server_name = parsed_url.host
    port = parsed_url.port
    return server_name, port


_get_client_lock = threading.Lock()
def _get_sync_client(url: str, setup: DictX) -> httpx.Client:
    """
    Returns httpx.Client instance from setup or creates a new one.
    """
    with _get_client_lock:
        if "url" is None or len(str(url).strip()) < 1:
            raise Exception(f'url must be a valid string')
        if setup is None or not isinstance(setup, DictX) or "http_version" not in setup.keys():
            raise Exception(f'setup must be a valid dictionary created by fetch_setup() function')
        # get server name and port
        server_name, port = get_server_name_and_port(url)
        client_name = f"{server_name}_{port}" if port else f"{server_name}:default"
        client_name += f':thread({str(setup["thread"] if "thread" in setup else 0)})'
        # create httpx_clients dict if not exists and save it to globals
        if "httpx_clients" not in globals():
            globals()["httpx_clients"] = {}
        clients: dict[str, httpx.Client] = globals()["httpx_clients"]
        # get http version
        http_version = setup["http_version"]
        # create httpx.Client instance
        if client_name not in clients.keys():
            client: httpx.Client = httpx.Client(http2=(http_version == "2.0"), verify=False)
        else:
            client: httpx.Client = clients.pop(client_name)
        # store httpx.Client instance as the last one in the dictionary
        globals()["httpx_clients"][client_name] = client
        # limit the number of clients
        if len(clients) > 1024:
            # remove the first client from the dictionary
            first_key = next(iter(clients))
            first_client = clients.pop(first_key)
            first_client.close()
        return client


_pool = concurrent.futures.ThreadPoolExecutor()
@contextlib.asynccontextmanager
async def _get_async_client_lock(lock):
    """
    Asynchronous context manager for acquiring a lock.
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(_pool, lock.acquire)
    try:
        yield
    finally:
        lock.release()

async def _get_async_client(url: str, setup: DictX) -> httpx.AsyncClient:
    """
    Returns httpx.AsyncClient instance from setup or creates a new one.
    """
    with _get_client_lock:
        if "url" is None or len(str(url).strip()) < 1:
            raise Exception(f'url must be a valid string')
        if setup is None or not isinstance(setup, DictX) or "http_version" not in setup.keys():
            raise Exception(f'setup must be a valid dictionary created by fetch_setup() function')
        server_name, port = get_server_name_and_port(url)
        client_name = f"{server_name}_{port}" if port else f"{server_name}:default"
        client_name += f':thread({str(setup["thread"] if "thread" in setup else 0)})'
        # create httpx_async_clients dict if not exists and save it to globals
        if "httpx_async_clients" not in globals():
            globals()["httpx_async_clients"] = {}
        clients: dict[str, httpx.AsyncClient] = globals().get("httpx_async_clients", {})
        # get http version
        http_version = setup["http_version"]
        # create httpx.Client instance
        if client_name not in clients.keys():
            client: httpx.AsyncClient = httpx.AsyncClient(http2=(http_version == "2.0"), verify=False)
        else:
            client: httpx.AsyncClient = clients.pop(client_name)
        # store httpx.Client instance as the last one in the dictionary
        globals()["httpx_async_clients"][client_name] = client
        # limit the number of clients
        if len(clients) > 1024:
            # remove the first client from the dictionary
            first_key = next(iter(clients))
            first_client = clients.pop(first_key)
            await first_client.aclose()
        return client


def _get_files_from_request_body(request_body: HttpBody) -> dict[str, tuple[str, BufferedReader, str]] | None:
    """
    Extracts files from a request body dictionary where values are file URIs.
    Iterates over the request body, identifies values that are file URIs (starting with "file:///"),
    opens the corresponding files in binary mode, determines their content type, and returns a dictionary
    mapping each key to a tuple containing the file name, file object, and content type.
    Args:
        request_body (HttpBody): The request body, expected to be a dictionary with possible file URIs as values.
    Returns:
        dict[str, tuple[str, BufferedReader, str]] | None: 
            A dictionary mapping keys to tuples of (file name, file object, content type), or None if no files are found.
    Raises:
        Exception: If a specified file does not exist.
    """
    if not isinstance(request_body, dict):
        return None
    # collect all files from request body
    files = {}
    # check if request body is a dictionary
    for key, value in request_body.items():
        # check if value is a file
        if isinstance(value, str) and value.lower().startswith("file:///"):
            # remove file:/// prefix and get file path
            value_str = value[len(f'file:///'):]
            # open file
            filename = Path(value_str)
            if not filename.exists():
                raise Exception(f'Cannot load file from "{str(filename)}"')
            # get pure file name
            pure_filename = filename.stem + ''.join(filename.suffixes)
            # open file
            f = open(str(filename.resolve()), 'rb')
            # get file content type
            file_content_type = _get_content_type_of_file(filename)
            # add new field containing the file
            file_item = (pure_filename, f, file_content_type)
            files[key] = file_item
    # delete processed files from request body
    for key in files.keys():
        del request_body[key]
    # if no files were found then return None
    if len(files) == 0:
        files = None
    return files


def _close_files(files: dict[str, tuple[str, BufferedReader, str]] | None) -> None:
    """
    Close all open file handles.
    :param files:
    :return:
    """
    if files is None:
        return
    for _, f, _ in files.values():
        try:
            f.close()
        except Exception as e:
            pass

def _translate_request_body(request_body: HttpBody) -> HttpBody:
    """
    Translates the request body into a format suitable for the HTTP call.
    :param request_body:
    :param setup:
    :return:
    """
    # If the request body is a dictionary, convert it to JSON
    if isinstance(request_body, dict):
        first_key = next(iter(request_body))
        if first_key == DataType.DICT.value or first_key == DataType.LIST.value:
            return request_body[first_key]
        if first_key == DataType.TEXT.value:
            return request_body[first_key]   
        if first_key == DataType.BINARY.value:
            return base64.b64decode(request_body[first_key])
        return request_body
    # If the request body is a string, return it as is
    elif isinstance(request_body, str):
        return request_body
    # If the request body is None, return an empty JSON object
    elif request_body is None:
        return None
    # If the request body is of an unexpected type, raise an exception
    else:
        raise Exception(f"Unexpected request body type: {type(request_body)}")
    

def get_data_type(value: DictX | None) -> str:
    if isinstance(value, DictX):
        return value.data_type.value
    return DataType.UNKNOWN.value


# __SYNC_SECTION_BEGIN__
# async def _async_call_run(url: str, method: str, request_body: HttpBody, setup: DictX) -> httpx.Response: #__ASYNC__
def _sync_call_run(url: str, method: str, request_body: HttpBody, setup: DictX) -> httpx.Response: #__SYNC__
    """

    :param url:
    :param method:
    :param request_headers:
    :param request_body:
    :param setup:
    :return:
    """
    # get headers
    headers: DictX = setup["headers"]
    # gets client setup
    client = _get_sync_client(url, setup) #__SYNC__
    # client = await _get_async_client(url, setup) #__ASYNC__
    # translates request body
    request_body = _translate_request_body(request_body)
    # initialize variables
    content = None
    data = None
    json = None
    params = None
    # get files from request body
    files = _get_files_from_request_body(request_body)
    is_post_put_patch = method in [RestMethod.POST.value, RestMethod.PUT.value, RestMethod.PATCH.value]
    if len(files or {}) > 0 and not is_post_put_patch:
        # if there are files and method is not POST then raise exception
        return raise_exception(f'File uploads are not supported for HTTP method {method}. '
                               f'Only the POST, PUT, PATCH methods support file uploads.', setup)
    # detect content type and prepare variables  
    content_type = headers.case_insensitive_get_value("content-type")
    if content_type is not None:
        content_type = str(content_type).lower()
    if request_body is not None:
        # if method is post and files are present and request body is type of dict or list
        if is_post_put_patch and len(files or {}) > 0 and (isinstance(request_body, dict) or isinstance(request_body, list)):
            json = request_body
        # if method is post and no files are present and content_type is application/x-www-form-urlencoded
        elif is_post_put_patch and isinstance(request_body, dict) and content_type == "application/x-www-form-urlencoded":
            data = request_body
        # if method is post and no files are present
        elif is_post_put_patch and (isinstance(request_body, dict) or isinstance(request_body, list)):
            json = request_body
        # if method is get and request_body is a dict
        elif not is_post_put_patch and isinstance(request_body, dict):
            params = request_body
        # if method is post and request_body is a string and content_type is multipart/form-data
        elif is_post_put_patch and isinstance(request_body, str) and isinstance(content_type, str) and \
            content_type.find("multipart/form-data") > -1 and content_type.find("boundary=") > -1:
            content = request_body.encode()
        # if method is post and request_body is a string and content_type is application/x-www-form-urlencoded
        elif is_post_put_patch and isinstance(request_body, str):
            content = request_body.encode()
        # if method is get and request_body is a string
        elif not is_post_put_patch and isinstance(request_body, str):
            params = request_body
        # if method is post and request_body is a string and content_type is application/binary or application/zip
        elif is_post_put_patch and isinstance(request_body, (bytes, bytearray)):
            content = request_body
            if content_type is None:
                headers.case_insensitive_update({"content-type": "application/binary"}) 
        else:
            return raise_exception("Unknown content-type of the request_body. content-type header "
                                   "is not set and Fetch is not able to detect the content-type automatically", setup)

    try:
        # if verbose then print header
        if setup["verbose_level"] >= 2:
            verbose_message = ""
            # get inputs to request
            content_str = str(content) if content is not None else None
            data_str = str(data) if data is not None else None
            json_str = str(json) if json is not None else None
            params_str = str(params) if params is not None else None
            files_str = str([key for key in files.keys()]) if files is not None and len(files or {}) > 0 else None
            if is_post_put_patch:
                arguments = {"url": url, "headers": headers, "content": content_str, "data": data_str, "json": json_str, "files": files_str}
            else:
                arguments = {"url": url, "headers": headers, "params": params_str}
            # create message
            verbose_message += repeat_letter(value=f' HTTPX_{method} ', letter='-')
            verbose_message += repeat_letter(value=f' {timestamp()}(CALLID_{setup["uid"]}) ', letter='-')
            request_str = DictX(arguments).to_str()
            if setup["verbose_level"] == 2:
                request_str = str(shorten_text(request_str))
            verbose_message += request_str + "\n"
            print(verbose_message.strip())
        # call the server and return response
        if method == str(RestMethod.POST):
            result = client.post(url, content=content, data=data, json=json, files=files, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__SYNC__
            # result = await client.post(url, content=content, data=data, json=json, files=files, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__ASYNC__
        elif method == str(RestMethod.PUT):
            result = client.put(url, content=content, data=data, json=json, files=files, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__SYNC__
            # result = await client.put(url, content=content, data=data, json=json, files=files, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__ASYNC__
        elif method == str(RestMethod.PATCH):
            result = client.patch(url, content=content, data=data, json=json, files=files, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__SYNC__
            # result = await client.patch(url, content=content, data=data, json=json, files=files, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__ASYNC__
        elif method == str(RestMethod.GET):
            result = client.get(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__SYNC__
            # result = await client.get(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__ASYNC__
        elif method == str(RestMethod.OPTIONS):
            result = client.options(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__SYNC__
            # result = await client.options(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__ASYNC__
        elif method == str(RestMethod.HEAD):
            result = client.head(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__SYNC__
            # result = await client.head(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__ASYNC__
        elif method == str(RestMethod.DELETE):
            result = client.delete(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__SYNC__
            # result = await client.delete(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__ASYNC__
        else:
            return raise_exception({DataType.ERROR.value: f'Unknown method in _(a)sync_call_run. Currently only GET, POST, '
                                                 f'OPTIONS, HEAD, PUT, DELETE and PATCH methods are supported.'}, setup)
        _close_files(files)
        return result
    except Exception as err:
        _close_files(files)
        return raise_exception({DataType.ERROR.value: f'Error when calling "{str(url)}" with body "{str(request_body)}" using method "{str(method)}". '
                                             f'Exception "{str(type(err))}" was triggered.\n\n{get_allowed_letters(str(err))}'}, setup)
# __SYNC_SECTION_END__
# __ASYNC_SECTION_BEGIN__
async def _async_call_run(url: str, method: str, request_body: HttpBody, setup: DictX) -> httpx.Response: #__ASYNC__
# def _sync_call_run(url: str, method: str, request_body: HttpBody, setup: DictX) -> httpx.Response: #__SYNC__
    """

    :param url:
    :param method:
    :param request_headers:
    :param request_body:
    :param setup:
    :return:
    """
    # get headers
    headers: DictX = setup["headers"]
    # gets client setup
    # client = _get_sync_client(url, setup) #__SYNC__
    client = await _get_async_client(url, setup) #__ASYNC__
    # translates request body
    request_body = _translate_request_body(request_body)
    # initialize variables
    content = None
    data = None
    json = None
    params = None
    # get files from request body
    files = _get_files_from_request_body(request_body)
    is_post_put_patch = method in [RestMethod.POST.value, RestMethod.PUT.value, RestMethod.PATCH.value]
    if len(files or {}) > 0 and not is_post_put_patch:
        # if there are files and method is not POST then raise exception
        return raise_exception(f'File uploads are not supported for HTTP method {method}. '
                               f'Only the POST, PUT, PATCH methods support file uploads.', setup)
    # detect content type and prepare variables  
    content_type = headers.case_insensitive_get_value("content-type")
    if content_type is not None:
        content_type = str(content_type).lower()
    if request_body is not None:
        # if method is post and files are present and request body is type of dict or list
        if is_post_put_patch and len(files or {}) > 0 and (isinstance(request_body, dict) or isinstance(request_body, list)):
            json = request_body
        # if method is post and no files are present and content_type is application/x-www-form-urlencoded
        elif is_post_put_patch and isinstance(request_body, dict) and content_type == "application/x-www-form-urlencoded":
            data = request_body
        # if method is post and no files are present
        elif is_post_put_patch and (isinstance(request_body, dict) or isinstance(request_body, list)):
            json = request_body
        # if method is get and request_body is a dict
        elif not is_post_put_patch and isinstance(request_body, dict):
            params = request_body
        # if method is post and request_body is a string and content_type is multipart/form-data
        elif is_post_put_patch and isinstance(request_body, str) and isinstance(content_type, str) and \
            content_type.find("multipart/form-data") > -1 and content_type.find("boundary=") > -1:
            content = request_body.encode()
        # if method is post and request_body is a string and content_type is application/x-www-form-urlencoded
        elif is_post_put_patch and isinstance(request_body, str):
            content = request_body.encode()
        # if method is get and request_body is a string
        elif not is_post_put_patch and isinstance(request_body, str):
            params = request_body
        # if method is post and request_body is a string and content_type is application/binary or application/zip
        elif is_post_put_patch and isinstance(request_body, (bytes, bytearray)):
            content = request_body
            if content_type is None:
                headers.case_insensitive_update({"content-type": "application/binary"}) 
        else:
            return raise_exception("Unknown content-type of the request_body. content-type header "
                                   "is not set and Fetch is not able to detect the content-type automatically", setup)

    try:
        # if verbose then print header
        if setup["verbose_level"] >= 2:
            verbose_message = ""
            # get inputs to request
            content_str = str(content) if content is not None else None
            data_str = str(data) if data is not None else None
            json_str = str(json) if json is not None else None
            params_str = str(params) if params is not None else None
            files_str = str([key for key in files.keys()]) if files is not None and len(files or {}) > 0 else None
            if is_post_put_patch:
                arguments = {"url": url, "headers": headers, "content": content_str, "data": data_str, "json": json_str, "files": files_str}
            else:
                arguments = {"url": url, "headers": headers, "params": params_str}
            # create message
            verbose_message += repeat_letter(value=f' HTTPX_{method} ', letter='-')
            verbose_message += repeat_letter(value=f' {timestamp()}(CALLID_{setup["uid"]}) ', letter='-')
            request_str = DictX(arguments).to_str()
            if setup["verbose_level"] == 2:
                request_str = str(shorten_text(request_str))
            verbose_message += request_str + "\n"
            print(verbose_message.strip())
        # call the server and return response
        if method == str(RestMethod.POST):
            # result = client.post(url, content=content, data=data, json=json, files=files, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__SYNC__
            result = await client.post(url, content=content, data=data, json=json, files=files, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__ASYNC__
        elif method == str(RestMethod.PUT):
            # result = client.put(url, content=content, data=data, json=json, files=files, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__SYNC__
            result = await client.put(url, content=content, data=data, json=json, files=files, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__ASYNC__
        elif method == str(RestMethod.PATCH):
            # result = client.patch(url, content=content, data=data, json=json, files=files, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__SYNC__
            result = await client.patch(url, content=content, data=data, json=json, files=files, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__ASYNC__
        elif method == str(RestMethod.GET):
            # result = client.get(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__SYNC__
            result = await client.get(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__ASYNC__
        elif method == str(RestMethod.OPTIONS):
            # result = client.options(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__SYNC__
            result = await client.options(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__ASYNC__
        elif method == str(RestMethod.HEAD):
            # result = client.head(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__SYNC__
            result = await client.head(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__ASYNC__
        elif method == str(RestMethod.DELETE):
            # result = client.delete(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__SYNC__
            result = await client.delete(url, params=params, headers=headers, timeout=setup["timeout"], follow_redirects=True) #__ASYNC__
        else:
            return raise_exception({DataType.ERROR.value: f'Unknown method in _(a)sync_call_run. Currently only GET, POST, '
                                                 f'OPTIONS, HEAD, PUT, DELETE and PATCH methods are supported.'}, setup)
        _close_files(files)
        return result
    except Exception as err:
        _close_files(files)
        return raise_exception({DataType.ERROR.value: f'Error when calling "{str(url)}" with body "{str(request_body)}" using method "{str(method)}". '
                                             f'Exception "{str(type(err))}" was triggered.\n\n{get_allowed_letters(str(err))}'}, setup)
# __ASYNC_SECTION_END__


# __SYNC_SECTION_BEGIN__
# async def _async_call(url: str, method: str, body: HttpBody, setup: DictX) -> ResponseX: #__ASYNC__
def _sync_call(url: str, method: str, body: HttpBody, setup: DictX) -> ResponseX: #__SYNC__
    """
    Calls rest api endpoint
    :param url: URL of the REST api endpoint
    :param method: POST or GET
    :param request_headers:
    :param request_body: json body of the request
    :param setup:
    :return:
    """
    r = _sync_call_run(url=url, method=method, request_body=body, setup=setup) #__SYNC__
    # r = await _async_call_run(url=url, method=method, request_body=body, setup=setup) #__ASYNC__
    result = ResponseX(r)
    _print_verbose_output(result, setup)
    return result
# __SYNC_SECTION_END__
# __ASYNC_SECTION_BEGIN__
async def _async_call(url: str, method: str, body: HttpBody, setup: DictX) -> ResponseX: #__ASYNC__
# def _sync_call(url: str, method: str, body: HttpBody, setup: DictX) -> ResponseX: #__SYNC__
    """
    Calls rest api endpoint
    :param url: URL of the REST api endpoint
    :param method: POST or GET
    :param request_headers:
    :param request_body: json body of the request
    :param setup:
    :return:
    """
    # r = _sync_call_run(url=url, method=method, request_body=body, setup=setup) #__SYNC__
    r = await _async_call_run(url=url, method=method, request_body=body, setup=setup) #__ASYNC__
    result = ResponseX(r)
    _print_verbose_output(result, setup)
    return result
# __ASYNC_SECTION_END__


def _print_verbose_output(response: ResponseX, setup: DictX) -> None:
        # if verbose then print result
        verbose_message = ""
        if setup["verbose_level"] >= 2:
            verbose_message += repeat_letter(value=f' HTTP_RESPONSE_STATUS ', letter='-')
            verbose_message += repeat_letter(value=f' {timestamp()}(CALLID_{setup["uid"]}) ', letter='-')
            http_response_status = {
                "http_status_code": response.status_code,
                "content_type": response.content_type,
                "data_type": response.data_type
            }
            verbose_message += DictX(http_response_status).to_str() + "\n"
        if setup["verbose_level"] >= 3:
            verbose_message += repeat_letter(value=f' HTTP_RESPONSE_CONTENT ', letter='-')
            verbose_message += repeat_letter(value=f' {timestamp()}(CALLID_{setup["uid"]}) ', letter='-')
            verbose_message += str(response) + "\n"
        if setup["verbose_level"] in [1, 2]:
            verbose_message += repeat_letter(value=f' HTTP_RESPONSE_CONTENT ', letter='-')
            verbose_message += repeat_letter(value=f' {timestamp()}(CALLID_{setup["uid"]}) ', letter='-')
            payload = str(response)
            payload = str(shorten_text(payload)) + "\n"
            verbose_message += payload + "\n"
        if setup["verbose_level"] >= 3:
            verbose_message += repeat_letter(f' HINT ', "-")
            verbose_message += f'# Use "fetch_setup()[\'verbose_level\'] = 0" to stop console output\n'
        if setup["verbose_level"] >= 1:
            print(verbose_message.strip())
