"""A virtual client for the SimplyPrint.io Service."""
import asyncio
import io
import json
import pathlib
import platform
import re
import socket
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

import aiohttp

import psutil

from simplyprint_ws_client import NotificationEventPayload, NotificationEventSeverity, ResolveNotificationDemandData
from simplyprint_ws_client.const import VERSION as SP_VERSION
from simplyprint_ws_client.core.client import ClientConfigChangedEvent, DefaultClient
from simplyprint_ws_client.core.config import PrinterConfig
from simplyprint_ws_client.core.state import FilamentSensorEnum, FileProgressStateEnum, PrinterStatus
from simplyprint_ws_client.core.state.models import NotificationEventButtonAction
from simplyprint_ws_client.core.ws_protocol.messages import (
    ConnectedMsg,
    FileDemandData,
    GcodeDemandData,
    MeshDataMsg,
    PluginInstallDemandData,
    PrinterSettingsMsg,
)
from simplyprint_ws_client.shared.camera.mixin import ClientCameraMixin
from simplyprint_ws_client.shared.files.file_download import FileDownload
from simplyprint_ws_client.shared.hardware.physical_machine import PhysicalMachine

from yarl import URL

from . import __version__, ota
from .duet.api import RepRapFirmware
from .duet.model import DuetPrinterModel
from .gcode import GCodeBlock
from .network import get_local_ip_and_mac
from .state import map_duet_state_to_printer_status
from .task import async_supress, async_task
from .watchdog import Watchdog


@dataclass
class DuetPrinterConfig(PrinterConfig):
    """Configuration for the VirtualClient."""

    duet_name: Optional[str] = None
    duet_uri: Optional[str] = None
    duet_password: Optional[str] = None
    duet_unique_id: Optional[str] = None
    webcam_uri: Optional[str] = None


