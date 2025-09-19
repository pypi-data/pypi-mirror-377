from .api import api
from .DoorControl import DoorControl
from .Schedule import ScheduleEndpoint

class a1001:
    """
    A class that provides an interface to interact with Axis A1001
    """

    def __init__(self, host, user, password, timeout=5):
        """
        Initializes the Axis A1001
        """
        self.api = api(host=host, user=user, password=password, timeout=timeout)

        self.doorcontrol = DoorControl(self)
        self.schedule = ScheduleEndpoint(self)
