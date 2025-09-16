# This file is been placed in the Public Domain.


"available types"


from nixbot.persist import types


def ls(event):
    tps = types()
    if tps:
        event.reply(",".join([x.split(".")[-1].lower() for x in tps]))
    else:
        event.reply("no data yet.")
