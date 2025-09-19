# Vapix API Python Wrapper by Axis Communications

This Python library provides a seamless wrapper around the Vapix API by Axis Communications with support currently for the Axis A1001.

## Features

- Configuring Doors
- Creating and editting schedules
- Assigning unlock schedules to doors

## Installation

pip3 install axis_vapix

## Quick Start

```python
from axis_vapix.device import a1001

control1 = a1001(host="192.168.1.21", user="root", password="changem3")
```
