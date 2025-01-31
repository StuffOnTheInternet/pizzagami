from collections import Counter
from itertools import chain
from pathlib import Path

type Store = str
type Name = str
type Ingredient = str
type Ingredients = tuple[Ingredient, ...]

def main():
    stores: dict[Store, dict[Ingredients, Name]] = {}
    ingr_counter = Counter()
    for p in Path("pizzas").iterdir():
        store = p.name
        stores[store] = {}
        with open(p) as f:
            for pizza in f.read().splitlines():
                if ":" in pizza:
                    name, ingr = pizza.split(":")
                    name = name.strip()
                    ingr = tuple(sorted([i.strip() for i in ingr.strip().split(",")]))
                else:
                    name = pizza.strip()
                    ingr = tuple()
                stores[store][ingr] = name
                for i in ingr:
                    ingr_counter[i] += 1
    all_ingr: set[Ingredient] = set()
    all_pizzas: set[Ingredients] = set()
    for pizzas in stores.values():
        for ingr, name in pizzas.items():
            all_ingr |= set(ingr)
            all_pizzas.add(ingr)

    name_by_ingr: dict[Ingredients, tuple[Store, Name]] = dict() # { ingr => (store, name) }
    for store, pizzas in stores.items():
        for ingr, name in pizzas.items():
            if ingr in name_by_ingr:
                name_by_ingr[ingr].append((store, name))
            else:
                name_by_ingr[ingr] = [(store, name)]

    top_ten_ingr = {ingr for ingr, _ in ingr_counter.most_common(10)}

    # report unique pizzas for each store
    for store, pizzas in stores.items():
        print("")
        pizzagami = []
        for ingr, name in sorted(pizzas.items(), key=lambda kv: kv[1]):
            is_pizzagami = len(name_by_ingr[ingr]) == 1
            if is_pizzagami:
                pizzagami.append((name, ingr, all(i in top_ten_ingr for i in ingr)))
        if pizzagami:
            total_ingr_common_pizzagami = sum(1 for gami in pizzagami if gami[2])
            print("{}: {} pizzagami!".format(store, len(pizzagami)) + " (out of {}".format(len(pizzas)) + " total)")
            if total_ingr_common_pizzagami:
                print("...{} ingrdient-common pizzagami!".format(total_ingr_common_pizzagami))
            for name, ingr, is_common in pizzagami:
                print("  {} ({})".format(name, ", ".join(ingr)))
                if is_common:
                    print("    ingredient-common pizzagami!")
        else:
            print("{}: no pizzagami :(".format(store))

    print("all ingredients:")
    for ingr in sorted(all_ingr):
        print("  ", ingr)
    print("number of ingredients: ", len(all_ingr))
    print("number of possible pizzas: 2**{} = {}".format(len(all_ingr), 2**len(all_ingr)))
    print("number of seen pizzas: {} ({:.0E} %)".format(len(all_pizzas), 100 * len(all_pizzas) / (2**len(all_ingr))))
    print("10 most common ingredients: ", ingr_counter.most_common(10))

main()
