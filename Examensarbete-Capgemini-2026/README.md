# IoT Pet Tracker – Examensarbete i samarbete med Capgemini

Ett distribuerat IoT-system för säker, GPS-baserad positionsspårning av husdjur, utvecklat som examensarbete på Högskoleingenjörsprogrammet i datateknik vid Karlstads universitet, i samarbete med Capgemini.

## Om projektet

Systemet består av en bärbar tracker-enhet och en Raspberry Pi-baserad basstation som kommunicerar trådlöst över långa avstånd via LoRa, och vidarebefordrar positionsdata till en mobilapplikation via Bluetooth Low Energy (BLE). All kommunikation krypteras end-to-end med AES-256 för att skydda positionsdata från avlyssning och manipulation.

Fokus i arbetet har legat på:
- Säker, energieffektiv trådlös kommunikation mellan inbyggda enheter
- Kryptering och autentisering i en resursbegränsad IoT-miljö
- Robust drift och felhantering i en Linux/Raspberry Pi-miljö

## Arkitektur

```
[ Tracker (MicroPython) ]
   GPS-modul → position
   AES-256 (CBC) kryptering
        │  LoRa (radio)
        ▼
[ Basstation (Raspberry Pi, Python) ]
   LoRa-mottagning + AES-dekryptering
   BLE GATT-server (custom pairing/passkey)
        │  BLE
        ▼
[ Mobilapplikation ]
   Visar position i realtid
```

## Teknisk implementation

**Tracker** (`src/Tracker_secure.py`) – MicroPython på mikrokontroller:
- Läser GPS-position via UART
- Krypterar payload med AES-256 CBC innan sändning
- Skickar data trådlöst via LoRa (SPI mot radiomodul)

**Basstation** (`src/basstation_secure.py`) – Python på Raspberry Pi:
- Tar emot och avkodar LoRa-paket direkt via SPI-register mot radiomodulen
- Dekrypterar payload med AES-256 CBC
- Exponerar en BLE GATT-server (via BlueZ/D-Bus) med anpassad pairing-hantering (fast passkey) för säker anslutning till mobilapplikationen
- Hanterar konkurrens mellan LoRa-mottagning och BLE-serverns event-loop med trådhantering (`threading`)

## Säkerhet

- **AES-256 CBC-kryptering** av all positionsdata som skickas mellan tracker och basstation
- **PKCS7-padding** för korrekt blockstorlek
- **BLE-pairing med passkey** för att förhindra obehörig anslutning till basstationen
- Delade nycklar/PIN-koder hanteras via en lokal `config.py` som **inte** checkas in i git – se `src/config_example.py` för förväntad struktur

> Notera: `SHARED_KEY` och `BLE_PASSKEY` i exempelfilen är placeholder-värden. I en verklig driftsättning genereras en unik, slumpmässig 256-bitars nyckel per enhetspar.

## Teknikstack

Python, MicroPython, Raspberry Pi, Linux, LoRa (SPI), Bluetooth Low Energy (BLE/BlueZ/D-Bus), AES-256 (CBC), GPS, UART, multitrådad programmering

## Innehåll

```
Examensarbete-Capgemini-2026/
├── src/
│   ├── Tracker_secure.py       # Kod för tracker-enheten (MicroPython)
│   ├── basstation_secure.py    # Kod för basstationen (Raspberry Pi)
│   └── config_example.py       # Mall för nycklar/PIN-koder (config.py checkas ej in)
├── forstudie_pet-tracker.pdf   # Förstudie/projektplan
└── README.md
```

## Status

Examensarbetet är genomfört under vårterminen 2026. Koden i detta repo är ett urval av kärnfunktionaliteten (säker kommunikation) från det fullständiga systemet.

Fullständig rapport publicerad på DiVA: [Läs examensarbetet](https://www.diva-portal.org/smash/record.jsf?pid=diva2%3A2072275)
