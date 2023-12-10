import json
import folium

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

    # 将输入值标准化为大写
    normalized_airline = airline.upper() if airline else None
    normalized_departure = departure.upper() if departure else None
    normalized_distance_code = distance_code.upper() if distance_code else None

    # 获取飞机型号变体
    model_variants = get_plane_model_variants(plane_model.upper()) if plane_model and plane_model.upper() != "ANY" else None

    # 距离代码到距离范围的映射
    distance_categories = {
        "A": "1-650",
        "B": "651-1150",
        "C": "1151-2000",
        "D": "2001-4000",
        "E": "4001-7000",
        "F": "7000+"
    }
    distance_category = distance_categories.get(normalized_distance_code, None) if normalized_distance_code != "ANY" else None

    # 遍历搜索树
    for airline_key, departures in tree.items():
        if normalized_airline and airline_key != normalized_airline and normalized_airline != "ANY":
            continue

        for departure_key, distances in departures.items():
            if normalized_departure and departure_key != normalized_departure and normalized_departure != "ANY":
                continue

            for distance_range, routes in distances.items():
                if distance_category and distance_range != distance_category:
                    continue

                for route in routes:
                    if model_variants and not any(plane_variant in route['plane'].upper() for plane_variant in model_variants):
                        continue
                    result = f"{airline_key} {departure_key}-{route['arrival']} distance:{route['distance']} mi plane:{route['plane']}"
                    results.append(result)

    # 排序并返回结果
    return sorted(results, key=lambda x: float(x.split('distance:')[1].split(' ')[0]))

def get_sort_key(method, result):
    if method == '2':  # 按航空公司排序
        return result.split()[0]
    elif method == '3':  # 按出发地排序
        return result.split()[1].split('-')[0]
    elif method == '4':  # 按飞机型号排序
        return result.split('plane:')[1]
    else:  # 默认按距离排序
        return float(result.split('distance:')[1].split(' ')[0])

def search_airline_codes(airlines, query):
    matches = []
    query_lower = query.lower()
    for airline in airlines:
        if query_lower in airline['name'].lower():
            matches.append((airline['name'], airline['code']))
    return matches

def search_airport_codes(airports, query):
    matches = []
    query_lower = query.lower()
    for airport in airports:
        if query_lower in airport['name'].lower():
            matches.append((airport['name'], airport['code']))
    return matches

with open('json/airlines.json', 'r') as file:
    airlines_data = json.load(file)

with open('json/airports.json', 'r', encoding='utf-8') as file:
    airports_data = json.load(file)

# Create a dictionary for airport coordinates
airport_coords = {airport['code']: airport['coordinates'] for airport in airports_data}

def create_map(search_results):
    m = folium.Map(location=[0, 0], zoom_start=2)

    for result in search_results:
        # Extract airport codes from the result string
        parts = result.split()
        departure_code, arrival_code = parts[1].split('-')

        # Retrieve coordinates
        if departure_code in airport_coords and arrival_code in airport_coords:
            dep_coord = airport_coords[departure_code]
            arr_coord = airport_coords[arrival_code]

            # Add markers and lines to the map
            folium.Marker([dep_coord['lat'], dep_coord['lon']], tooltip=departure_code).add_to(m)
            folium.Marker([arr_coord['lat'], arr_coord['lon']], tooltip=arrival_code).add_to(m)
            folium.PolyLine([(dep_coord['lat'], dep_coord['lon']), (arr_coord['lat'], arr_coord['lon'])], color="blue").add_to(m)

    m.save('map.html')


while True:
    choice = input("Select option (1: Route Search, 2: Airline Code Search, 3: Airport Code Search, 4: Exit): ").strip()

    # 读取JSON数据
    if choice == '1':
        with open('json/processed_routes_with_distance.json', 'r') as file:
            routes_data = json.load(file)

        # 构建搜索树
        search_tree = build_search_tree(routes_data)

        # 交互式搜索
        airline_input = input("Enter airline code or 'any': ").strip()
        departure_input = input("Enter departure code or 'any': ").strip()
        plane_input = input("Enter plane model (e.g., 320, 330, 7x7) or 'any': ").strip()
        distance_code_input = input("Enter distance category (A: 1-650, B: 651-1150, C: 1151-2000, D: 2001-4000, E: 4001-7000, F: 7000+) or 'any': ").strip()

        # 执行搜索
        search_results = search_routes(search_tree, airline_input, departure_input, plane_input, distance_code_input)

        # 展示初始搜索结果
        print("Initial Search Results:")
        for result in search_results:
            print(result)

        while True:
            print("Options:")
            print("1: Return to Start")
            print("2: Change Sorting")
            print("3: Convert Miles to Kilometers")
            print("4: Create Map")
            print("5: Exit\n")
            option_choice = input("Choose an option: ").strip()

            if option_choice == '1':
                break  # 返回到循环的开始
            elif option_choice == '2':
                sorting_method_input = input("Choose sorting method (1: Distance, 2: Airline, 3: Departure, 4: Plane Model): \n").strip()
                sorted_search_results = sorted(search_results, key=lambda x: get_sort_key(sorting_method_input, x))
                print("Sorted Search Results:")
                for result in sorted_search_results:
                    print(result)
                print('\n')
            elif option_choice == '3':
                print("Converted Search Results (Miles to Kilometers):")
                for result in search_results:
                    # 分割字符串以获取距离值
                    distance_str = result.split('distance:')[1].split(' ')[0]
                    try:
                        # 尝试将距离值转换为浮点数
                        miles = float(distance_str)
                    except ValueError:
                        # 如果转换失败，跳过当前结果
                        print("Could not convert:", result)
                        continue

                    kilometers = miles * 1.60934  # 转换为公里
                    # 重新构建结果字符串
                    result_km = result.replace(f"{distance_str} mi", f"{round(kilometers, 2)} km")
                    print(result_km)
                    print('\n')
            elif option_choice == '4':
                create_map(search_results)
                print("Successfully load as map.html\n")
            elif option_choice == '5':
                print("Exiting program.")
                exit()  # 退出程序
            else:
                print("Invalid option. Please choose again.")

    elif choice == '2':
        # 航空公司代码搜索功能
        query = input("Enter partial airline name to search: ").strip()
        search_results = search_airline_codes(airlines_data, query)

        # 展示航空公司搜索结果
        if search_results:
            print("Matching Airlines:")
            for name, code in search_results:
                print(f"{name} (Code: {code})")
            print('\n')
        else:
            print("No matching airlines found.\n")

    elif choice == '3':
        # 航空公司代码搜索功能
        query = input("Enter partial airport name to search: ").strip()
        search_results = search_airline_codes(airports_data, query)

        # 展示航空公司搜索结果
        if search_results:
            print("Matching Airlines:")
            for name, code in search_results:
                print(f"{name} (Code: {code})")
            print('\n')
        else:
            print("No matching airlines found.\n")

    elif choice == '4':
    # 退出程序
        print("Exiting program.")
        break

    else:
        print("Invalid choice. Please restart the script and choose a valid option.")