# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

### Based on example from
### https://github.com/adafruit/Adafruit_CircuitPython_DotStar/tree/master/examples

import time
import random
import board
import adafruit_ws2801
import numpy as np
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

### Beschaltung: Datenleitung (MOSI) und Taktleitung (SCK) des WS2801-Streifens
odata = board.MOSI
oclock = board.SCK

# Größe der Buchstaben-Matrix: 11 Spalten x 10 Zeilen (= die Wortuhr-Front)
M_BREIT=11
M_HOCH=10
# Gesamtzahl LEDs: 11x10 Matrix-Pixel + 4 zusätzliche LEDs für die Minuten-Punkte (Eck-LEDs)
numleds = M_BREIT*M_HOCH+4
bright = 1.0
leds = adafruit_ws2801.WS2801(
    oclock, odata, numleds, brightness=bright, auto_write=False
)
######################### HELPERS ##############################

# Jede UHR_*-Funktion liefert eine 10x11-Matrix (numpy, dtype=uint8) zurück,
# in der genau die Felder auf 1 gesetzt sind, die das jeweilige Wort auf der
# Front der Wortuhr bilden (1 = LED an, 0 = LED aus). Die Matrizen werden später
# per bitweisem OR (|=) kombiniert, um die komplette Anzeige für eine Uhrzeit
# zusammenzusetzen (siehe set_minute_words/set_houres).
#
# Die Kommentare im alten C-Stil (#define ...) stammen aus der ursprünglichen
# Arduino-Vorlage und beschreiben dieselbe Bit-Maske, hier nur als Bitmuster
# pro Zeile (matrix[offscreenPage][zeile] |= 0bMASKE) statt als 2D-Matrix.

#define VOR          matrix[offscreenPage][3] |= 0b11100000000
#define NACH         matrix[offscreenPage][3] |= 0b00000001111
#define ESIST        matrix[offscreenPage][0] |= 0b11011100000
#define UHR          matrix[offscreenPage][9] |= 0b00000000111
def UHR_VOR():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[3,(0,1,2)] = 1
    return m

def UHR_NACH():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[3,(7,8,9,10)] = 1
    return m

def UHR_ESIST():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[0,(0,1,3,4,5)] = 1
    return m

def UHR_UHR():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[9,(8,9,10)] = 1
    return m

#define FUENF        matrix[offscreenPage][0] |= 0b00000001111
#define ZEHN         matrix[offscreenPage][1] |= 0b11110000000
#define VIERTEL      matrix[offscreenPage][2] |= 0b00001111111
#define ZWANZIG      matrix[offscreenPage][1] |= 0b00001111111
#define HALB         matrix[offscreenPage][4] |= 0b11110000000
#define DREIVIERTEL  matrix[offscreenPage][2] |= 0b11111111111
def UHR_FUENF():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[0,(7,8,9,10)] = 1
    return m

def UHR_ZEHN():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[1,(0,1,2,3)] = 1
    return m

def UHR_VIERTEL():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[2,(4,5,6,7,8,9,10)] = 1
    return m

def UHR_ZWANZIG():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[1,(4,5,6,7,8,9,10)] = 1
    return m

def UHR_HALB():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[4,(0,1,2,3)] = 1
    return m

def UHR_DREIVIERTEL():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[2,:] = 1
    return m

#define H_EIN        matrix[offscreenPage][5] |= 0b11100000000
#define H_EINS       matrix[offscreenPage][5] |= 0b11110000000
#define H_ZWEI       matrix[offscreenPage][5] |= 0b00000001111
#define H_DREI       matrix[offscreenPage][6] |= 0b11110000000
#define H_VIER       matrix[offscreenPage][6] |= 0b00000001111
#define H_FUENF      matrix[offscreenPage][4] |= 0b00000001111
#define H_SECHS      matrix[offscreenPage][7] |= 0b11111000000
#define H_SIEBEN     matrix[offscreenPage][8] |= 0b11111100000
#define H_ACHT       matrix[offscreenPage][7] |= 0b00000001111
#define H_NEUN       matrix[offscreenPage][9] |= 0b00011110000
#define H_ZEHN       matrix[offscreenPage][9] |= 0b11110000000
#define H_ELF        matrix[offscreenPage][4] |= 0b00000111000
#define H_ZWOELF     matrix[offscreenPage][8] |= 0b00000011111

