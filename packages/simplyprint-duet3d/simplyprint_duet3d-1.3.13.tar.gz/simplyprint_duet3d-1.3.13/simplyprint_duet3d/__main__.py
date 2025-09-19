"""Main entry point for the Duet SimplyPrint connector."""
import ipaddress
import logging
import socket
from urllib.parse import urlparse

import click
import PIL  # noqa

from simplyprint_ws_client.const import IS_TESTING
from simplyprint_ws_client.core.app import ClientApp
from simplyprint_ws_client.core.config import ConfigManagerType
from simplyprint_ws_client.core.settings import ClientSettings
from simplyprint_ws_client.core.ws_protocol.connection import ConnectionMode
from simplyprint_ws_client.shared.cli.cli import ClientCli
from simplyprint_ws_client.shared.logging import setup_logging

from . import __version__
from .cli.autodiscover import AutoDiscover
from .cli.install import install_as_service
from .printer import DuetPrinter, DuetPrinterConfig
from .watchdog import Watchdog
from .webcam import DuetSnapshotCamera


def rescan_existing_networks(app):
    """
    Rescan the existing networks.

    Gather all the existing networks and password from the configuration
    manager and scan them.
    """
    configs = app.config_manager.get_all()
    networks = {}
    for config in configs:
        try:
            # Attempt to resolve the URI as a URL via DNS
            hostname = urlparse(config.duet_uri).hostname  # Extract hostname from URI

            addr_info = socket.getaddrinfo(hostname, None)
            for result in addr_info:
                family, socktype, _, _, sockaddr = result
                if socktype == socket.SOCK_STREAM:
                    if family == socket.AF_INET:
                        ip_address = sockaddr[0]
                        network = ipaddress.ip_network(ip_address, strict=False).supernet(new_prefix=24)
                        break
                    elif family == socket.AF_INET6:
                        ip_address = sockaddr[0]
                        # Using /64 as prefix is to large as it includes 18,446,744,073,709,551,616 addresses
                        # Using /120 as prefix is small enough as it includes 256 addresses
                        network = ipaddress.ip_network(ip_address, strict=False).supernet(new_prefix=120)
                        break
        except (socket.gaierror, ValueError, TypeError):
            # If DNS resolution fails, treat it as an IP address directly
            network = ipaddress.ip_network(config.duet_uri, strict=False).supernet(new_prefix=24)
        networks[f"{network}"] = config.duet_password
    return networks


def run_app(autodiscover: AutoDiscover, app, profile, watchdog: Watchdog):
    """Run the application."""
    click.echo("Starting the Meltingplot Duet SimplyPrint.io Connector")
    click.echo('Perform network scans for existing networks')

    networks = rescan_existing_networks(app)

    try:
        for network, pwd in networks.items():
            click.echo(f"Scanning existing network: {network} with password {pwd}")
            if ':' in network:
                autodiscover.autodiscover(password=pwd, ipv6_range=network, ipv4_range='127.0.0.1/32', timeout=5)
            else:
                autodiscover.autodiscover(password=pwd, ipv4_range=network, ipv6_range="::1/128", timeout=5)
    except Exception as e:
        click.echo(f"Error during network scan: {e}")
        logging.error(f"Error during network scan: {e}")

    if profile:
        import cProfile
        import atexit
        import pstats
        import io

        click.echo("Profiling enabled")
        pr = cProfile.Profile()
        pr.enable()

        def app_exit():
            click.echo("Exiting the Meltingplot Duet SimplyPrint.io Connector")
            pr.disable()
            s = io.StringIO()
            sortby = 'cumulative'
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            click.echo(s.getvalue())

        atexit.register(app_exit)

    watchdog.reset_sync(offset=600)  # Reset the watchdog timer
    watchdog.start()  # Start the watchdog to start the timer
    app.run_blocking()


def main():
    """Initiate the connector as the main entry point."""
    watchdog = Watchdog(timeout=300)
    DuetPrinter.watchdog = watchdog

    settings = ClientSettings(
        name="DuetConnector",
        version=__version__,
        mode=ConnectionMode.MULTI,
        client_factory=DuetPrinter,
        config_factory=DuetPrinterConfig,
        allow_setup=True,
        config_manager_t=ConfigManagerType.JSON,
        camera_workers=1,
        camera_protocols=[DuetSnapshotCamera],
        development=IS_TESTING,
    )

    setup_logging(settings)
    logging.getLogger("PIL").setLevel(logging.INFO)
    logging.getLogger("aiohttp.client").setLevel(logging.INFO)

    app = ClientApp(settings)
    cli = ClientCli(app)

    autodiscover = AutoDiscover(app)

    cli.add_command(autodiscover.command)
    cli.add_command(install_as_service)
    cli.add_command(
        click.Command(
            "start",
            callback=lambda profile: run_app(autodiscover, app, profile, watchdog),
            help="Start the client",
            params=[click.Option(["--profile"], is_flag=True, help="Enable profiling")],
        ),
    )
    cli(prog_name="python -m simplyprint_duet3d")


if __name__ == "__main__":
    main()
