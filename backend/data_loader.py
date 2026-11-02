from backend.apple_health_parser import parse_apple_health

def load_health_data():

    file_path = "data/export.xml"

    df = parse_apple_health(file_path)

    return df