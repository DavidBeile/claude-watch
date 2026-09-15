---
typ: handoff
projekt: claude-watch / NFL-Shorts
datum: 2026-09-15
session-dauer: ein Arbeitstag (09:56–22:10 UTC, mit Pausen)
tags: [handoff]
---

# Handoff: NFL-Shorts-Playbook + YouTube/Codex-Anbindung — 2026-09-15

> **Übergabe von einer Cloud-Session an eine lokale Session auf dem Mac.**
> Der Grund für den Wechsel steht in Block „Was gescheitert ist" — kurz: Die
> Cloud-Session kommt weder an YouTube noch an den Obsidian-Vault. Beides
> funktioniert lokal.

## 🎯 Ziel

Nach dem Ende der WM 2026 einen NFL-Shorts-Kanal aufbauen — **englischsprachig,
faceless**, auf dem **bestehenden WM-Kanal**. Dazu ein datengetriebener
Workflow: `/watch` zur Wettbewerbsanalyse, YouTube Analytics für die eigene
Retention, Codex als zweiter Agent für Review und abgegrenzte Implementierung.

## 📊 Aktueller Stand

### Was funktioniert

- **NFL-Playbook vollständig** — `playbooks/nfl-shorts/`: Marktanalyse,
  Copyright (3 Ebenen, Risikostufen A–D), 14 Formate, Integrationsplan,
  Quellenliste. Auf Englisch + faceless + remote ausgerichtet.
- **`hookboard.py`** — aggregiert viele `/watch`-Reports zu einem Musterboard,
  inkl. Median-Split nach Views (Top vs. Rest). Reine Stdlib, **26 Tests grün**,
  an Beispieldaten durchgelaufen.
- **`scripts/youtube.py`** — lesender YouTube Data + Analytics Client. Liefert
  Retention-Kurve mit `steepest_drop` (in Sekunden) und
  `worst_relative_performance`. Read-only Scopes. **20 Tests grün**,
  HTTP-Layer gegen die echten Google-Endpunkte verifiziert.
- **Hook-Mikroskop-Fix** — übersprang vorher alle Videos < 30s, also die
  Mehrheit aller Shorts. Kurze Videos bekommen jetzt die Wort-Zeitstempel,
  nur der Frame-Repass entfällt. **12 Tests grün**.
- **`docs/codex-and-vault.md`** — vollständige Codex-Anleitung, gegen die
  aktuellen Quellen geprüft.

### Was nicht funktioniert / unfertig

- **Die `/watch`-Wettbewerbsanalyse ist nie gelaufen.** Das Harness steht
  komplett bereit, aber kein einziges Short wurde analysiert. Das ist die
  größte offene Lücke — alle Hook-Empfehlungen im Playbook sind bislang
  **begründete Annahmen, keine Messung.**
- **`scripts/youtube.py` ist nicht live durchgelaufen.** Verifiziert sind
  Request-Aufbau, Formularkodierung und die 401/403-Pfade gegen die echten
  Endpunkte. **Nicht** verifiziert: der OAuth-Zustimmungsflow (braucht Browser
  + Credentials) und das Parsen echter Antwortdaten. Es existiert kein
  Google-Cloud-Projekt.
- **Codex ist nicht verbunden.** Weder das Plugin installiert noch `AGENTS.md`
  im Vault angelegt.
- ~~Der `/watch`-Report zum Codex-Video liegt ungelesen im Vault.~~
  **Erledigt** — die lokale Session hat ihn nach
  `playbooks/nfl-shorts/analysis/video-codex-report.md` gepusht, er ist
  ausgewertet und in `docs/codex-and-vault.md` eingearbeitet.
- **Kein Short produziert.** Es gibt bisher nur Strategie und Werkzeug.

### Status

- Committed/gepusht: **ja** — 9 Commits auf `claude/kind-goldberg-uxgdfp`,
  Working Tree sauber
- Tests grün: **ja** — 44 in `scripts/tests/` (2 übersprungen, vorbestehend),
  26 in `playbooks/nfl-shorts/analysis/`

