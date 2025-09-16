class TraceDispatcher:
    def __init__(self):
        self._observers = []

    def register(self, observer):
        self._observers.append(observer)

    def notify(self, event_type, payload):
        for observer in self._observers:
            observer.on_event(event_type, payload)
