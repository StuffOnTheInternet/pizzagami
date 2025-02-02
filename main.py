from collections import Counter
from pathlib import Path
from typing import Optional

type Store = str
type Name = str
type Ingredient = str
type Ingredients = tuple[Ingredient, ...]

ingr_common_limit = 10

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

    name_by_ingr: dict[Ingredients, tuple[Store, Name]] = dict()
    for store, pizzas in stores.items():
        for ingr, name in pizzas.items():
            if ingr in name_by_ingr:
                name_by_ingr[ingr].append((store, name))
            else:
                name_by_ingr[ingr] = [(store, name)]

    top_ten_ingr = [ingr for ingr, _ in ingr_counter.most_common(ingr_common_limit)]

    # report unique pizzas for each store
    ingr_common_pizzagami_per_n = {i: 0 for i in range(1, ingr_common_limit+1)}
    for store, pizzas in stores.items():
        print("")
        pizzagami: list[tuple[Name, Ingredients, Optional[int]]] = []

        for ingr, name in sorted(pizzas.items(), key=lambda kv: kv[1]):
            is_pizzagami = len(name_by_ingr[ingr]) == 1

            if is_pizzagami:
                is_ingr_common = all(i in top_ten_ingr for i in ingr)
                ingr_common_level = None
                if is_ingr_common:
                    ingr_common_level = max(top_ten_ingr.index(i) for i in ingr)
                    ingr_common_pizzagami_per_n[ingr_common_level] += 1
                pizzagami.append((name, ingr, ingr_common_level))

        if pizzagami:
            num_ingr_common_pizzagami = sum(1 for gami in pizzagami if gami[2] is not None)
            print("{}: {} pizzagami!".format(store, len(pizzagami)) + " (out of {}".format(len(pizzas)) + " total)")
            if num_ingr_common_pizzagami:
                print("...{} ingredient-common pizzagami".format(num_ingr_common_pizzagami))

            for name, ingr, common_ingr_level in pizzagami:
                print("  {} ({})".format(name, ", ".join(ingr)))
                if common_ingr_level is not None:
                    print("    {}-ingredient-common pizzagami".format(common_ingr_level))
        else:
            print("{}: no pizzagami :(".format(store))

    # print("all ingredients:")
    # for ingr in sorted(all_ingr):
    #     print("  ", ingr)
    print("number of ingredients: ", len(all_ingr))
    print("number of possible pizzas: 2**{} = {}".format(len(all_ingr), 2**len(all_ingr)))
    print("number of seen pizzas: {} ({:.0E} %)".format(len(all_pizzas), 100 * len(all_pizzas) / (2**len(all_ingr))))
    print("{} most common ingredients:".format(ingr_common_limit, ingr_counter.most_common(ingr_common_limit)))
    for i, (ingr, amount) in enumerate(ingr_counter.most_common(ingr_common_limit)):
        print("  {:>2}. ({:>3}) {}".format(i, amount, ingr))
    print("{} ingredient-common pizzagami".format(sum(ingr_common_pizzagami_per_n.values())))
    for level in ingr_common_pizzagami_per_n:
        amount = sum(v for k,v in ingr_common_pizzagami_per_n.items() if k <= level)
        print("  {:>2}-ingredient-common pizzagami: {}".format(level, amount))

main()
