import xml.etree.ElementTree as ET
import pandas as pd


def parse_apple_health(xml_file):

    tree = ET.parse(xml_file)
    root = tree.getroot()

    records = []

    for record in root.findall("Record"):

        record_type = record.get("type")
        value = record.get("value")
        date = record.get("startDate")

        records.append({
            "type": record_type,
            "value": value,
            "date": date
        })

    df = pd.DataFrame(records)

    return df