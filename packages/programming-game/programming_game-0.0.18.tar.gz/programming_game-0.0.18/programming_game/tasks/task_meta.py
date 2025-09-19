class TaskMeta(type):
    def __new__(cls, name, bases, attrs):
        _on_tick_method = []
        _on_event_method = []

        for _attr_name, attr_value in attrs.items():
            if getattr(attr_value, "_on_tick_method", False):
                _on_tick_method.append(attr_value)
                attr_value._last_run = 0
                if interval := getattr(attr_value, "interval", None):
                    attr_value._interval = interval
            if getattr(attr_value, "_on_event_method", False):
                _on_event_method.append((attr_value, getattr(attr_value, "_event_filter", None)))

        attrs["_on_tick_method"] = _on_tick_method
        attrs["_on_event_method"] = _on_event_method

        return super().__new__(cls, name, bases, attrs)