## 📂 Files in Arbeit

Alle Pfade relativ zum Repo-Root. **Alles committet und gepusht.**

### Playbook (Strategie)
- `playbooks/nfl-shorts/README.md` — Einstieg, Entscheidungsstand
- `playbooks/nfl-shorts/01-marktanalyse.md` — NFL vs. WM, Sprachentscheidung, November-Block
- `playbooks/nfl-shorts/02-copyright.md` — **das wichtigste Dokument**: 3 Ebenen, Risikostufen A–D
- `playbooks/nfl-shorts/03-formate.md` — 14 Formate, Faceless-Ausführung, Startempfehlung
- `playbooks/nfl-shorts/04-integration-plan.md` — YouTube + Codex, Reihenfolge
- `playbooks/nfl-shorts/05-quellen.md` — Belege, inkl. blockierter Quellen

### Wettbewerbsanalyse (Werkzeug, ungenutzt)
- `playbooks/nfl-shorts/analysis/README.md` — **Protokoll in 5 Schritten, hier anfangen**
- `playbooks/nfl-shorts/analysis/hookboard.py` — Aggregator, 380 Zeilen
- `playbooks/nfl-shorts/analysis/test_hookboard.py` — 26 Tests
- `playbooks/nfl-shorts/analysis/candidates.md` — leere Arbeitsliste, 18 Zeilen
- `playbooks/nfl-shorts/analysis/coding.example.json` — Kopiervorlage

### Code
- `scripts/youtube.py` — neu, 549 Zeilen, read-only Client
- `scripts/tests/test_youtube.py` — 20 Tests
- `scripts/hook.py` — geändert, < 30s-Skip entfernt
- `scripts/watch.py` — geändert, Gate + präzise Skip-Gründe
- `scripts/report.py` — geändert, weist `frames_source` aus
- `scripts/setup.py` — geändert, `YOUTUBE_CLIENT_ID/SECRET` im ENV-Template
- `scripts/tests/test_hook.py` — 12 Tests

### Doku
- `docs/codex-and-vault.md` — Codex-Anleitung
- `docs/templates/vault-AGENTS.md` — Vorlage fürs Vault-Wurzelverzeichnis
- `.gitattributes` — `playbooks/` export-ignored (sonst im Skill-Bundle)
- `CHANGELOG.md` — Unreleased-Block

## 🔄 Geändert seit Start

- **Sprache: Englisch statt Deutsch.** Ich hatte Deutsch empfohlen
  (Muttersprachen-Vorteil im Hook, wachsender deutscher Markt, dünnere
  Konkurrenz). Der User hat Englisch entschieden. Das Playbook ist darauf
  umgebaut; die Begründung für Deutsch steht bewusst weiter in `01-` drin,
  damit die Abwägung nachvollziehbar bleibt.
