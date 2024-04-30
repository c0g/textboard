import os
import re
import scipy

def get_terminal_width():
    return os.get_terminal_size().columns

def target_length(length):
    return min(length or get_terminal_width(), get_terminal_width())

def text(text, bold=False, length=None):
    if bold:
        return [f'\x1b[1m{text}\x1b[0m']
    return [text]

def resample(values, length):
    return scipy.signal.resample(values, length)

boxes = "▁▂▃▄▅▆▇█"
def sparklines(values, num_lines: int=2) -> list[str]:
    # shift values to be positive
    mn = min(values)
    values = [v - mn for v in values]
    mx = max(values)
    mn = 0
    segment_per_box = (mx - mn) / (num_lines * len(boxes))
    lines = []
    for i in range(num_lines - 1, -1, -1):
        line = ''
        for v in values:
            value = v - i * segment_per_box * len(boxes)
            if value < 0:
                line += ' '
            else:
                box_index = int(value / segment_per_box)
                # clamp to top box if we're just providing something for a higher box to sit on
                box_index = min(len(boxes) - 1, box_index)
                line += boxes[box_index]
        lines.append(line)
    return lines

def plot(values, height: int=4, title=None, length=None) -> list[str]:
    length = target_length(length)
    if length < len(values):
        values = resample(values, length)
    lines = sparklines(values, num_lines=height)
    if title:
        return text(title, bold=True, length=length) + lines
    return lines

def hist1d(values, height, labels=None, title=None, length=None) -> list[str]:
    length = target_length(length)
    lines = sparklines(values, num_lines=height)
    if title:
        lines = text(title, bold=True) + lines
    if labels:
        lines.append(''.join(labels))
    return lines

def progress(step, total, length=None):
    text = f"{step}/{total}"
    length = target_length(length)  - len(text) - 2
    filled_parts = int(step / total * length)
    bar = '▊' * (filled_parts - 1) + '█' + '▕' * (length - filled_parts)
    return [f"{bar} {step}/{total}"]

def split(template):
    split_regex = r"(\w+\(.*?\))\s*"
    parts = []
    for line in template.split('\n'):
        parts.append(re.findall(split_regex, line))
    return parts

def no_terminal_crap_length(string):
    return len(re.sub(r'\x1b\[[0-9;]*m', '', string))

def render_template(template, args):
    parts = split(template)
    terminal_width = get_terminal_width() - 1 # :shrug emoji:
    rendered_lines = []
    for part in parts:
        if not part:
            rendered_lines.append([''])
            continue

        # Render
        lines = []
        target_length = terminal_width // len(part)
        for func_call in part:
            func_call = func_call.rstrip(')') + f', length={target_length})'
            lines.append(eval(func_call, globals(), args))
        lines = list(map(list, zip(*lines)))

        # Check if horizontally stacked blocks are actually too long
        need_flatten = False
        for line in lines:
            if sum(no_terminal_crap_length(l) for l in line) > terminal_width:
                need_flatten = True
                break
        if need_flatten:
            lines = list(map(list, zip(*lines)))
            flat_lines = []
            for line in lines:
                flat_lines.extend([l] for l in line)
            lines = flat_lines

        # Padding
        column_width = [0 for _ in lines[0]]
        for line in lines:
            for i, column in enumerate(line):
                column_width[i] = max(column_width[i],
                                      no_terminal_crap_length(column))
        padded_lines = []
        for line in lines:
            padded_line = []
            for i, column in enumerate(line):
                padded_line.append(column + ' ' * (column_width[i] - no_terminal_crap_length(column)))
            padded_lines.append(padded_line)
        lines = padded_lines

        rendered_lines.extend(lines)
    return rendered_lines

class TextBoard:
    def __init__(self, template):
        self.template = template
        self.args = {}
        self.did_render_once = False

    def print(self,
              args,
              extra_lines = [],
              cleanup_previous = True):
        if self.did_render_once and cleanup_previous:
            for _ in range(self.last_length):
                print('\033[F\033[K', end='')
        self.args.update(args)
        lines = render_template(self.template, self.args)
        for line in lines + extra_lines:
            print(' '.join(line))
        self.did_render_once = True
        self.last_length = len(lines)