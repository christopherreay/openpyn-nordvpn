#!/usr/bin/python3

import subprocess
import argparse
import requests
import operator
import random


def main(server, country, udp, background):
    port = "tcp443"
    if udp:
        port = "udp1194"

    if country:
        country = country.lower()
        bestServers = findBestServers(country)
        chosenServer = chooseBestServer(bestServers)
        connection = connect(chosenServer, port, background)
    elif server:
        server = server.lower()
        connection = connect(server, port, background)


def findBestServers(country):
    serverList = []
    BestServerList = []
    countryDic = {
        'au': 'Australia', 'ca': 'Canada', 'at': 'Austria', 'be': 'Belgium',
        'ba': 'Brazil', 'de': 'Denmark', 'es': 'Estonia', 'fi': 'Finland'}
    country = countryDic[country]
    url = "https://nordvpn.com/wp-admin/admin-ajax.php?group=Standard+VPN\
    +servers&country=" + country + "&action=getGroupRows"

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

    try:
        response = requests.get(url, headers=headers).json()
    except HTTPError as e:  # @todo ask for server instead
        print("Cannot GET the json from nordvpn.com")

    for i in response:
        # only add if the server is online
        if i["exists"] is True:
            serverList.append([i["short"], i["load"]])

    print(serverList)
    # sort list by the server load
    serverList.sort(key=operator.itemgetter(1))
    print(serverList)
    # only choose servers with < 70% load then top 5 of them
    for server in serverList:
        serverLoad = int(server[1])
        if serverLoad < 70 and len(BestServerList) < 5:
            BestServerList.append(server)

    print(BestServerList)
    return BestServerList


def chooseBestServer(BestServerList):
    chosenServerList = BestServerList[random.randrange(0, len(BestServerList))]
    chosenServer = chosenServerList[0]  # the first value, "server name"
    return chosenServer


def connect(server, port, background):
    print("CONNECTING TO SERVER", server, port)
    if background:
        subprocess.Popen(["sudo", "openvpn", "--config", "./files/" + server + ".nordvpn.com." + port + ".ovpn", "--auth-user-pass", "pass.txt"])
    else:
        subprocess.run(["sudo", "openvpn", "--config", "./files/" + server + ".nordvpn.com." + port + ".ovpn", "--auth-user-pass", "pass.txt"], stdin=subprocess.PIPE)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Script to Connect to OpenVPN')
    parser.add_argument(
        '-s', '--server', help='server name, i.e. ca64 or au10',)
    parser.add_argument(
        '-u', '--udp', help='use port UDP-1194 instead of the default TCP-443',
        action='store_true')
    parser.add_argument(
        '-c', '--country', help='Specifiy Country with 2 letter name, i.e au,\
         A server among the top 5 servers will be used automatically.')
    parser.add_argument(
        '-b', '--background', help='Run script in the background',
        action='store_true')

    args = parser.parse_args()
    main(args.server, args.country, args.udp, args.background)
