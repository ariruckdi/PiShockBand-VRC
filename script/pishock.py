from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from configparser import ConfigParser

import requests
import asyncio
import json

INTENSITY_TOO_HIGH_WARNING = "WARNING: Intensity limit exeeded, sending max intensity"
DURATION_TOO_HIGH_WARNING = "WARNING: Duration limit exeeded, sending max duration"
SHOCKS_DISABLED_WARNING = "WARNING: Sending shocks was disabled in config, sending beep instead"
TYPELIST_STR = ["shock", "vibrate", "beep"]


class PishockConfig:
    def __init__(self, config = 'pishock.cfg'):
        self.parser = ConfigParser()
        self.config = config
        self.read_config()

    def read_config(self):
        self.parser.read(self.config)
        self.apikey = self.read_str('API', 'APITOKEN')
        self.username = self.read_str('API', 'USERNAME')
        self.name = self.read_str('API', 'APPNAME')
        self.sharecodes = self.read_str_list('SHARECODES', 'SHARECODES')
        self.ip = self.read_ip("SETTINGS", "IP")
        self.port = self.read_int("SETTINGS", "PORT", 0, 65535, 9001)
        self.verbose = self.read_bool("DEBUG", "VERBOSE_OUTPUT")
        self.max_intensity = self.read_int("SAFETY", "MAX_INTENSITY", 1, 100, 25)
        self.max_duration = self.read_int("SAFETY", "MAX_DURATION", 1, 15, 5)
        self.sleeptime_offset = self.read_float("SAFETY", "SLEEPTIME_OFFSET", 0, 100, 1.7)
        self.limit_shocks_only = self.read_bool("SAFETY", "ONLY_LIMIT_SHOCKS")
        self.no_shocks = self.read_bool("SAFETY", "DISABLE_SHOCKS")

    def read_str(self, category, value_name):
        return self.parser[category][value_name]

    def read_str_list(self, category, value_name):
        return self.parser[category][value_name].split()

    def read_int(self, category, value_name, min_value, max_value, default):
        str_unsafe = self.parser[category][value_name]
        if str_unsafe.isnumeric():
            int_unsafe = int(str_unsafe)
            if int_unsafe >= min_value and int_unsafe <= max_value:
                return int_unsafe
        self.print_error(value_name, "int", default, min_value, max_value)
        return default
    
    def read_float(self, category, value_name, min_value, max_value, default):
        str_unsafe = self.parser[category][value_name]
        if str_unsafe.replace(".", "").isnumeric():
            float_unsafe = float(str_unsafe)
            if float_unsafe >= min_value and float_unsafe <= max_value:
                return float_unsafe
        self.print_error(value_name, "float", default, min_value, max_value)
        return default

    def read_ip(self, category, value_name, default = "127.0.0.1"):
        ip_unsafe = self.parser[category][value_name]
        ip_list = ip_unsafe.split(".")
        for ip_int_str_unsafe in ip_list:
            if not ip_int_str_unsafe.isnumeric():
                self.print_error(value_name, "IP adress", default)
                return default
            ip_int_unsafe = int(ip_int_str_unsafe)
            if ip_int_unsafe < 0 or ip_int_unsafe > 255:
                self.print_error(value_name, "IP adress", default)
                return default
        return ip_unsafe

    def read_bool(self, category, value_name):
        return self.parser[category][value_name].lower() == "true"

    def print_error(self, value_name, type, default, min_value = None, max_value = None):
        error_message = f"ERROR: {value_name} was misconfigured (needs to be {type}). Using default value of {default}. "
        if min_value != None and max_value != None:
            error_message += f"The value has to be between {min_value} and {max_value}."
        #print(error_message)

    def print_values(self):
        print(f"apikey:             {self.apikey}")
        print(f"username:           {self.username}")
        print(f"name:               {self.name}")
        print(f"sharecodes:         {self.sharecodes}")
        print(f"ip:                 {self.ip}")
        print(f"port:               {self.port}")
        print(f"verbose:            {self.verbose}")
        print(f"max_intensity:      {self.max_intensity}")
        print(f"max_duration:       {self.max_duration}")
        print(f"sleeptime_offset:   {self.sleeptime_offset}")
        print(f"limit_shocks_only:  {self.limit_shocks_only}")
        print(f"no_shocks:          {self.no_shocks}")


class PiShocker:
    def __init__(self, config = "pishock.cfg", default_type = 1, default_intensity = 5, default_duration = 1):
        global print
        self.current_output = "__NONE__"
        try:
            self.config = PishockConfig(config)
            self.target = self.config.sharecodes[0]
        except:
            self.output_to_log("ERROR: Config not found. Please create 'pishock.cfg' in the root folder of the project.")
        self.type = default_type
        self.intensity = default_intensity
        self.duration = default_duration
        self.fire = False

    def output_to_log(self, text):
        if self.current_output == "__NONE__": self.current_output = ""
        self.current_output += "\n" + text
    
    def set_target(self, address, *args):
        self.target = self.config.sharecodes[args[0]]
        if self.config.verbose: self.output_to_log(f"OSC: Target set to {self.target}")

    def set_type(self, adress, *args):
        self.type = int(args[0])
        #if self.config.verbose: self.output_to_log(f"  OSC: Type set to {self.type}")

    def set_intensity(self, address, *args):
        self.intensity = int(args[0] * 100)
        #if self.config.verbose: self.output_to_log(f"  OSC: Intensity set to {self.intensity}")

    def set_duration(self, address, *args):
        self.duration = int(args[0] * 15)
        #if self.config.verbose: self.output_to_log(f"  OSC: Duration set to {self.duration}")

    def set_fire(self, address:str, *args) -> None:
        self.fire = args[0]
        if self.config.verbose and self.fire: self.output_to_log(f"OSC: Triggered send to {self.target}")


