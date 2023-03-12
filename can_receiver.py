import can


class CanReceiver:

    def __init__(self, name: str, chanel: str, bitrate: int = 500000, callback=None):
        self.name = name
        self.bus = can.Bus(interface='socketcan',
                           channel=chanel,
                           bitrate=bitrate,
                           fd=True)
        self.print_listener = can.Printer()
        listener = can.BufferedReader()
        listener.on_message_received = callback
        self.notifier = can.Notifier(self.bus, [self.print_listener, listener])

    def set_callback(self, callback):
        listener = can.BufferedReader()
        listener.on_message_received = callback
        self.notifier.add_listener(listener)

    def close(self) -> None:
        self.print_listener.stop()
        self.notifier.stop()
        self.bus.shutdown()