def UHR_H_EIN():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[5,(0,1,2)] = 1
    return m

def UHR_H_EINS():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[5,(0,1,2,3)] = 1
    return m

def UHR_H_ZWEI():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[5,(7,8,9,10)] = 1
    return m

def UHR_H_DREI():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[6,(0,1,2,3)] = 1
    return m

def UHR_H_VIER():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[6,(7,8,9,10)] = 1
    return m

def UHR_H_FUENF():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[4,(7,8,9,10)] = 1
    return m

def UHR_H_SECHS():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[7,(0,1,2,3,4)] = 1
    return m

def UHR_H_SIEBEN():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[8,(0,1,2,3,4,5)] = 1
    return m

def UHR_H_ACHT():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[7,(7,8,9,10)] = 1
    return m

def UHR_H_NEUN():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[9,(3,4,5,6)] = 1
    return m

def UHR_H_ZEHN():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[9,(0,1,2,3)] = 1
    return m

def UHR_H_ELF():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[4,(5,6,7)] = 1
    return m

def UHR_H_ZWOELF():
    m=np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    m[8,(6,7,8,9,10)] = 1
    return m


# Farbpalette der Wortuhr. Jede c_farbeX-Konstante ist eine (R,G,B)-Tupel-Farbe,
# die laut Kommentar einem bestimmten Tageszeit-Fenster zugeordnet ist
# (siehe select_color_by_hour weiter unten, dort werden diese Konstanten den
# einzelnen Stunden zugewiesen). c_blue/c_red/default_color sind feste
# Sonderfarben (z.B. für das Herz-Easter-Egg oder als Fallback).
c_blue   =(255,200,0) #blue
c_red   =(255,0,0) #blue
c_farbe1 =(255,69,0)# 5 - 6
c_farbe2 =(255,140,0)# 6 - 8
c_farbe3 =(255,200,0)# 8 - 10
c_farbe4 =(50,200,0)# 10 - 12
c_farbe5 =(0,120,0)# 12 - 14
c_farbe6 =(255,20,147)# 14 - 16
c_farbe7 =(255,0,255)# 16 - 18
c_farbe8 =(153,50,204)# 18 - 20
c_farbe9 =(138,43,226)# 20 - 21
c_farbe10=(25,25,112)# 21 - 23
c_farbe11=(10,0,100)# 23 - 24
c_farbe0 =(0,255,127)# 24 - 5
default_color = (255,255,255)

######################### HELPERS ##############################


# Liefert eine zufällige Helligkeitsstufe (0, 32, 64, ..., 192) -> ungenutzter Helfer
def random_color():
    return random.randrange(0, 7) * 32

def matrix_to_list(matrix):
    """Wandelt die logische 10x11-Buchstaben-Matrix in die physische LED-Reihenfolge um.

    Der LED-Streifen ist mäanderförmig ("Schlangenlinie"/Boustrophedon) hinter der
    Front verlegt: eine Zeile läuft von links nach rechts, die nächste von rechts
    nach links usw. Deshalb müssen die ungeraden Zeilen (1,3,5,7,9) gespiegelt
    werden, bevor die Matrix zu einer flachen Liste in LED-Anschlussreihenfolge
    "abgerollt" werden kann. Die Liste wird abschließend umgedreht, da die
    LED-Kette an der Matrix-Position [9,10] (unten rechts) beginnt zu zählen.
    """
    m=np.ndarray.copy(matrix)
    m[1,:]=np.flipud(m[1,:])
    m[3,:]=np.flipud(m[3,:])
    m[5,:]=np.flipud(m[5,:])
    m[7,:]=np.flipud(m[7,:])
    m[9,:]=np.flipud(m[9,:])
    l=list(m.flatten())

    return list(reversed(l))

def clear():
    """Schaltet alle LEDs (Buchstaben-Matrix + Minutenpunkte) aus."""
    for idx in range(numleds):
        leds[idx] = (0,0,0)
    leds.show()
    time.sleep(1)

