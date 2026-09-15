# 04 — Integrationsplan: YouTube ↔ Claude und Claude ↔ Codex

Stand: **Schritt 2 (Analytics, nur lesend) ist gebaut** — siehe Abschnitt
*Eingerichtet* unten. Upload und Codex-Brücke sind weiterhin Plan.

---

## Das Zielbild

Die drei Teile ergeben zusammen einen geschlossenen Kreislauf, in dem jede
Produktion aus den Daten der vorherigen lernt:

```
   ┌───────────────────────────────────────────────────────────┐
   │                                                           │
   │   ①  RECHERCHE          Claude + WebSearch                │
   │       Wochenthemen, Storylines, Zahlen                    │
   │                    ↓                                      │
   │   ②  WETTBEWERBS-       /watch  (dieses Repo)             │
   │       ANALYSE           Hook-Mikroskop, Pacing            │
   │                    ↓                                      │
   │   ③  EIGENE DATEN       YouTube MCP → Analytics API       │
   │       Retention, welcher Hook hielt                       │
   │                    ↓                                      │
   │   ④  SKRIPT             Claude                            │
   │       Hook + Struktur + Text, Rechtestufe markiert        │
   │                    ↓                                      │
   │   ⑤  PRODUKTION         manuell / Render-Pipeline         │
   │                    ↓                                      │
   │   ⑥  UPLOAD             YouTube MCP → Data API v3         │
   │       Titel, Tags, Planung                                │
   │                    ↓                                      │
   │   ⑦  MESSUNG  ──────────────────────────────┐             │
   │                                             │             │
   └─────────────────────────────────────────────┘             │
                     Rückkopplung zu ③                          │
   ─────────────────────────────────────────────────────────────┘

   Querschnitt:  CODEX  als MCP-Server — übernimmt Code-Aufgaben
                 (Render-Skripte, Grafik-Templates, Automatisierung)
```

Der wertvolle Teil ist ③ → ④. Fast alle Creator schreiben Skripte nach Gefühl.
Mit Retention-Daten aus der Analytics API kann Claude sehen, **an welcher
Sekunde** Zuschauer abgesprungen sind — und das nächste Skript daraufhin bauen.
Das ist der eigentliche Hebel der ganzen Integration.

---

## Teil 1 — YouTube ↔ Claude

### Was technisch geht

Zwei Google-APIs, beide über OAuth 2.0:

| API | Liefert | Wofür |
|---|---|---|
| **YouTube Data API v3** | Upload, Metadaten, Playlists, Kommentare, Suche | Schritt ⑥ |
| **YouTube Analytics API** | Views, Retention-Kurven, Traffic-Quellen, Demografie | Schritt ③ |

### Was die Analytics API konkret hergibt — verifiziert

Der Kernnutzen steht und fällt damit, ob die Retention-Kurve wirklich abrufbar
ist. Sie ist es. Der **Audience-Retention-Report** liefert:

| Metrik / Dimension | Bedeutung |
|---|---|
| `elapsedVideoTimeRatio` | Dimension: welcher Anteil des Videos verstrichen ist (0–1) |
| `audienceWatchRatio` | Wie oft dieser Abschnitt gesehen wurde, relativ zu den Gesamtaufrufen |
| `relativeRetentionPerformance` | Vergleich zu **anderen YouTube-Videos ähnlicher Länge**. Über 0,5 = besser als der Vergleichswert |

`relativeRetentionPerformance` ist der eigentlich wertvolle Wert: Er sagt nicht
nur "hier springen Leute ab", sondern "hier springen mehr Leute ab als bei
vergleichbaren Videos". Das erste ist bei Shorts normal, das zweite ist ein
Befund.

Zwei Einschränkungen, die das Tool-Design bestimmen:

- Der Retention-Report akzeptiert **genau eine Video-ID** — keine
  komma-separierte Liste. Ein Board über 20 eigene Shorts heißt also 20
  Aufrufe.
- `maxResults` muss ≤ 200 sein.

**Wichtig zur Abgrenzung:** Die Analytics API liefert Daten nur für Kanäle, die
dir gehören. Für fremde Kanäle gibt es über die Data API nur öffentliche Werte
(Views, Likes, Kommentare) — **keine Retention**. Die Wettbewerbsanalyse in
[`analysis/`](analysis/README.md) bleibt deshalb auf `/watch` angewiesen; die
Analytics-Anbindung betrifft ausschließlich die eigenen Videos.

### OAuth-Scopes

| Scope | Wofür | Nötig ab |
|---|---|---|
| `https://www.googleapis.com/auth/yt-analytics.readonly` | Reichweite, Retention, Traffic-Quellen | Schritt 2 |
| `https://www.googleapis.com/auth/youtube.readonly` | Videoliste, Metadaten des eigenen Kanals | Schritt 2 |
| `https://www.googleapis.com/auth/youtube.upload` | Upload | Schritt 3 |
| `https://www.googleapis.com/auth/yt-analytics-monetary.readonly` | Umsatzzahlen | optional, später |

