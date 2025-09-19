from __future__ import annotations
from typing import TYPE_CHECKING
import json
import icalendar
from datetime import datetime

# Import for type hints only
if TYPE_CHECKING:
    from .device import device


class ScheduleEndpoint:

    def __init__(self, device: device) -> None:

        self.api = device.api
        self.api.base_url = "http://" + self.api.host + "/vapix"

        self.schedules = {}

        self.update_schedules()

    def update_schedules(self):

        resp = self.api._send_request("schedule/GetScheduleInfoList")

        for schedule in resp['ScheduleInfo']:

            self.schedules[schedule['token']] = Schedule(token=schedule['token'], schedule=self)

    def create_schedule(self, name, operator="addition", token = "") -> None:

        self.schedules[token] = Schedule(token=token, schedule=self)

        self.schedules[token].name = name
        self.schedules[token].operator = operator
        self.schedules[token].enabled = True

        self.schedules[token].update()
        self.schedules[token].get_schedule()

    def enable_schedules(self, token):

        if token in self.schedules.keys():

            self.schedules[token].enabled = True
            self.schedules[token].get_schedule()

class Schedule:

    def __init__(self, schedule: ScheduleEndpoint, token = "") -> None:

        self.api = schedule.api

        self.name = ""
        self.token = token
        self.description = ""
        self.attribute = []

        self.operator = "addition"
        self.calendar = icalendar.Calendar()

        self.limit = 10000
        self.postfix = 1
        self.parent = token
        self.children = set()
        self.enabled = False

        self.get_schedule()

    def get_schedule(self) -> None:

        if self.enabled:
            resp = self.api._send_request("schedule/GetSchedule", params={"Token": self.token})

            if len(resp['Schedule']) == 0:
                self.calendar = icalendar.Calendar()

                return None

            self.name = resp['Schedule'][0]['Name']
            self.description = resp['Schedule'][0]['Description']
            self.attribute = resp['Schedule'][0]['Attribute']

            if resp['Schedule'][0]['ScheduleDefinition'] != '':
                schedule = resp['Schedule'][0]['ScheduleDefinition']

            elif resp['Schedule'][0]['ExceptionScheduleDefinition']:
                schedule = resp['Schedule'][0]['ExceptionScheduleDefinition']

            self.calendar = icalendar.Calendar.from_ical(schedule)

    def get_ical(self) -> str:

        return icalendar.Calendar.to_ical(self.calendar).decode("utf-8")

    def update(self) -> None:

        if self.enabled:
            if self.operator == "addition":
                scheduledefinition = self.get_ical()
                exceptionscheduledefinition = ""
            else:
                scheduledefinition = ""
                exceptionscheduledefinition = self.get_ical()

            resp = self.api._send_request(
                ("schedule"),
                method="POST",
                params={
                    "axsch:SetSchedule": {
                        "Schedule":[
                        {
                            "Name": self.name,
                            "Description": "",
                            "ScheduleDefinition": scheduledefinition,
                            "ExceptionScheduleDefinition": exceptionscheduledefinition,
                            "Attribute":[],
                            "token": self.token
                        }
                        ]
                    }
                }
            )

    def add_event(self, name, start, end, rrules = "") -> None:

        event = icalendar.Event()

        event.add('summary', name)
        event.add('dtstart', start.replace(tzinfo=None))
        event.add('dtend', end.replace(tzinfo=None))
        event.add('dtstamp', datetime.now())

        if rrules != "":
            event.add('rrules', rrules)

        self.get_schedule()

        self.calendar.add_component(event)

        if len(self.get_ical()) <= self.limit:
            self.update()
        else:
            current = self.postfix
            self.postfix += 1
            
            if self.name.endswith(str(current)):
                self.name = self.name.replace((" " + str(current)), (" " + str(self.postfix)))
                self.token = self.token.replace(("_" + str(current)), ("_" + str(self.postfix)))
            else:
                self.name = self.name + " " + str(self.postfix)
                self.token = self.token + "_" + str(self.postfix)
            
            self.get_schedule()
            self.children.add(self.token)

            self.add_event(name=name, start=start, end=end, rrules=rrules)