def send_shock(current_shocker):
    if current_shocker.config.no_shocks and current_shocker.type == 0:
        current_shocker.output_to_log(SHOCKS_DISABLED_WARNING)
        current_shocker.type = 2

    if current_shocker.config.limit_shocks_only and current_shocker.type != 0:
        pass #dont check maximums for vibrate and beep if set in config
    else:
        if current_shocker.intensity > current_shocker.config.max_intensity:
            current_shocker.output_to_log(INTENSITY_TOO_HIGH_WARNING)
            current_shocker.intensity = current_shocker.config.max_intensity
        if current_shocker.duration > current_shocker.config.max_duration:
            current_shocker.output_to_log(DURATION_TOO_HIGH_WARNING)
            current_shocker.duration = current_shocker.config.max_duration

    current_shocker.output_to_log(f"Sending {TYPELIST_STR[current_shocker.type]} at {current_shocker.intensity} for {current_shocker.duration} seconds to target {current_shocker.target}")
    datajson = str({"Username":current_shocker.config.username,
                        "Name":current_shocker.config.name,
                        "Code":current_shocker.target,
                        "Intensity":current_shocker.intensity,
                        "Duration":current_shocker.duration,
                        "Apikey":current_shocker.config.apikey,
                        "Op":current_shocker.type})
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    sendrequest = requests.post('https://do.pishock.com/api/apioperate', data=datajson, headers=headers)

    current_shocker.output_to_log(f"{sendrequest} {sendrequest.text}")
    current_shocker.fire = False


async def loop(shocker, touchpoint_shocker):  
    await asyncio.sleep(0.1)

    if shocker.fire:
        send_shock(shocker)
        sleeptime = shocker.duration + shocker.config.sleeptime_offset
        shocker.output_to_log(f"Waiting {sleeptime} before next command\n")
        await asyncio.sleep(sleeptime)

    if touchpoint_shocker.fire:
        send_shock(touchpoint_shocker)
        sleeptime = touchpoint_shocker.duration + touchpoint_shocker.config.sleeptime_offset
        touchpoint_shocker.output_to_log(f"Waiting {sleeptime} before next command\n")
        await asyncio.sleep(sleeptime)

#---not used anymore---

async def init_main():
    server = AsyncIOOSCUDPServer((shocker.config.ip, shocker.config.port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()

    print(f"PiShock-OSC started, listening at IP: {shocker.config.ip} | Port: {shocker.config.port}")
    print(f"Safety Settings:        Max Intensity: {shocker.config.max_intensity}  | Max Duration: {shocker.config.max_duration} |  Minimum Pause: {shocker.config.sleeptime_offset}\n")
    print(f"Loading default values, change values in the expression menu once to sync them to VRChat")
    print(f"Default Values:         Target: {shocker.target} | Type: {shocker.type} | Intensity: {shocker.intensity} | Duration: {shocker.duration}\n")

    while True:
        await loop(shocker, touchpoint_shocker)

    transport.close()


def main():
    global shocker, touchpoint_shocker, dispatcher
    shocker = PiShocker("pishock.cfg", 1, 10, 1)
    touchpoint_shocker = PiShocker("pishock.cfg", 1, 10, 1)

    if shocker.config.verbose:
        print(shocker.config.config)
        shocker.config.print_values()
        print()

    #pythonosc dispatcher
    dispatcher = Dispatcher()

    #dispatchers for pet functions
    dispatcher.map("/avatar/parameters/pishock/Type", shocker.set_type)
    dispatcher.map("/avatar/parameters/pishock/Intensity", shocker.set_intensity)
    dispatcher.map("/avatar/parameters/pishock/Duration", shocker.set_duration)
    dispatcher.map("/avatar/parameters/pishock/Shock", shocker.set_fire)
    dispatcher.map("/avatar/parameters/pishock/Target", shocker.set_target)

    #dispatchers for touchpoint functions
    dispatcher.map("/avatar/parameters/pishock/TPType", touchpoint_shocker.set_type)
    dispatcher.map("/avatar/parameters/pishock/TPIntensity", touchpoint_shocker.set_intensity)
    dispatcher.map("/avatar/parameters/pishock/TPDuration", touchpoint_shocker.set_duration)
    dispatcher.map("/avatar/parameters/pishock/Touchpoint_*", touchpoint_shocker.set_fire)

    asyncio.run(init_main())


if __name__ == "__main__":
    main()