Nicht `youtube.force-ssl` nehmen — der Scope gibt Vollzugriff inklusive
Löschen, und für nichts davon besteht Bedarf.

### Die Quota-Lage — eine gute Nachricht

Die Quota-Mechanik hat sich 2025/26 grundlegend geändert, und die meisten
Anleitungen im Netz sind veraltet:

- **Früher:** `videos.insert` kostete ~1.600 Einheiten aus einem gemeinsamen
  Topf von 10.000/Tag → **maximal 6 Uploads pro Tag**. Das war der Grund, warum
  automatisierte Upload-Pipelines regelmäßig scheiterten.
- **Seit dem 4. Dezember 2025:** Upload-Kosten auf ~100 Einheiten gesenkt.
- **Seit dem 1. Juni 2026:** `videos.insert` rechnet gegen einen **eigenen
  Topf** — 1 Einheit pro Aufruf, Standardlimit **100 Aufrufe pro Tag**. Auch
  Suche hat einen eigenen Topf.

Ein Projekt hat damit drei getrennte Kontingente, und Uploads konkurrieren nicht
mehr mit Lesezugriffen. Für unseren Bedarf (6–10 Shorts/Woche) ist die Quota
damit **kein Thema mehr**.

> Vor der Umsetzung trotzdem einmal gegen die offizielle Google-Doku
> gegenprüfen — Quota-Regeln ändern sich, und die Zahlen oben stammen aus
> Sekundärquellen.

### Umsetzungsoptionen

**Option A — Fertigen MCP-Server nutzen.**
Es gibt mehrere (Upload-fokussiert, Analytics-fokussiert, Composio-Toolkit).
Schnell startklar.
*Nachteil, und der wiegt schwer:* Wir würden einem fremden Repo
Schreibzugriff auf deinen YouTube-Kanal geben. Bei einem Kanal, der
Geschäftsgrundlage werden soll, ist das die falsche Abwägung.

**Option B — Eigener schlanker MCP-Server in diesem Repo. ← Empfehlung**

Passt strukturell perfekt: Das Repo hat bereits eine saubere Python-Konvention
(`scripts/whisper.py` ist reiner Stdlib-Code), eine Setup-/Preflight-Mechanik
(`scripts/setup.py`), Config-Handling über `~/.config/watch/.env` mit `0600`,
und mit `.claude-plugin/` sowie `.codex-plugin/` bereits Multi-Surface-Packaging.

Ein `scripts/youtube.py` plus MCP-Wrapper mit vier Tools deckt alles ab:

| Tool | Zweck |
|---|---|
| `youtube_upload` | Video hochladen, Metadaten setzen, terminieren |
| `youtube_analytics` | Retention-Kurve und Kennzahlen für ein Video |
| `youtube_channel_stats` | Kanalentwicklung über Zeit |
| `youtube_competitor` | Öffentliche Daten fremder Videos → Übergabe an `/watch` |

Aufwand: überschaubar, ein Arbeitsblock. Dafür: voller Einblick in den Code,
Credentials bleiben lokal, und es fügt sich in das bestehende Plugin ein statt
daneben zu stehen.

### Sicherheit

- OAuth-Credentials gehören **nicht** ins Repo. Muster von `watch` übernehmen:
  `~/.config/watch/.env`, Rechte `0600`.
- `.gitignore` prüfen, bevor irgendetwas mit Tokens angelegt wird.
- **Scopes minimal halten.** `youtube.upload` und `yt-analytics.readonly`
  reichen; `youtube.force-ssl` gibt deutlich mehr Rechte als nötig.
- Upload grundsätzlich als **`private` oder `unlisted`** anlegen. Das
  Veröffentlichen bleibt eine bewusste menschliche Entscheidung — ein Agent,
  der versehentlich öffentlich publiziert, ist ein Problem, das man nicht
  zurücknehmen kann.

---

## Eingerichtet: `scripts/youtube.py`

Der lesende Teil steht. Reine Stdlib, keine Abhängigkeiten, read-only Scopes.

### Einrichtung (einmalig, ~15 Minuten)

