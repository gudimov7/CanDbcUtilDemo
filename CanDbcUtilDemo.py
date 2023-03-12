import can
import cantools
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer
from common_ui import MessageValueBlock, NonDbcValueBlock
from can_receiver import CanReceiver
from can_sender import CanSender


class CanDbcUtilApp(App):
    TITLE: str = "Can Util App"
    CSS_PATH = "app_ui.css"
    BINDINGS = [
        ("q", "quit", "Quit")
    ]

    def __init__(self, dbc_file_path: str):
        super().__init__()
        self.channel = 'can0'
        self.can_sender = CanSender(name="sender", chanel=self.channel)
        self.can_monitor = CanReceiver(
            name="receiver", chanel=self.channel, callback=self.can_msg_received)
        self.db = None
        self.db_messages = None
        self.container = None

        self.load_db(dbc_file_path)

    def action_quit(self) -> None:
        self.can_sender.close()
        self.can_monitor.close()
        self.exit()

    def load_db(self, dbc_file_path):
        try:
            self.db = cantools.database.load_file(dbc_file_path)
            self.db_messages = self.db.messages
        except IOError as e:
            print(f"Could not open DataBase {str(e)}")

    def compose(self) -> ComposeResult:
        self.container = Container(id="container")

        if self.db_messages is not None:
            for msg in self.db_messages:
                message_widget = MessageValueBlock(
                    id=f"fr-{msg.frame_id}",
                    frame_name=msg.name,
                    frame_id=msg.frame_id,
                    signals=msg.signals,
                    callback=self.can_send_frame)

                self.container.mount(message_widget)

        yield Header()
        yield self.container
        yield Footer()

    def rcv_msg_in_db(self, msg_id: int) -> bool:
        for msg in self.db_messages:
            if msg.frame_id == msg_id:
                return True
        return False

    def can_msg_received(self, msg: can.Message):
        msg_id = msg.arbitration_id
        data = msg.data

        if self.rcv_msg_in_db(msg_id):
            try:
                frame_map = self.db.decode_message(msg_id, data)
                self.container.get_child_by_id(
                    f"fr-{msg_id}").update_signals(frame_map)
            except can.CanError as e:
                print(f"Can Decode error {str(e)}")

    def can_send_frame(self, msg_name: int, frame_map: dict[str, any]) -> None:
        if msg_name is not None:
            frame_msg = self.db.get_message_by_name(msg_name)
            msg_id = frame_msg.frame_id
            data: bytearray = None
            if frame_map is not None:
                try:
                    data = frame_msg.encode(frame_map)
                except cantools.EncodeError as e:
                    print(f"Can Encode error {str(e)}")

            self.can_sender.send_msg(
                msg_id=msg_id, msg=data, is_ext=frame_msg.is_extended_frame, is_fd=frame_msg.is_fd)


if __name__ == "__main__":
    dbc_path = 'db/demo.dbc'
    app = CanDbcUtilApp(dbc_path)
    app.run()
