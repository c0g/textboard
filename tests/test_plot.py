import os

import textboard as tb
import time

os.environ['COLUMNS'] = '80'

def test_bold():
    assert tb.text("Test", bold=True) == ["\x1b[1mTest\x1b[0m"]
    assert tb.text("Test", bold=False) == ["Test"]

def test_plot_values_none():
    template = "plot(values)"
    board = tb.TextBoard(template)
    lines = board.render({})
    assert [el == ' ' * 79 for el in lines]

def test_plot_values_none_with_title():
    template = "plot(values, title='Values')"
    board = tb.TextBoard(template)
    lines = board.render({})
    assert [tb.text("Values", bold=True)[0] + " " * 73] == lines[0]
    assert [el == ' ' * 79 for el in lines[1:]]

def test_choo_choo():
    template = "progress(step, total, choo_choo=True, bold=False)"
    board = tb.TextBoard(template)

    lines = board.render({"step": 0, "total": 100})
    assert lines == [
        [' ' * 79],
        [' ' * 79],
        [' ' * 79],
        [' ' * 74 + "0/100"],
    ]

    lines = board.render({"step": 4, "total": 79})
    assert lines == [
        [' ' * 79],
        ['_' + ' ' * 78],
        ['_|<' + ' ' * 76],
        ['o\\' + ' ' * 73 + "4/79"],
    ]

    lines = board.render({"step": 20, "total": 79})
    train = [r"____        ",
             r"|DD|____T_  ",
             r"|_ |______|<",
             r"@-@-@---oo\ "]
    assert lines == [
        [' ' * 6 + train[0] + ' ' * 61],
        [' ' * 6 + train[1] + ' ' * 61],
        [' ' * 6 + train[2] + ' ' * 61],
        [' ' * 6 + train[3] + ' ' * 56 + '20/79'],
    ]

def test_plot_not_none():
    template = "plot(values, height=4)"
    values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    board = tb.TextBoard(template)
    lines = board.render({"values": values})
    assert lines == [
        ['                                                           ▁▁▂▂▂▃▃▄▄▄▅▅▆▆▆▇▇███'],
        ['                                       ▁▁▁▂▂▃▃▃▄▄▅▅▅▆▆▇▇▇██████████████████████'],
        ['                    ▁▁▂▂▂▃▃▄▄▄▅▅▆▆▆▇▇██████████████████████████████████████████'],
        ['▁▁▁▂▂▃▃▃▄▄▅▅▅▆▆▇▇▇█████████████████████████████████████████████████████████████']
    ]

def test_plot_not_none_show_values():
    template = "plot(values, height=4, show_vals=True)"
    values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    board = tb.TextBoard(template)
    lines = board.render({"values": values})
    assert lines == [
        ['                                                        ▁▁▂▂▂▃▃▄▄▅▅▅▆▆▇▇███9.0 '],
        ['                                      ▁▁▂▂▃▃▄▄▄▅▅▆▆▇▇▇█████████████████████    '],
        ['                   ▁▁▂▂▂▃▃▄▄▅▅▅▆▆▇▇████████████████████████████████████████    '],
        ['▁▁▁▂▂▃▃▄▄▄▅▅▆▆▇▇▇██████████████████████████████████████████████████████████0   ']
    ]