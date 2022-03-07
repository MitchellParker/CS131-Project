
# My Google Places API key
places_API_key = "AIzaSyBBnXdxhhg6w2paIm5FgZCjkia9Jr0NUmE"

# Hardcoded hosting on seasnet localhost
host_name = "localhost"
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