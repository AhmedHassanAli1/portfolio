# WGER – Vidareutveckling av öppen webbapplikation (fitness & nutrition)

> **Om detta repo:** WGER är en befintlig, öppen källkods-webbapplikation för träning- och kostspårning. Det här repot innehåller vårt teams vidareutveckling av WGER som kursprojekt i Software Engineering (DVGB20) vid Karlstads universitet – **inte** ett projekt byggt från grunden. Se avsnittet [Min roll i projektet](#min-roll-i-projektet) nedan för vad jag personligen ansvarade för.

## Projektöversikt

Projektet genomfördes i kursen *Fundamentals of Software Engineering* (DVGB20) vid Karlstads universitet. Syftet var att vidareutveckla webbapplikationen WGER enligt agil Scrum-metodik över fem sprintar, med fokus på:

- Förbättrad användarupplevelse för tränings- och kostplaner
- Förbättrade utvecklingsflöden och dokumenterad arkitektur
- Förbättringar av MVT-arkitekturen (Model-View-Template)

## Min roll i projektet

Jag var en av fem utvecklare i teamet (tillsammans med Huthaifa, Tasneem, Anton och Filip, under ledning av Scrum Master Linus Haag). Jag bidrog bland annat med:

- Att sätta mig in i en stor, befintlig kodbas byggd på Django (MVT-arkitektur)
- Nya funktioner samt förbättringar av arkitektur och dokumentation
- Arbete med användarhantering, autentisering och skydd av person-/kontodata i en flerroll-miljö
- Testning och driftsättning i containerbaserad miljö (Docker) med PostgreSQL/SQLite

## Funktioner

- **Träningsprogram** – användare kan skapa, hantera och följa upp egna träningsplaner
- **Kostplaner** – logga näringsintag och kostschema
- **Behörigheter & säkerhet** – separata roller för admin/gym-personal och vanliga användare, med skydd av inloggnings- och kontouppgifter

## Teknikstack

Python, Django (MVT), PostgreSQL/SQLite, Docker & Docker Compose, Git, Scrum

## Kom igång lokalt

### Krav
- Git
- Docker
- Python 3.x
- PostgreSQL eller SQLite

### Klona repot

```bash
git clone <repo-url>
cd group-02-dvgb20-vt-25
```

### Sätt upp utvecklingsmiljön

```bash
# 1. Navigera till projektets docker/dev-mapp
cd docker/dev

# 2. Kopiera miljöfilen och fyll i egna värden (t.ex. WGER_CODEPATH)
cp .env.example .env

# 3. Starta Docker-containrarna
docker compose up --watch

# 4. Gå in i web-containern
docker compose exec web /bin/bash

# 5. Initiera applikationen
wger bootstrap
python3 manage.py migrate
python3 manage.py sync-exercises
wger load-online-fixtures

# 6. Starta servern
python3 manage.py runserver 0.0.0.0:8000
```

Applikationen är sedan tillgänglig på `http://localhost:8000`.

## Användning

**Skapa träningsprogram:** registrera/logga in → gå till träningssidan → lägg till övningar och mål.

**Skapa kostplaner:** registrera/logga in → gå till kostsidan → logga måltider för att följa dagligt kaloriintag.

## Dokumentation

Teamets fullständiga arkitektur-, design- och utvecklardokumentation finns i projektets GitLab-wiki (Karlstads universitets interna GitLab – kräver universitetskonto för åtkomst):

- Arkitekturdokumentation
- Kodddokumentation
- Designdokumentation
- Utvecklardokumentation
- Slutanvändardokumentation
- Presentationer
- Utvärderingar och resultat

## Upphovspersoner

**Scrum Master / projektledare:** Linus Haag
**Utvecklare:** Huthaifa, Tasneem, Ahmed Hassan Ali, Anton, Filip
**Särskilt tack:** Leonardo Horn Iwaya, Pavithra Herath, Hans Hedbom

## Projektstatus

Kursprojektet är avslutat (vårterminen 2025). Den bas-applikation som vidareutvecklats (WGER) är i sig ett aktivt underhållet öppen källkods-projekt; se [wger-projektets officiella repo](https://github.com/wger-project/wger) för den senaste versionen.
