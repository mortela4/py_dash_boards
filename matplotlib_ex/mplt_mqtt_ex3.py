"""
@file mplt_mqtt_ex3.py

@brief Graphing ISS position and velocity data w. Matplotlib.
The position/velocity data is in the following JSON format:
{
    "name":"ISS (ZARYA)",
    "timestamp":1706038908569,
    "position":
        {
            "x":1971162.2089,
            "y":-5601577.7301,
            "z":-3317897.1995,
            "lat":-29.3472,
            "lon":-128.7091,
            "alt":429291.3161,
            "speed":7652.1088,
            "bearing":42.8144
        },
    "velocity":
        {
            "x":6000.958871576156,
            "y":-667.5434490407952,
            "z":4700.813475006011
        }
}
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style


import paho.mqtt.client as mqtt
import json


# Define the MQTT broker details
broker_address = "test.mosquitto.org"
broker_port = 1883
topic = "Satellite/Iss"

# Animation:
UPDATE_INTERVAL_MS = 500    # 500 ms update-interval, i.e. 0.5 sec.

# Debug:
DATA_STREAM_DEBUG = False
 
# style.use('fivethirtyeight')      # Optional ...


# ********************************** Basic Helpers **************************************

def get_value_from_json(raw_data: str|dict, value_key: str) -> tuple:
    if isinstance(raw_data, str):
        json_data = json.loads(raw_data)
    else:
        json_data = raw_data    # Raw data is already a 'dict' - no need to load from string!
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


# ********************************* Data-specific Helpers **************************************

def get_xy_coordinates(raw_data: str) -> tuple:
    """
    Get XYZ-coordinates in 'raw' values from MQTT data.
    Values represent distance in meters (from ORIGO = center-of-earth).

    Args:
        raw_data (str): MQTT data in JSON format.

    Returns:
        tuple: timestamp(from data) and XYZ-values (scaled down w. a factor=1:100000).
    """
    json_data = json.loads(raw_data)
    # Get timestamp:
    t_stamp = json_data["timestamp"]
    # Get coordinates:
    position_data = json_data["position"]
    # Extract position's XYZ-coordinates:
    x_val = float(position_data["x"]) / 100000
    y_val = float(position_data["y"]) / 100000
    z_val = float(position_data["z"]) / 100000
    #
    return t_stamp, x_val, y_val, z_val


def get_position(raw_data: str) -> tuple:
    """
    Get GEOPOS-value from MQTT data, i.e. timestamped lat/lon/alt value.

    Args:
        raw_data (str): MQTT data in JSON format.

    Returns:
        tuple: timestamp + GEOPOS-value(lat,lon,alt).
    """
    json_data = json.loads(raw_data)
    # Get timestamp:
    t_stamp = json_data["timestamp"]
    # Get coordinates:
    position_data = json_data["position"]
    # Extract position's XYZ-coordinates:
    lat_val = get_value_from_json(position_data, "lat") 
    lon_val = get_value_from_json(position_data, "lon") 
    alt_val = get_value_from_json(position_data, "alt") 
    #
    return t_stamp, lat_val, lon_val, alt_val


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


fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

xs = []
ys = []
sample_counter = 0
sample_counter_prev = 0

def on_message(client, userdata, msg):
    #
    global sample_counter, xs, ys
    #
    if client:
        pass
    #
    if userdata:
        pass
    #
    data = msg.payload.decode("utf-8")
    if DATA_STREAM_DEBUG:
        print(f"Received data for sample-count {sample_counter}: {data}")
    #
    time_stamp, lat, lon, alt = get_position(data)
    #
    sample_counter += 1
    #
    xs.append(lon)
    ys.append(lat)


# Create a MQTT client and connect to the broker
mqtt_client = mqtt_setup(broker_address=broker_address, broker_port=broker_port, topic=topic, msg_event_handler=on_message)


def animate(i):
    global xs, ys, sample_counter, sample_counter_prev
    #
    if 0 != i and 0 == i % 10:
        print(f"Update {i} ...")
    #
    if sample_counter != sample_counter_prev:
        ax1.clear()
        ax1.plot(xs, ys)
        sample_counter_prev = sample_counter
    else:
        if DATA_STREAM_DEBUG:
            print("No new data ...")
        else:
            pass


_ = animation.FuncAnimation(fig, animate, interval=UPDATE_INTERVAL_MS)    # NOTE: 'animation'-object is NOT used elsewhere, i.e. does NOT need a name!

# Start the MQTT client loop
mqtt_client.loop_start()

# Then show plot:
plt.show()

