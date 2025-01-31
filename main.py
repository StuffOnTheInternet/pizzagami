from itertools import chain
from pathlib import Path

type Store = str
type Name = str
type Ingredient = str
type Ingredients = tuple[Ingredient, ...]

def main():
    stores: dict[Store, dict[Ingredients, Name]] = {}
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

    # report unique pizzas for each store
    for store, pizzas in stores.items():
        print("")
        pizzagamis = []
        for ingr, name in sorted(pizzas.items(), key=lambda kv: kv[1]):
            if len(name_by_ingr[ingr]) == 1:
                pizzagamis.append((name, ingr))
        if pizzagamis:
            print("{}: {} pizzagami!".format(store, len(pizzagamis)) + " (out of {}".format(len(pizzas)) + " total)")
            for name, ingr in pizzagamis:
                print("  {} ({})".format(name, ", ".join(ingr)))
        else:
            print("{}: no pizzagami :(".format(store))

    print("all ingredients:")
    for ingr in sorted(all_ingr):
        print("  ", ingr)
    print("number of ingredients: ", len(all_ingr))
    print("number of possible pizzas: 2**{} = {}".format(len(all_ingr), 2**len(all_ingr)))
    print("number of seen pizzas: {} ({:.0E} %)".format(len(all_pizzas), 100 * len(all_pizzas) / (2**len(all_ingr))))
main()
