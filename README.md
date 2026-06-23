# Wortuhr

Eine selbstgebaute LED-Wortuhr ("zeigt die Uhrzeit in Worten") auf Basis eines
Raspberry Pi und eines WS2801-RGB-LED-Streifens. Die Front besteht aus einer
11x10-Buchstaben-Matrix ("ES IST FÜNF NACH ZEHN UHR" ...) plus 4 einzelnen
Minuten-Punkt-LEDs für die Minuten, die nicht durch ein Wort abgedeckt werden.

## Funktionsweise

- Jede Sekunde *(genauer: alle 5s)* wird die aktuelle Systemzeit ausgelesen.
- Ändert sich Stunde oder Minute, wird die Anzeige neu berechnet:
  - Die Minute wird in 12 Blöcke à 5 Minuten eingeteilt (z. B. "FÜNF NACH",
    "VIERTEL NACH", "HALB", "FÜNF VOR" ...).
  - Ab "fünf vor halb" bezieht sich das Stundenwort bereits auf die kommende
    Stunde (wie im gesprochenen Deutsch: "fünf vor halb drei" = 14:25).
  - Die restlichen 0-4 Minuten innerhalb eines 5-Minuten-Blocks werden über
    die 4 separaten Minuten-Punkt-LEDs angezeigt.
  - Die Anzeigefarbe richtet sich nach der Tageszeit (siehe `select_color_by_hour`
    in [ws2801_newBib.py](ws2801_newBib.py)) – z. B. warme Farben morgens/abends,
    kühlere Farben tagsüber, dunkles Blau/Violett nachts.
- An zwei festen Zeitpunkten (14:06 und 23:06 Uhr) zeigt die Uhr statt der
  Zeit ein rotes Herz als Easter Egg.
- Da der LED-Streifen mäanderförmig ("Schlangenlinie") hinter der Matrix
  verlegt ist, wird die logische Buchstaben-Matrix vor der Ausgabe passend
  umsortiert (`matrix_to_list`).

## Dateien

| Datei | Zweck |
|---|---|
| [ws2801_newBib.py](ws2801_newBib.py) | Hauptprogramm der Wortuhr (CircuitPython-Bibliothek `adafruit_ws2801`). Enthält die Wort-Matrizen, die Zeit-zu-Wort-Logik und die Hauptschleife. |
| [ws2801.py](ws2801.py) | Älteres Demo-/Testskript (legacy `Adafruit_WS2801`-Bibliothek + Hardware-SPI) zum reinen Testen der LED-Verkabelung mit ein paar Lichteffekten (Regenbogen, Ausblenden, Blinken). Wird für den eigentlichen Uhrbetrieb nicht benötigt. |

## Hardware

- Raspberry Pi (oder kompatibles Board mit `board`/CircuitPython-Unterstützung)
- WS2801-RGB-LED-Streifen, mäanderförmig hinter einer 11x10-Buchstabenschablone
  verlegt, plus 4 zusätzliche LEDs für die Minutenpunkte (insgesamt 114 LEDs)
- SPI-Verkabelung: Datenleitung an `board.MOSI`, Taktleitung an `board.SCK`

## Installation

```bash
pip install adafruit-circuitpython-ws2801 numpy adafruit-blinka
```

`adafruit-blinka` stellt das `board`-Modul für Single-Board-Computer wie den
Raspberry Pi bereit.

## Verwendung

```bash
python3 ws2801_newBib.py
```

Das Skript läuft als Endlosschleife, prüft alle 5 Sekunden die Systemzeit und
aktualisiert die Anzeige bei Bedarf. Über `logging.basicConfig(level=...)` am
Anfang von `__main__` lässt sich die Ausführlichkeit der Konsolenausgabe
anpassen (`logging.DEBUG` zeigt z. B. die berechnete Matrix bei jedem Update).

Zum reinen Testen der LED-Verkabelung (ohne Uhrzeit-Logik) kann alternativ
[ws2801.py](ws2801.py) ausgeführt werden.
