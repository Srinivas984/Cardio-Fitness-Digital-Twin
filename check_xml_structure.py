"""Check the full XML structure for all sections"""

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

# Count all element types at different levels
print("Elements in document:")

def count_elements(elem, path="", max_depth=5, depth=0):
    if depth >= max_depth:
        return
    
    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
    
    for child in elem:
        child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        count = len(list(child.findall('.//' + ('{urn:hl7-org:v3}' if '}' not in child.tag else ''))))
        print(f"  {'  ' * depth}{child_tag}")

count_elements(root)

# Find all observation types via code element
print("\n\nObservation codes:")
observations = root.findall('.//cda:observation', ns)
codes_found = Counter()

for obs in observations:
    code = obs.find('.//cda:code', ns)
    if code is not None:
        code_val = code.get('displayName', code.get('code', 'unknown'))
        codes_found[code_val] += 1

for code, count in codes_found.most_common():
    print(f"  {count}x {code}")

# Check for other document sections
print("\n\nDifferent entry types:")
entries = root.findall('.//cda:entry', ns)
print(f"Total entries: {len(entries)}")

entry_types = Counter()
for entry in entries:
    # Get the child type (organizer, act, etc)
    for child in entry:
        child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        entry_types[child_tag] += 1

for etype, count in entry_types.most_common():
    print(f"  {count}x {etype}")
