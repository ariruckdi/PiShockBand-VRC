import sys
sys.path.append(".\\script")

import pishock
#from pishock import *
import PySimpleGUIQt as gui

def init_window():
    global window
    #set up GUI
    layout = [
        [gui.Text("PiShockOSC stopped", key="IP_PORT_DISPLAY")],
        [gui.Text(" ", key="CURRENT_VALUES")],
        [gui.Button("Exit")]
    ]
    window = gui.Window("PiShock-OSC", layout)
    
    pishock.asyncio.run(init_main())


async def init_main():
    global transport
    server = pishock.AsyncIOOSCUDPServer((shocker.config.ip, shocker.config.port), dispatcher, pishock.asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()

    print(f"PiShock-OSC started, listening at IP: {shocker.config.ip} | Port: {shocker.config.port}")
    print(f"Safety Settings:        Max Intensity: {shocker.config.max_intensity}  | Max Duration: {shocker.config.max_duration} |  Minimum Pause: {shocker.config.sleeptime_offset}\n")
    print(f"Loading default values, change values in the expression menu once to sync them to VRChat")
    print(f"Default Values:         Target: {shocker.target} | Type: {shocker.type} | Intensity: {shocker.intensity} | Duration: {shocker.duration}\n")

    while True:
        gui_loop()
        await pishock.loop(shocker, touchpoint_shocker)
        if event == gui.WIN_CLOSED or event == 'Exit':
            break


    transport.close()
    window.close()

def gui_loop():
    global event, values
    event, values = window.read(timeout=100, timeout_key="UPDATE_VALUES")   # Read the event that happened and the values dictionary
    if event != 'UPDATE_VALUES': print(event, values)
    if event == gui.WIN_CLOSED or event == 'Exit':
        transport.close()
        window.close()
    if event == 'UPDATE_VALUES':
        window["IP_PORT_DISPLAY"].update(f"PiShock-OSC running, listening at IP: {shocker.config.ip} | Port: {shocker.config.port}")
        window["CURRENT_VALUES"].update(f"Target: {shocker.target} | Type: {shocker.type} ({pishock.TYPELIST_STR[shocker.type]}) | Intensity: {shocker.intensity} | Duration: {shocker.duration}")

def main():
    global shocker, touchpoint_shocker, dispatcher, window
    shocker = pishock.PiShocker("pishock.cfg", 1, 10, 1)
    touchpoint_shocker = pishock.PiShocker("pishock.cfg", 1, 10, 1)

    if shocker.config.verbose:
        print(shocker.config.config)
        shocker.config.print_values()
        print()

    #pythonosc dispatcher
    dispatcher = pishock.Dispatcher()

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

    init_window()

if __name__ == "__main__":
    main()
