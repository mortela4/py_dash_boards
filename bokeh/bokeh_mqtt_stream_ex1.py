"""
@file bokeh_mqtt_stream_ex1.py

@brief Realtime line-chart showing MQTT streaming data.
"""

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.models.widgets import Div
from bokeh.layouts import column
from bokeh.server.server import Server
from bokeh.themes import Theme
from bokeh.palettes import Category10

import paho.mqtt.client as mqtt
import json


# Define the MQTT broker details
broker_address = "test.mosquitto.org"
broker_port = 1883
topic = "1/testPoints/sinus"


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


# *************************************** Bokeh Setup *************************************************

# Create a figure for the line chart
p = figure(x_axis_type='datetime', title='Real-Time Time-Series Data', sizing_mode='stretch_both')
p.xaxis.axis_label = 'Time'
p.yaxis.axis_label = 'Value'

# Create a data source for the line chart
source = ColumnDataSource(data=dict(time=[0.0], value=[0.0]))

# Create a line glyph for the line chart
line = p.line(x='time', y='value', source=source, line_width=2, line_color=Category10[10][0])

# Create a hover tool for the line chart
hover_tool = HoverTool(renderers=[line], tooltips=[('Time', '@time{%F %T}'), ('Value', '@value')], formatters={'@time': 'datetime'})
p.add_tools(hover_tool)

# Create a div widget to display the latest value
div = Div(text='', width=200, height=50)

# Define the callback function for MQTT message reception
"""
def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    time = data['time']
    value = data['value']
    source.stream(dict(time=[time], value=[value]))

    # Update the div widget with the latest value
    div.text = f'Latest Value: {value}'
"""

sample_counter = 0

def on_message(client, userdata, msg):
    #
    global source
    global sample_counter
    #
    if client:
        pass
    #
    if userdata:
        pass
    #
    data = msg.payload.decode("utf-8")
    sinus_val = get_value_from_raw(data)
    print(f"Received data for sample-count {sample_counter}: {data}")
    #
    sample_counter += 1
    # Update the dashboard with the new data
    if source.stream:
        print("'Source' ready - now add data to stream ...")
        # TODO:: fix document locking!!
        source.stream(dict(time=[float(sample_counter)], value=[sinus_val]))    
    else:
        print("WARN: source-stream NOT set up yet!!") 


# Create a MQTT client and connect to the broker
mqtt_client = mqtt_setup(broker_address=broker_address, broker_port=broker_port, topic=topic, msg_event_handler=on_message)


# Define the callback function for Bokeh server initialization
def modify_doc(doc):
    doc.add_root(column(p, div))

# Create a Bokeh server and start it
server = Server({'/': modify_doc}, num_procs=1)     # NOTE: on WinXX, 'num_procs' MUST be =1 !!
server.start()

# Start the MQTT client loop
mqtt_client.loop_start()

# Run the Bokeh server
if __name__ == '__main__':
    server.io_loop.add_callback(server.show, '/')
    server.io_loop.start()