- **Faceless statt Talking Head.** Format 5 („The Outsider Take") wurde von
  Gesicht auf Voiceover umgebaut. Wichtige Randbedingung im Playbook:
  **eigene Stimme, keine AI-Stimme** — sonst greift YouTubes
  Inauthentic-Content-Policy auf Kanalebene.
- **Kein München-Trip.** Format 6 ist ein Remote-Block geworden; eigenes
  Stadionmaterial entfällt.
- **NFL-Videos auf dem bestehenden WM-Kanal.** Ich hatte einen neuen Kanal
  empfohlen (saubere Themensignale). Entschieden ist der alte. Konsequenz, die
  in `04-` dokumentiert ist: Die ersten 10–20 NFL-Shorts werden dem
  WM-Publikum ausgespielt und performen schlecht — das ist **Audience-Mismatch,
  kein Content-Problem.** Maßgeblich sind stattdessen der Anteil neuer
  Zuschauer und die Traffic-Quelle. Vorteil: Analytics-Daten ab Tag eins, und
  Hook-Retention ist sportartunabhängig übertragbar.
- **Verworfen: eigener YouTube-MCP-Server von Dritten.** Stattdessen eigenes
  Skript in `scripts/`, weil ein fremdes Repo sonst Schreibzugriff auf den
  Kanal bekäme.
- **Verworfen: `codex mcp-server`.** Siehe unten.

## ❌ Was gescheitert ist

**Brutal ehrlich — das hier verhindert, dass die nächste Session dieselben
Sackgassen abläuft.**

- **Versucht:** `/watch` auf NFL-Shorts und auf das Codex-Video
  (`L7NPhaUBpZE`) aus der Cloud-Session.
  **Warum gescheitert:** `www.youtube.com` und `googlevideo.com` werden vom
  Egress-Proxy mit **403 beim CONNECT** abgelehnt (Org-Policy). Zusätzlich sind
  `yt-dlp` und `ffmpeg` im Container nicht installiert.
  **Lehre:** Aus der Cloud-Session **niemals** `/watch` auf YouTube versuchen.
  Das ist der Hauptgrund für den Wechsel auf lokal. Lokal läuft es (belegt:
  der User hat den Video-Report lokal erzeugt und in den Vault ingested).

- **Versucht:** Aus dem Fehlschlag oben zu schließen, „Google ist nicht
  erreichbar", und das als Begründung zu nehmen, warum `scripts/youtube.py`
  ungetestet bleiben muss.
  **Warum gescheitert:** Falsche Verallgemeinerung. Blockiert sind nur
  `youtube.com` und `googlevideo.com`. `oauth2.googleapis.com`,
  `youtubeanalytics.googleapis.com` und `www.googleapis.com` sind **erreichbar**
  — ein echter API-Call liefert einen sauberen 401.
  **Lehre:** Egress **pro Host** testen, nie von einem blockierten Host auf
  einen Anbieter schließen. Nach der Korrektur ließ sich der HTTP-Layer doch
  verifizieren.

- **Versucht:** Codex per `codex mcp-server` in Claude Code einhängen.
  **Warum gescheitert:** Der Befehl wurde mit **Codex CLI v0.149.1 am
  24.08.2026 abgekündigt**, ersetzt durch den Codex App Server. Die
  Vorgänger-Session „Codex mit Claude/Vault verbinden" hatte denselben Fehler
  („MCP-Bridge").
  **Lehre:** Bei CLI-Integrationen immer das **Datum der Quelle** prüfen.
  Richtig ist das offizielle Plugin `openai/codex-plugin-cc`.

- **Versucht:** Aus einem Datum in einer Suchergebnis-Zusammenfassung
  (31.03.2026) zu schließen, das verlinkte YouTube-Video zeige den
  abgekündigten Weg.
  **Warum gescheitert:** Das Datum stimmte nicht. Der `/watch`-Report zeigt:
  Das Video demonstriert exakt den **aktuellen** Weg. `mcp`, `config.toml`
  und `AGENTS.md` kommen im Transkript nicht ein einziges Mal vor.
  **Lehre:** Metadaten aus Suchergebnis-Zusammenfassungen sind unzuverlässig.
  Wenn die Quelle nicht erreichbar ist, ist die richtige Aussage „weiß ich
  nicht" — nicht eine datumsgestützte Vermutung.

- **Versucht:** Den Verlauf der Session „Codex mit Claude/Vault verbinden"
  (`session_01TuU46vALvLiaeGZ4qo3t8j`) auszulesen.
  **Warum gescheitert:** `list_events` ist im Toolset dieser Session nicht
  verfügbar; ihr Branch `claude/exciting-keller-9o45cv` wurde **nie gepusht**
  (existiert auf dem Remote nicht); Cloud-Sessions können auf `SendMessage`
  nicht antworten.
  **Lehre:** Von anderen Cloud-Sessions ist nur die automatische
  Zusammenfassung zugänglich. Wenn Inhalte übergeben werden sollen: **pushen.**

- **Versucht:** Die NFL-Lizenzbedingungen im Original zu lesen.
  **Warum gescheitert:** `nfl.com`, `media.nfl.com`, `digiday.com` und
  `sportsvideo.org` sind per Egress-Policy blockiert.
  **Lehre:** Alle NFL-Lizenzaussagen in `02-copyright.md` stammen aus
  **Sekundärquellen**. Vor kommerzieller Nutzung die
  „NFL Video Highlights License" und die Social-Media-Rules **im Original
  prüfen** — lokal möglich. In `05-quellen.md` markiert.

- **Versucht:** `spawn_task`, um den Hook-Mikroskop-Fix als separate Aufgabe
  abzulegen.
  **Warum gescheitert:** MCP-Timeout nach 60s.
  **Lehre:** Kein Blocker — der Fix wurde direkt erledigt. Aber auf
  `spawn_task` nicht verlassen.

- **Versucht:** Den Vault-Report aus dem Container zu lesen.
  **Warum gescheitert:** Kein Berechtigungsproblem, sondern **eine andere
  Maschine**. `$WATCH_VAULT_DIR` ist nicht gesetzt, keiner der
  Standard-Vault-Pfade existiert, `$HOME` enthält nur Container-Kram.
  **Lehre:** Cloud-Container sehen ausschließlich das geklonte Repo. Alles, was
  den Vault braucht, gehört in eine lokale Session.

## ➡️ Nächster Schritt

**Die `/watch`-Wettbewerbsanalyse durchführen — nach
`playbooks/nfl-shorts/analysis/README.md`, Schritte 1–5.**

Konkret: 15–20 englischsprachige NFL-Shorts auswählen (⅔ Gewinner, ⅓ Ausreißer
nach unten — der Kontrast ist die Information), jedes mit
`/watch <URL> --out-dir ~/nfl-analysis/<slug>` durchlaufen, pro Short eine
`coding.json` füllen (**`views` ist das wichtigste Feld** — ohne ihn kann das
Board Gewinner nicht von Verlierern trennen), dann:

```bash
python3 playbooks/nfl-shorts/analysis/hookboard.py ~/nfl-analysis -o hookboard.md
```

Das ist der Schritt, der die Hook-Empfehlungen im Playbook von Annahmen zu
Messungen macht — und er ist der Grund, warum lokal gearbeitet wird.

> **Vorarbeit erledigt:** Der Video-Report ist ausgewertet und in
> `docs/codex-and-vault.md` eingearbeitet (Usage-Arbitrage via
> `/codex:rescue`, die 7 Angriffsflächen des adversarial review, die
> Cross-Check-Zahlen). Codex einrichten dauert jetzt ~15 Minuten und kann
> parallel laufen.

## 🔗 Kontext-Links

- **Branch:** `claude/kind-goldberg-uxgdfp` (9 Commits, gepusht)
- **Einstieg Strategie:** `playbooks/nfl-shorts/README.md`
- **Einstieg nächster Schritt:** `playbooks/nfl-shorts/analysis/README.md`
- **Codex einrichten:** `docs/codex-and-vault.md` — vier Schritte, ~15 Min
- **Ungelesener Report:** `$WATCH_VAULT_DIR/raw/watched/<slug>/report.md`
- **Vorgänger-Session:** „Codex mit Claude/Vault verbinden"
  (`session_01TuU46vALvLiaeGZ4qo3t8j`) — kein Code, nur Beratung
- **Ankerdatum:** 15.11.2026, Patriots vs. Lions in München — Amon-Ra
  St. Brown (halb-deutsch, Mutter aus Leverkusen) als Story-Aufhänger

### Offene Entscheidungen

- Google-Cloud-Projekt für `scripts/youtube.py` anlegen (blockiert die
  Analytics-Anbindung komplett)
- Vor dem nächsten Release: `scripts/youtube.py` wandert ins
  `watch.skill`-Bundle. Ohne Credentials inert, erweitert aber das
  veröffentlichte Plugin um einen OAuth-Client. Falls unerwünscht: nach
  `playbooks/` verschieben (dort greift `export-ignore`).

---
*Handoff erstellt am 2026-09-15 via session-handoff skill.*
