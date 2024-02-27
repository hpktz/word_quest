from xml.etree import ElementTree as ET

with open('test.xml', 'r') as file:
    data = file.read().replace('\n', '')

root = ET.fromstring(data)

translations = []
examples = []
for cit in root.findall('.//cit'):
    translation = cit.find('quote').text
    translations.append(translation)

# Extraction des exemples
for cit in root.findall('.//cit[@type="example"]'):
    example = cit.find('quote').text
    examples.append(example)