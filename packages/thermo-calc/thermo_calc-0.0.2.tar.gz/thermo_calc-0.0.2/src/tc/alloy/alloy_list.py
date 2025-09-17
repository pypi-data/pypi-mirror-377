from .alloy_properties import alloy_properties


def alloy_names() -> list[str]:
    comp_rows = alloy_properties()
    names: list[str] = []
    for row in comp_rows:
        name = row.get("Name")
        if name is not None:
            names.append(name)

    return names
