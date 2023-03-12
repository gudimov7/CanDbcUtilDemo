import can
import cantools


def runner() -> None:
    bus = can.Bus(interface='socketcan', channel='vcan0', bitrate=500000, receive_own_messages=True, fd=True)
    db = cantools.database.load_file('db/demo.dbc')

    for msg in db.messages:
        print(f"{msg.name}")
        print(f"{msg.frame_id}")
        print(f"{msg.signal_tree}")

    bus.shutdown()


if __name__ == "__main__":
    runner()
