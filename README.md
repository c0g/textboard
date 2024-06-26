# Terminal based training progress looker atter

## wat

it makes nice graphs and stuff and prints them to the terminal for you

## why

* wandb once took 5 minutes to register a run
* tensorboard is slow and doens't find new runs automatically
* wandb once took down a training job several hours in because the server shat itself
* attempting to see trends by performing a running average of printed numbers in my head is surprisingly hard

## how

write a template

```python
template = """plot(loss, title="Loss", height=2) plot(score, title="Score", height=2)


text("Next letter probabilities", bold=True)
hist1d(probs[0], height=2, labels=letters) hist1d(probs[1], height=2, labels=letters) hist1d(probs[3], height=2, labels=letters)
hist1d(probs[3], height=2, labels=letters) hist1d(probs[4], height=2, labels=letters) hist1d(probs[5], height=2, labels=letters)

text("Progress", bold=True)
progress(step, total)"""
board = TextBoard(template)
```

then pass it things in your training loop and call print:

```python
args = {
    'loss': loss,
    'score': score,
    'probs': probs,
    'letters': string.ascii_lowercase,
    'step': 0,
    'total': 100
}

board = TextBoard(template)
board.print(args)
for i, el in data:
    rez = model(el)
    if i % 3 == 0:
        these_args['loss'] = rez['loss']
        these_args['score'] = rez['score']
        these_args['probs'] = rez['probs']
    these_args['step'] = i
    board.print(these_args)
    time.sleep(0.5)
```

and it will using the magic of eval it will print stuff like

```
Loss                                                  Score                                                
▆▅▄▄▃▂▁                          ▁▂▃▄▅▅▆▇▇████████▇▇▆ ▆▅▄▄▃▂▁                          ▁▂▃▄▅▅▆▇▇████████▇▇▆
████████▇▆▅▄▃▃▂▁▁▁▁▁▁▁▁▁▂▂▃▃▄▅▆▇█████████████████████ ████████▇▆▅▄▃▃▂▁▁▁▁▁▁▁▁▁▂▂▃▃▄▅▆▇█████████████████████


Next letter probabilities
              █                █                          █   ▃    ▁ ▃          
▇▂▁▂▁▃▂▁▂▂▄▂▂▁█▁▇▁▁▄▁▂▁▃▁▃ ▅▃▁▃█▂▁▂▁▅▁▆▁▁▂█▁▂▂▂▂▂▂▁▃▁ ▄▂▃▄█▁▂▁██▁▁▄█▇█▁▃▆▄▁▂▂▄▅▁
abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz
    █   ▃    ▁ ▃             ▅               █                   █              
▄▂▃▄█▁▂▁██▁▁▄█▇█▁▃▆▄▁▂▂▄▅▁ ▁▂█▁▃▅▂▃▅▁▂▁▂▁▁▁▁▅█▂▇▁▇▃▁▃ ▁▁▁▁▁▁▁▁▁▁▁█▁▂▁▁▁▁▁▂▁▁▁▁▁▁
abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz

Progress
▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕▕ 16/100
```

(you can see this beauty by running `python -m textboard`)