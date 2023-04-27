import sys
sys.path.append(".\\script")

import pishock
import os.path
import PySimpleGUIQt as gui

CONFIG_DEFAULTS = [["API", "APPNAME", "VRC-OSC"],
                ["DEBUG", "VERBOSE_OUTPUT", "True"],
                ["SAFETY", "ONLY_LIMIT_SHOCKS", "True"]]

CONFIG_FILE = os.path.expandvars(r'%APPDATA%\PiShock-OSC\pishock.cfg')


#---CONFIG SETUP AND SETTINGS---
#TODO Check inputs somehow
def write_config_value(category, key, value):
    if not config_handler.has_section(category): config_handler.add_section(category)
    config_handler.set(category, key, value)
    with open(CONFIG_FILE, "w") as configfile:
        config_handler.write(configfile)
    configfile.close()


def config_setup():
    global shocker, touchpoint_shocker, dispatcher, window
    global config_window, config_handler

    if not 'config_handler' in globals(): config_handler = pishock.ConfigParser()

    row_lenght = 30
    row_height = 1

    column1 = [
        [gui.Text("PiShock Config Setup",
                   size=(row_lenght, row_height*1.2))],
        [gui.Text("API Key: ", size=(row_lenght, row_height))],
        [gui.Text("Username: ", size=(row_lenght, row_height))],
        [gui.Text("Sharecode: ", size=(row_lenght, row_height))],
        [gui.Text(" ", size=(row_lenght, row_height))],
        [gui.Text("IP: ", size=(row_lenght, row_height))],
        [gui.Text("Port: ", size=(row_lenght, row_height))],
        [gui.Text(" ", size=(row_lenght, row_height))],
        [gui.Text("Maximum Intensity: ", size=(row_lenght, row_height))],
        [gui.Text("Maximum Duration: ", size=(row_lenght, row_height))],
        [gui.Text("Minimum Time Between Shocks: ", size=(row_lenght, row_height))],
        [gui.Text("Disable Shocks: ", size=(row_lenght, row_height))]
    ]

    column2 = [
        [gui.Text("", size=(row_lenght, row_height*1.2))],
        [gui.InputText(key="API/APITOKEN", default_text="Your PiShock API key", size=(row_lenght, row_height))],
        [gui.InputText(key="API/USERNAME", default_text="Your PiShock username",size=(row_lenght, row_height))],
        [gui.InputText(key="SHARECODES/SHARECODES", default_text="Your PiShock sharecode",size=(row_lenght, row_height))],
        [gui.Text("", size=(row_lenght, row_height))],
        [gui.InputText(key="SETTINGS/IP", default_text="127.0.0.1", size=(row_lenght, row_height))],
        [gui.InputText(key="SETTINGS/PORT", default_text="9001", size=(row_lenght, row_height))],
        [gui.Text("", size=(row_lenght, row_height))],
        [gui.InputText(key="SAFETY/MAX_INTENSITY", default_text="25", size=(row_lenght, row_height))],
        [gui.InputText(key="SAFETY/MAX_DURATION", default_text="5", size=(row_lenght, row_height))],
        [gui.InputText(key="SAFETY/SLEEPTIME_OFFSET", default_text="1.5", size=(row_lenght, row_height))],
        [gui.Checkbox("", key="SAFETY/DISABLE_SHOCKS", default=False, size=(row_lenght, row_height))],
        [gui.Button("Save config", key="SAFE_CONFIG", size=(row_lenght, row_height))]
    ]

    config_layout = [
        [gui.Column(column1), gui.Column(column2)]
    ]

    config_window = gui.Window("PiShock Settings", config_layout)
    
    while True:
        config_event, config_values = config_window.read()
        #print(config_event, config_values)
        #print(config_values.keys())
        if config_event == gui.WIN_CLOSED or config_event == 'Exit':
            break
        if config_event == "SAFE_CONFIG":
            for config_key in config_values.keys():
                config_adress_list = config_key.split("/")
                #print((config_adress_list[0], config_adress_list[1], str(config_values[config_key])))
                write_config_value(config_adress_list[0], config_adress_list[1], str(config_values[config_key]))
            for additional_value in CONFIG_DEFAULTS:
                write_config_value(*additional_value)
            config_window.close()
            break

