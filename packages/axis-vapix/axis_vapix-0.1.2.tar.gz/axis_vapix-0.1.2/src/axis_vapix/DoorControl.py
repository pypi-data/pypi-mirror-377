from __future__ import annotations
from typing import TYPE_CHECKING

# Import for type hints only
if TYPE_CHECKING:
    from .device import device


class DoorControl:

    def __init__(self, device: device) -> None:

        self.api = device.api
        self.api.base_url = "http://" + self.api.host + "/vapix"

        self.doors = {}

        self.get_doors()

    def get_doors(self):
        """
        Gets the door info.

        Returns:
            list: A dictionary containing door info.
        """
        resp = self.api._send_request(
            "doorcontrol/GetDoorInfoList",
        )

        for door in resp['DoorInfo']:

            self.doors[door['Name']] = Door(token=door['token'], controller=self)

class Door:

    def __init__(self, token, controller: DoorControl) -> None:

        self.controller = controller

        self.actions_table = {
            "Blocked": ("Block","DoubleLock", "Lock", "LockDown", "LockDownRelease", "LockOpen", "LockOpenRelease", "Unlock",),
            "DoubleLocked": ("Block","DoubleLock","Lock","LockDown","LockDownRelease","LockOpen","LockOpenRelease","Unlock"),
            "Locked": ("Block", "DoubleLock","Lock","LockDown", "LockDownRelease", "LockOpen", "LockOpenRelease", "Unlock",),
            "LockedDown": ("LockDown","LockDownRelease",),
            "LockedDownRelease": ("Block", "DoubleLock", "Lock", "LockDown","LockDownRelease", "LockOpen", "LockOpenRelease", "Unlock",),
            "LockedOpen": ("LockOpen", "LockOpenRelease",),
            "LockedOpenRelease": ("Block", "DoubleLock", "Lock", "LockDown", "LockOpen", "LockOpenRelease", "Unlock",),
            "Unlocked": ("Block", "DoubleLock", "Lock", "LockDown", "LockDownRelease", "LockOpen", "LockOpenRelease","Unlock",),
        }

        self.actions = ("Block","DoubleLock","Lock","LockDown","LockDownRelease","LockOpen","LockOpenRelease","Unlock")

        self.Name = 'Door'
        self.Description = 'Door'
        self.Capabilities = {}
        self.token = token
        
        self.DoorPhysicalState = False
        self.Alarm = False
        self.Mode = False

        self.LastUpdate = True
        self.Status = 'Door Created'

        self.unlockschedules = set()
        
        self.update_info()
        self.update_state()
        self.get_unlockschedules()

    def _check_action(self, token, action) -> None:
        """
        Gets the door info.

        Returns:
            list: A dictionary containing door state info.
        """

        if action in self.actions_table[self.Mode] and self.Capabilities[action]:
            return True
        else:
            return False
    
    def update_info(self) -> None:
        """
        Gets the door info.

        Returns:
            list: A dictionary containing door info.
        """
        resp = self.controller.api._send_request(
            "doorcontrol/GetDoorInfo",
            params={"Token": self.token},
        )

        self.Name = resp['DoorInfo'][0]['Name']
        self.Description = resp['DoorInfo'][0]['Description']
        self.Capabilities = resp['DoorInfo'][0]['Capabilities']
        self.token = resp['DoorInfo'][0]['token']

    def update_state(self) -> None:
        """
        Gets the door info.

        Returns:
            list: A dictionary containing door state info.
        """
        resp = self.controller.api._send_request(
            "doorcontrol/GetDoorState",
            params={"Token": self.token},
        )

        if self.Capabilities['DoorMonitor']:
            self.DoorPhysicalState = resp['DoorState']['DoorPhysicalState']
        if self.Capabilities['Alarm']:
            self.Alarm = resp['DoorState']['Alarm']

        self.Mode = resp['DoorState']['DoorMode']

    def set_mode(self, action) -> None:
        """
        Set Door Mode.
        """

        if action in self.actions and self._check_action(token=self.token, action=action):

            resp = self.controller.api._send_request(
                ("doorcontrol/" + action + "Door"),
                params={"Token": self.token},
            )

            self._get_state()

            if self.Mode.startswith(action):
                self.LastUpdate = True
                self.Status = "State Updated"
            else:
                self.LastUpdate = False
                self.Status = "State Not Updated"

        else:

            self.LastUpdate = False
            self.Status = "Action Not Supported"

    def get_unlockschedules(self) -> None:
        """
        Set Door Mode.
        """

        resp = self.controller.api._send_request(
            endpoint="doorcontrol",
            method="POST",
            params={"axtdc:GetDoorScheduleConfiguration":{"Token":[self.token]}}
        )

        self.unlockschedules = set(resp['DoorScheduleConfiguration'][0]['DoorSchedule'][0]['ScheduledState'][0]['ScheduleToken'])

    def set_unlockschedules(self, token="", reset=False):

        if reset:
            self.unlockschedules = set()

        if type(token) is str:
            self.unlockschedules.add(token)
        elif type(token) is list:
            self.unlockschedules.update(token)
        
        resp = self.controller.api._send_request(
            endpoint="doorcontrol",
            method="POST",
            params={
                "axtdc:SetDoorScheduleConfiguration": {
                    "DoorScheduleConfiguration": [
                    {
                        "token": self.token,
                        "Name": '',
                        "Description": '',
                        "DoorSchedule": [
                        {
                            "ScheduledState": [
                            {
                                "ScheduleToken": list(self.unlockschedules),
                                "EnterAction": "Unlock"
                            },
                            ],
                            "PriorityLevel": ''
                        }
                        ]
                    }
                    ]
                }
            }
        )

        self.get_unlockschedules()
