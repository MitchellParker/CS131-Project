import sys
import asyncio

# Hardcoded ports for use on seasnet
ports = {"Juzang": 10311, "Bernard": 10312, "Jaquez": 10313, "Johnson": 10314, "Clark": 10315}
# Hardcoded connections between servers
connections = {
  "Juzang": ["Bernard", "Johnson", "Clark"],
  "Bernard": ["Juzang", "Jaquez", "Johnson"],
  "Jaquez": ["Bernard", "Clark"],
  "Johnson": ["Juzang", "Bernard"],
  "Clark": ["Juzang", "Jaquez"]
}

def main():
  if len(sys.argv) == 2 and sys.argv[1] in ports.keys():
    # port for this instance of server.py
    my_port = ports.get(sys.argv[1])
    # ports of servers this instance should talk to
    my_neighbors = [ports.get(x) for x in connections.get(sys.argv[0])]
    doThing(my_port, my_neighbors) # unclear as of yet what exactly the thing to do is
  else:
    print("Usage: server.py SERVERNAME")


if __name__ == "__main__":
  main()