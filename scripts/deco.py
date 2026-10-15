#!/usr/bin/env python3
"""Thin CLI over the tplink-deco-api SDK (https://github.com/roquerodrigo/tplink-deco-api).

Talks to the TP-Link Deco local web API on the LAN. Reads credentials from
the environment only; never hardcode them.
"""

from __future__ import annotations

import argparse
import dataclasses
import ipaddress
import json
import os
import re
import sys

DEFAULT_HOST = "192.168.68.1"
MAC_RE = re.compile(r"^[0-9A-Fa-f]{2}(?:[:-][0-9A-Fa-f]{2}){5}$")


def fail(message: str) -> None:
    print(f"deco: {message}", file=sys.stderr)
    sys.exit(1)


def dump(payload: object) -> None:
    print(json.dumps(payload, indent=2))


def as_dict(obj: object) -> dict:
    return dataclasses.asdict(obj)


def check_mac(value: str) -> str:
    if not MAC_RE.match(value):
        fail(f"'{value}' is not a MAC address (expected AA:BB:CC:DD:EE:FF)")
    return value


def check_ipv4(value: str) -> str:
    try:
        return str(ipaddress.IPv4Address(value))
    except ipaddress.AddressValueError:
        fail(f"'{value}' is not an IPv4 address")


def parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        fail(f"invalid JSON: {error}")


def load_sdk():
    try:
        import tplink_deco_api
    except ImportError:
        fail(
            "the tplink-deco-api package is not installed. "
            "Run: pip install tplink-deco-api (requires Python 3.14+)"
        )
    return tplink_deco_api


def read_env() -> tuple[str, str, str]:
    host = os.environ.get("DECO_HOST", DEFAULT_HOST)
    user = os.environ.get("DECO_USER")
    password = os.environ.get("DECO_PASSWORD")
    if not user or not password:
        fail(
            "DECO_USER and DECO_PASSWORD are not set. They are the credentials of the "
            "Deco web admin (the owner TP-Link ID). Verify them by signing in at "
            f"https://tplinkdeco.net or http://{host} from a browser on the Deco network"
        )
    return host, user, password


# Read commands


def cmd_status(args: argparse.Namespace, sdk, deco) -> None:
    dump(
        {
            "internet": as_dict(deco.get_internet_status()),
            "mode": as_dict(deco.get_device_mode()),
            "performance": as_dict(deco.get_performance()),
        }
    )


def cmd_nodes(args: argparse.Namespace, sdk, deco) -> None:
    dump([as_dict(node) for node in deco.get_device_list()])


def cmd_clients(args: argparse.Namespace, sdk, deco) -> None:
    dump([as_dict(client) for client in deco.get_client_list(args.node or "default")])


def cmd_totals(args: argparse.Namespace, sdk, deco) -> None:
    dump(as_dict(deco.get_client_totals(args.node or "default")))


def cmd_wan(args: argparse.Namespace, sdk, deco) -> None:
    dump(as_dict(deco.get_wan_info()))


def cmd_wlan(args: argparse.Namespace, sdk, deco) -> None:
    dump(as_dict(deco.get_wlan_config()))


def cmd_dsl(args: argparse.Namespace, sdk, deco) -> None:
    dump(as_dict(deco.get_dsl_status(args.node or "default")))


def cmd_blocked(args: argparse.Namespace, sdk, deco) -> None:
    dump([as_dict(client) for client in deco.clients.get_blocked()])


# State-changing commands


def cmd_block(args: argparse.Namespace, sdk, deco) -> None:
    mac = args.mac
    name = args.name
    client_type = args.client_type
    if not name or not client_type:
        for client in deco.get_client_list():
            if client.mac.lower() == mac.lower():
                name = name or client.name
                client_type = client_type or (client.client_type or None)
                break
    if not name:
        fail(f"could not resolve a name for {mac}; pass --name")
    if not client_type:
        fail(f"could not resolve a client type for {mac}; pass --type (e.g. phone, pc)")
    deco.clients.block(mac, name, client_type)
    dump({"blocked": mac, "name": name, "client_type": client_type})


def cmd_unblock(args: argparse.Namespace, sdk, deco) -> None:
    deco.clients.unblock(args.mac)
    dump({"unblocked": args.mac})


def cmd_rename(args: argparse.Namespace, sdk, deco) -> None:
    deco.clients.update(args.mac, args.name)
    dump({"renamed": args.mac, "name": args.name})


def cmd_forget(args: argparse.Namespace, sdk, deco) -> None:
    deco.clients.remove(args.mac)
    dump({"forgotten": args.mac})


def cmd_reservations(args: argparse.Namespace, sdk, deco) -> None:
    dump(as_dict(deco.address_reservations.get_table()))


def cmd_reserve(args: argparse.Namespace, sdk, deco) -> None:
    deco.address_reservations.add(sdk.AddressReservation(args.mac, args.ip))
    dump({"reserved": {"mac": args.mac, "ip": args.ip}})


def cmd_unreserve(args: argparse.Namespace, sdk, deco) -> None:
    deco.address_reservations.remove(args.mac)
    dump({"removed": args.mac})


