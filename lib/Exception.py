#Exception when the API request is not successful
class ApiException(Exception):
    pass

#Exception when the closest V-lib stations of the start and of the end are the same
class SameStation(Exception):
    pass
