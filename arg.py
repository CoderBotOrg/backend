import argparse
parser = argparse.ArgumentParser(description="CoderBot wifi config manager and daemon initializer", prog="wifi.py")
subparsers = parser.add_subparsers()
up = subparsers.add_parser('updatecfg', help="update configuration")
up.add_argument('mode', choices=['ap', 'client'],  help='wifi mode')
up.add_argument('ssid',  help='wifi ssid')
up.add_argument('pwd',  help='wifi password')
up.add_argument('name',  help='coderbot unique id')
args = vars(parser.parse_args())
print(args)