class DuetPrinter(DefaultClient[DuetPrinterConfig], ClientCameraMixin[DuetPrinterConfig]):
    """A Websocket client for the SimplyPrint.io Service."""

    duet: DuetPrinterModel
    watchdog: Watchdog

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the client."""
        super().__init__(*args, **kwargs)

        self.initialize_camera_mixin(
            pause_timeout=10,
            max_cache_age=timedelta(seconds=1),
            **kwargs,
        )

    async def init(self) -> None:
        """Initialize the client."""
        self.logger.info('Initializing the client')

        try:
            await self._initialize_tasks()
            self.camera_uri = URL(self.config.webcam_uri) if self.config.webcam_uri else None
            await self._initialize_printer_info()
            await self._initialize_duet()
        except Exception as e:
            self.logger.exception(
                "An exception occurred while initializing the client",
                exc_info=e,
            )
            # TODO log to sentry
            self.active = False

    async def _initialize_duet(self) -> None:
        """Initialize the Duet printer."""
        if not self.config.duet_uri.startswith(('http://', 'https://')):
            self.config.duet_uri = f'http://{self.config.duet_uri}'
            await self.event_bus.emit(ClientConfigChangedEvent)

        duet_api = RepRapFirmware(
            address=self.config.duet_uri,
            password=self.config.duet_password,
            logger=self.logger.getChild('duet_api'),
        )

        self._printer_timeout = time.time() + 60 * 5  # 5 minutes

        self.duet = DuetPrinterModel(
            logger=self.logger.getChild('duet'),
            api=duet_api,
        )

        self.duet.events.on('connect', self._duet_on_connect)
        self.duet.events.on('objectmodel', self._duet_on_objectmodel)
        self.duet.events.on('state', self._duet_on_state)

    async def _initialize_tasks(self) -> None:
        """Initialize background tasks."""
        self._background_task = set()
        self._is_stopped = False

    async def _initialize_printer_info(self) -> None:
        """Initialize the printer info."""
        self.printer.info.core_count = psutil.cpu_count(logical=False)
        self.printer.info.total_memory = psutil.virtual_memory().total
        self.printer.info.hostname = socket.getfqdn()
        self.printer.info.os = "Meltingplot Duet Connector v{!s}".format(__version__)
        self.printer.info.sp_version = SP_VERSION
        self.printer.info.python_version = platform.python_version()
        if self.config.in_setup:
            self.printer.info.machine = self.config.duet_name or self.config.duet_uri
        else:
            self.printer.info.machine = PhysicalMachine.machine()
        self.printer.webcam_info.connected = self.config.webcam_uri is not None

    async def _notify_with_setup_code(self) -> str:
        r = await self.duet.gcode(
            f'M291 P"Code: {self.config.short_id}" R"SimplyPrint.io Setup" S2',
        )

        return r

    async def _duet_on_connect(self) -> None:
        """Connect to the Duet board."""
        if self.config.in_setup:
            await self._notify_with_setup_code()
        else:
            await self._check_and_set_cookie()

        board = self.duet.om['boards'][0]
        network = self.duet.om['network']

        if self.config.duet_unique_id is None:
            await self._set_duet_unique_id(board)
        else:
            self._validate_duet_unique_id(board)

        self._set_printer_name(network)
        self._set_firmware_info(board)

    async def _duet_on_state(self, old_state) -> None:
        """Handle State changes."""
        self.logger.debug(f"Duet state changed from {old_state} to {self.duet.state}")

    async def _set_duet_unique_id(self, board: dict) -> None:
        """Set the unique ID if it is not set and emit an event to notify the client."""
        self.config.duet_unique_id = board['uniqueId']
        await self.event_bus.emit(ClientConfigChangedEvent)

    def _validate_duet_unique_id(self, board: dict) -> None:
        """Validate the unique ID."""
        if self.config.duet_unique_id != board['uniqueId']:
            self.logger.error(
                'Unique ID mismatch: {0} != {1}'.format(self.config.duet_unique_id, board['uniqueId']),
            )
            self.printer.status = PrinterStatus.OFFLINE
            raise ValueError('Unique ID mismatch')

    def _set_printer_name(self, network: dict) -> None:
        """Set the printer name."""
        name_search = re.search(
            r'(meltingplot)([-\. ])(MBL[ -]?[0-9]{3})([ -]{0,3})(\w{6})?[ ]?(\w+)?',
            network['name'],
            re.I,
        )
        try:
            printer_name = name_search.group(3).replace('-', ' ').strip()
            self.printer.firmware.machine_name = f"Meltingplot {printer_name}"
        except (AttributeError, IndexError):
            self.printer.firmware.machine_name = network['name']

    def _set_firmware_info(self, board: dict) -> None:
        """Set the firmware information."""
        self.printer.firmware.name = board['firmwareName']
        self.printer.firmware.version = board['firmwareVersion']
        self.printer.set_api_info("Duet", __version__)
        self.printer.set_ui_info("Duet", __version__)

    async def _duet_on_objectmodel(self, old_om) -> None:
        """Handle Objectmodel changes."""
        await self._update_printer_status()
        await self._update_filament_sensor()
        await self._mesh_compensation_status(old_om=old_om)

        try:
            self._update_temperatures()
        except KeyError:
            self.printer.bed.temperature.actual = 0.0
            self.printer.tool0.actual = 0.0

        self._update_heater_fault_notifications()

        if await self._is_printing():
            await self._update_job_info()

    @async_task
    async def _duet_printer_task(self):
        """Duet Printer task."""
        while not self._is_stopped:
            try:
                if self._printer_timeout < time.time():
                    self.printer.status = PrinterStatus.OFFLINE
                    await self.duet.close()
                await self._ensure_duet_connection()
                await self.duet.tick()
                self._printer_timeout = time.time() + 60 * 5
                await asyncio.sleep(0.5)
            except TimeoutError:
                continue
            except asyncio.CancelledError as e:
                await self.duet.close()
                raise e
            except Exception:
                self.logger.exception(
                    "An exception occurred while ticking duet printer",
                )
                # TODO: log to sentry
                await asyncio.sleep(10)

    async def _ensure_duet_connection(self):
        """Ensure the Duet connection is active."""
        try:
            if not self.duet.connected():
                await self.duet.connect()
        except (
            aiohttp.ClientConnectionError,
            aiohttp.ClientResponseError,
            asyncio.TimeoutError,
        ):
            self.logger.debug('Failed to connect to Duet')
            await self.duet.close()
            await asyncio.sleep(30)
            raise TimeoutError

    async def on_connected(self, data: ConnectedMsg) -> None:
        """Connect to SimplyPrint.io."""
        self.logger.info(f'Connected to SimplyPrint.io name={data.data.name} setup_code={data.data.short_id}')

        self.use_running_loop()
        self._is_stopped = False

        await self._duet_printer_task()
        await self._connector_status_task()

    async def on_remove_connection(self, _) -> None:
        """Remove the connection."""
        self.logger.info('Disconnected from SimplyPrint.io')
        self._is_stopped = True
        for task in self._background_task:
            task.cancel()

    async def on_printer_settings(
        self,
        event: PrinterSettingsMsg,
    ) -> None:
        """Update the printer settings."""
        self.logger.debug("Printer settings: %s", event.data)

    @async_task
    async def deferred_gcode(self, event: GcodeDemandData) -> None:
        """
        Defer the GCode event.

        List of GCodes received from SP
        M104 S1 Tool heater on
        M140 S1 Bed heater on
        M106 Fan on
        M107 Fan off
        M221 S1 control flow rate
        M220 S1 control speed factor
        G91
        G1 E10
        G90
        G1 X10
        G1 Y10
        G1 Z10
        G28 Z
        G28 XY
        G29
        M18
        M17
        M190
        M109
        M155 # not supported by reprapfirmware
        M701 S"filament name" load filament
        M702 unload filament
        """
        self.logger.debug("Received Gcode: {!r}".format(event.list))

        gcode = GCodeBlock().parse(event.list)
        self.logger.debug("Parsed Gcode: {!r}".format(gcode))

        allowed_commands = [
            'M17',
            'M18',
            'M104',
            'M106',
            'M107',
            'M109',
            'M112',
            'M140',
            'M190',
            'M220',
            'M221',
            'M562',
            'M701',
            'M702',
            'M290',
            'G1',
            'G28',
            'G29',
            'G90',
            'G91',
        ]

        response = []

        for item in gcode.code:
            if item.code in allowed_commands and not self.config.in_setup:
                response.append(await self.duet.gcode(item.compress()))
            elif item.code == 'M300' and self.config.in_setup:
                response.append(
                    await self._notify_with_setup_code(),
                )
            elif item.code == 'M997':
                await self._perform_self_upgrade()
            else:
                response.append('{!s} G-Code blocked'.format(item.code))
                # TODO: notify sentry

        self.logger.debug("Gcode response: {!s}".format("\n   [gcode] ".join(response)))

    async def _perform_self_upgrade(self) -> None:
        """Perform self-upgrade and restart the API."""
        self.logger.info('Performing self upgrade')
        try:
            subprocess.check_call([
                sys.executable,
                '-m',
                'pip',
                'install',
                '--upgrade',
                'simplyprint_duet3d',
            ])
        except subprocess.CalledProcessError as e:
            self.logger.error('Error upgrading: {0}'.format(e))
            # TODO: notify sentry
        self.logger.info("Restarting API")
        # Since the API runs as a systemd service, we can restart it by terminating the process.
        raise KeyboardInterrupt()

    async def on_gcode(self, event: GcodeDemandData) -> None:
        """
        Receive GCode from SP and send GCode to duet.

        The GCode is checked for allowed commands and then sent to the Duet.
        """
        await self.deferred_gcode(event)

    def _upload_file_progress(self, progress: float) -> None:
        """Update the file upload progress."""
        # contrains the progress from 50 - 90 %
        self.printer.file_progress.percent = min(round(50 + (max(0, min(50, progress / 2))), 0), 90.0)

    async def _auto_start_file(self, filename: str) -> None:
        """Auto start the file after it has been uploaded."""
        self.logger.debug(f"Auto starting file {filename}")
        self.printer.job_info.filename = filename
        timeout = time.time() + 400  # seconds

        while timeout > time.time():
            try:
                response = await self.duet.api.rr_fileinfo(
                    name=f"0:/gcodes/{filename}",
                    timeout=aiohttp.ClientTimeout(total=10),
                )
                if response['err'] == 0:
                    break
            except (
                aiohttp.ClientConnectionError,
                TimeoutError,
                asyncio.TimeoutError,
            ):
                pass

            timeleft = 10 - ((timeout - time.time()) * 0.025)
            self.printer.file_progress.percent = min(99.9, (90.0 + timeleft))

            await asyncio.sleep(1)
        else:
            raise TimeoutError('Timeout while waiting for file to be ready')

        asyncio.run_coroutine_threadsafe(
            self.on_start_print(None),
            self.event_loop,
        )

    @async_task
    async def _fileprogress_task(self) -> None:
        """
        Periodically send file upload progress updates.

        This task ensures that file upload progress is sent every 5 seconds to prevent
        timeouts on clients with low bandwidth. The progress step between 0.5% can exceed
        the default timeout of 30 seconds, so frequent updates are necessary.
        """
        while not self._is_stopped and self.printer.file_progress.state == FileProgressStateEnum.DOWNLOADING:
            self.printer.file_progress.model_set_changed("state", "percent")
            await asyncio.sleep(5)

    @async_task
    @async_supress
    async def _download_file_from_sp_and_upload_to_duet(
        self,
        event: FileDemandData,
    ) -> None:
        """Download a file from SimplyPrint.io and upload it to the printer."""
        self.logger.debug(f"Downloading file from {event.url}")
        downloader = FileDownload(self)

        self.printer.file_progress.state = FileProgressStateEnum.DOWNLOADING
        self.printer.file_progress.percent = 0.0

        # Initiate the file progress task to send updates every 10 seconds.
        await self._fileprogress_task()

        with tempfile.NamedTemporaryFile(suffix='.gcode') as f:
            async for chunk in downloader.download(
                data=event,
                clamp_progress=(lambda x: float(max(0.0, min(50.0, x / 2.0)))),
            ):
                f.write(chunk)

            f.seek(0)
            prefix = '0:/gcodes/'
            retries = 3

            while retries > 0:
                try:
                    # Ensure progress updates are sent during the upload process.
                    response = await self.duet.api.rr_upload_stream(
                        filepath=f'{prefix}{event.file_name}',
                        file=f,
                        progress=self._upload_file_progress,
                    )
                    if response['err'] != 0:
                        self.printer.file_progress.state = FileProgressStateEnum.ERROR
                        return
                    break
                except aiohttp.ClientResponseError as e:
                    if e.status in {401, 500, 503}:
                        await self.duet.api.reconnect()
                    else:
                        # TODO: notify sentry
                        self.logger.exception(
                            "An exception occurred while uploading file to Duet",
                            exc_info=e,
                        )
                        raise e
                finally:
                    retries -= 1

        if event.auto_start:
            await self._auto_start_file(event.file_name)

        self.printer.file_progress.percent = 100.0
        self.printer.file_progress.state = FileProgressStateEnum.READY

    async def on_file(self, data: FileDemandData) -> None:
        """Download a file from SimplyPrint.io to the printer."""
        self.logger.debug(f"on_file called with {data}")
        await self._download_file_from_sp_and_upload_to_duet(event=data)

    async def on_start_print(self, _) -> None:
        """Start the print job."""
        await self.duet.gcode(
            f'M23 "0:/gcodes/{self.printer.job_info.filename}"',
        )
        await self.duet.gcode('M24')

    async def on_pause(self, _) -> None:
        """Pause the print job."""
        await self.duet.gcode('M25')

    async def on_resume(self, _) -> None:
        """Resume the print job."""
        await self.duet.gcode('M24')

    async def on_cancel(self, _) -> None:
        """Cancel the print job."""
        await self.duet.gcode('M25')
        await self.duet.gcode('M0')

    def _update_temperatures(self) -> None:
        """Update the printer temperatures."""
        heaters = self.duet.om['heat']['heaters']
        bed_heater_index = self.duet.om['heat']['bedHeaters'][0]

        self.printer.bed.temperature.actual = heaters[bed_heater_index]['current']
        self.printer.bed.temperature.target = (
            heaters[bed_heater_index]['active'] if heaters[0]['state'] != 'off' else 0.0
        )

        self.printer.tool_count = len(self.duet.om['tools']) or 1

        for tool_idx, tool in enumerate(self.printer.tools):
            heater_idx = self.duet.om['tools'][tool_idx]['heaters'][0]
            tool.temperature.actual = heaters[heater_idx]['current']
            tool.temperature.target = (heaters[heater_idx]['active'] if heaters[1]['state'] != 'off' else 0.0)

        self.printer.ambient_temperature.ambient = 20

    def _update_heater_fault_notifications(self):
        heaters = self.duet.om['heat']['heaters']
        bed_heater_index = self.duet.om['heat']['bedHeaters'][0]
        heater_idx_to_tool_idx = {tool['heaters'][0]: tool_idx for tool_idx, tool in enumerate(self.duet.om['tools'])}

        retained_events = []

        for heater_idx, heater in enumerate(heaters):
            if heater['state'] != 'fault':
                continue

            event_key = ("heater_fault", heater_idx)
            description = f"heater {heater_idx}"

            if heater_idx == bed_heater_index:
                description = "bed"
            elif heater_idx in heater_idx_to_tool_idx:
                tool_idx = heater_idx_to_tool_idx[heater_idx]
                description = f"nozzle {tool_idx}"

            _ = self.printer.notifications.keyed(
                event_key,
                severity=NotificationEventSeverity.ERROR,
                payload=NotificationEventPayload(
                    title="Heater Fault",
                    message=f"Heater fault on {description}. Only clear the fault if you are sure it is safe!",
                    data={"heater": heater_idx},
                    actions={"reset": NotificationEventButtonAction(label="Reset fault")},
                ),
            )

            retained_events.append(event_key)

        # Only keep heater fault events that are still active.
        self.printer.notifications.filter_retain_keys(
            lambda x: isinstance(x, tuple) and x[0] == "heater_fault",
            *retained_events,
        )

    async def _check_and_set_cookie(self) -> None:
        """Check if the cookie is set and set it if it is not."""
        self.logger.debug('Checking if cookie is set')
        try:
            async for _ in self.duet.api.rr_download(filepath='0:/sys/simplyprint-connector.json'):
                break
            await asyncio.sleep(1)
            await self.duet.api.rr_delete(filepath='0:/sys/simplyprint-connector.json')
        except aiohttp.client_exceptions.ClientResponseError:
            self.logger.debug('Cookie not set, setting cookie')

        cookie_data = {
            'hostname': self.printer.info.hostname,
            'ip': self.printer.info.local_ip,
            'mac': self.printer.info.mac,
        }
        cookie_json = json.dumps(cookie_data).encode('utf-8')
        await self.duet.api.rr_upload_stream(
            filepath='0:/sys/simplyprint-connector.json',
            file=io.BytesIO(cookie_json),
        )

    @async_task
    async def _mesh_compensation_status(self, old_om) -> None:
        """Task to check for mesh compensation changes and send mesh data to SimplyPrint."""
        old_compensation = old_om.get('move', {}).get('compensation', {})
        compensation = self.duet.om.get('move', {}).get('compensation', {})

        if compensation.get('file') and old_compensation.get('file') != compensation['file']:
            try:
                await self._send_mesh_data()
            except Exception as e:
                self.logger.exception(
                    "An exception occurred while sending mesh data",
                    exc_info=e,
                )

    async def _send_mesh_data(self) -> None:
        bed = await self.duet.heightmap()

        data = {
            'mesh_min': [bed['y_min'], bed['x_min']],
            'mesh_max': [bed['y_max'], bed['x_max']],
            'mesh_matrix': bed['mesh_data'],
        }

        # mesh data is matrix of y,x and z
        await self.send(
            MeshDataMsg(data=data),
        )

    async def _update_cpu_and_memory_info(self) -> None:
        self.printer.cpu_info.usage = psutil.cpu_percent(interval=1)
        try:
            self.printer.cpu_info.temp = psutil.sensors_temperatures()['coretemp'][0].current
        except KeyError:
            self.printer.cpu_info.temp = 0.0
        self.printer.cpu_info.memory = psutil.virtual_memory().percent

    async def _update_printer_status(self) -> None:
        old_printer_state = self.printer.status
        is_printing = await self._is_printing()
        self.printer.status = map_duet_state_to_printer_status(self.duet.om, is_printing)

        if self.printer.status == PrinterStatus.CANCELLING and old_printer_state == PrinterStatus.PRINTING:
            self.printer.job_info.cancelled = True
        elif self.printer.status == PrinterStatus.OPERATIONAL:
            if self.printer.job_info.started or old_printer_state == PrinterStatus.PRINTING:
                await self._mark_job_as_finished()

    async def _mark_job_as_finished(self) -> None:
        """Mark the current job as finished."""
        self.printer.job_info.finished = True
        self.printer.job_info.progress = 100.0

    @async_task
    async def _connector_status_task(self) -> None:
        """Task to gather connector infos and send data to SimplyPrint."""
        while not self._is_stopped:
            await self._update_cpu_and_memory_info()
            self._update_network_info()
            await asyncio.sleep(120)

    def _update_network_info(self) -> None:
        """Update the network information."""
        netinfo = get_local_ip_and_mac()
        self.printer.info.local_ip = netinfo.ip
        self.printer.info.mac = netinfo.mac

    async def _update_filament_sensor(self) -> None:
        filament_monitors = self.duet.om.get('sensors', {}).get('filamentMonitors', [])

        for monitor in filament_monitors:
            if monitor.get('enableMode', 0) > 0:
                self.printer.settings.has_filament_settings = True
                if monitor.get('status') == 'ok':
                    self.printer.filament_sensor.state = FilamentSensorEnum.LOADED
                else:
                    self.printer.filament_sensor.state = FilamentSensorEnum.RUNOUT
                    break  # only one sensor is needed

                calibrated = monitor.get('calibrated')
                configured = monitor.get('configured', {})
                if calibrated and self.printer.status == PrinterStatus.PAUSED:
                    if calibrated.get('percentMin', 0) < configured.get('percentMin', 0):
                        self.printer.filament_sensor.state = FilamentSensorEnum.RUNOUT
                        break  # only one sensor is needed
                    if calibrated.get('percentMax', 0) < configured.get('percentMax', 0):
                        self.printer.filament_sensor.state = FilamentSensorEnum.RUNOUT
                        break  # only one sensor is needed

    async def _is_printing(self) -> bool:
        """Check if the printer is currently printing."""
        if self.printer.status in {
            PrinterStatus.PRINTING,
            PrinterStatus.PAUSED,
            PrinterStatus.PAUSING,
            PrinterStatus.RESUMING,
        }:
            return True

        job_status = self.duet.om.get('job', {}).get('file', {})
        return bool(job_status.get('filename'))

    async def _update_times_left(self, times_left: dict) -> None:
        self.printer.job_info.time = times_left.get('filament') or times_left.get(
            'slicer',
        ) or times_left.get('file') or 0

    async def _update_job_info(self) -> None:
        job_status = self.duet.om.get('job', {})

        await self._update_job_progress(job_status)
        await self._update_job_times_left(job_status)
        await self._update_job_filename(job_status)
        await self._update_job_layer(job_status)

    async def _update_job_progress(self, job_status: dict) -> None:
        try:
            total_filament_required = sum(job_status['file']['filament'])
            current_filament = float(job_status['rawExtrusion'])
            self.printer.job_info.progress = min(
                current_filament * 100.0 / total_filament_required,
                100.0,
            )
            self.printer.job_info.filament = round(current_filament, None)
        except (TypeError, KeyError, ZeroDivisionError):
            self.printer.job_info.progress = 0.0

    async def _update_job_times_left(self, job_status: dict) -> None:
        try:
            await self._update_times_left(times_left=job_status['timesLeft'])
        except (TypeError, KeyError):
            self.printer.job_info.time = 0

    async def _update_job_filename(self, job_status: dict) -> None:
        try:
            filepath = job_status['file']['fileName']
            filename = pathlib.PurePath(filepath).name

            if self.printer.job_info.filename != filename:
                self.printer.job_info.filename = filename

            if job_status.get('duration', 0) < 10:
                self.printer.job_info.started = True
        except (TypeError, KeyError):
            pass

    async def _update_job_layer(self, job_status: dict) -> None:
        self.printer.job_info.layer = job_status.get('layer', 0)

    async def tick(self, _) -> None:
        """Update the client state."""
        await self.watchdog.reset()  # Reset the watchdog timer
        try:
            await self.send_ping()
        except Exception as e:
            self.logger.exception(
                "An exception occurred while ticking the client state",
                exc_info=e,
            )

    async def halt(self) -> None:
        """Halt the client."""
        self.logger.debug('halting the client')
        self._is_stopped = True
        for task in self._background_task:
            task.cancel()
        await self.duet.close()

    async def on_api_restart(self) -> None:
        """Restart the API."""
        self.logger.info("Restarting API")
        # the api is running as a systemd service, so we can just restart the service
        # by terminating the process
        raise KeyboardInterrupt()

    async def on_resolve_notification(self, data: ResolveNotificationDemandData):
        """Handle notification resolution events."""
        event = self.printer.notifications.notifications.get(data.event_id)
        if not event:
            return

        # Handle heater fault reset action.
        if data.action == "reset" and event.payload.data.get("heater") is not None:
            heater_idx = event.payload.data["heater"]
            tools = self.duet.om['tools']
            bed_heater_index = self.duet.om['heat']['bedHeaters'][0]

            # Reset heater fault
            await self.duet.gcode(f"M562 P{heater_idx}")

            # Reactivate the heater
            if heater_idx == bed_heater_index:
                # Make bed active.
                await self.duet.gcode("M144 S1")
            else:
                for tool_idx, tool in enumerate(tools):
                    if heater_idx in tool['heaters']:
                        # Make tool active.
                        await self.duet.gcode(f"M568 P{tool_idx} A2")

    async def on_plugin_install(self, event: PluginInstallDemandData) -> None:
        """Handle plugin installation demand event."""
        # XXX: Least thread-safe code on the planet.
        plugin = event.plugins.pop()

        if plugin.get("type") != "install" and plugin.get("name") != "simplyprint-duet3d":
            self.logger.warning(f"Plugin install demand received for {plugin}, but it is not supported.")
            return

        ret = ota.self_update("simplyprint_duet3d", extra_index_url="https://www.piwheels.org/simple")

        if ret == 0:
            self.logger.info("Plugin updated successfully, restarting API.")
            await self.on_api_restart()
            return

        await self.push_notification(
            severity=NotificationEventSeverity.WARNING,
            payload=NotificationEventPayload(
                title="Failed to update plugin",
                message="An error occurred while updating the SimplyPrint Duet3D plugin. Please check the logs.",
            ),
        )
