"""
Simple script to inspect the parsed CDA XML structure and find where the health data actually is.
"""
import xml.etree.ElementTree as ET
import io
from pathlib import Path

xml_file = Path(r'C:\Users\sssri\Downloads\export\apple_health_export\export_cda.xml')

print("Streaming XML to extract first document...")
content_lines = []
in_first_doc = False
found_closing = False
total_lines = 0

with open(xml_file, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        total_lines += 1
        
        if '<ClinicalDocument' in line and not in_first_doc and '>' in line:
            in_first_doc = True
        
        if in_first_doc:
            content_lines.append(line)
            
            if '</ClinicalDocument>' in line and in_first_doc:
                found_closing = True
                break

content = ''.join(content_lines)
print(f"Extracted {len(content_lines)} lines, {len(content)//1000}kB")

# Parse it
tree = ET.parse(io.StringIO(content))
root = tree.getroot()

print(f"\nRoot element: {root.tag}")

# Find text elements with health data
def find_health_data(elem, depth=0, max_depth=6):
    if depth > max_depth:
        return
    
    for child in list(elem)[:10]:  # Limit scanning
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        
        if tag == 'text':
            # Found a text element - check its children for health data
            children_text = []
            for text_child in list(child)[:15]:
                tc_tag = text_child.tag.split('}')[-1] if '}' in text_child.tag else text_child.tag
                tc_val = (text_child.text or '')[:30]
                children_text.append(f"{tc_tag}={tc_val}")
            
            if children_text:
                print(f"{' '*depth}text element children: {children_text}")
        
        if depth < max_depth:
            find_health_data(child, depth+1, max_depth)

print("\nScanning for text elements with health data structure:")
find_health_data(root)

# Count some key elements
print(f"\nElement counts:")
print(f"  entry: {len(root.findall('.//entry'))}")
print(f"  observation: {len(root.findall('.//observation'))}")
print(f"  text: {len(root.findall('.//text'))}")
print(f"  value: {len(root.findall('.//value'))}")  
print(f"  type: {len(root.findall('.//type'))}")

# Show a sample text element with its children
texts = root.findall('.//text')
if texts:
    print(f"\n✅ Found {len(texts)} text elements")
    print("\nFirst text element structure:")
    first_text = texts[0]
    for i, child in enumerate(list(first_text)[:15]):
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        val = (child.text or '')[:60]
        print(f"  {i:2d}. {tag:20s}: {val}")
