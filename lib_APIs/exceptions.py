
class ApiException(Exception):
    """
    Exception when the API request is not successful
    """
    pass

class SameStation(Exception):
    """
    Exception when the closest V-lib_APIs stations of the start and of the end are the same
    """
    pass
