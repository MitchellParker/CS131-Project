import sys
import asyncio
import globals

# Starts a server with correct port and neighbors
async def main() -> None:
  if len(sys.argv) == 2 and sys.argv[1] in globals.ports.keys():
    # port for this instance of server.py
    my_port = globals.ports.get(sys.argv[1])
    # ports of servers which this instance should talk to
    my_neighbors = [globals.ports.get(x) for x in globals.connections.get(sys.argv[1])]
    # create this instance
    my_server = Server(globals.host_name, my_port, my_neighbors)
    await my_server.start_server_forever()
  else:
    print("Usage: python3 server.py SERVERNAME")

class Server:
  def __init__(self, host, port, neighbor_ports):
    self.host = host
    self.port = port
    self.neighbor_ports = neighbor_ports

  async def handle_client(self, reader, writer):
    raw_message = await reader.read()
    message = raw_message.decode()
    print(f"Message \"{raw_message}\" recieved from: {writer.get_extra_info('peername')}")
    writer.close()
    await writer.wait_closed()
  
  async def start_server_forever(self):
    async_server = await asyncio.start_server(self.handle_client, host=self.host, port=self.port)
    await async_server.serve_forever()


if __name__ == "__main__":
  asyncio.run(main())