def drawMinute(minutes,color):
    """Steuert die 4 einzelnen Minuten-Punkte (LED-Index 110-113) an.

    Jeder 5-Minuten-Block wird durch die Wörter abgedeckt; der Rest
    (0-4 Minuten innerhalb des Blocks) wird durch 0 bis 4 leuchtende
    Punkte dargestellt (minutes % 5 Punkte an).
    """
    if(minutes%5==0):
        leds[110] = (0,0,0)
        leds[111] = (0,0,0)
        leds[112] = (0,0,0)
        leds[113] = (0,0,0)
        leds.show()

    if(minutes%5==1):
        leds[110] = color
        leds[111] = (0,0,0)
        leds[112] = (0,0,0)
        leds[113] = (0,0,0)
        leds.show()
    if(minutes%5==2):
        leds[110] = color
        leds[111] = color
        leds[112] = (0,0,0)
        leds[113] = (0,0,0)
        leds.show()
    if(minutes%5==3):
        leds[110] = color
        leds[111] = color
        leds[112] = color
        leds[113] = (0,0,0)
        leds.show()
    if(minutes%5==4):
        leds[110] = color
        leds[111] = color
        leds[112] = color
        leds[113] = color
        leds.show()

def draw_matrix(matrix,color):
    """Zeichnet die Buchstaben-Matrix (ohne die 4 Minutenpunkte) in der gegebenen Farbe.

    Jedes Matrixfeld mit Wert 1 wird in `color` eingefärbt, alle anderen
    Felder werden ausgeschaltet. Die 4 Minutenpunkte am Ende der LED-Kette
    werden hier nicht berührt (siehe drawMinute).
    """
    #clear()
    ml=matrix_to_list(matrix)
    for idx in range(numleds-4):
        if(ml[idx]==1):
            leds[idx] = (color)
        else:
            leds[idx] = (0,0,0)

    # show all leds in led string
    leds.show()

def set_herz():
    """Sonder-Anzeige: zeichnet ein Herz auf die Matrix (Easter Egg zu bestimmten Zeiten)."""
    matrix = np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    matrix[0,(2,3,7,8)] = 1
    matrix[1,(1,4,6,9)] = 1
    matrix[2,(0,5,10)] = 1
    matrix[3,(0,10)] = 1
    matrix[4,(0,10)] = 1
    matrix[5,(1,9)] = 1
    matrix[6,(2,8)] = 1
    matrix[7,(3,7)] = 1
    matrix[8,(4,6)] = 1
    matrix[9,(5)] = 1
    # matrix[0]|=0b00110001100;
    # matrix[1]|=0b01001010010;
    # matrix[2]|=0b10000100001;
    # matrix[3]|=0b10000000001;
    # matrix[4]|=0b10000000001;
    # matrix[5]|=0b01000000010;
    # matrix[6]|=0b00100000100;
    # matrix[7]|=0b00010001000;
    # matrix[8]|=0b00001010000;
    # matrix[9]|=0b00000100000;
    return matrix

def select_color_by_hour(hour):
    """Liefert die für die jeweilige Tagesstunde vorgesehene Anzeigefarbe."""

    # Mapping der Stunden zu Farben
    color_map = {
        0: c_farbe0, 1: c_farbe0, 2: c_farbe0, 3: c_farbe0, 4: c_farbe0,
        5: c_farbe1,
        6: c_farbe2, 7: c_farbe2,
        8: c_farbe3, 9: c_farbe3,
        10: c_farbe4, 11: c_farbe4,
        12: c_farbe5, 13: c_farbe5,
        14: c_farbe6, 15: c_farbe6,
        16: c_farbe7, 17: c_farbe7,
        18: c_farbe8, 19: c_farbe8,
        20: c_farbe9,
        21: c_farbe10, 22: c_farbe10,
        23: c_farbe11
    }

    # Farbe für die aktuelle Stunde zurückgeben, oder Standardfarbe, wenn nicht definiert
    return color_map.get(hour, default_color)