def config_modify():
    #TODO dont repeat yourself
    global shocker, touchpoint_shocker, dispatcher, window
    global config_window, config_handler, config_event

    if not 'config_writer' in globals(): config_handler = pishock.ConfigParser()
    config_handler.read(CONFIG_FILE)

    row_lenght = 30
    row_height = 1

    column1 = [
        [gui.Text("PiShock-OSC Settings",
                   size=(row_lenght, row_height*1.2))],
        [gui.Text("API Key: ", size=(row_lenght, row_height))],
        [gui.Text("Username: ", size=(row_lenght, row_height))],
        [gui.Text("Sharecode: ", size=(row_lenght, row_height))],
        [gui.Text(" ", size=(row_lenght, row_height))],
        [gui.Text("IP: ", size=(row_lenght, row_height))],
        [gui.Text("Port: ", size=(row_lenght, row_height))],
        [gui.Text(" ", size=(row_lenght, row_height))],
        [gui.Text("Maximum Intensity: ", size=(row_lenght, row_height))],
        [gui.Text("Maximum Duration: ", size=(row_lenght, row_height))],
        [gui.Text("Minimum Time Between Shocks: ", size=(row_lenght, row_height))],
        [gui.Text("Disable Shocks: ", size=(row_lenght, row_height))]
    ]

    column2 = [
        [gui.Text("", size=(row_lenght, row_height*1.2))],
        [gui.InputText(key="API/APITOKEN", default_text=config_handler["API"]["APITOKEN"], size=(row_lenght, row_height))],
        [gui.InputText(key="API/USERNAME", default_text=config_handler["API"]["USERNAME"], size=(row_lenght, row_height))],
        [gui.InputText(key="SHARECODES/SHARECODES", default_text=config_handler["SHARECODES"]["SHARECODES"], size=(row_lenght, row_height))],
        [gui.Text("", size=(row_lenght, row_height))],
        [gui.InputText(key="SETTINGS/IP", default_text=config_handler["SETTINGS"]["IP"], size=(row_lenght, row_height))],
        [gui.InputText(key="SETTINGS/PORT", default_text=config_handler["SETTINGS"]["PORT"], size=(row_lenght, row_height))],
        [gui.Text("", size=(row_lenght, row_height))],
        [gui.InputText(key="SAFETY/MAX_INTENSITY", default_text=config_handler["SAFETY"]["MAX_INTENSITY"], size=(row_lenght, row_height))],
        [gui.InputText(key="SAFETY/MAX_DURATION", default_text=config_handler["SAFETY"]["MAX_DURATION"], size=(row_lenght, row_height))],
        [gui.InputText(key="SAFETY/SLEEPTIME_OFFSET", default_text=config_handler["SAFETY"]["SLEEPTIME_OFFSET"], size=(row_lenght, row_height))],
        [gui.Checkbox("", key="SAFETY/DISABLE_SHOCKS", default=config_handler["SAFETY"]["DISABLE_SHOCKS"].lower == 'true', size=(row_lenght, row_height))],
        [gui.Button("Save config", key="SAFE_CONFIG_MODIFY", size=(row_lenght, row_height))]
    ]

    config_layout = [
        [gui.Column(column1), gui.Column(column2)]
    ]

    config_window = gui.Window("PiShock Settings", config_layout)

    while True:
        config_event, config_values = config_window.read()
        #print(config_event, config_values)
        #print(config_values.keys())
        if config_event == gui.WIN_CLOSED or config_event == 'Exit':
            break
        if config_event == "SAFE_CONFIG_MODIFY":
            for config_key in config_values.keys():
                config_adress_list = config_key.split("/")
                #print((config_adress_list[0], config_adress_list[1], str(config_values[config_key])))
                write_config_value(config_adress_list[0], config_adress_list[1], str(config_values[config_key]))
            for additional_value in CONFIG_DEFAULTS:
                write_config_value(*additional_value)
            config_window.close()
            
            break

def print_config_values(shocker):
        print(f"API-Key:            {shocker.config.apikey}")
        print(f"Username:           {shocker.config.username}")
        print(f"Program Name:       {shocker.config.name}")
        print(f"Sharecode:          {shocker.config.sharecodes}")
        print(f"IP:                 {shocker.config.ip}")
        print(f"Port:               {shocker.config.port}")
        print(f"Verbose:            {shocker.config.verbose}")
        print(f"Max Intensity:      {shocker.config.max_intensity}")
        print(f"Max Duration:       {shocker.config.max_duration}")
        print(f"Sleeptime Offset:   {shocker.config.sleeptime_offset}")
        print(f"Limit Shocks Only:  {shocker.config.limit_shocks_only}")
        print(f"No Shocks:          {shocker.config.no_shocks}")
        print()


