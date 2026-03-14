"""Check what health metric types are in the XML"""

import xml.etree.ElementTree as ET
import io
from collections import Counter

xml_file = r'C:\Users\sssri\Downloads\export\apple_health_export\export_cda.xml'

content_lines = []
in_first_doc = False

with open(xml_file, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if '<ClinicalDocument' in line and not in_first_doc and '>' in line:
            in_first_doc = True
        
        if in_first_doc:
            content_lines.append(line)
            if '</ClinicalDocument>' in line:
                break

content = ''.join(content_lines)
tree = ET.parse(io.StringIO(content))
root = tree.getroot()

ns = {'cda': 'urn:hl7-org:v3'}

# Find all observations
observations = root.findall('.//cda:observation', ns)
print(f"Total observations: {len(observations)}\n")

# Collect all metric types
types_found = Counter()
all_data_keys = Counter()

for obs in observations:
    # Get text element
    text_elem = obs.find('.//cda:text', ns)
    if text_elem is None:
        continue
    
    # Extract data
    data = {}
    for child in text_elem:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        value = child.text if child.text else ''
        if value and value.strip():
            data[tag] = value.strip()
            all_data_keys[tag] += 1
    
    if 'type' in data:
        types_found[data['type']] += 1

print("Metric types found:")
for metric_type, count in types_found.most_common():
    print(f"  {count:3d}x {metric_type}")

print("\nAll data field keys:")
for key, count in all_data_keys.most_common():
    print(f"  {count:3d}x {key}")
