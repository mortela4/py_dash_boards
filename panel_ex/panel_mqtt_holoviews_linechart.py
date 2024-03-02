import paho.mqtt.client as mqtt
import pandas as pd
import hvplot.pandas
from holoviews.streams import Buffer

import json


# Define the MQTT broker details:
broker_address = "test.mosquitto.org"
broker_port = 1883
topic = "1/testPoints/sinus"


# Debug:
DATA_STREAM_DEBUG = False


# ********************************** Helpers **************************************

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

# DATA setup
# ==========
sample_counter = 0
# Create a buffer to store incoming data:
buffer = Buffer(pd.DataFrame(data={'x': [], 'y': []}))

# MQTT Callback
def on_message(client, userdata, msg):
    global sample_counter
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
    sample_counter += 1
    #
    data = msg.payload.decode("utf-8")
    sine_val = get_value_from_raw(data)
    x, y = float(sample_counter), sine_val
    #
    buffer.send(pd.DataFrame(data={'x': [x], 'y': [y]}))


# Connect to MQTT Broker
client = mqtt_setup(broker_address=broker_address, broker_port=broker_port, topic=topic, msg_event_handler=on_message)
client.loop_start()

# Create the dashboard
line_chart = buffer.add_subscriber(hvplot.plot(x='x', y='y', width=800, height=400))

line_chart
