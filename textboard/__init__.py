"""A thing to make text-based training loggers"""

__version__ = "0.1.3"

import ast
import os
import re
import numpy as np
import scipy
import scipy.interpolate
import scipy.signal


def get_terminal_width():
    if "COLUMNS" in os.environ:
        return int(os.environ["COLUMNS"])
    return os.get_terminal_size().columns


def target_length(length):
    return min(length or get_terminal_width(), get_terminal_width())


def _bold(text):
    return f"\x1b[1m{text}\x1b[0m"

def text(text, bold=False, length=None):
    if bold:
        return [_bold(text)]
    return [text]


def resample(values, length):
    x = np.arange(len(values))
    return np.interp(np.linspace(0, len(values) - 1, length), x, values).tolist()
    # f = scipy.interpolate.interp1d(x, values, kind='linear')
    # new_x = np.linspace(0, len(values)-1, length, endpoint=False)
    # return f(new_x).tolist()

boxes = "▁▂▃▄▅▆▇█"

def format_scientific(n):
    """
    Format a number using scientific notation with one significant figure
    if it would be shorter than printing the number itself.
    """
    if n == 0:
        return "0"
    elif abs(n) < 1e-3 or abs(n) > 1e3:
        return "{:.0e}".format(n)
    else:
        return '{:.1f}'.format(n)


def sparklines(values, num_lines=2, show_vals=False):
    mn = min(values)

    mn_txt = format_scientific(mn)
    mx_txt = format_scientific(max(values))
    
    # shift values to be positive
    values = [v - mn for v in values]
    mx = max(values)
    val_offset = max(len(mn_txt), len(mx_txt))
    mn = 0
    segment_per_box = (mx - mn) / (num_lines * len(boxes))
    if show_vals:
        values = resample(values, len(values) - val_offset - 1)
    if segment_per_box == 0:
        return ["_" * len(values)] * num_lines
    lines = []
    for i in range(num_lines - 1, -1, -1):
        line = ''
        for v in values:
            value = v - i * segment_per_box * len(boxes)
            if value < 0:
                line += " "
            else:
                box_index = int(value / segment_per_box)
                # clamp to top box if we're just providing something for a higher box to sit on
                box_index = min(len(boxes) - 1, box_index)
                line += boxes[box_index]
        if show_vals:
            if i == num_lines - 1:
                line += mx_txt + " " * (val_offset - len(mx_txt)) + " "
            elif i == 0:
                line += mn_txt + " " * (val_offset - len(mn_txt)) + " "
            else:
                line += " " * val_offset + " "
        lines.append(line)
    return lines


def plot(values=None, height=4, title=None, length=None, show_vals=False):
    length = target_length(length)
    if values is None:
        lines = [" " * length] * height
    else:
        values = resample(values, length)
        lines = sparklines(values, num_lines=height, show_vals=show_vals)
    if title:
        return text(title, bold=True, length=length) + lines
    return lines


def hist1d(values=None, height=4, labels=None, title=None, length=None):
    length = target_length(length)
    if values is None:
        lines = [" " * length] * height
    else:
        lines = sparklines(values, num_lines=height)
    if title:
        lines = text(title, bold=True) + lines
    if labels:
        lines.append("".join(labels))
    return lines


def progress(step, total=None, length=None, choo_choo=False, bold=False):
    if step is None:
        step = "?"
    if total is None:
        total = "?"
    text = f"{step}/{total}"
    train = [r"____        ",
             r"|DD|____T_  ",
             r"|_ |______|<",
             r"@-@-@---oo\ "]
    if choo_choo:
        length = target_length(length) - len(text)
        bar_length = int(step / total * length)
        lines = []
        for i in range(4):
            if bar_length == 0:
                train_part = ''
            else:
                train_part = train[i][-bar_length:]
            if len(train_part) < bar_length:
                train_part = " " * (bar_length - len(train_part)) + train_part
            if i < 3:
                train_part += " " * (length - len(train_part)) + " " * len(text)
            else:
                train_part += " " * (length - len(train_part)) + text
            lines.append(train_part)
        if bold:
            return [_bold(l) for l in lines]
        return lines
    else:
        length = target_length(length) - len(text)
        filled_parts = int(step / total * length)
        bar = "▊" * (filled_parts - 1) + "█" + "▕" * (length - filled_parts)
        if bold:
            return [_bold(f"{bar} {step}/{total}")]
        return [f"{bar} {step}/{total}"]


def split(template):
    split_regex = r"(\w+\(.*?\))\s*"
    parts = []
    for line in template.split("\n"):
        parts.append(re.findall(split_regex, line))
    return parts


def no_terminal_crap_length(string):
    return len(re.sub(r"\x1b\[[0-9;]*m", "", string))


def render_template(template, args):
    parts = split(template)
    terminal_width = get_terminal_width() - 1  # :shrug emoji:
    rendered_lines = []
    for part in parts:
        if not part:
            rendered_lines.append([""])
            continue

        # Render
        lines = []
        target_length = terminal_width // len(part)
        for func_call in part:
            tree = ast.parse(func_call)
            call = tree.body[0].value
            no_val_args = [arg.id for arg in call.args if isinstance(arg, ast.Name) and arg.id not in args]
            local_args = args.copy()
            local_args.update({a: None for a in no_val_args})
            func_call = func_call.rstrip(")") + f", length={target_length})"
            lines.append(eval(func_call, globals(), local_args))
        lines = list(map(list, zip(*lines)))

        # Check if horizontally stacked blocks are actually too long
        need_flatten = False
        for line in lines:
            if sum(no_terminal_crap_length(part) for part in line) > terminal_width:
                need_flatten = True
                break
        if need_flatten:
            lines = list(map(list, zip(*lines)))
            flat_lines = []
            for line in lines:
                flat_lines.extend([part] for part in line)
            lines = flat_lines

        # Padding
        column_width = [0 for _ in lines[0]]
        for line in lines:
            for i, column in enumerate(line):
                column_width[i] = max(column_width[i], no_terminal_crap_length(column))
        padded_lines = []
        for line in lines:
            padded_line = []
            for i, column in enumerate(line):
                padded_line.append(
                    column + " " * (column_width[i] - no_terminal_crap_length(column))
                )
            padded_lines.append(padded_line)
        lines = padded_lines

        rendered_lines.extend(lines)
    return rendered_lines


class TextBoard:
    def __init__(self, template):
        self.template = template
        self.args = {}
        self.did_render_once = False

    def render(self, args, extra_lines=[]):
        self.args.update(args)
        return render_template(self.template, self.args) + extra_lines
    
    def append(self, key,  value):
        self.args.setdefault(key, []).append(value)

    def set(self, key, value):
        self.args[key] = value

    def wrap(self, iterable):
        if isinstance(iterable, range):
            total = (iterable.stop - iterable.start) / iterable.step
        elif hasattr(iterable, "__len__"):
            total = len(iterable)
        else:
            total = None
        for i, item in enumerate(iterable):
            self.print({'step': i, 'total': total})
            yield item

    def print(self, args={}, extra_lines=[], cleanup_previous=True):
        if self.did_render_once and cleanup_previous:
            for _ in range(self.last_length):
                print("\033[F\033[K", end="")
        lines = self.render(args, extra_lines)
        for line in lines + extra_lines:
            print(" ".join(line))
        self.did_render_once = True
        self.last_length = len(lines)
