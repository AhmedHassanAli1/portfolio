# LeadFlow

LeadFlow är ett enkelt SaaS-verktyg för små serviceföretag som hjälper dem att hantera inkommande kundförfrågningar och automatisera uppföljning. Syftet är att minska antalet missade affärer genom att säkerställa att alla leads följs upp.

---

# Funktioner

## Autentisering

* Registrering av användare
* Inloggning med JSON Web Token (JWT)
* Isolering av data per användare

## Leads

* Skapa leads via API (simulerad inkommande kontakt)
* Visa leads i en dashboard
* Uppdatera status (till exempel "NY" eller "KONTAKTAD")

## Automation

* Skapa regler för uppföljning baserat på tid
* Exempel: skicka ett meddelande efter 24 timmar om leaden inte hanterats
* Körs automatiskt i bakgrunden via schemalagd process

## Användargränssnitt

* Enkel dashboard byggd med HTML och Tailwind CSS
* Fokus på tydlighet och snabb användning
* Anpassad för demonstration och vidare utveckling

---

# Projektstruktur

```
lead-saas/
│
├── server/
│   ├── index.js        # Startar servern
│   ├── db.js           # In-memory databas
│   ├── routes.js       # API endpoints
│   ├── auth.js         # Autentisering och lösenordshantering
│   ├── middleware.js   # Skydd av privata endpoints
│   └── jobs.js         # Automation (schemalagda jobb)
│
├── client/
│   ├── login.html      # Inloggningssida
│   ├── dashboard.html  # Dashboard
│   ├── app.js          # Frontend logik
│   └── auth.js         # Hantering av login
│
├── package.json
└── README.md
```

---

# Installation

## Förutsättningar

* Node.js (version 18 eller senare rekommenderas)
* npm

## Steg

1. Klona eller ladda ner projektet

2. Installera beroenden

```
npm install
```

3. Skapa en lokal `.env`-fil utifrån mallen och fyll i egna värden

```
cp .env.example .env
```

4. Starta servern

```
npm start
```

Servern körs på:

```
http://localhost:3000
```

5. Öppna frontend

Öppna filen:

```
client/login.html
```

i en webbläsare.

---

# Användning

## 1. Skapa användare

Skicka en POST-request till:

```
/register
```

med:

```json
{
  "email": "test@example.com",
  "password": "123456"
}
```

## 2. Logga in

POST:

```
/login
```

Svar:

```json
{
  "token": "..."
}
```

Spara token lokalt (frontend gör detta automatiskt).

---

## 3. Skapa lead

POST:

```
/sms
```

Headers:

```
Authorization: <token>
```

Body:

```json
{
  "message": "Behöver hjälp med elinstallation"
}
```

---

## 4. Hämta leads

GET:

```
/leads
```

---

## 5. Uppdatera status

POST:

```
/leads/:id
```

Body:

```json
{
  "status": "KONTAKTAD"
}
```

---

## 6. Skapa automation

POST:

```
/automations
```

Body:

```json
{
  "delayHours": 24,
  "message": "Vill du boka detta?"
}
```

---

## 7. Hämta automationer

GET:

```
/automations
```

---

# Hur automation fungerar

Systemet kör en bakgrundsprocess som regelbundet:

1. Hämtar alla leads
2. Hämtar användarens automation-regler
3. Kontrollerar:

   * om leaden fortfarande har status "NY"
   * om tillräcklig tid har passerat
4. Simulerar utskick av meddelande (loggas i servern)

---

# Begränsningar (MVP)

Detta är en minimal version av produkten och innehåller följande begränsningar:

* Data lagras i minnet (försvinner vid omstart)
* Ingen riktig SMS-integration
* Ingen betalningslösning
* Ingen användarhantering utöver grundläggande login
* Ingen validering eller rate limiting


