python_date_directives = [
    "a",
    "A",
    "w",
    "d",
    "b",
    "B",
    "m",
    "y",
    "Y",
    "H",
    "I",
    "p",
    "M",
    "S",
    "f",
    "z",
    "Z",
    "j",
    "U",
    "W",
    "x",
    "x",
    "X",
]

python_date_directives = ["%" + i for i in python_date_directives]

custom_app_directives = ["software", "camera_maker", "camera_model"]
custom_app_directives = ["%" + i for i in custom_app_directives]
