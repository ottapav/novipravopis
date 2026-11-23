# Noví pravopis

Jednoduchá webová aplikace, která převede český text podle nového pravopisného pravidla:

> Po obojetných souhláskách (**b, f, l, m, p, s, v, z**) se píše **měkké i/í**.
> Výjimku tvoří cizí slova.

Text napíšete (nebo vložíte) do levého pole, kliknete na **Převést na nový pravopis** a výsledek se
objeví v pravém poli. Změněná písmena jsou zvýrazněná (zvýraznění jde vypnout), cizí slova, která
zůstala beze změny, jsou označená tečkovaným podtržením.

| Původní text | Noví pravopis |
|--------------|---------------|
| byl, být, mýt | bil, bít, mít |
| slyšet, mysl, sýr | slišet, misl, sír |
| vysoký, obyvatel | visoký, obivatel |
| systém, symbol, analýza, psychologie *(cizí slova)* | beze změny |

## Spuštění

```bash
python -m venv .venv
source .venv/bin/activate          # ve Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload      # http://localhost:8000
```

Testy:

```bash
pip install -r requirements-dev.txt
pytest
```

Vyžaduje Python 3.9 nebo novější.

## Struktura

- `app/converter.py` – vlastní pravidlo (`convert(text)`)
- `app/exceptions.py` – seznam kmenů cizích slov (výjimky); lze libovolně rozšiřovat
- `app/main.py` – FastAPI server, `POST /api/convert`, statické soubory, `GET /healthz`
- `public/` – webové rozhraní (HTML, CSS, JS)
- `tests/` – testy (pytest)
- `render.yaml` – volitelný blueprint pro Render

## API

`POST /api/convert` s tělem `{ "text": "..." }` vrátí:

```json
{
  "text": "Bil systém.",
  "segments": [
    { "t": "B", "k": "plain" },
    { "t": "i", "k": "changed" },
    { "t": "l ", "k": "plain" },
    { "t": "systém", "k": "foreign" },
    { "t": ".", "k": "plain" }
  ],
  "stats": { "changedLetters": 1, "changedWords": 1, "foreignKept": 1 }
}
```

Maximální délka textu je 100 000 znaků a velikost požadavku 1 MB. Chyby se vracejí jako
`{ "error": "..." }` (400 pro chybějící nebo špatný text, 413 pro příliš dlouhý).

## Nasazení na Render

Web Service z tohoto repozitáře s nastavením:

- **Runtime:** Python 3
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health check path:** `/healthz`

## Poznámky k výjimkám

Cizí slovo se pozná podle seznamu kmenů v `app/exceptions.py` (po případných předponách jako *ne-*,
*nej-*, *a-*, *anti-*). Takové slovo zůstává celé beze změny, tedy i odvozeniny typu *nejsystémovější*.
Aplikace nemá slovník celé češtiny, takže u méně obvyklých přejatých slov a jmen je potřeba seznam doplnit.
