import pytest

from app.converter import convert


def out(s: str) -> str:
    return convert(s)["text"]


@pytest.mark.parametrize(
    "src,expected",
    [
        ("byl", "bil"),
        ("být", "bít"),
        ("mýt", "mít"),
        ("slyšet", "slišet"),
        ("mysl", "misl"),
        ("sýr", "sír"),
        ("vysoký", "visoký"),
        ("obyvatel", "obivatel"),
        ("zvykat", "zvikat"),
        ("pýcha", "pícha"),
        # každá z obojetných souhlásek b, f, l, m, p, s, v, z
        ("byt", "bit"),
        ("fyk", "fik"),
        ("lyko", "liko"),
        ("myš", "miš"),
        ("pytel", "pitel"),
        ("syn", "sin"),
        ("vyr", "vir"),
        ("zyk", "zik"),
    ],
)
def test_y_po_obojetnych_souhlaskach_se_meni(src, expected):
    assert out(src) == expected


@pytest.mark.parametrize("word", ["dobrý", "tyto", "hrdý", "chyba", "žyt", "yeti", "kuy"])
def test_po_ostatnich_pismenech_se_nic_nemeni(word):
    assert out(word) == word


@pytest.mark.parametrize(
    "src,expected",
    [("Byl", "Bil"), ("BYL", "BIL"), ("Být", "Bít"), ("SÝR", "SÍR"), ("bYl", "bIl")],
)
def test_velikost_pismen_se_zachova(src, expected):
    assert out(src) == expected


@pytest.mark.parametrize(
    "word",
    [
        "systém", "Systém", "symbol", "symetrie", "analýza", "analyzovat",
        "psychologie", "fyzika", "olympiáda", "pyramida", "polymer",
        "synonymum", "syntax", "hobby", "baby", "lobby", "mykologie",
        "nejsystémovější", "nesymetrický", "asymetrie", "Sydney",
    ],
)
def test_cizi_slova_zustavaji(word):
    assert out(word) == word


@pytest.mark.parametrize(
    "src,expected",
    [
        ("syn", "sin"),
        ("sypat", "sipat"),
        ("polykat", "polikat"),
        ("lyže", "liže"),
        ("pyl", "pil"),
    ],
)
def test_domaci_slova_podobna_cizim_se_meni(src, expected):
    assert out(src) == expected


def test_interpunkce_mezery_a_radky_zustavaji():
    assert out("Byl, jsem!\n\n  Mysl…\tsýr.") == "Bil, jsem!\n\n  Misl…\tsír."
    assert out("") == ""
    assert out("123 -- !?") == "123 -- !?"


def test_rozlozene_znaky_nfd_se_normalizuji():
    assert out("sýr") == "sír"  # s + y + kombinující čárka


def test_veta_se_smisenymi_slovy():
    assert out("Byl jsem u slyšení o systému analýzy.") == "Bil jsem u slišení o systému analýzy."


def test_segmenty_davaji_dohromady_vysledek_a_oznacuji_zmeny():
    r = convert("Byl systém sýr.")
    assert "".join(s["t"] for s in r["segments"]) == r["text"]
    assert [s["t"] for s in r["segments"] if s["k"] == "changed"] == ["i", "í"]
    assert [s["t"] for s in r["segments"] if s["k"] == "foreign"] == ["systém"]


def test_statistiky():
    assert convert("Byl vysoký sýr, systém a dobrý den.")["stats"] == {
        "changedLetters": 3,
        "changedWords": 3,
        "foreignKept": 1,
    }
    assert convert("dobrý den")["stats"] == {
        "changedLetters": 0,
        "changedWords": 0,
        "foreignKept": 0,
    }


def test_slovo_s_vice_zmenami_se_pocita_jednou():
    r = convert("bylybyly")
    assert r["text"] == "bilibili"
    assert r["stats"]["changedLetters"] == 4
    assert r["stats"]["changedWords"] == 1


def test_none_je_prazdny_text():
    assert convert(None)["text"] == ""


@pytest.mark.parametrize(
    "src,expected",
    [
        ("mapy", "mapi"),
        ("zuby", "zubi"),
        ("kovy", "kovi"),
        ("psy", "psi"),
        ("brzy", "brzi"),
        ("Brzy", "Brzi"),
        ("malý", "malí"),
        ("zdravý", "zdraví"),
    ],
)
def test_slova_s_y_na_konci_se_meni(src, expected):
    assert out(src) == expected


@pytest.mark.parametrize("word", ["ženy", "hory", "party", "dobrý", "hobby", "baby"])
def test_slova_s_y_na_konci_beze_zmeny(word):
    # po jiné souhlásce než obojetné, nebo cizí slovo (hobby, baby)
    assert out(word) == word


def test_nazev_stranky():
    assert out("Nový pravopis") == "Noví pravopis"
