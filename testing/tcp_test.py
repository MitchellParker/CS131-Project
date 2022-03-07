import asyncio

async def main():
  message = "IAMAT client +34.068931-118.445127 1600000000\nWHATSAT client 10 5"
  timeout = None

  reader, writer = await asyncio.open_connection("localhost", 10311)
  # write
  writer.write(str(message).encode())
  await writer.drain()
  writer.write_eof()
  # read
  if timeout is None:
      data = await reader.read()
  else:
      read_func = reader.read()
      try:
          data = await asyncio.wait_for(read_func, timeout=timeout)
      except asyncio.TimeoutError:
          writer.close()
          print("TIME OUT")
  writer.close()
  print(data.decode().strip())

if __name__ == "__main__":
  asyncio.run(main())