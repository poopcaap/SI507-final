import json

def build_search_tree(data):
    tree = {}
    for entry in data:
        airline = entry['airline']
        departure = entry['departure']
        planes = entry['planes']
        # 将距离从公里转换为英里
        distance = entry['distance'] * 0.621371

        if airline not in tree:
            tree[airline] = {}
        if departure not in tree[airline]:
            tree[airline][departure] = {}

        for plane in planes:
            # 根据距离分级
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

def get_plane_model_variants(model):
    # 如果输入模型以'7'开头且长度为3，则生成以前两个字符开头的模型列表
    if len(model) == 3 and model[0] == '7' and model[2] == '7':
        base_model = model[:2]
        model_variants = [base_model + str(i) for i in range(10)]  # 7x0到7x9
        model_variants += [base_model + chr(i) for i in range(ord('A'), ord('Z')+1)]  # 7xA到7xZ
        return model_variants

    if len(model) == 3 and model[0] == '3' and model[2] == '0':
        base_model = model[:2]
        model_variants = [base_model + str(i) for i in range(10)]  # 7x0到7x9
        model_variants += [base_model + chr(i) for i in range(ord('A'), ord('Z')+1)]  # 7xA到7xZ
        return model_variants

    return [model]

def search_routes(tree, airline, departure, plane_model, distance_code):
    results = []
    model_variants = get_plane_model_variants(plane_model.lower()) if plane_model.lower() != "any" else None
    distance_categories = {
        "a": "1-650",
        "b": "651-1150",
        "c": "1151-2000",
        "d": "2001-4000",
        "e": "4001-7000",
        "f": "7000+"
    }
    distance_category = distance_categories.get(distance_code.lower(), None) if distance_code.lower() != "any" else None

    for airline_key, departures in tree.items():
        if airline.lower() != "any" and airline_key.lower() != airline.lower():
            continue
        for departure_key, distances in departures.items():
            if departure.lower() != "any" and departure_key.lower() != departure.lower():
                continue
            for distance_range, routes in distances.items():
                if distance_category and distance_range.lower() != distance_category.lower():
                    continue
                for route in routes:
                    if model_variants and not any(plane_variant.lower() in route['plane'].lower() for plane_variant in model_variants):
                        continue
                    results.append(f"{airline_key.upper()} {departure_key.upper()}-{route['arrival'].upper()} distance:{route['distance']} mi plane:{route['plane'].upper()}")

    # Sort results by distance
    return sorted(results, key=lambda x: float(x.split('distance:')[1].split(' ')[0]))

# Reading the JSON data
with open('processed_routes_with_distance.json', 'r') as file:
    routes_data = json.load(file)

# Building the search tree
search_tree = build_search_tree(routes_data)

# Interactive search
airline_input = input("Enter airline code or 'any': ").strip()
departure_input = input("Enter departure code or 'any': ").strip()
plane_input = input("Enter plane model (e.g., 320, 330, 7x7) or 'any': ").strip()
distance_code_input = input("Enter distance category (A: 1-650, B: 651-1150, C: 1151-2000, D: 2001-4000, E: 4001-7000, F: 7000+) or 'any': ").strip()

search_results = search_routes(search_tree, airline_input, departure_input, plane_input, distance_code_input)

print("\nSearch Results:")
for result in search_results:
    print(result)