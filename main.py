from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterator, Optional
import functools

type Store = str
type Name = str
type Ingredient = str
type Pizza = frozenset[Ingredient]

ingr_common_limit = 10


class Input:
    result: dict[Store, dict[Pizza, Name]]

    def __init__(self, pizzadir):
        self.result = {}
        for p in Path(pizzadir).iterdir():
            store = p.name
            self.result[store] = {}
            with open(p) as f:
                for pizza in f.read().splitlines():
                    if ":" in pizza and not pizza.strip().endswith(":"):
                        name, ingr = pizza.split(":")
                        name = name.strip().lower()
                        ingr = frozenset(
                            [i.strip().lower() for i in ingr.strip().split(",")]
                        )
                    else:
                        name = pizza.strip().lower()
                        ingr = frozenset()
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

    def __init__(self, inp: Input, common_ingr: list[Ingredient]):
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

    def count(self, pizza):
        return len(self._names_of_pizza[pizza])

    def is_pizzagami(self, pizza: Pizza):
        return self.count(pizza) == 1

    def short_report(self):
        for store, pizzagami in self.result.items():
            if pizzagami:
                num_ingr_common_pizzagami = sum(
                    1 for gami in pizzagami if gami[2] is not None
                )
                print(
                    "{}: {} pizzagami!".format(store, len(pizzagami))
                    + " (out of {}".format(self._pizza_per_store[store])
                    + " total)"
                    + " {}%".format(
                        round(
                            len(pizzagami) * 100 / self._pizza_per_store[store],
                        )
                    )
                )
                if num_ingr_common_pizzagami:
                    print(
                        "...{} ingredient-common pizzagami".format(
                            num_ingr_common_pizzagami
                        )
                    )
            else:
                print("{}: no pizzagami :(".format(store))
            print()

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
                    print("  {} ({})".format(name, ", ".join(sorted(pizza))))
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


class SameThings:
    same_name: dict[Name, set[Pizza]]
    same_ingredients: dict[Pizza, set[Name]]

    def __init__(self, inp: Input):
        self.same_name = defaultdict(set)
        self.same_ingredients = defaultdict(set)
        for _, pizza, name in inp.iter_pizzas():
            self.same_name[name].add(pizza)
            self.same_ingredients[frozenset(pizza)].add(name)
        self.same_name = {
            name: pizzas for name, pizzas in self.same_name.items() if len(pizzas) > 1
        }
        self.same_ingredients = {
            pizza: names
            for pizza, names in self.same_ingredients.items()
            if len(names) > 1
        }

    def report(self):
        if self.same_name:
            print("same name, different ingredients:")
            for name, pizzas in sorted(self.same_name.items()):
                print(f"  {name}:")
                for pizza in pizzas:
                    print("    {}".format(", ".join(sorted(pizza))))
        if self.same_ingredients:
            print("same pizza, different names:")
            for pizza, names in self.same_ingredients.items():
                print("  {}:".format(", ".join(sorted(pizza))))
                for name in sorted(names):
                    print(f"    {name}")


class ConditionalProbabilityOfIngredients:
    # sorted list of P(first ingredient -> second ingredient)
    result: list[tuple[float, tuple[Ingredient, int], tuple[Ingredient, int]]]

    def __init__(self, inp: Input, min_pizzas_to_report: int):
        self.result = []
        pizzas_with: dict[Ingredient, list[Pizza]] = defaultdict(list)
        for pizza in set(pizza for _, pizza, _ in inp.iter_pizzas()):
            for ingr in pizza:
                pizzas_with[ingr].append(pizza)
        for ingr, pizzas in sorted(pizzas_with.items()):
            if len(pizzas) < min_pizzas_to_report:
                continue
            other_ingr = set()
            for p in pizzas:
                other_ingr |= set(p)
            other_ingr.remove(ingr)
            for ingr2 in other_ingr:
                n = sum(1 for p in pizzas if ingr2 in p)
                prob = n / len(pizzas)
                self.result.append((prob, (ingr, len(pizzas)), (ingr2, n)))
        self.result.sort(reverse=True)

    def report(self, limit=30):
        for i, (p, (i1, n1), (i2, n2)) in enumerate(self.result[:limit]):
            print(f"{i+1:>3} {p:.2} {i1} ({n1}) -> {i2} ({n2})")


class FeasiblePizzas:
    # a pizza is feasible if it exists or its ingredients are a subset of a feasible pizza
    all_feasible: set[Pizza]
    not_seen: set[Pizza]

    @functools.cache
    @staticmethod
    def _all_below(pizza: Pizza) -> set[Pizza]:
        if not pizza:
            return set()
        below = {pizza}
        for i in pizza:
            below |= FeasiblePizzas._all_below(pizza - {i})
        return below

    def __init__(self, inp: Input):
        self.all_feasible = set()
        all_pizzas = set()
        for _, pizza, _ in inp.iter_pizzas():
            self.all_feasible |= FeasiblePizzas._all_below(pizza)
            all_pizzas.add(pizza)
        self.not_seen = self.all_feasible - all_pizzas

    def report(self):
        p = 100 * (1.0 - (len(self.not_seen) / len(self.all_feasible)))
        print(f"{len(self.all_feasible)} feasible pizzas ({p:.1f}% seen)")


def all_ingredients(inp: Input) -> set[Ingredient]:
    all_ingr = set()
    for _, pizza, _ in inp.iter_pizzas():
        all_ingr |= set(pizza)
    return all_ingr


def all_pizzas(inp: Input) -> set[Pizza]:
    return set(pizza for _, pizza, _ in inp.iter_pizzas())


def main():
    inp = Input("pizzas")
    ingr_count = IngredientCount(inp)
    common_ingr = ingr_count.common_ingr(ingr_common_limit)

    pizzagami = Pizzagami(inp, common_ingr)
    pizzagami.short_report()

    num_ingr = len(all_ingredients(inp))
    num_pizzas = len(all_pizzas(inp))
    # print("all ingredients:")
    # for ingr in sorted(all_ingredients(inp)):
    #    print("  ", ingr)
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

    is_pizzagami = [
        sorted(pizza) for pizza in all_pizzas(inp) if pizzagami.is_pizzagami(pizza)
    ]
    non_pizzagami = [
        sorted(pizza) for pizza in all_pizzas(inp) if not pizzagami.is_pizzagami(pizza)
    ]
    print(len(is_pizzagami), len(non_pizzagami), len(all_pizzas(inp)))

    non_pizzagami_counts = sorted(
        (pizzagami.count(p), p)
        for p in all_pizzas(inp)
        if not pizzagami.is_pizzagami(p)
    )
    max_count = max((a for a, _ in non_pizzagami_counts))
    for c, p in non_pizzagami_counts:
        print("." * c, " " * (max_count - c), ", ".join(p))

    # CountIngredientCommonPizzagami(pizzagami).report()
    # IngredientsAtOneStore(inp).report()
    # SameThings(inp).report()
    # ConditionalProbabilityOfIngredients(inp, min_pizzas_to_report=5).report()
    FeasiblePizzas(inp).report()


main()