1. [console.cloud.google.com](https://console.cloud.google.com) → neues Projekt
2. Zwei APIs aktivieren: **YouTube Data API v3** und **YouTube Analytics API**
3. OAuth-Zustimmungsbildschirm → **External** → **Testing**, dich selbst als
   Testnutzer eintragen. Kein Google-Review nötig, solange nur du das nutzt.
4. Anmeldedaten → **OAuth-Client-ID** → Anwendungstyp **Desktop-App**
5. ID und Secret in `~/.config/watch/.env` eintragen:
   ```
   YOUTUBE_CLIENT_ID=....apps.googleusercontent.com
   YOUTUBE_CLIENT_SECRET=...
   ```
6. Einmal autorisieren:
   ```bash
   python3 scripts/youtube.py auth
   ```
   Öffnet den Browser, fängt den Callback auf `127.0.0.1` ab und legt den
   Refresh-Token unter `~/.config/watch/youtube-token.json` (Modus `0600`) ab.

### Befehle

```bash
# Die erfolgreichsten eigenen Shorts
python3 scripts/youtube.py videos --short-form --limit 50

# Retention-Kurve eines Videos — der eigentliche Zweck
python3 scripts/youtube.py retention <video-id>

# Kanalentwicklung Tag für Tag
python3 scripts/youtube.py channel --days 90

# Woher die Aufrufe kamen (optional pro Video)
python3 scripts/youtube.py traffic --days 30 --video-id <video-id>
```

`retention` liefert neben der Rohkurve eine Zusammenfassung:

- **`steepest_drop`** — wo am meisten Zuschauer abspringen, in **Sekunden**
  umgerechnet statt nur als Anteil. Bei einem 30-Sekunden-Short ist "Sekunde 3"
  eine Ansage, "0,1" nicht.
- **`worst_relative_performance`** — der Punkt mit dem schlechtesten Vergleich
  zu Videos ähnlicher Länge, plus `below_average` als Flag. Das ist der Wert,
  der einen Befund von normalem Short-Form-Verhalten unterscheidet.

### Sicherheit

Die Scopes sind `yt-analytics.readonly` und `youtube.readonly` — **kein**
Upload, kein Bearbeiten, kein Löschen. `youtube.force-ssl` wurde bewusst nicht
genommen. Ohne gesetzte Credentials tut das Skript nichts.

> **Zu bedenken vor dem nächsten Release:** `scripts/` wird ins
> `watch.skill`-Bundle und den Plugin-Tarball gepackt. `youtube.py` würde also
> mit ausgeliefert. Das Skript ist ohne Credentials inert, aber es erweitert
> den Funktionsumfang des veröffentlichten Plugins um einen OAuth-Client. Falls
> das nicht gewollt ist: nach `playbooks/` verschieben (dort greift
> `export-ignore`) oder vor dem Tag entfernen.

---

## Teil 2 — Claude ↔ Codex

> **Korrektur gegenüber der ersten Fassung dieses Plans.** Dort stand, Codex
> lasse sich per `codex mcp-server` als MCP-Server in Claude Code einhängen.
> Das stimmt nicht mehr: **`codex mcp-server` wurde mit Codex CLI v0.149.1 am
> 24. August 2026 abgekündigt.** Der Befehl stammte aus der Zeit vor dem Codex
> **App Server** — einem vollwertigen JSON-RPC-2.0-Daemon, der seit Anfang 2026
> der maßgebliche Integrationspunkt ist. Für den Weg Claude Code → Codex gibt
> es inzwischen etwas Besseres als eine MCP-Verdrahtung: ein offizielles Plugin.

### Der aktuelle Weg: das offizielle OpenAI-Plugin

OpenAI pflegt ein Plugin, das Codex direkt in Claude Code verfügbar macht:
[`openai/codex-plugin-cc`](https://github.com/openai/codex-plugin-cc). Es
umschließt die lokale Codex-CLI samt App Server und **erbt dabei deine
vorhandene Authentifizierung, deine `config.toml`, deine MCP-Konfiguration und
deine Umgebungsvariablen** — es gibt also keine zweite Konfiguration zu pflegen.

**Voraussetzungen:** ChatGPT-Abo (Free genügt) oder OpenAI-API-Key, dazu
Node.js 18.18 oder neuer.

**Installation**, in Claude Code:

```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

`/codex:setup` prüft, ob Codex einsatzbereit ist, und installiert es bei Bedarf
per npm nach. Falls Codex nicht angemeldet ist: `!codex login`.

**Befehle:**

| Befehl | Zweck |
|---|---|
| `/codex:review` | Code-Review der uncommitteten Änderungen oder eines Branches |
| `/codex:adversarial-review` | Review, das Designentscheidungen und Annahmen gezielt angreift |
| `/codex:rescue` | Aufgabe an Codex delegieren (Debugging, Fixes, Untersuchungen) |
| `/codex:transfer` | Aus der Claude-Code-Session einen persistenten Codex-Thread erzeugen |
| `/codex:status` | Laufende und kürzliche Codex-Jobs |
| `/codex:result` | Ergebnis eines abgeschlossenen Jobs |
| `/codex:cancel` | Laufenden Hintergrund-Job abbrechen |

> **Zusammengeführt mit der Session „Codex mit Claude/Vault verbinden".** Die
> hatte drei Wege genannt (gemeinsamer Ordner, MCP-Bridge, Shell-Exec) und lag
> bei der MCP-Variante aus demselben Grund daneben wie diese Session hier. Der
> gemeinsame Ordner ist dagegen richtig — und beantwortet zugleich die
> Vault-Frage. Der vollständige, abgeglichene Weg inklusive Vault-Einrichtung
> steht in [`docs/codex-and-vault.md`](../../docs/codex-and-vault.md).

### Die Gegenrichtung steht schon

`/watch` in Codex nutzen geht bereits — das Repo hat `.codex-plugin/plugin.json`,
und der Installationsweg ist dokumentiert:

```bash
git clone https://github.com/taoufik123-collab/claude-watch.git ~/.codex/skills/watch
```

Die Brücke ist also in beide Richtungen offen.

### Wofür das in diesem Workflow taugt — ehrlich betrachtet

Ein zweiter Agent, der dasselbe tut wie der erste, bringt nichts. Sinnvoll wird
es dort, wo die Trennung inhaltlich ist:

- **`/codex:adversarial-review` auf `scripts/youtube.py`.** Der Netzwerkpfad
  ist gegen die echten Google-Endpunkte geprüft (Request-Aufbau,
  Formularkodierung, 401/403-Behandlung). Offen bleiben der
  OAuth-Zustimmungsflow — der braucht Browser und echte Credentials — und das
  Parsen echter Antwortdaten. Ein unabhängiges Review dieser Stellen ist mehr
  wert als ein weiteres Feature.
- **Render-Pipeline für die Grafikformate** (Formate 2, 3, 9): Daten rein,
  fertiges MP4 raus. Abgegrenzt, gut spezifizierbar — typische Delegationsarbeit.
- **Batch-Verarbeitung** von Thumbnails und Textoverlays.

Claude behält Recherche, Analyse, Strategie und Skript; Codex bekommt umrissene
Implementierungs- und Prüfaufgaben.

## Reihenfolge

Vorschlag, nach Nutzen pro Aufwand:

| Schritt | Was | Warum zuerst |
|---|---|---|
| **1** | `/watch`-Wettbewerbsanalyse (Schritt ②) | Braucht **keine** Integration — läuft heute schon. Direkt nutzbar. |
| ~~**2**~~ | ~~YouTube **Analytics**, nur lesend~~ | ✅ gebaut — `scripts/youtube.py` |
| **3** | YouTube **Upload** | Erst wenn ein Format steht und Frequenz da ist. Vorher automatisiert man Chaos. |
| **4** | Codex-Plugin für Claude Code | Sofort möglich, vier Befehle. Erster Einsatz: adversarial review von `scripts/youtube.py`. |

Schritt 1 ist sofort möglich. Schritt 2 ist gebaut. Schritt 3 lohnt erst ab
Volumen. Schritt 4 ist inzwischen so billig (vier Befehle, kein eigener Code),
dass die alte Einordnung "Komfort, später" nicht mehr stimmt — es lohnt sich
jetzt, schon wegen des Reviews.

---

## Was vorher geklärt werden muss

- **Google-Cloud-Projekt** vorhanden oder neu anlegen? Für die APIs nötig.
- **OAuth-Verifizierung:** Für den Eigenbedarf reicht der Testing-Modus mit dem
  eigenen Konto als Testnutzer — kein Google-Review nötig. Nur bei Weitergabe an
  Dritte wird es aufwendig.
- **Kanal:** Neuer NFL-Kanal oder bestehender WM-Kanal? Das hat Auswirkungen
  über die Technik hinaus — ein Kanal mit WM-Historie hat ein Publikum, das für
  NFL nur teilweise passt, und der Algorithmus braucht dann Zeit zum Umlernen.
  Meine Tendenz: **neuer Kanal**, saubere Themen-Signale.

  **Aber für die Analytics-Anbindung gilt das Gegenteil:** Ein neuer Kanal hat
  keine Daten, also gibt es in den ersten Wochen nichts zu lesen. Der alte
  WM-Kanal hat welche — und Hook-Retention ist **sportartunabhängig**. Welcher
  Hook-Typ deine Zuschauer in Sekunde 2 gehalten hat, ist auf NFL übertragbar,
  auch wenn das Thema nicht passt. Falls der WM-Kanal noch existiert, ist er
  damit vom ersten Tag an nutzbares Trainingsmaterial für die Skripte, selbst
  wenn dort nie wieder etwas hochgeladen wird. Das wäre ein Argument, die
  Analytics-Anbindung **zuerst auf den alten Kanal** zu richten.
- **Ablageort für Rohmaterial** — lokal, Cloud, oder im Obsidian-Vault, den
  `/watch` bereits anbinden kann.
