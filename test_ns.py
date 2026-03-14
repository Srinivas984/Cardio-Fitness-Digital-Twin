import xml.etree.ElementTree as ET
import io
from pathlib import Path

xml_file = Path(r'C:\Users\sssri\Downloads\export\apple_health_export\export_cda.xml')

# Extract first document
content_lines = []
with open(xml_file, 'r', encoding='utf-8', errors='ignore') as f:
    in_doc = False
    for line in f:
        if '<ClinicalDocument' in line and not in_doc:
            in_doc = True
        if in_doc:
            content_lines.append(line)
            if '</ClinicalDocument>' in line:
                break

content = ''.join(content_lines)
tree = ET.parse(io.StringIO(content))
root = tree.getroot()

ns = {'cda': 'urn:hl7-org:v3'}

# Test different search methods
print('Search methods:')
print(f'  .//text: {len(root.findall(".//text"))}')
print(f'  .//cda:text (with ns dict): {len(root.findall(".//cda:text", ns))}')
print(f'  .//{{urn:hl7-org:v3}}text: {len(root.findall(".//{urn:hl7-org:v3}text"))}')

# If we found text elements, examine the first one
texts = root.findall('.//cda:text', ns)
if texts:
    print(f'\n✅ Found {len(texts)} text elements with .//cda:text')
    first_text = texts[0]
    print('\nFirst text element children (first 10):')
    for i, child in enumerate(list(first_text)[:10]):
        short_tag = child.tag.split('}')[-1]
        val = (child.text or 'None')[:40]
        print(f'  {i:2d}. {short_tag:20s}: {val}')
else:
    print("\n⚠️ No texts found with any method")
