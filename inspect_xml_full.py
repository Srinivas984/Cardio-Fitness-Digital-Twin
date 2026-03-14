"""Inspect the full XML structure to find where dates are"""

import xml.etree.ElementTree as ET
import io

# Load the XML
xml_file = r'C:\Users\sssri\Downloads\export\apple_health_export\export_cda.xml'

content_lines = []
in_first_doc = False

with open(xml_file, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if '<ClinicalDocument' in line and not in_first_doc and '>' in line:
            in_first_doc = True
        
        if in_first_doc:
            content_lines.append(line)
            if '</ClinicalDocument>' in line and in_first_doc:
                break

content = ''.join(content_lines)
tree = ET.parse(io.StringIO(content))
root = tree.getroot()

ns = {'cda': 'urn:hl7-org:v3'}

# Find first text element
text_elems = root.findall('.//cda:text', ns)
print(f"Found {len(text_elems)} text elements\n")

if text_elems:
    first_text = text_elems[0]
    
    # Walk up the tree to find parents
    def get_path_to_element(root, target):
        """Find path from root to target element"""
        path = []
        
        def walk(elem, current_path):
            if elem == target:
                path.append(current_path + [elem])
                return True
            
            for child in elem:
                if walk(child, current_path + [elem]):
                    return True
            
            return False
        
        walk(root, [])
        return path[0] if path else []
    
    path = get_path_to_element(root, first_text)
    
    print("Path to first text element:")
    for i, elem in enumerate(path[:-1]):  # Exclude the text element itself
        indent = "  " * i
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        print(f"{indent}{tag}")
        
        # Show attributes
        for attr, val in elem.attrib.items():
            attr_name = attr.split('}')[-1] if '}' in attr else attr
            print(f"{indent}  @{attr_name}={val}")
        
        # Show important child elements
        for child in elem:
            child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            child_text = (child.text[:30] + "...") if child.text and len(str(child.text)) > 30 else child.text
            print(f"{indent}  <{child_tag}>{child_text}")
    
    print("\nFirst text element structure:")
    print(f"  <text>")
    for child in first_text:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        text = child.text[:50] if child.text else "(nested)"
        print(f"    <{tag}>{text}")
    print(f"  </text>")
    
    # Check parent element
    print("\n\nLooking for parent element with timestamps...")
    
    # Try to find the parent observation
    observations = root.findall('.//cda:observation', ns)
    print(f"Found {len(observations)} observation elements")
    
    if observations:
        print("\nFirst observation element attributes:")
        first_obs = observations[0]
        for attr, val in first_obs.attrib.items():
            print(f"  {attr}={val}")
        
        # Find effectiveTime elements
        eff_times = first_obs.findall('.//cda:effectiveTime', ns)
        print(f"  effectiveTime elements: {len(eff_times)}")
        
        for eff_time in eff_times:
            print(f"    effectiveTime: {eff_time.attrib}")
            for child in eff_time:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                print(f"      <{tag}> {child.attrib}")
