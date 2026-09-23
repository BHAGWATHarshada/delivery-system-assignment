from collections import defaultdict

from utils import euclidean


def assign_packages_to_agents(data):

    # getting warehouse ,agents and packages from the input data

    warehouses = data.get('warehouses', {})
    agents = data.get('agents', {})
    packages = data.get('packages', [])

    # here converting warehouse list into a dictionary only if needed
    if isinstance(warehouses, list):
        warehouse_data = {}

        for warehouse in warehouses:
            warehouse_id = warehouse.get('id') or warehouse.get('name')
            location = warehouse.get('location') or warehouse.get('coords')

            if warehouse_id and location:
                warehouse_data[warehouse_id] = location

        warehouses = warehouse_data

    if isinstance(agents, list):
        agent_data = {}

        for agent in agents:
            agent_id = agent.get('id') or agent.get('name')
            location = agent.get('location') or agent.get('coords')

            if agent_id and location:
                agent_data[agent_id] = location

        agents = agent_data

    #  converting different coordinate formats into (x, y)
    def coord(value):
        # handling coordinates stored inside another list
        if isinstance(value, list) and value and isinstance(value[0], list):
            value = value[0]

        #  coordinates x,y
        if isinstance(value, dict):
            if 'x' in value and 'y' in value:
                return float(value['x']), float(value['y'])

            value = list(value.values())

        # here take the first two values if x and y are not present
        return float(value[0]), float(value[1])

    # converting all warehouse coordinates
    warehouse_locations = {}

    for warehouse_id, location in warehouses.items():
        warehouse_locations[warehouse_id] = coord(location)

    # agents
    agent_locations = {}

    for agent_id, location in agents.items():
        agent_locations[agent_id] = coord(location)

    assigned = defaultdict(list)

    for package in packages:
        # Get the warehouse id from  package
        warehouse_id = (
            package.get('warehouse')
            or package.get('warehouse_id')
            or package.get('from_warehouse')
        )

        if not agent_locations:
            raise ValueError('no agents available in input data')

        if warehouse_id not in warehouse_locations:

            #to skip or assignment of nearest agent from  destination
            destination = package.get('destination', (0, 0))

            if isinstance(destination, list) and destination and isinstance(destination[0], list):
                destination = destination[0]

            destination = (float(destination[0]), float(destination[1]))

            # find nearest agent to destination
            nearest_agent = None
            nearest_distance = float('inf')

            for agent_id, agent_location in agent_locations.items():
                current_distance = euclidean(agent_location, destination)

                if current_distance < nearest_distance:
                    nearest_distance = current_distance
                    nearest_agent = agent_id

        else:
            warehouse_location = warehouse_locations[warehouse_id]

            # find nearest agent to warehouse
            nearest_agent = None
            nearest_distance = float('inf')

            for agent_id, agent_location in agent_locations.items():
                current_distance = euclidean(
                    agent_location,
                    warehouse_location
                )

                if current_distance < nearest_distance:
                    nearest_distance = current_distance
                    nearest_agent = agent_id

        assigned[nearest_agent].append(package)

    return assigned, agent_locations, warehouse_locations


def simulate_agent_route(agent_position, packages, warehouse_locations):
    total_distance = 0
    current_position = agent_position

    # creating group of packages by warehouse
    warehouse_packages = defaultdict(list)

    for package in packages:
        warehouse_id = package.get('warehouse')
        warehouse_packages[warehouse_id].append(package)

    # visit warehouses
    for warehouse_id in sorted(warehouse_packages):
        warehouse_position = warehouse_locations.get(warehouse_id, (0, 0))

        total_distance += euclidean(current_position, warehouse_position)
        current_position = warehouse_position

        # deliver packages simple nearest neighbour from warehouse
        destinations = []

        for package in warehouse_packages[warehouse_id]:
            destinations.append(
                package.get('destination', (0, 0))
            )

        while destinations:
            # find nearest destination from current position
            nearest_index = 0

            for i in range(1, len(destinations)):
                current_distance = euclidean(current_position, destinations[i])
                nearest_distance = euclidean(current_position, destinations[nearest_index])

                if current_distance < nearest_distance:
                    nearest_index = i

            destination = destinations.pop(nearest_index)

            total_distance += euclidean(current_position, destination)
            current_position = destination

    return total_distance

# generating the report
def generate_report(data):
    assigned, agent_coords, wh_coords = assign_packages_to_agents(data)

    report = {}
    agents = sorted(agent_coords.keys())
    for a in agents:
        pkgs = assigned.get(a, [])
        total_distance = 0.0
        if pkgs:
            total_distance = simulate_agent_route(agent_coords[a], pkgs, wh_coords)
        delivered = len(pkgs)
        efficiency = total_distance / delivered if delivered else 0.0
        report[a] = {
            'packages_delivered': delivered,
            'total_distance': round(total_distance, 2),
            'efficiency': round(efficiency, 2)
        }
    # here we are determining the best agent by finding avd distance per package . if same or zero deleveries then we prefer with more deliveries
    candidates = [ (a, v) for a, v in report.items() if v['packages_delivered']>0 ]
    if candidates:
        best = min(candidates, key=lambda av: (av[1]['efficiency'], -av[1]['packages_delivered'], av[1]['total_distance']))[0]
    else:
        # if no deleveries then select agent with smallest total distance
        best = agents[0] if agents else None

    report['best_agent'] = best
    return report

#  top performer feature addition
def export_top_performer_csv(report, output_path):
    
    if not report or 'best_agent' not in report:
        return

    best_agent = report['best_agent']
    best_data = report.get(best_agent, {})

    with open(output_path, 'w', newline='', encoding='utf-8') as file:
        file.write('agent,packages_delivered,total_distance,efficiency\n')
        file.write(
            f"{best_agent},{best_data.get('packages_delivered', 0)},{best_data.get('total_distance', 0.0)},{best_data.get('efficiency', 0.0)}\n"
        )
