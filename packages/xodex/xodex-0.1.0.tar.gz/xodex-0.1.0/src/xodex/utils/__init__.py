class EventBus:
    _subscribers = {}

    @classmethod
    def subscribe(cls, event_type, handler):
        cls._subscribers.setdefault(event_type, []).append(handler)

    @classmethod
    def emit(cls, event_type, *args, **kwargs):
        for handler in cls._subscribers.get(event_type, []):
            handler(*args, **kwargs)
