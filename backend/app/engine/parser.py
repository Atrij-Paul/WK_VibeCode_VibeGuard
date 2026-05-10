import hcl2
import os

def parse_terraform(file_path: str):
    """
    Parses a terraform file and returns the structured data.
    """
    try:
        with open(file_path, 'r') as f:
            data = hcl2.load(f)
        return data
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

def extract_resources(parsed_data):
    """
    Flattens the hcl2 parsed data into a list of resources.
    """
    resources = []
    if not parsed_data or 'resource' not in parsed_data:
        return resources
    
    for resource_block in parsed_data['resource']:
        for resource_type, resource_instances in resource_block.items():
            for resource_name, resource_config in resource_instances.items():
                resources.append({
                    "type": resource_type,
                    "name": resource_name,
                    "config": resource_config
                })
    return resources
