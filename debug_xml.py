import xml.etree.ElementTree as ET
import io

# Read file
print("Reading XML file...")
with open(r'C:\Users\sssri\Downloads\export\apple_health_export\export_cda.xml', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print(f"File size: {len(content)} chars")

# Remove XML declarations (they cause issues when wrapping)
content_clean = content.replace('<?xml version="1.0"?>', '')

# Wrap in root
wrapped = '<?xml version="1.0"?><root>' + content_clean + '</root>'

try:
    print("Parsing wrapped XML...")
    tree = ET.parse(io.StringIO(wrapped))
    root = tree.getroot()
    print('✅ Successfully parsed wrapped XML')
    print(f'Root tag: {root.tag}')
    
    # Find all unique element tags
    def get_all_tags(elem, tags=None, depth=0):
        if tags is None:
            tags = set()
        if depth > 7:
            return tags
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        tags.add(tag)
        for child in list(elem)[:100]:  # Limit to 100 children per level
            get_all_tags(child, tags, depth+1)
        return tags
    
    all_tags = get_all_tags(root)
    print('\nUnique tags found (first 40):')
    for tag in sorted(all_tags)[:40]:
        print(f'  - {tag}')
    
    # Count key elements
    obs = root.findall('.//observation')
    print(f'\nElement counts:')
    print(f'  observation: {len(obs)}')
    print(f'  text: {len(root.findall(".//text"))}')
    print(f'  entry: {len(root.findall(".//entry"))}')
    print(f'  organizer: {len(root.findall(".//organizer"))}')
    print(f'  component: {len(root.findall(".//component"))}')
    
    # Try to find data in entries directly
    entries = root.findall('.//entry')
    if entries:
        print(f'\n✅ Found {len(entries)} entry elements')
        print('First entry immediate children:')
        first_entry = entries[0]
        for i, child in enumerate(list(first_entry)[:5]):
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            attribs = child.attrib
            print(f'    {i}: {tag} {attribs}')
    
    # Show structure of first observation's text element
    if obs:
        print(f'\n✅ Found {len(obs)} observation elements')
        first_obs = obs[0]
        print('First observation structure:')
        texts = first_obs.findall('.//text')
        if texts:
            print(f'  Has {len(texts)} text elements')
            for j, text in enumerate(texts[:1]):
                print(f'\n  Text element {j} children (first 10):')
                for k, child in enumerate(list(text)[:10]):
                    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                    val = (child.text or 'None')[:40]
                    print(f'    {tag}: {val}')

except Exception as e:
    print(f'❌ Parse error: {e}')
    import traceback
    traceback.print_exc()
