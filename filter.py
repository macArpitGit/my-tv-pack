import urllib.request

# Define URLs
MASTER_URL = "https://iptv-org.github.io/iptv/countries/in.m3u"
WHITELIST_FILE = "whitelist.txt"
OUTPUT_FILE = "custom_tv.m3u"

# Read the channels you want to keep
with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
    allowed_channels = [line.strip().lower() for line in f if line.strip()]

# Fetch the heavy 700+ channel master list from GitHub
print("Downloading master playlist...")
with urllib.request.urlopen(MASTER_URL) as response:
    master_data = response.read().decode("utf-8").splitlines()

# Process and filter the M3U file
filtered_lines = ["#EXTM3U\n"]
keep_next_line = False

for line in master_data:
    if line.startswith("#EXTINF:"):
        # Check if any of your whitelisted names are in the channel metadata line
        if any(channel in line.lower() for channel in allowed_channels):
            filtered_lines.append(line + "\n")
            keep_next_line = True
    elif keep_next_line and line.startswith("http"):
        # Append the actual streaming link for that matched channel
        filtered_lines.append(line + "\n")
        keep_next_line = False

# Save your clean, lightweight list
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(filtered_lines)

print(f"Success! Created {OUTPUT_FILE} with filtered channels.")
