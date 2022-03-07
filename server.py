from copy import copy
import json
import os
from pathlib import Path
import sys
import asyncio

import globals
from messages import AT, IAMAT, WHATSAT
from utils import currentPosixTime

# Starts a server with correct port and neighbors
async def main() -> None:
  if len(sys.argv) == 2 and sys.argv[1] in globals.ports.keys():
    # # port for this instance of server.py
    # my_port = ports.get(sys.argv[1])
    # # ports of servers which this instance should talk to
    # my_neighbors = [ports.get(x) for x in connections.get(sys.argv[1])]
    # create this instance
    my_server = Server(sys.argv[1])
    await my_server.start_server_forever()
  else:
    print('Usage: python3 server.py SERVERNAME')

class Server:
  def __init__(self, name):
    self.name = name
    self.host = globals.host_name
    self.port = globals.ports[name]
    self.neighbors = {x:globals.ports[x] for x in globals.connections[name]}
    self.locations = {}
    path = os.path.join('.', name)
    Path(path).mkdir(exist_ok=True)
    self.log_file = os.path.join(path, f"{name}.log")
    self.location_files = os.path.join(path, 'locations')
    Path(self.location_files).mkdir(exist_ok=True)
    self.load_locations()
  
  async def start_server_forever(self):
    async_server = await asyncio.start_server(self.handle_client, host=self.host, port=self.port)
    await async_server.serve_forever()

  async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    connected_server = None
    while not reader.at_eof():
      # initialize some stuff
      time = currentPosixTime()
      raw_message = await reader.readline() # no byte limit >:)
      message = raw_message.decode()
      if message.strip() == "":
        break
      message_parts = message.split()
      peer = writer.get_extra_info('peername')
      # AT messages only come from other servers, and only as one line messages
      # this jank only logs those specific connections to satisfy the spec
      if message_parts[0] == "AT":
        connected_server = message_parts[6]
        self.log(f"Incoming connection from {connected_server}")

      # do something based on type of message
      self.log(f"Recieved from {peer}: Message {raw_message}")
      response = await self.handle_message(message_parts, time)
      if response:
        writer.write(response.encode())
        await writer.drain()
        self.log(f"Sent to {peer}: Reply {response.encode()}")

    # finish up
    writer.write_eof()
    writer.close()
    await writer.wait_closed()
    if connected_server:
      self.log(f"Connection ended with {connected_server}")
  
  # does the appropriate operations for handling any kind of
  # message, and return the response that should be sent back
  async def handle_message(self, message_parts, time):
    try:
      match message_parts[0]:
        case "IAMAT":
          return await self.handle_IAMAT(IAMAT.fromParts(message_parts[1:]), time)
        case "WHATSAT":
          return await self.handle_WHATSAT(WHATSAT.fromParts(message_parts[1:]))
        case "AT":
          # flood AT info to other servers
          await self.flood_AT_message(AT.fromParts(message_parts[1:]))
          return None # no response necessary
        case _:
          raise ValueError("Unrecognized message")
    except IOError as e:
      e.with_traceback('Invalid message')
      # "It's a trick, send no reply" -Obi Wan
      self.log('Invalid message')
      return '? ' + ' '.join(message_parts)
  
  async def handle_IAMAT(self, msg: IAMAT, time):
    location = AT(msg.id, msg.lat, msg.lng, msg.time, self.name, time)
    await self.flood_AT_message(location)
    return str(location) 

  async def handle_WHATSAT(self, message: WHATSAT):
    location = self.locations.get(message.id)
    if not location:
      raise ValueError('WHATSAT id unknown')
    # TODO get place data from google
    places = {}
    return str(location) + json.dumps(places)

  # ensure that the AT message reaches all servers it should reach
  # forwards the AT message to everyone besides the server who sent it
  # if the message is out of date or already known by this server, it
  # doesn't get passed on
  async def flood_AT_message(self, msg: AT):
    # copy the message so that there's no side effects
    message = AT(msg.id, msg.lat, msg.lng, msg.time, msg.serverId, msg.serverTime, msg.fromId)
    msg.fromId = None
    if not self.update_location(msg):
      return # nothing relevant to pass on to others
    fromId = message.fromId
    message.fromId = self.name
    for neighbor, port in self.neighbors.items():
      if neighbor != fromId:
        try:
          # open connection
          reader, writer = await asyncio.open_connection(globals.host_name, port)
          self.log(f"Opened connection with {neighbor}")
          # send message
          try:
            writer.write(str(message).encode())
            await writer.drain()
            writer.write_eof()
            self.log(f"Sent to {neighbor}: Message {str(message).encode()}")
          except:
            self.log(f"Issue sending message to {neighbor}")
          # close connection
          writer.close()
          await writer.wait_closed()
          self.log(f"Closed connection with {neighbor}")
        except:
          self.log(f"Error in connection with {neighbor}")
  
  # remembers the location of the AT message if necessary
  # returns true iff new information was committed to memory
  # that is, if this is the first AT for an id, or a more recent
  # version than what is already recorded
  def update_location(self, message: AT) -> bool:
    existing_AT = self.locations.get(message.id)
    if existing_AT and message.time <= existing_AT.time:
      return False
    self.locations[message.id] = message
    file = open(os.path.join(self.location_files, f"{message.id}.txt"), 'w')
    file.write(str(message))
    file.close()
    return True
  
  # for when a server goes down, then comes back up
  # loads location information from previously left text files, if any
  def load_locations(self):
    for path in Path(self.location_files).iterdir():
      file = open(path, 'r')
      message = file.read()
      file.close()
      loc = AT.fromParts(message.split()[1:])
      self.locations[loc.id] = loc

      


  def log(self, string: str):
    log = open(self.log_file, 'a')
    log.write(string + '\n')
    log.close()

if __name__ == '__main__':
  asyncio.run(main())