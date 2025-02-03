from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterator, Optional

type Store = str
type Name = str
type Ingredient = str
type Pizza = tuple[Ingredient, ...]

ingr_common_limit = 127


class Input:
    result: dict[Store, dict[Pizza, Name]]

    def __init__(self, pizzadir):
        self.result = {}
        for p in Path(pizzadir).iterdir():
            store = p.name
            self.result[store] = {}
            with open(p) as f:
                for pizza in f.read().splitlines():
                    if ":" in pizza:
                        name, ingr = pizza.split(":")
                        name = name.strip()
                        ingr = tuple(
                            sorted([i.strip() for i in ingr.strip().split(",")])
                        )
                    else:
                        name = pizza.strip()
                        ingr = tuple()
                    self.result[store][ingr] = name

    def iter_pizzas(self) -> Iterator[tuple[Store, Pizza, Name]]:
        yield from (
            (store, pizza, name)
            for store, pizzas in self.result.items()
            for pizza, name in pizzas.items()
        )


class IngredientsAtOneStore:
    result: dict[Store, set[Ingredient]]

    def __init__(self, inp: Input):
        ingr_seen_once: dict[Ingredient, Store] = {}
        ingr_seen_more: set[Ingredient] = set()

        for store, ingrs, _ in inp.iter_pizzas():
            for i in ingrs:
                if i in ingr_seen_more:
                    pass
                elif i in ingr_seen_once and ingr_seen_once[i] != store:
                    ingr_seen_more.add(i)
                    del ingr_seen_once[i]
                else:
                    ingr_seen_once[i] = store

        self.result = {store: set() for _, store in ingr_seen_once.items()}
        for ingr, store in ingr_seen_once.items():
            self.result[store].add(ingr)

    def report(self):
        print("ingredients only used at one store:")
        for store, ingrs in self.result.items():
            print("  {}: {}".format(store, ", ".join(sorted(ingrs))))


class IngredientCount:
    result: Counter[Ingredient]

    def __init__(self, inp: Input):
        self.result = Counter()
        for _, pizzas in inp.result.items():
            for ingrs in pizzas:
                for i in ingrs:
                    self.result[i] += 1

    def common_ingr(self, n) -> list[Ingredient]:
        return [ingr for ingr, _ in self.result.most_common(n)]


class Pizzagami:
    result: dict[Store, list[tuple[Name, Pizza, Optional[int]]]]

    def __init__(self, inp: Input, common_ingr=list[Ingredient]):
        self._names_of_pizza = defaultdict(list)
        for store, pizza, name in inp.iter_pizzas():
            self._names_of_pizza[pizza].append((store, name))

        self.result = {}
        self._pizza_per_store = {}
        for store, pizzas in inp.result.items():
            self.result[store] = []
            self._pizza_per_store[store] = len(pizzas)
            for pizza, name in sorted(pizzas.items(), key=lambda kv: kv[1]):
                if self.is_pizzagami(pizza):
                    is_ingr_common = all(i in common_ingr for i in pizza)
                    ingr_common_level = (
                        max(common_ingr.index(i) for i in pizza)
                        if is_ingr_common
                        else None
                    )
                    self.result[store].append((name, pizza, ingr_common_level))

    def is_pizzagami(self, pizza: Pizza):
        return len(self._names_of_pizza[pizza]) == 1

    def report(self):
        for store, pizzagami in self.result.items():
            if pizzagami:
                num_ingr_common_pizzagami = sum(
                    1 for gami in pizzagami if gami[2] is not None
                )
                print(
                    "{}: {} pizzagami!".format(store, len(pizzagami))
                    + " (out of {}".format(self._pizza_per_store[store])
                    + " total)"
                )
                if num_ingr_common_pizzagami:
                    print(
                        "...{} ingredient-common pizzagami".format(
                            num_ingr_common_pizzagami
                        )
                    )

                for name, pizza, common_ingr_level in pizzagami:
                    print("  {} ({})".format(name, ", ".join(pizza)))
                    if common_ingr_level is not None:
                        print(
                            "    {}-ingredient-common pizzagami".format(
                                common_ingr_level
                            )
                        )
            else:
                print("{}: no pizzagami :(".format(store))
            print()


class CountIngredientCommonPizzagami:
    _per_level: dict[int, int]
    _total: int

    def __init__(self, pizzagami: Pizzagami):
        self._per_level = {i: 0 for i in range(1, ingr_common_limit + 1)}
        for _, pizzagamis in pizzagami.result.items():
            for _, _, ingr_common_level in pizzagamis:
                if ingr_common_level is not None:
                    self._per_level[ingr_common_level] += 1
        self._total = sum(self._per_level.values())

    def report(self):
        print("{} ingredient-common pizzagami".format(self._total))
        for level in self._per_level:
            amount = sum(v for k, v in self._per_level.items() if k <= level)
            print("  {:>2}-ingredient-common pizzagami: {}".format(level, amount))


def all_ingredients(inp: Input) -> set[Ingredient]:
    all_ingr = set()
    for _, pizza, _ in inp.iter_pizzas():
        all_ingr |= set(pizza)
    return all_ingr


def all_pizzas(inp: Input) -> set[Pizza]:
    return set(pizza for _, pizza, _ in inp.iter_pizzas())


def main():
    inp = Input("pizzas")
    ingr_at_one_store = IngredientsAtOneStore(inp)
    ingr_count = IngredientCount(inp)
    common_ingr = ingr_count.common_ingr(ingr_common_limit)

    pizzagami = Pizzagami(inp, common_ingr)
    ingr_common_count = CountIngredientCommonPizzagami(pizzagami)
    pizzagami.report()

    num_ingr = len(all_ingredients(inp))
    num_pizzas = len(all_pizzas(inp))
    # print("all ingredients:")
    # for ingr in sorted(all_ingredients(inp)):
    #     print("  ", ingr)
    print("number of ingredients: ", num_ingr)
    print("number of possible pizzas: 2**{} = {}".format(num_ingr, 2**num_ingr))
    print(
        "number of seen pizzas: {} ({:.0E} %)".format(
            num_pizzas, 100 * num_pizzas / (2**num_ingr)
        )
    )
    print("{} most common ingredients:".format(ingr_common_limit, common_ingr))
    for i, (pizza, amount) in enumerate(
        ingr_count.result.most_common(ingr_common_limit)
    ):
        print("  {:>2}. ({:>3}) {}".format(i, amount, pizza))

    ingr_common_count.report()
    ingr_at_one_store.report()

    is_pizzagami = [sorted(pizza) for pizza in all_pizzas(inp) if pizzagami.is_pizzagami(pizza)]
    non_pizzagami = [sorted(pizza) for pizza in all_pizzas(inp) if not pizzagami.is_pizzagami(pizza)]
    for i, p in enumerate(sorted(non_pizzagami)):
        print(i, ", ".join(p))

    print(len(is_pizzagami), len(non_pizzagami), len(all_pizzas(inp)))

    for non_p in non_pizzagami:
        print(non_p)


main()
