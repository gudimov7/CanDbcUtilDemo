import can


class CanSender:

    def __init__(self, name: str, chanel: str, bitrate: int = 500000):
        self.name = name
        self.bus = can.Bus(interface='socketcan',
                           channel=chanel, bitrate=bitrate, fd=True)
        self.msg = None

    def send_msg(self, msg_id: int, msg: bytearray, is_ext: bool = False, is_fd: bool = False) -> str:
        self.msg = can.Message(
            arbitration_id=msg_id,
            data=msg,
            is_extended_id=is_ext,
            is_fd=is_fd
        )
        try:
            self.bus.send(self.msg)
            return f"Message sent on {self.bus.channel_info}\n{self.msg.data}"

        except can.CanError as e:
            return f"Message NOT sent {str(e)}"

    def close(self) -> None:
        self.bus.shutdown()
