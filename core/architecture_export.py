import json

def export_architecture_json(data, filename='architecture.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
