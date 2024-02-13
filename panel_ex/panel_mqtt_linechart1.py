import panel as pn
import pandas as pd
import paho.mqtt.client as mqtt
import json


# Define the MQTT broker details
broker_address = "test.mosquitto.org"
broker_port = 1883
topic = "1/testPoints/sinus"

# Animation:
UPDATE_INTERVAL_MS = 500    # 500 ms update-interval, i.e. 0.5 sec.

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

# DATA setup:
xs = []
ys = []
sample_counter = 0
sample_counter_prev = 0
data = {
        'SampleNo': xs,
        'SineVal': ys
       }
df = pd.DataFrame(data)

# Create a line chart using hvplot
line_chart = df.hvplot.line(x='SampleNo', y='Sales')

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
    sine_val = get_value_from_raw(data)
    print(f"Received data for sample-count {sample_counter}: {data}")
    #
    sample_counter += 1
    #
    xs.append(sample_counter)
    ys.append(sine_val)


# Create a MQTT client and connect to the broker
mqtt_client = mqtt_setup(broker_address=broker_address, broker_port=broker_port, topic=topic, msg_event_handler=on_message)


# Start the MQTT loop
mqtt_client.loop_start()

# Create a Panel line chart
#chart = pn.pane.Matplotlib()

# Define the update function to update the chart with new data
def update_chart():
    global chart
    # Get the data from the MQTT topic and update the chart
    chart.show()

# Create a Panel dashboard
dashboard = pn.Column(chart)

# Define the update interval in milliseconds
update_interval = 1000

# Define the periodic callback to update the chart
pn.state.add_periodic_callback(update_chart, update_interval)

# Show the dashboard
dashboard.show()