def set_minute_words(hours,minutes):
    """Baut die Wort-Matrix für "ES IST <Minutenwort> <VOR/NACH> <Stundenwort> [UHR]".

    Die Minuten werden in 12 Blöcke à 5 Minuten eingeteilt (minutes // 5).
    Ab dem 6. Block (ab "5 vor halb") bezieht sich die Stundenanzeige bereits
    auf die kommende Stunde (deshalb set_houres(hours + 1, ...)), so wie man
    es auch im Deutschen sagt ("5 vor halb drei" bezieht sich auf 3 Uhr).
    Der verbleibende Rest (0-4 Minuten) wird separat über drawMinute als
    Punkte angezeigt.
    """
    m = np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    # Bestimmen der Minuten-Gruppen
    minutes_group = minutes // 5

    m |= UHR_ESIST()

    if minutes_group == 0:
        var1=0
        # Glatte Stunde
        m |=set_houres(hours, True)
    elif minutes_group == 1:
        # 5 nach
        m |=UHR_FUENF()
        m |=UHR_NACH()
        m |=set_houres(hours, False)
    elif minutes_group == 2:
        # 10 nach
        m |=UHR_ZEHN()
        m |=UHR_NACH()
        m |=set_houres(hours, False)
    elif minutes_group == 3:
        # Viertel nach
        m |=UHR_VIERTEL()
        m |=UHR_NACH()
        m |=set_houres(hours, False)
    elif minutes_group == 4:
        # 20 nach
        m |=UHR_ZWANZIG()
        m |=UHR_NACH()
        m |=set_houres(hours, False)
    elif minutes_group == 5:
        # 5 vor halb
        m |=UHR_FUENF()
        m |=UHR_VOR()
        m |=UHR_HALB()
        m |=set_houres(hours + 1, False)
    elif minutes_group == 6:
        # Halb
        m |=UHR_HALB()
        m |=set_houres(hours + 1, False)
    elif minutes_group == 7:
        # 5 nach halb
        m |=UHR_FUENF()
        m |=UHR_NACH()
        m |=UHR_HALB()
        m |=set_houres(hours + 1, False)
    elif minutes_group == 8:
        # 10 nach halb
        m |=UHR_ZWANZIG()
        m |=UHR_VOR()
        m |=set_houres(hours + 1, False)
    elif minutes_group == 9:
        # Dreiviertel
        m |=UHR_VOR()
        m |=UHR_VIERTEL()
        m |=set_houres(hours + 1, False)
    elif minutes_group == 10:
        # 10 vor
        m |=UHR_ZEHN()
        m |=UHR_VOR()
        m |=set_houres(hours + 1, False)
    elif minutes_group == 11:
        # 5 vor
        m |=UHR_FUENF()
        m |=UHR_VOR()
        m |=set_houres(hours + 1, False)
    return m

def set_houres(hours, glatt):
    """Baut die Wort-Matrix für das Stundenwort (EIN(S)/ZWEI/.../ZWÖLF).

    `hours` ist hier bereits die "sprachliche" Stunde (0-23, evtl. von
    set_minute_words um +1 verschoben). `glatt=True` bedeutet "volle Stunde"
    (z.B. "ES IST EIN UHR" statt "ES IST EINS"), wodurch zusätzlich das Wort
    UHR angezeigt und EIN statt EINS verwendet wird.
    """
    m = np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    # Bei "glatt" UHR hinzufügen
    if glatt:
        m |=UHR_UHR()
    # Auswahl der Stunde
    if hours in {0, 12, 24}:
        m |=UHR_H_ZWOELF()
    elif hours in {1, 13}:
        if glatt:
            m |=UHR_H_EIN()
        else:
            m |=UHR_H_EINS()
    elif hours in {2, 14}:
        m |=UHR_H_ZWEI()
    elif hours in {3, 15}:
        m |=UHR_H_DREI()
    elif hours in {4, 16}:
        m |=UHR_H_VIER()
    elif hours in {5, 17}:
        m |=UHR_H_FUENF()
    elif hours in {6, 18}:
        m |=UHR_H_SECHS()
    elif hours in {7, 19}:
        m |=UHR_H_SIEBEN()
    elif hours in {8, 20}:
        m |=UHR_H_ACHT()
    elif hours in {9, 21}:
        m |=UHR_H_NEUN()
    elif hours in {10, 22}:
        m |=UHR_H_ZEHN()
    elif hours in {11, 23}:
        m |=UHR_H_ELF()
    return m

######################### FUN FUNC ##############################
# Reine Effekt-Funktionen für den Start (Regenbogen-Begrüßung), unabhängig
# von der eigentlichen Uhrzeit-Anzeige.
def RGB_to_color(r, g, b):
    """Convert three 8-bit red, green, blue component values to a single 24-bit
    color value.
    """
    return ((r & 0xFF) << 16) | ((g & 0xFF) << 8) | (b & 0xFF)
