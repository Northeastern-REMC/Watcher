from datetime import datetime
from zoneinfo import ZoneInfo

NREMC_TIMEZONE_NAME = "America/New_York"
NREMC_TIMEZONE = ZoneInfo(NREMC_TIMEZONE_NAME)
IGNITION_EPOCH = datetime(2024, 12, 1, 0, 0, 0, 0, NREMC_TIMEZONE)

ITEMS_PER_PAGE = 5

FAULT_BIT_MAP = {
    2: "Insulation Failure Protection",
    3: "Battery Undervoltage (Primary Protection)",
    4: "Battery Overvoltage Protection",
    5: "Cluster Discharge Undervoltage (Primary)",
    6: "Cluster Charge Overvoltage Protection",
    7: "Cluster Discharge Overcurrent (Primary)",
    8: "Cluster Charge Overcurrent (Primary)",
    9: "Reactor Bus Overcurrent Discharge (Primary)",
    10: "Stack Bus Overcurrent Charge (Primary)",
    11: "Low Temperature (Primary)",
    12: "Overtemperature (Primary)",
    20: "BCMS Device Self-Protection",
    22: "Emergency Stop Fault",
    24: "DC SPD Fault",
    25: "Heap Isolator Protection",
    27: "EMMU Device Self-Protection",
    28: "Cluster Total Pressure Imbalance Protection",
    30: "Fuse Failure Protection",
    33: "Battery Undervoltage (Secondary Protection)",
    34: "Battery Charging Overvoltage (Secondary)",
    35: "Cluster Discharge Undervoltage (Secondary)",
    36: "Cluster Charge Overvoltage (Secondary)",
    37: "Cluster Discharge Overcurrent (Secondary)",
    38: "Cluster Charge Overcurrent (Secondary)",
    39: "Reactor Bus Overcurrent Discharge (Secondary)",
    40: "Heap Bus Charging Overcurrent (Secondary)",
    41: "Low Temperature (Secondary)",
    42: "Overtemperature (Secondary)",
    43: "BA-EMS/LC Comm Exception Protection",
    44: "Temperature Rise Over Limit Protection",
}

ALARM_BIT_MAP = {
    3: "Battery Undervoltage",
    4: "Battery Overvoltage",
    5: "Cluster Discharge Undervoltage",
    6: "Cluster Charge Overvoltage",
    7: "Cluster Overcurrent",
    8: "Cluster Charging Overcurrent",
    9: "Heap Bus Overcurrent",
    10: "Heap Bus Overcurrent Charge",
    11: "Low Temperature",
    12: "Overtemperature",
    14: "Battery Voltage Range Too Large",
    15: "Battery Temperature Range Too Large",
    16: "PCS Communication Exception",
    17: "BMU Communication Exception",
    18: "BC Communication Exception",
    19: "BA-SA Communication Exception",
    20: "BC-SA Communication Exception",
    21: "SOC Too High",
    22: "SOC Too Low",
    25: "EMMU Self Alarm",
    26: "DC SPD Alarm",
    27: "BA-EMS/LC Communication Exception",
    28: "BA-Cabinet Communication Exception",
    29: "Fan Fault",
}
