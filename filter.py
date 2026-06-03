import urllib.request

# 1. The Master Global Community Databases
SOURCES = [
    "https://iptv-org.github.io/iptv/index.m3u",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8"
]

WHITELIST_FILE = "whitelist.txt"
OUTPUT_FILE = "custom_tv.m3u"

print("Loading your custom channel order...")
with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
    # Read your list and preserve the exact order
    desired_channels = [line.strip().lower() for line in f if line.strip()]

# Dictionary to hold the final matched streams
found_streams = {channel: None for channel in desired_channels}

print("Downloading and indexing global community playlists...")
for source in SOURCES:
    print(f"Scanning {source}...")
    try:
        req = urllib.request.Request(source, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = response.read().decode("utf-8").splitlines()
            
            current_extinf = None
            
            for line in data:
                line = line.strip()
                if line.startswith("#EXTINF:"):
                    current_extinf = line
                elif current_extinf and (line.startswith("http") or line.startswith("https")):
                    # We found a complete channel block (metadata + stream link)
                    # Check if it matches any channel in your whitelist that we haven't found yet
                    for desired in desired_channels:
                        if found_streams[desired] is None and desired in current_extinf.lower():
                            found_streams[desired] = (current_extinf, line)
                            break  # Move to next line in the database
                    
                    current_extinf = None  # Reset for the next channel in the master list
    except Exception as e:
        print(f"Failed to read {source}: {e}")

print("Building your custom ordered TV list...")
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for desired in desired_channels:
        if found_streams[desired]:
            f.write(found_streams[desired][0] + "\n")
            f.write(found_streams[desired][1] + "\n")
        else:
            print(f"WARNING: Could not find a working stream for '{desired}'")

print("Success! Your global premium list is ready.")
