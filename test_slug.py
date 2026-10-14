from export_functions import slugify  # or wherever it lives

tests = [
    "Turkey Taco Skillet",
    "Upgraded Kimchi Noodles",
    "  Scrambled Eggs  ",
    "Café au Lait",
    "Recipe #1!!!",
    "!!!",
    "Pasta -- Carbonara",
    "Crème Brûlée",
]

for name in tests:
    print(f"{repr(name):40} → {repr(slugify(name))}")