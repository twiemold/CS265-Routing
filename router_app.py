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

"""

import requests as req
import sys
import json

TEST_URL = "http://www.goatgoose.com"
PLAIDNET_URL = "https://132.198.11.11"
SOCKET = ":2222"


def deploy_tables():
    # deploy the forwarding tables to the network via the controller
    pass


def comp_tables():
    # compute forwarding
    # tables to support optimal routing between three hosts
    pass


def query_network():
    # TODO: Add error handling
    # TODO: Parameterize arguments
    topo_link = '/get_topology/topology1'
    response = req.get(TEST_URL + SOCKET + topo_link, timeout=10)
    json_topo = response.json()
    return json_topo


def main():
    topo = query_network()


if __name__ == '__main__':
    main()
