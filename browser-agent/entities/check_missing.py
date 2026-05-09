from entity_manager import load_registry

registry = load_registry()

missing = [
    "Lucas Bergvall",
    "Gabriel Martinelli",
    "RB Leipzig",
    "Yan Diomande",
    "Bournemouth",
    "Eli Junior Kroupi",
    "Luis Campos",
    "Chelsea",
    "Arsenal",
    "Tottenham",
    "Lucas Bergvall",
    "Manchester United",
    "Real Madrid",
    "Aston Villa",
    "Unai Emery",
    "Eli Junior Kroupi",
]

print("Total registry entries:", len(registry))
print()
for name in missing:
    in_reg = name in registry
    status = "IN REGISTRY" if in_reg else "MISSING"
    print(name + ": " + status)