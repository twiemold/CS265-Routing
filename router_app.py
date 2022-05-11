"""
Thomas Wiemold
5/5/2022
CS265A
Programming Assignment #2

Per Instructions:
When integrated with other services, your application will query the
network controller for its topology (RESTfully), compute forwarding
tables to support optimal routing between three hosts, and then deploy
the forwarding tables to the network via the controller.

Link to RFC:
http://ceskalka.w3.uvm.edu/265/sdn-assignment/

Dijkstra's Algorithm adapted from:
https://www.udacity.com/blog/2021/10/implementing-dijkstras-algorithm-in-python.html

"""

import requests as req
import sys

TEST_URL = "http://www.goatgoose.com"
PLAIDNET_URL = "https://132.198.11.11"
SOCKET = ":2222"


def deploy_tables(table, arguments):
    response = req.post(f'http://{arguments[0]}{SOCKET}/set_tables/{arguments[1]}',
                        table,
                        timeout=10)
    if response.status_code != req.codes.ok:
        response.raise_for_status()
        return 8
    else:
        return 0


def create_entry(node, dest):
    table_entry = {
        "switch_id": node[0],
        "dst_ip": f"{dest}",
        "out_port": node[1]
    }
    return table_entry


def find_path(dest, previous_nodes, start_node):
    path = []
    node = (dest, 0)

    while node[0] != start_node:
        path.append(node)
        node = previous_nodes[node[0]]

    path.remove((dest, 0))
    path.reverse()
    return path


def create_tables(dest, previous_nodes, start_node, tables):
    path = find_path(dest, previous_nodes, start_node)
    for node in path:
        tables["table entries"].append(create_entry(node, dest))
    return tables


def initialize_paths(topo):
    paths = {}
    shortest_paths = {}
    previous_nodes = {}
    hosts = []
    unvisited_nodes = []
    for i in range(len(topo['connected'])):
        src_node = topo['connected'][i][0]
        dst_node = topo['connected'][i][1]
        port = topo['connected'][i][2]
        if src_node not in hosts and isinstance(src_node, str):
            hosts.append(src_node)
        if src_node not in unvisited_nodes:
            unvisited_nodes.append(src_node)
        if src_node in paths:
            paths[src_node].append([dst_node, port])
        else:
            paths[src_node] = [[dst_node, port]]
    for src_node in unvisited_nodes:
        shortest_paths[src_node] = sys.maxsize
    return paths, shortest_paths, previous_nodes, hosts, unvisited_nodes


def comp_paths(topo, initial_node):
    # compute forwarding
    # tables to support optimal routing between three hosts
    paths, shortest_paths, \
        previous_nodes, hosts, unvisited_nodes = initialize_paths(topo)
    switches = list(paths.keys() - hosts)
    if initial_node == -1:
        start_node = unvisited_nodes[0]
    else:
        start_node = initial_node
    shortest_paths[start_node] = 0
    while unvisited_nodes:
        current_min = None
        for node in unvisited_nodes:
            if current_min is None:
                current_min = node
            elif shortest_paths[node] < shortest_paths[current_min]:
                current_min = node
        neighbors = paths[current_min]
        for neighbor in neighbors:
            tentative_value = shortest_paths[current_min] + 1
            if tentative_value < shortest_paths[neighbor[0]]:
                shortest_paths[neighbor[0]] = tentative_value
                previous_nodes[neighbor[0]] = (current_min, neighbor[1])
        unvisited_nodes.remove(current_min)
    return previous_nodes, shortest_paths, switches, hosts


def query_network(arguments):
    response = req.get(f'http://{arguments[0]}{SOCKET}/get_topology/{arguments[1]}', timeout=10)
    if response.status_code != req.codes.ok:
        response.raise_for_status()
        return 8
    else:
        json_topo = response.json()
        return json_topo


def main():
    if len(sys.argv) < 1 or len(sys.argv) > 4:
        print("Incorrect number of arguments passed, exiting...")
        return 8
    arguments = (sys.argv[1], sys.argv[2])
    topo = query_network(arguments)
    if topo == 8:
        print("Error querying network, exiting...")
        return 8
    previous_nodes, shortest_paths, switches, hosts = comp_paths(topo, -1)
    forwarding_tables = {"table entries": []}
    node_tables = {}
    for host in hosts:
        previous_nodes, shortest_paths, switches, hosts = comp_paths(topo, host)
        node_tables[host] = previous_nodes
    for i in range(len(hosts)):
        if i == len(hosts) - 1:
            forwarding_tables = create_tables(hosts[i], node_tables[hosts[0]], hosts[0], forwarding_tables)
        else:
            forwarding_tables = create_tables(hosts[i], node_tables[hosts[i+1]], hosts[i+1], forwarding_tables)

    deploy_result = deploy_tables(forwarding_tables, arguments)
    if deploy_result == 8:
        print("Error deploying tables, exiting...")
        return 8
    else:
        print("Successfully deployed optimal routing tables")
        print("Table output:")
        for entry in forwarding_tables["table entries"]:
            print(entry)



if __name__ == '__main__':
    main()
