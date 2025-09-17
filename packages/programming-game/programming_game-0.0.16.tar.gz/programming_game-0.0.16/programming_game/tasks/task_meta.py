from collections import defaultdict


class TaskMeta(type):
    def __new__(cls, name, bases, attrs):
        _on_tick_method = []

        for _attr_name, attr_value in attrs.items():
            if getattr(attr_value, "_on_tick_method", False):
                _on_tick_method.append(attr_value)
                attr_value._last_run = 0
                if interval := getattr(attr_value, "interval", None):
                    attr_value._interval = interval

        attrs["_on_tick_method"] = _on_tick_method

        return super().__new__(cls, name, bases, attrs)
