import urllib.request

SOURCES = [
    "https://iptv-org.github.io/iptv/index.m3u",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8"
]

WHITELIST_FILE = "whitelist.txt"
OUTPUT_FILE = "custom_tv.m3u"

print("Loading your custom channel order...")
with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
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
                    extinf_lower = current_extinf.lower()
                    url_lower = line.lower()
                    
                    for desired in desired_channels:
                        # 1. Ensure the channel name matches
                        if desired in extinf_lower:
                            
                            # 2. AGGRESSIVE FILTERS: Skip known bad/incompatible links
                            if "youtube.com" in url_lower or "youtu.be" in url_lower:
                                continue  # Skip YouTube links (breaks most IPTV players)
                            if "geo-blocked" in extinf_lower:
                                continue  # Skip region-locked streams
                            if ".m3u8" not in url_lower:
                                continue  # Strict standard for standard IPTV compatibility
                            
                            # 3. STREAM SELECTION & UPGRADING
                            if found_streams[desired] is None:
                                # Take the first valid link we find
                                found_streams[desired] = (current_extinf, line)
                            else:
                                # If we already have a link, check if this new one is better (720p/1080p)
                                current_best_extinf = found_streams[desired][0].lower()
                                
                                # Prioritize 720p as requested, or 1080p if 720p isn't there
                                if "720p" in extinf_lower and "720p" not in current_best_extinf:
                                    found_streams[desired] = (current_extinf, line)
                                elif "1080p" in extinf_lower and "720p" not in current_best_extinf and "1080p" not in current_best_extinf:
                                    found_streams[desired] = (current_extinf, line)
                            
                            break # Move to the next URL in the database
                    
                    current_extinf = None 
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
            print(f"WARNING: Could not find a working standard stream for '{desired}'")

print("Success! Your aggressively filtered list is ready.")
