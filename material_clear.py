from material_model import *


def clear_wordchar():
    total = 0
    with open('wordlist.txt', 'w') as f:
        for wc in list(Wordchar.select().order_by(Wordchar.counter.desc())):
            total += 1
            print(total, wc.wordchar)
            if len(wc.explains) == 0:
                wc.delete_instance()
                print("removed")
                continue

            wc.counter = 0
            wc.save()
            f.write(wc.wordchar)
            f.write('\n')


if __name__ == '__main__':
    with material.transaction():
        clear_wordchar()
