SimplyPrint Duet3d integration
================================================

Many thanks to `Tim Schneider <https://github.com/timschneider>`_  at https://github.com/Meltingplot/duet-simplyprint-connector/ for originally creating this integration and allowing us to use it.

This package acts as a bridge between Duet-based 3D printers and the SimplyPrint.io cloud service.

It communicates with the printer using the Duet HTTP API.
For more information, visit https://github.com/Duet3D/RepRapFirmware/wiki/HTTP-requests.

Communication with SimplyPrint.io is handled via the `simplyprint-ws-client`.

------------
Status
------------

Supported features:

- Printer registration
- Printer status update
- Webcam snapshot livestream
- GCode receiving
- File downloading
- Printer control (start, pause, resume, cancel)
- Self Upgrading VIA G-Code M997
- Device healts update
- Bed leveling
- Filament Sensor
- Duet auto discovery with tracking based on BoardID
- Leave a cookie on the printer to identify the printer in the future (`0:/sys/simplyprint-connector.json`)
- Grab the webcam url from DWC Settings file from the Printer
- Allow Webcam URL to be an Snapshot Endpoint or MJPEG Stream

Missing features:

- PSU Control
- GCode Macros / Scripts [not yet implemented by SimplyPrint.io for Duet]
- GCode terminal [not yet implemented by SimplyPrint.io for Duet]
- Receive messages from Printer in SimplyPrint.io [not yet implemented by SimplyPrint.io for Duet]


------------
Installation
------------
Open an SSH session to your SimplyPrint-connected device, such as a Raspberry Pi 4B.

.. code-block:: sh

    source <(curl -sSL https://raw.githubusercontent.com/simplyprint/integration-duet3d/refs/heads/main/install.sh)


-----------------------------
Content of DuetConnector.json
-----------------------------

The default password for the Duet is `reprap`, even if the web interface does not require a login.

.. code-block:: json

    [
        {
            "id": null,
            "token": null,
            "name": null,
            "in_setup": true,
            "short_id": null,
            "public_ip": null,
            "unique_id": "...",
            "duet_uri": "http://192.168.1.0",
            "duet_password": "reprap",
            "duet_unique_id": "YOUR_DUET_BOARD_ID",
            "duet_name": "YOUR_DUET_NAME",
            "webcam_uri": "http://URI_OF_WEBCAM_SNAPSHOT_ENDPOINT/webcam"
        }
    ]


-----------------------------------------------
Usage of Meltingplot Duet SimplyPrint Connector
-----------------------------------------------

- Create a configuration with `simplyprint-duet3d autodiscover`
- *Optional* Edit the configuration file `~/.config/SimplyPrint/DuetConnector.json`
- Start the duet simplyprint connector with `simplyprint-duet3d start` or `systemctl start simplyprint-duet3d.service`
- Add the printer via the SimplyPrint.io web interface.