#---STARTUP---
def init_window():
    global window, print
    #set up GUI
    layout = [
        [gui.Text("PiShockOSC stopped", key="IP_PORT_DISPLAY")],
        [gui.Text(" ", key="CURRENT_VALUES")],
        [gui.Button("Settings", key="SETTINGS"), gui.Button("Exit")],
        [gui.Multiline('', size=(70,20), key="GUI_LOG", font=("Consolas", 10))]
    ]
    window = gui.Window("PiShock-OSC", layout)
    window.read(timeout=500)
    print = lambda *args, **kwargs: window["GUI_LOG"].print(*args, **kwargs)
    pishock.asyncio.run(init_main())


async def init_main():
    global transport, shocker, touchpoint_shocker, config_event
    config_event = ""
    try:
        server = pishock.AsyncIOOSCUDPServer((shocker.config.ip, shocker.config.port), dispatcher, pishock.asyncio.get_event_loop())
        transport, protocol = await server.create_serve_endpoint()
    except:
        gui.popup_ok("Error while starting the OSC server!\n\nPlease check if any other programs are listening on the selected port.\nPorts can be only used once, you might need to use an OSC router.", title="OSC Server Error")
        window.Close()
        return

    print(f"PiShock-OSC started, listening at IP: {shocker.config.ip} | Port: {shocker.config.port}")
    print(f"Safety Settings:        Max Intensity: {shocker.config.max_intensity}  | Max Duration: {shocker.config.max_duration} |  Minimum Pause: {shocker.config.sleeptime_offset}\n")
    print(f"Loading default values, change values in the expression menu once to sync them to VRChat")
    print(f"Default Values:         Target: {shocker.target} | Type: {shocker.type} | Intensity: {shocker.intensity} | Duration: {shocker.duration}\n")
    if shocker.config.verbose: print_config_values(shocker)

    while True:
        gui_loop()
        await pishock.loop(shocker, touchpoint_shocker)
        if shocker.current_output != "__NONE__":
            print(shocker.current_output)
            shocker.current_output = "__NONE__"
        if touchpoint_shocker.current_output != "__NONE__":
            print(touchpoint_shocker.current_output)
            touchpoint_shocker.current_output = "__NONE__"
        if event == gui.WIN_CLOSED or event == 'Exit':
            break
        if config_event == "SAFE_CONFIG_MODIFY":
            shocker = pishock.PiShocker(CONFIG_FILE, 1, 10, 1)
            touchpoint_shocker = pishock.PiShocker(CONFIG_FILE, 1, 10, 1)
            config_event = ""
            start_dispatch()
            if shocker.config.verbose: print(""); print_config_values(shocker)
    transport.close()
    window.close()


#---MAINLOOP---
def gui_loop():
    global event, values
    event, values = window.read(timeout=100, timeout_key="UPDATE_VALUES")   # Read the event that happened and the values dictionary
    #if event != 'UPDATE_VALUES': print(event, values)
    if event == gui.WIN_CLOSED or event == 'Exit':
        transport.close()
        window.close()
    if event == 'UPDATE_VALUES':
        window["IP_PORT_DISPLAY"].update(f"PiShock-OSC running, listening at IP: {shocker.config.ip} | Port: {shocker.config.port}")
        window["CURRENT_VALUES"].update(f"Target: {shocker.target} | Type: {shocker.type} ({pishock.TYPELIST_STR[shocker.type]}) | Intensity: {shocker.intensity} | Duration: {shocker.duration}")
    if event == "SETTINGS":
        config_modify()

def start_dispatch():
    global dispatcher, touchpoint_shocker, shocker
    
    #dispatchers for menu functions
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

#---MAIN---
def main():
    global shocker, touchpoint_shocker, dispatcher, window

    if not os.path.isfile(CONFIG_FILE):
        new_config_file = open(CONFIG_FILE, "x")
        new_config_file.close()
        config_setup()

    shocker = pishock.PiShocker(CONFIG_FILE, 1, 10, 1)
    touchpoint_shocker = pishock.PiShocker(CONFIG_FILE, 1, 10, 1)

    dispatcher = pishock.Dispatcher()
    start_dispatch()
    init_window()

if __name__ == "__main__":
    main()
