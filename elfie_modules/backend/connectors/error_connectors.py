from uuid import uuid4
from time import time

import requests

from elfie_modules.backend.abstract import functionalconnector
from elfie_modules.backend.channels.handlers import StdErrHandler
from elfie_modules.backend.connectors import ERROR_ADDERROR, ERROR_LIST_ERRORS, ERROR_SEARCH_SOLUTION

ERROR_LIST = {}

@functionalconnector(ERROR_LIST_ERRORS)
def list_errors():
    return list(ERROR_LIST.values())

@functionalconnector(ERROR_ADDERROR)
def add_error(error):
    error_id = uuid4().__str__()
    ERROR_LIST[error_id] = {
        "timestamp": time(),
        **error,
        "id": error_id,
    }
    print("error added")
    return error_id

@functionalconnector(ERROR_SEARCH_SOLUTION)
def search_solution(error_id):
    if error_id not in ERROR_LIST:
        return None
    error = ERROR_LIST[error_id]
    recommendation = StdErrHandler.getRecommendations(error['error'])
    return recommendation