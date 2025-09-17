import datetime
import functools
import json
import math
import random
import re
import base64
import uuid

from pyjexl.jexl import JEXL


class ExtendedGrammar:
    def __init__(self, jexl: JEXL):
        self.jexl = jexl

    """String functions"""

    @staticmethod
    def to_string(value, prettify=False):
        if isinstance(value, (dict, list)):
            value = (
                json.dumps(value)
                if prettify
                else json.dumps(value, separators=(",", ":"))
            )
        return str(value)

    @staticmethod
    def to_json(value):
        return json.loads(value)

    @staticmethod
    def length(value):
        return len(value)

    @staticmethod
    def substring(value: any, start: int, length: int = None):
        if not isinstance(value, str):
            value = ExtendedGrammar.to_string(value)
        fin = start + length if length else len(value)
        return value[start:fin]

    @staticmethod
    def substring_before(value: any, chars: any):
        if not isinstance(value, str):
            value = ExtendedGrammar.to_string(value)
        if not isinstance(chars, str):
            chars = ExtendedGrammar.to_string(chars)
        index = value.find(chars)
        if index == -1:
            return value
        return value[:index]

    @staticmethod
    def substring_after(value: any, chars: any):
        if not isinstance(value, str):
            value = ExtendedGrammar.to_string(value)
        if not isinstance(chars, str):
            chars = ExtendedGrammar.to_string(chars)
        index = value.find(chars)
        if index == -1:
            return ""
        ini = index + len(chars)
        return value[ini:]

    @staticmethod
    def uppercase(value):
        return ExtendedGrammar.to_string(value).upper()

    @staticmethod
    def lowercase(value):
        return ExtendedGrammar.to_string(value).lower()

    @staticmethod
    def camel_case(value):
        value = ExtendedGrammar.to_string(value)
        value = re.sub(
            r"(?<!^)(?=[A-Z])|[`~!@#%^&*()|+\\\-=?;:'.,\s_']+", "_", value
        ).lower()
        parts = value.split("_")
        camel_case_value = parts[0] + "".join(x.title() for x in parts[1:])
        return camel_case_value

    @staticmethod
    def pascal_case(value):
        value = ExtendedGrammar.to_string(value)
        value = re.sub(
            r"(?<!^)(?=[A-Z])|[`~!@#%^&*()|+\\\-=?;:'.,\s_']+", "_", value
        ).lower()
        parts = value.split("_")
        camel_case_value = "".join(x.title() for x in parts)
        return camel_case_value

    @staticmethod
    def trim(value, trim_char=" "):
        return ExtendedGrammar.to_string(value).strip(trim_char)

    @staticmethod
    def pad(value, width, char=" "):
        value = ExtendedGrammar.to_string(value)
        if not isinstance(char, str):
            char = str(char)
        if width > 0:
            return value.ljust(width, char)
        else:
            return value.rjust(-width, char)

    @staticmethod
    def contains(value, search):
        return search in value

    @staticmethod
    def starts_with(value, search):
        value = ExtendedGrammar.to_string(value)
        return value.startswith(search)

    @staticmethod
    def ends_with(value, search):
        value = ExtendedGrammar.to_string(value)
        return value.endswith(search)

    @staticmethod
    def split(value: str, sep=","):
        return value.split(sep)

    @staticmethod
    def join(value, sep=","):
        return sep.join(value)

    @staticmethod
    def replace(value: str, search: str, replace=""):
        return value.replace(search, replace)

    @staticmethod
    def base64_encode(input: str):
        return base64.b64encode(input.encode("utf-8")).decode("utf-8")

    @staticmethod
    def base64_decode(input: str):
        return base64.b64decode(input.encode("utf-8")).decode("utf-8")

    @staticmethod
    def form_url_encoded(value):
        # Only works for dicts
        if isinstance(value, dict):
            return "&".join(f"{k}={v}" for k, v in value.items())
        return str(value)

    """Number functions"""

    @staticmethod
    def to_number(value):
        return float(value)

    @staticmethod
    def to_int(value):
        if isinstance(value, str):
            value = value.strip('"')
        return int(float(value))

    @staticmethod
    def abs(value):
        return abs(value)

    @staticmethod
    def floor(value):
        return math.floor(value)

    @staticmethod
    def ceil(value):
        return math.ceil(value)

    @staticmethod
    def round(value, precision=0):
        return round(value, precision)

    @staticmethod
    def power(value, power=2):
        return math.pow(value, power)

    @staticmethod
    def sqrt(value):
        return math.sqrt(value)

    @staticmethod
    def random():
        return random.random()

    @staticmethod
    def format_number(value, format="0,0.000"):
        # Determine if we need to include commas
        if "," in format:
            format = format.replace(",", "")
            formatted_value = "{:,.{precision}f}".format(
                value, precision=len(format.split(".")[1])
            )
        else:
            formatted_value = "{:.{precision}f}".format(
                value, precision=len(format.split(".")[1])
            )

        return formatted_value

    @staticmethod
    def format_base(value, base=10):
        if base == 10:
            return str(value)
        elif base == 16:
            return hex(value)[2:]  # Remove the '0x' prefix
        elif base == 8:
            return oct(value)[2:]  # Remove the '0o' prefix
        elif base == 2:
            return bin(value)[2:]  # Remove the '0b' prefix
        else:
            # Custom implementation for other bases
            digits = "0123456789abcdefghijklmnopqrstuvwxyz"
            if base > len(digits):
                raise ValueError("Base too large")
            result = ""
            while value > 0:
                result = digits[value % base] + result
                value //= base
            return result or "0"

    @staticmethod
    def format_integer(value, format="0000000"):
        # Convert the value to an integer
        integer_value = int(float(value))

        # Format the integer value according to the specified format
        formatted_value = f"{integer_value:0{len(format)}d}"

        return formatted_value

    @staticmethod
    def sum(value, *rest):
        if not isinstance(value, list):
            value = [value]
        rest = [v for v in rest]
        if len(rest) > 0 and isinstance(rest[0], list):
            rest = [v for va in rest for v in va]
        values = value + rest
        return sum(values)

    @staticmethod
    def max(value, *rest):
        if not isinstance(value, list):
            value = [value]
        rest = [v for v in rest]
        if len(rest) > 0 and isinstance(rest[0], list):
            rest = [v for va in rest for v in va]
        values = value + rest
        return max(values)

    @staticmethod
    def min(value, *rest):
        if not isinstance(value, list):
            value = [value]
        rest = [v for v in rest]
        if len(rest) > 0 and isinstance(rest[0], list):
            rest = [v for va in rest for v in va]
        values = value + rest
        return min(values)

    @staticmethod
    def avg(value, *rest):
        if not isinstance(value, list):
            value = [value]
        rest = [v for v in rest]
        if len(rest) > 0 and isinstance(rest[0], list):
            rest = [v for va in rest for v in va]
        values = value + rest
        return sum(values) / len(values)

    @staticmethod
    def to_boolean(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value != 0
        if isinstance(value, str):
            value = value.strip().lower()
            if value == "true" or value == "1":
                return True
            if value == "false" or value == "0":
                return False
            return None
        return bool(value)

    @staticmethod
    def not_(value):
        return not ExtendedGrammar.to_boolean(value)

    """ Array functions """

    @staticmethod
    def array_append(value, *rest):
        if not isinstance(value, list):
            value = [value]
        rest = [v for v in rest]
        if len(rest) > 0 and isinstance(rest[0], list):
            rest = [v for va in rest for v in va]
        return value + rest

    @staticmethod
    def array_reverse(value, *rest):
        if not isinstance(value, list):
            value = [value]
        rest = [v for v in rest]
        if len(rest) > 0 and isinstance(rest[0], list):
            rest = [v for va in rest for v in va]
        return (value + rest)[::-1]

    @staticmethod
    def array_shuffle(value):
        if not isinstance(value, list):
            value = [value]
        random.shuffle(value)
        return value

    @staticmethod
    def array_sort(value, reverse=False):
        if not isinstance(value, list):
            value = [value]
        return sorted(value, reverse=reverse)

    @staticmethod
    def array_distinct(value):
        if not isinstance(value, list):
            value = [value]
        return list(set(value))

    @staticmethod
    def array_to_object(input, val=None):
        if isinstance(input, str):
            return {input: val}
        if not isinstance(input, list):
            return {}
        return functools.reduce(
            lambda acc, kv: (
                acc.update({kv[0]: kv[1]}) or acc
                if isinstance(kv, list) and len(kv) == 2
                else acc.update({kv: val}) or acc
            ),
            input,
            {},
        )

    @staticmethod
    def array_mapfield(input, field):
        if not isinstance(input, list):
            return []
        return [item[field] for item in input]

    def array_map(self, input, expression):
        if not isinstance(input, list):
            return None
        expr = self.jexl.parse(expression)
        return [
            expr.eval({"value": value, "index": index, "array": input})
            for index, value in enumerate(input)
        ]

    def array_any(self, input, expression):
        if not isinstance(input, list):
            return False
        expr = self.jexl.parse(expression)
        return any(
            [
                expr.eval({"value": value, "index": index, "array": input})
                for index, value in enumerate(input)
            ]
        )

    def array_every(self, input, expression):
        if not isinstance(input, list):
            return False
        expr = self.jexl.parse(expression)
        return all(
            [
                expr.eval({"value": value, "index": index, "array": input})
                for index, value in enumerate(input)
            ]
        )

    def array_filter(self, input, expression):
        if not isinstance(input, list):
            return []
        expr = self.jexl.parse(expression)
        return [
            value
            for index, value in enumerate(input)
            if expr.eval({"value": value, "index": index, "array": input})
        ]

    def array_find(self, input, expression):
        if not isinstance(input, list):
            return None
        expr = self.jexl.parse(expression)
        return next(
            (
                value
                for index, value in enumerate(input)
                if expr.eval({"value": value, "index": index, "array": input})
            ),
            None,
        )

    def array_reduce(self, input, expression, initialValue=None):
        if not isinstance(input, list):
            return None
        expr = self.jexl.parse(expression)
        return functools.reduce(
            lambda acc, value: expr.eval({"accumulator": acc, "value": value}),
            input,
            initialValue,
        )

    """ Object functions """

    @staticmethod
    def object_keys(input):
        if isinstance(input, dict):
            return list(input.keys())
        return None

    @staticmethod
    def object_values(input):
        if isinstance(input, dict):
            return list(input.values())
        return None

    @staticmethod
    def object_entries(input):
        if isinstance(input, dict):
            return list(input.items())
        return None

    @staticmethod
    def object_merge(*args):
        result = {}
        for arg in args:
            if isinstance(arg, list):
                for obj in arg:
                    if isinstance(obj, dict):
                        result.update(obj)
            elif isinstance(arg, dict):
                result.update(arg)
        return result

    """ Date functions """

    @staticmethod
    def now():
        return datetime.datetime.isoformat(datetime.datetime.now())

    @staticmethod
    def millis():
        return datetime.datetime.now().timestamp() * 1000

    @staticmethod
    def to_datetime(value):
        return datetime.datetime.fromtimestamp(value / 1000).isoformat()

    @staticmethod
    def to_millis(value):
        return datetime.datetime.fromisoformat(value).timestamp() * 1000

    @staticmethod
    def datetime_add(input, unit, value):
        input_datetime = datetime.datetime.fromisoformat(input)
        if not str.endswith(unit, "s"):
            unit = unit + "s"
        if unit == "years":
            return input_datetime + datetime.timedelta(days=365 * value)
        if unit == "months":
            return input_datetime + datetime.timedelta(days=30 * value)
        if unit == "days":
            return input_datetime + datetime.timedelta(days=value)
        if unit == "hours":
            return input_datetime + datetime.timedelta(hours=value)
        if unit == "minutes":
            return input_datetime + datetime.timedelta(minutes=value)
        if unit == "seconds":
            return input_datetime + datetime.timedelta(seconds=value)
        if unit == "milliseconds":
            return input_datetime + datetime.timedelta(milliseconds=value)
        return None

    """ Misc """

    def _eval(self, input, expression):
        if not isinstance(expression, str) and isinstance(input, str):
            return self.jexl.evaluate(expression)
        if isinstance(input, dict) and isinstance(expression, str):
            return self.jexl.evaluate(expression, input)
        return None

    def uuid(self):
        return str(uuid.uuid4())