# Define the wheel function to interpolate between different hues.
def wheel(pos):
    if pos < 85:
        return RGB_to_color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return RGB_to_color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return RGB_to_color(0, pos * 3, 255 - pos * 3)
def rainbow_cycle_successive(pixel, wait=0.1):
    """Lässt beim Start einmalig einen Regenbogen über alle LEDs der Kette laufen."""
    for i in range(numleds):
        # tricky math! we use each pixel as a fraction of the full 96-color wheel
        # (thats the i / strip.numPixels() part)
        # Then add in j which makes the colors go around per pixel
        # the % 96 is to make the wheel cycle around
        pixel[i]=wheel(((i * 256 // numleds)) % 256) 
        pixel.show()
        if wait > 0:
            time.sleep(wait)

######################### MAIN LOOP ##############################
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Beim Start: alle LEDs ausschalten und einmal als "Lebenszeichen" einen
    # Regenbogen über die ganze Kette laufen lassen.
    logger.info('Started')
    clear()
    rainbow_cycle_successive(leds)
    clear()
    matrix = np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)

    
    # matrix[2,0] = 1
    # matrix[3,0] = 1
    # matrix[4,0] = 1
    # matrix[5,0] = 1
    # matrix[6,0] = 1
    # matrix[7,0] = 1
    # matrix[8,0] = 1
    # matrix[9,0] = 1

    # Aktuelle Uhrzeit auslesen 
    aktuelle_uhrzeit = datetime.now() 
    stunde_debug = aktuelle_uhrzeit.hour 
    minute_debug = aktuelle_uhrzeit.minute 
    # Ausgabe der Stunde und Minute 
    logger.debug(f"Die aktuelle Stunde ist:{stunde_debug}")
    logger.debug(f"Die aktuelle Minute ist:{minute_debug}")

    # matrix = set_herz()

    logger.debug(f"m\n{matrix}")

    ml=matrix_to_list(matrix)
    logger.debug(f"l\n{ml}")

    
  #  print(f"Start script n_leds {n_leds}")
    #matrix=set_herz()
    clear()

    matrix |= UHR_UHR()
    aktuelle_color=c_farbe1
    logger.debug(f"m\n{matrix}")
    # stunde/minute halten den zuletzt angezeigten Stand, damit die Matrix nur
    # bei einer tatsächlichen Änderung neu gezeichnet wird (kein Flackern).
    stunde = 0
    minute = 0
    #matrix = np.zeros([M_HOCH,M_BREIT],dtype=np.uint8)
    while True:
        # Aktuelle Uhrzeit auslesen
        aktuelle_uhrzeit = datetime.now()
        if (aktuelle_uhrzeit.hour != stunde) or  (aktuelle_uhrzeit.minute != minute):
            # Neue Minute/Stunde erkannt -> Anzeige aktualisieren
            stunde = aktuelle_uhrzeit.hour
            minute = aktuelle_uhrzeit.minute

            # Farbe passend zur Tageszeit auswählen und Wort-Matrix berechnen
            aktuelle_color=select_color_by_hour(stunde)
            matrix=set_minute_words(stunde,minute)

            # Special overwrite: an festen Datums-/Zeitpunkten (hier jeweils
            # Minute 6 um 14 bzw. 23 Uhr) wird statt der Uhrzeit ein Herz
            # in Rot angezeigt (Easter Egg).
            if(stunde == 14 and minute==6):
                matrix = set_herz()
                aktuelle_color = c_red
            elif(stunde == 23 and minute==6):
                matrix = set_herz()
                aktuelle_color = c_red

            logger.info(f"Die aktuelle Stunde {stunde} Minute {minute}")
            logger.debug(f"{matrix}")
            logger.info(f"Farbe {aktuelle_color}")

            # Buchstaben-Matrix und Minutenpunkte auf den LEDs ausgeben
            draw_matrix(matrix,aktuelle_color)
            drawMinute(minute,aktuelle_color)

        # Alle 5 Sekunden auf eine geänderte Uhrzeit prüfen
        time.sleep(5)