# Raw access to the full endpoint catalogue


def cmd_raw(args: argparse.Namespace, sdk, deco) -> None:
    data = parse_json(args.data) if args.data else {"operation": "read"}
    dump(deco.request(args.path, args.form, data))


def cmd_raw_list(args: argparse.Namespace, sdk, deco) -> None:
    data = parse_json(args.data) if args.data else {"operation": "read"}
    dump(deco.request_list(args.path, args.form, data))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deco",
        description="Thin CLI over the TP-Link Deco local web API (tplink-deco-api SDK).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="request timeout in seconds (default: 10)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("status", help="internet status, device mode, CPU/memory")
    p.set_defaults(handler=cmd_status)

    p = sub.add_parser("nodes", help="Deco mesh units (model, firmware, role, IP)")
    p.set_defaults(handler=cmd_nodes)

    p = sub.add_parser("clients", help="connected clients (name, IP, MAC, band, online)")
    p.add_argument("--node", help="limit to one Deco unit (MAC address)")
    p.set_defaults(handler=cmd_clients)

    p = sub.add_parser("totals", help="aggregated up/down speeds")
    p.add_argument("--node", help="limit to one Deco unit (MAC address)")
    p.set_defaults(handler=cmd_totals)

    p = sub.add_parser("wan", help="WAN/LAN IP configuration, including DNS servers")
    p.set_defaults(handler=cmd_wan)

    p = sub.add_parser("wlan", help="Wi-Fi configuration (contains Wi-Fi passwords)")
    p.set_defaults(handler=cmd_wlan)

    p = sub.add_parser("dsl", help="DSL link status (DSL models only)")
    p.add_argument("--node", help="limit to one Deco unit (MAC address)")
    p.set_defaults(handler=cmd_dsl)

    p = sub.add_parser("blocked", help="clients cut off from the internet")
    p.set_defaults(handler=cmd_blocked)

    p = sub.add_parser("block", help="cut a client off from the internet")
    p.add_argument("mac")
    p.add_argument("--name", help="label for the blocklist entry (default: current name)")
    p.add_argument(
        "--type",
        dest="client_type",
        help="device category, e.g. phone, pc (default: current type)",
    )
    p.set_defaults(handler=cmd_block)

    p = sub.add_parser("unblock", help="restore internet access for a client")
    p.add_argument("mac")
    p.set_defaults(handler=cmd_unblock)

    p = sub.add_parser("rename", help="rename a client")
    p.add_argument("mac")
    p.add_argument("name")
    p.set_defaults(handler=cmd_rename)

    p = sub.add_parser("forget", help="forget an offline client")
    p.add_argument("mac")
    p.set_defaults(handler=cmd_forget)

    p = sub.add_parser("reservations", help="DHCP address reservation table")
    p.set_defaults(handler=cmd_reservations)

    p = sub.add_parser("reserve", help="reserve a fixed IP for a client")
    p.add_argument("mac")
    p.add_argument("ip")
    p.set_defaults(handler=cmd_reserve)

    p = sub.add_parser("unreserve", help="remove a DHCP address reservation")
    p.add_argument("mac")
    p.set_defaults(handler=cmd_unreserve)

    p = sub.add_parser("raw", help="raw request to any endpoint (object result)")
    p.add_argument("path", help="endpoint path, e.g. admin/device")
    p.add_argument("form", help="endpoint form, e.g. device_list")
    p.add_argument("data", nargs="?", help='request JSON (default: {"operation": "read"})')
    p.set_defaults(handler=cmd_raw)

    p = sub.add_parser("raw-list", help="raw request to any endpoint (list result)")
    p.add_argument("path")
    p.add_argument("form")
    p.add_argument("data", nargs="?", help='request JSON (default: {"operation": "read"})')
    p.set_defaults(handler=cmd_raw_list)

    return parser


def prevalidate(args: argparse.Namespace) -> None:
    """Reject bad input before any import or network call."""
    node = getattr(args, "node", None)
    if node:
        check_mac(node)
    if args.command in {"block", "unblock", "rename", "forget", "reserve", "unreserve"}:
        check_mac(args.mac)
    if args.command == "reserve":
        check_ipv4(args.ip)


def run(args: argparse.Namespace) -> None:
    prevalidate(args)
    host, user, password = read_env()
    sdk = load_sdk()
    deco = sdk.DecoClient(host, user, password, timeout=args.timeout)
    try:
        with deco:
            args.handler(args, sdk, deco)
    except sdk.AuthenticationError as error:
        print(f"deco: login failed: {error}", file=sys.stderr)
        print(
            "deco: check DECO_USER/DECO_PASSWORD against the web admin login "
            f"(https://tplinkdeco.net or http://{host})",
            file=sys.stderr,
        )
        sys.exit(1)
    except sdk.TransportError as error:
        print(f"deco: cannot reach the router: {error}", file=sys.stderr)
        print(
            "deco: check DECO_HOST and that this machine is on the Deco network",
            file=sys.stderr,
        )
        sys.exit(1)
    except (sdk.DecoError, ValueError) as error:
        print(f"deco: {error}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    args = build_parser().parse_args()
    try:
        run(args)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
