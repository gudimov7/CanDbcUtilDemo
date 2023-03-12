from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Static


class NonDbcValueBlock(Static):
    def __init__(self, id: str, frame_name: str, frame_id: int, data: bytearray, callback: callable = None):
        super().__init__(id=id)
        self.frame_name = frame_name
        self.frame_id = frame_id
        self.data = data
        self.callback = callback
        self.msg_container = None
        self.signals_container = None

    def compose(self) -> ComposeResult:
        self.msg_container = Container(id="msg-container")

        signal_container = Container(id="header-container")
        frame_name_lbl = Static(self.frame_name, id="frame-name")
        frame_id_lbl = Static(f"{self.frame_id :08}", id="frame-id")
        data_str = ''.join('{:02X} '.format(x) for x in self.data)
        data_lbl = Static(f"[ {data_str}]", id="data-lbl")

        signal_container.mount(frame_name_lbl, frame_id_lbl, data_lbl)
        self.msg_container.mount(signal_container)
        yield self.msg_container


class MessageValueBlock(Static):
    def __init__(self, id: str, frame_name: str, frame_id: int, signals: dict[str, any], callback: callable = None):
        super().__init__(id=id)
        self.frame_name = frame_name
        self.frame_id = frame_id
        self.signals = signals
        self.callback = callback
        self.msg_container = None
        self.signals_container = None

    def compose(self) -> ComposeResult:
        self.msg_container = Container(id="msg-container")

        header_container = Container(id="header-container")
        frame_name_lbl = Static(self.frame_name, id="frame-name")
        frame_id_lbl = Static(f"{self.frame_id :08}", id="frame-id")
        send_btn = Button("send", id="send-btn", variant="success")

        header_container.mount(frame_name_lbl, frame_id_lbl, send_btn)

        self.signals_container = Container(id="signals-container")
        for signal in self.signals:
            self.signals_container.mount(
                SignalValueBlock(id=f"sig-{signal.name}",
                                 signal_name=signal.name,
                                 min_value=signal.minimum,
                                 max_value=signal.maximum))

        self.msg_container.mount(header_container, self.signals_container)

        yield self.msg_container

    def update_signals(self, map: dict[str, any]) -> None:
        for key in map:
            self.signals_container.get_child_by_id(
                f"sig-{key}").set_value(map[key])

    def get_frame_map(self) -> dict[str, any]:
        current_map: dict[str, any] = {}
        for sig in self.signals_container.children:
            # [k, v] = sig.get_values()
            v = sig.get_values()
            # current_map[k] = v
            current_map.update(v)

        return current_map

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        assert button_id is not None
        if button_id == "send-btn":
            frame_map = self.get_frame_map()
            if self.callback:
                self.callback(self.frame_name, frame_map)


class SignalValueBlock(Static):
    def __init__(self, id: str, signal_name: str, value: float = 0, min_value: int = 0, max_value: int = 100, allow_exceed: bool = True):
        super().__init__(id=id)
        self.signal_name = signal_name
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.allow_exceed = allow_exceed
        self.signal_value = Static(
            f"{self.value}", id="signal-value", classes="sig-child")

        if min_value is None:
            self.min_value = 0

        if max_value is None:
            self.max_value = 1000

        # boolean values dont exceed
        if self.min_value == 0 and self.max_value == 1:
            self.allow_exceed = False

    def compose(self) -> ComposeResult:
        yield Static(self.signal_name, id="signal-label")

        val_container = Container(id="val-container")
        btn_dwn = Button("-", id="signal-minus-btn",
                         variant="success", classes="sig-child")
        btn_up = Button("+",  id="signal-plus-btn",
                        variant="success", classes="sig-child")

        val_container.mount(btn_dwn, self.signal_value, btn_up)

        yield val_container

    def set_value(self, n: any):
        self.value = n
        self.signal_value.update(f"{self.value}")
        return self

    def get_values(self) -> dict[str, any]:
        return {self.signal_name: self.value}

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        assert button_id is not None

        # update signal value
        if button_id == "signal-plus-btn":
            if (self.value < self.max_value) or self.allow_exceed:
                self.value += 1

        if button_id == "signal-minus-btn":
            if (self.value > self.min_value) or self.allow_exceed:
                self.value -= 1

        # set value background color
        if self.min_value <= self.value <= self.max_value:
            self.signal_value.styles.background = None
        elif self.value > self.max_value:
            self.signal_value.styles.background = 'red'
        else:
            self.signal_value.styles.background = 'blue'

        self.set_value(self.value)
