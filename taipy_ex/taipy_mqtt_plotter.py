import time
from threading import Thread
from taipy.gui import Gui, State, invoke_callback, get_state_id   # NOTE: 'State' class, and associated 'get_state_id()' function, are REQUIRED! (to keep track of GUI state)
import numpy as np
import pandas as pd

import paho.mqtt.client as mqtt
import json


# Define the MQTT broker details
broker_address = "test.mosquitto.org"
broker_port = 1883
topic = "1/testPoints/sinus"

# Globals:
times = []
mqtt_single_data = []
current_sample_count = 0
prev_sample_count = 0
current_sample = 0.0


# ********************************** MQTT Helpers **************************************

def get_value_from_json(raw_data: str, value_key: str) -> tuple:
    json_data = json.loads(raw_data)
    # Get value:
    try:
        f_val = float(json_data[value_key])
    except ValueError:
        print(f"ERROR: could NOT extract FLOAT-data w. key={value_key}' from JSON:\n{json_data}")
        f_val = 0.0
    #
    return f_val


def get_value_from_raw(raw_data: str) -> tuple:
    # Get value:
    try:
        f_val = float(raw_data)
    except ValueError:
        print(f"ERROR: could NOT extract FLOAT-data from raw string = '{raw_data}'")
        f_val = 0.0
    #
    return f_val


def mqtt_setup(broker_address: str, broker_port: int, topic: str, msg_event_handler: object=None, conn_event_handler: object=None) -> mqtt.Client:
    """
    Complete setup of MQTT-client, including connecting event-handlers to events.
    
    TODO: add handlers for 'on_disconnect' etc(??).

    Args:
        broker_address (str): _description_
        broker_port (int): _description_
        topic (str): _description_
        msg_event_handler (object, optional): _description_. Defaults to None.
        conn_event_handler (object, optional): _description_. Defaults to None.

    Returns:
        mqtt.Client: MQTT-client instance.
    """
    def default_msg_handler(client, userdata, msg):
        if client:
            pass
        #
        if userdata:
            pass
        #
        data = msg.payload.decode("utf-8")
        print(f"Received data: {data}")
    #
    def default_connect_handler(client, userdata, flags, rc: int=0):
        if client:
            pass
        #
        if userdata:
            pass
        #
        if flags:
            pass
        #
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("ERROR: failed to connect, return code %d\n", rc)    

    # Create an MQTT client and connect to the broker
    client = mqtt.Client()
    client.connect(broker_address, broker_port)
    # Subscribe to the MQTT topic
    client.subscribe(topic)
    # Set the callback function for 'on_connected' event':
    if conn_event_handler:
        client.on_connect = conn_event_handler
    else:
        client.on_connect = default_connect_handler
    # Set the callback function for incoming messages:
    if msg_event_handler:
        client.on_message = msg_event_handler
    else:
        client.on_message = default_msg_handler
    #
    return client

# *********************************************************************************


# ********************************* MQTT Callbacks ********************************

def on_message(client, userdata, msg):
    #
    global sample_counter, current_sample
    #
    if client:
        pass
    #
    if userdata:
        pass
    #
    data = msg.payload.decode("utf-8")
    sine_val = get_value_from_raw(data)
    print(f"Received data for sample-count {sample_counter}: {data}")
    #
    sample_counter += 1
    #
    current_sample = sine_val


def new_data_received() -> bool:
    global current_sample_count
    global prev_sample_count
    global current_sample
    #
    got_new_data = current_sample_count != prev_sample_count
    #
    if got_new_data:
       prev_sample_count = current_sample_count
    #
    return got_new_data

# ************************************************************************************

# ************************** MQTT Setup ******************************************
mqtt_client = mqtt_setup(broker_address=broker_address, broker_port=broker_port, topic=topic, msg_event_handler=on_message)
# Start MQTT-client thread:
mqtt_client.loop_start()
# ********************************************************************************

# **************************** GUI stuff *****************************************
line_data = pd.DataFrame({"Time": [], "Value": []})

layout_line = {
    "title": "MQTT Realtime Data Display",
    "yaxis": {"range": [-180, 180]},
}

options = {
    "opacity": 0.8,
    "colorscale": "Bluered",
    "zmin": 0,
    "zmax": 140,
    "colorbar": {"title": "Value"},
    "hoverinfo": "none",
}

config = {"scrollZoom": False, "displayModeBar": False}

   
# GUI data handler:
def client_handler(gui: Gui, state_id_list: list):
    global current_sample
    global current_sample_count
    # 
    while 100 > current_sample_count:
        if new_data_received():
            print(f"Data received: {current_sample}")
            if hasattr(gui, "_server") and state_id_list:
                invoke_callback(gui, state_id_list[0], update_value, current_sample)
        else:
            time.sleep(1)
    #
    print("I'm DONE -goodbye!")
        

# Gui declaration
Gui.add_shared_variable("line_data")        # TODO: check - should this be 'mqtt_single_data' ???

state_id_list = []

def on_init(state: State):
    state_id = get_state_id(state)
    if (state_id := get_state_id(state)) is not None:
        state_id_list.append(state_id)
    print("Initialized GUI ...")
    

def update_value(new_sample: float):
    global current_sample_count
    global mqtt_single_data
    global line_data
    # Add data to list:
    mqtt_single_data.append(new_sample)
    # Add an INCREMENT to the time(=sample count):
    time_steps = range(current_sample_count)
    line_data = pd.DataFrame(
        {
            "Time": time_steps,
            "Value": mqtt_single_data,
        }
    )


# Set up GUI(='page'):
page = """
<|part|class_name=card|
<|{line_data[-30:]}|chart|type=lines|x=Time|y=Value|layout={layout_line}|height=40vh|>
|>
|>
"""
gui = Gui(page=page)

t = Thread(
    target=client_handler,
    args=(gui, state_id_list),
)
t.start()
gui.run(run_browser=False)

