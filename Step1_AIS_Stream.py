import asyncio
import websockets
import json
from datetime import datetime, timezone

# Define the coroutine that will be run in the event loop
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
            # If the message is a PositionReport, print out the ship's position
            if message_type == "PositionReport":
                ais_message = message['Message']['PositionReport']
                print(f"[{datetime.now(timezone.utc)}] ShipId: {ais_message['UserID']} Latitude: {ais_message['Latitude']} Longitude: {ais_message['Longitude']}")

# Run the event loop to execute the coroutine
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





    
    
    