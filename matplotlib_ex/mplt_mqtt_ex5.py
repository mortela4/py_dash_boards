"""
@file mplt_mqtt_ex5.py

@brief Graphing ISS spaceship's position and velocity data w. Matplotlib.
Position is shown in 3D-map.
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
from mpl_toolkits.mplot3d import Axes3D         # For 3D-plot.


import paho.mqtt.client as mqtt
import json
from math import sin, cos 

EARTH_RADIUS_KM = 6371         # Earth's radius in [km].

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
    alt_val = get_value_from_json(position_data, "alt") / 1000    # Value is in meters, but we want [km] (altitude is varying very little)
    # Process longitude - discontinuity at the meridian line (=Greenwich):
    """
    if 0 > lon_val:
        lon_val = -lon_val                      # NOTE: this makes value-range 0-180 degrees instead of -180 to +180!! (but continuos across 0-meridian)
    """
    #  
    return t_stamp, lat_val, lon_val, alt_val


def get_3d_vector(lat: float, lon: float, alt: float, radius: float=EARTH_RADIUS_KM) -> tuple:
    """
    Calculate carthesian 3D-coordinates(x,y,z) from GEO-position (lat, lon, alt).
    NOTE: no elliptic globe-approximation (i.e. WGS-24 projection)!
    Length of vector is always: l = sqrt(x^2 + y^2 + z^2) = radius + altitude 

    Args:
        lat (float): latitude (in degrees)
        lon (float): longitude (in degrees)
        alt (float): altitude (in kilometres)
        radius (float, optional): XYZ-vector length. Defaults to EARTH_RADIUS_KM.

    Returns:
        tuple: 3D-vector XYZ-values as tuple.
    """
    x = radius * cos(lat) * cos(lon)
    y = radius * cos(lat) * sin(lon)
    z = ( radius + alt ) * sin(lat)      # NOTE: imperative that 'radius' and 'alt' are both given in [km]!!
    #
    return x, y, z


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

xs = []
ys = []
zs = []
sample_counter = 0
sample_counter_prev = 0

fig = plt.figure()
fig.add_subplot(111, projection="3d")
#
ax1 = fig.gca()
ax1.set_xlabel('longitude')
ax1.set_ylabel('latitude')
ax1.set_label('altitude')
ax1.plot(xs, ys, zs)
ax1.legend()

def on_message(client, userdata, msg):
    #
    global ax1, sample_counter, xs, ys, zs
    #
    if client:
        pass
    #
    if userdata:
        pass
    #
    data = msg.payload.decode("utf-8")
    print(f"Received data for sample-count {sample_counter}: {data}")
    # Get GEOPOS-data:
    time_stamp, lat, lon, alt = get_position(data)
    # Convert to 3D-coordinates:
    x, y, z = get_3d_vector(lat, lon, alt)
    #
    sample_counter += 1
    #
    xs.append(x)
    ys.append(y)
    zs.append(z)
    # Update plot:
    ax1.clear()
    ax1.plot(xs, ys, zs)
    ax1.redraw_in_frame()


# Create a MQTT client and connect to the broker
mqtt_client = mqtt_setup(broker_address=broker_address, broker_port=broker_port, topic=topic, msg_event_handler=on_message)

"""
def animate(i):
    global xs, ys, sample_counter, sample_counter_prev
    #
    if DATA_STREAM_DEBUG and 0 != i and 0 == i % 10:
        print(f"Update {i} ...")
    #
    if sample_counter != sample_counter_prev:
        ax1.clear()
        ax1.plot(xs, ys, zs)
        sample_counter_prev = sample_counter
    else:
        if DATA_STREAM_DEBUG:
            print("No new data ...")
        else:
            pass
"""

def update_plot(i):
    """ Dummy callback - only to update display """
    pass

_ = animation.FuncAnimation(fig, update_plot, interval=UPDATE_INTERVAL_MS)    # NOTE: 'animation'-object is NOT used elsewhere, i.e. does NOT need a name!

# Start the MQTT client loop
mqtt_client.loop_start()

# Then show plot:
plt.show()



