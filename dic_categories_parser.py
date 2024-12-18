import json

def parse_categories_from_typemap(file_path):
    # Read and parse the JSON file
    with open(file_path, 'r') as file:
        type_map = json.load(file)
    
    # Extract category names (top-level keys that start with 'ma_')
    ma_categories = sorted([cat for cat in type_map.keys()])
    
    # Print in the desired format
    print("content_classes:")
    print("    ?       - GENERATED_CONTENT")
    print("            - ma")
    print("    :")
    for category in ma_categories:
        print(f"            - CATEGORY_NAME: {category}")

# Example usage
parse_categories_from_typemap('./CACHE/work/scan-ma-type-map_old.json')
