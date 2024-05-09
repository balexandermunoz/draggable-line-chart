from typing import Any, Callable

from ..utils import component, get_func_name, register
from ..utils.data_validation import validate_bezier_data
from ..utils.options import set_options


def bezier_chart(
    data: dict,
    t: float = 0.5,
    options: dict = None,
    on_change: Callable = None,
    args: tuple[Any, ...] = None,
    kwargs: dict[str, Any] = None,
    key: str = None
) -> dict:
    register(key, on_change, args, kwargs)
    validate_bezier_data(data, options)
    data = add_control_points(data, options, t)
    data, options = set_options(data, options)
    default_data = {k: v for k, v in data.items() if k not in options["fixed_lines"]}
    return component(id=get_func_name(), kw=locals(), default=default_data, key=key)


def add_control_points(data: dict, options: dict, t: float = 0.5) -> dict:
    for trace_name, trace_data in data.items():
        if len(trace_data['x']) < 2 or trace_name in options["fixed_lines"]:
            continue
        control_points = calculate_control_points(trace_data, t)
        # Add control points into data:
        for i, (x_c, y_c) in enumerate(control_points):
            trace_data['x'].insert(2 * i + 1, x_c)
            trace_data['y'].insert(2 * i + 1, y_c)
    return data


def calculate_control_points(trace_data: dict, t: float) -> list:
    control_points = []
    for i in range(len(trace_data['x']) - 1):
        x_0, y_0 = trace_data['x'][i], trace_data['y'][i]
        x_1, y_1 = trace_data['x'][i + 1], trace_data['y'][i + 1]
        if i == 0:
            x_c, y_c = calculate_first_control_point(x_0, y_0, x_1, y_1, t)
        else:
            x_c, y_c = calculate_next_control_point(x_c, y_c, x_0, y_0, x_1)
        control_points.append((x_c, y_c))
    return control_points


def calculate_first_control_point(
    x_0: float, y_0: float,
    x_1: float, y_1: float,
    t: float
) -> tuple[float, float]:
    x_c = x_0 + (x_1 - x_0) / 2
    y_c = y_0 + t * (y_1 - y_0)
    return x_c, y_c


def calculate_next_control_point(
    x_c: float, y_c: float,
    x_0: float, y_0: float,
    x_1: float
) -> tuple[float, float]:
    m = (y_0 - y_c) / (x_0 - x_c)
    b = y_0 - m * x_0
    x_cn = x_0 + (x_1 - x_0) / 2
    y_cn = m * x_cn + b
    return x_cn, y_cn
