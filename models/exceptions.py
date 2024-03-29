class DisabilityCompatibleException(Exception):
    """
    Exception raised when the itinerary is not accessible for disabled people
    """
    pass

class LoadedCompatibleException(Exception):
    """
    Exception raised when the itinerary is not compatible with heavy loads
    """
    pass

class RainCompatibleException(Exception):
    """
    Exception raised when the itinerary is not rain compatible
    """
    pass

class ForbiddenVehicleException(Exception):
    """
    Exception raised when the user doesn't own the vehicle (ex: car)
    """
    pass