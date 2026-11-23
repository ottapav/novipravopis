"""Výjimky z pravidla: cizí slova.

Slovo se považuje za cizí, pokud začíná některým z kmenů níže (případně po
jedné či dvou běžných předponách, např. ne-, nej-, a-, anti-). Takové slovo
zůstane celé beze změny, tj. "systém", "nejsystémovější", "analýza" apod.

Seznam lze snadno rozšířit – stačí přidat další kmen malými písmeny
(s diakritikou tak, jak se v kmeni píše).
"""

FOREIGN_STEMS = [
    # sy-, sý-
    "sym", "syst", "synt", "synag", "synap", "synchr", "syndr", "syndik",
    "synerg", "synest", "synkop", "synkret", "synod", "synonym", "synopt",
    "sybar", "sydney", "sylab", "sylv", "sylog", "syfil",
    "sýrie", "sýrsk", "sýrčan",

    # ly-, lý-
    "lyr", "lyc", "lymf", "lynč", "lyon", "lydi", "lyz", "lyofil",
    "analy", "analý", "paraly", "paralý", "kataly", "katalý",
    "dialy", "dialý", "hydroly", "hydrolý", "elektroly", "elektrolý",
    "olymp",
    "polyg", "polym", "polyp", "polyf", "polyt", "polyes", "polyet",
    "polyvi", "polyc", "polyhist", "polyné", "polyne",

    # my-, mý-
    "myko", "mykó", "myst", "mytol", "mytic", "myrt", "myrh", "myo", "mycel",
    "mýtus", "mýtu", "mýtů", "amyl", "enzym",

    # py-, pý-
    "pyr", "pyž", "pyg", "pyth", "tapyr",

    # by-, bý-
    "byz", "byrokr", "byron",

    # fy-, fý-
    "fyz", "fyt", "fyl", "fykol", "fotosynt", "biosynt",

    # zy-, zý-
    "zyg", "zym",

    # psy-
    "psych",

    # anglicismy a jiná přejatá slova
    "baby", "body", "copy", "hobby", "lobby", "happy", "family", "fly",
]

# Předpony, které se smějí objevit před cizím kmenem (max. dvě za sebou).
ALLOWED_PREFIXES = [
    "nej", "ne", "anti", "super", "ultra", "mega", "mini",
    "pro", "po", "za", "do", "od", "roz", "pře", "před", "při", "bez",
    "a", "an",
]
