from . import TextBoard

import torch
import time
import string

template = """plot(loss, title="Loss", height=2) plot(score, title="Score", height=2)


text("Next letter probabilities", bold=True)
hist1d(probs[0], height=2, labels=letters) hist1d(probs[1], height=2, labels=letters) hist1d(probs[3], height=2, labels=letters)
hist1d(probs[3], height=2, labels=letters) hist1d(probs[4], height=2, labels=letters) hist1d(probs[5], height=2, labels=letters)

text("Progress", bold=True)
progress(step, total)"""

letters = "abcdefghijklmnopqrstuvwxyz"
loss = torch.sin(torch.linspace(0, 2 * 3.14, 100)).numpy()
score = torch.cos(torch.linspace(0, 2 * 3.14, 100)).numpy()
logits = torch.randn(6, 26)
probs = torch.softmax(logits, dim=-1).numpy()
step = 10
total = 100

args = {
    "loss": loss,
    "score": score,
    "probs": probs,
    "letters": string.ascii_lowercase,
    "step": 0,
    "total": 100,
}

board = TextBoard(template)
board.print(args)
for i in range(0, 100):
    these_args = {}
    if i % 3 == 0:
        these_args["loss"] = torch.sin(i + torch.linspace(0, 2 * 3.14, 100)).numpy()
        these_args["score"] = torch.cos(i + torch.linspace(0, 2 * 3.14, 100)).numpy()
        these_args["probs"] = torch.softmax(torch.randn(6, 26), dim=-1).numpy()
    these_args["step"] = i
    board.print(these_args)
    time.sleep(0.5)
