# KAU News & Events – Publiceringsplattform med rollstyrning

En webbplattform byggd från grunden i ett kursprojekt (Software Engineering, Karlstads universitet) för publicering och hantering av nyheter och evenemang, med flera användarroller, godkännandeflöden och kalenderfunktionalitet.

## Om projektet

Plattformen låter en organisation publicera nyheter och evenemang, samla anmälningar/närvaro och hantera innehåll genom ett rollbaserat granskningsflöde – från idé till godkänd publicering. Projektet byggdes av ett projektteam från grunden, utan att utgå från ett befintligt ramverk för innehållshantering.

### Huvudfunktioner

- **Flera användarroller och behörighetsnivåer** – Admin, Publicist och vanlig Användare, med en anpassad användarmodell (`authuser`) som validerar rollkombinationer
- **Godkännandeflöde** – publicister granskar inskickade evenemang/nyheter och kan godkänna eller avslå dem, med automatiska e-postnotifieringar vid avslag
- **Kalender med återkommande evenemang** – datumlogik som stödjer återkommande mönster (RRULE-liknande)
- **Anmälan/närvaro** – användare kan anmäla sig till evenemang, och arrangörer kan följa upp närvaro
- **Filtrering** – innehåll kan filtreras på avdelning och tagg via en enkel klientlogik i vanilla JavaScript
- **Anpassad Django-admin** (`custom_admin`) för behörighetsstyrd administration

## Arkitektur & appar

Projektet är uppdelat i tydligt avgränsade Django-appar efter ansvarsområde:

| App | Ansvar |
|---|---|
| `authuser` | Anpassad användarmodell med roller (Admin/Publicist/Användare) och rollvalidering |
| `login` / `Registration` | Autentisering och kontoregistrering |
| `Publication` | Nyheter/evenemang, inskick och godkännandeflöde, e-postnotifiering |
| `CalenderEvents` | Kalendervy och hantering av återkommande evenemang |
| `attendance` | Anmälan och närvaroregistrering kopplat till evenemang |
| `staffuser` | Granskningsvyer och filtrering för publicister/personal |
| `custom_admin` | Anpassad adminpanel |
| `frontpage` | Publik startsida och sidvisning |

## Teknikstack

Python, Django, PostgreSQL, Docker & Docker Compose, Git, HTML/CSS (handskriven), vanilla JavaScript, e-postintegration (Django mail)

## Kom igång lokalt

Projektet är fullt containeriserat med Docker.

```bash
# Bygg och starta
docker compose build
docker compose up

# Gå in i webb-containern
docker exec -it deploy-softeng-2025-1-web /bin/bash

# Gå in i databas-containern
docker exec -it deploy-softeng-2025-1-postgres /bin/bash
# och därefter:
su postgres
psql
```

Se filen `web/run` för fler användbara kommandon.

Efter att fixtures laddats finns ett admin-konto:
- **Användarnamn:** `admin`
- **Lösenord:** `admin`

> Detta är enbart avsett för lokal utveckling/demo – ändra alltid standardlösenord innan en eventuell driftsättning.

## Innehåll

```
.
├── web/               # Django-projektet (se apparna i tabellen ovan)
├── tests/             # Tester
└── README.md
```
