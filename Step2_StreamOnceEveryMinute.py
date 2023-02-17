import asyncio
import websockets
import json
from datetime import datetime, timezone, timedelta

sampling_interval = 300 # 5 minutes
sliding_window = [] # initialize sliding window

async def connect_ais_stream():
    # Connect to the AIS stream using websockets
    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        # Create a message to subscribe to the stream with
        subscribe_message = {"APIKey": "70b297df15fd87f3f01c6084d8d66d93fc96c08d", "BoundingBoxes": [[[-180, -90], [180, 90]]]}
        subscribe_message_json = json.dumps(subscribe_message)
        # Send the subscription message to the stream
        await websocket.send(subscribe_message_json)
        # Start receiving messages from the stream
        async for message_json in websocket:
            # Parse the message as JSON
            message = json.loads(message_json)
            # Get the type of the message
            message_type = message["MessageType"]
            # If the message is a PositionReport, add it to the sliding window
            if message_type == "PositionReport":
                ais_message = message['Message']['PositionReport']
                sliding_window.append(ais_message)
            # Check if the sliding window is full
            if len(sliding_window) == sampling_interval:
                # Calculate the aggregate value (average latitude and longitude)
                avg_latitude = sum([msg['Latitude'] for msg in sliding_window]) / sampling_interval
                avg_longitude = sum([msg['Longitude'] for msg in sliding_window]) / sampling_interval
                # Output the downsampled data point
                output_data_point(avg_latitude, avg_longitude)
                # Remove the oldest data point from the sliding window
                sliding_window.pop(0)

def output_data_point(latitude, longitude):
    # Open the file in append mode and write the downsampled data point as a line in the file
    with open("AllPOS.txt", "a") as file:
        file.write(f"{datetime.now(timezone.utc)} {latitude} {longitude}\n")

if __name__ == "__main__":
    # Check if an event loop is already running
    try:
        loop = asyncio.get_running_loop()
    # If there's no event loop running, create a new one
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    # Create a task to run the coroutine in the event loop
    loop.create_task(connect_ais_stream())
    # Start the event loop
    loop.run_forever()
    # Close the event loop when we're done
    loop.close()
