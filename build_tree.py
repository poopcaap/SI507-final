import json

def build_search_tree(data):
    tree = {}
    for entry in data:
        airline = entry['airline']
        departure = entry['departure']
        planes = entry['planes']
        # turn mile to km
        distance = entry['distance'] * 0.621371

        if airline not in tree:
            tree[airline] = {}
        if departure not in tree[airline]:
            tree[airline][departure] = {}

        for plane in planes:
            # level by distance
            if distance <= 650:
                distance_category = "1-650"
            elif distance <= 1150:
                distance_category = "651-1150"
            elif distance <= 2000:
                distance_category = "1151-2000"
            elif distance <= 4000:
                distance_category = "2001-4000"
            elif distance <= 7000:
                distance_category = "4001-7000"
            else:
                distance_category = "7000+"

            if distance_category not in tree[airline][departure]:
                tree[airline][departure][distance_category] = []

            tree[airline][departure][distance_category].append({
                'arrival': entry['arrival'],
                'distance': distance,
                'plane': plane
            })

    return tree
# read original data
with open('json/processed_routes_with_distance.json', 'r') as file:
    routes_data = json.load(file)

# create search tree
search_tree = build_search_tree(routes_data)

# save search tree as json file
with open('json/search_tree.json', 'w') as file:
    json.dump(search_tree, file)