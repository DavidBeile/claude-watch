# Codex + Claude optimal verbinden

Vollständige Anleitung. Stand: 15. September 2026.

Zusammengeführt aus zwei Sessions dieses Repos und gegen die aktuellen Quellen
geprüft.

---

## Vorab: warum ältere Tutorials hier schaden

Der Standardweg hat sich im August 2026 geändert. Alles, was vor dem
**24. August 2026** veröffentlicht wurde, zeigt mit hoher Wahrscheinlichkeit
den abgekündigten Weg.

**`codex mcp-server` existiert nicht mehr.** Der Befehl wurde mit Codex CLI
**v0.149.1** abgekündigt. Er stammte aus der Zeit vor dem Codex **App Server**,
einem JSON-RPC-2.0-Daemon, der seit Anfang 2026 der maßgebliche
Integrationspunkt ist.

Wenn eine Anleitung dir eines der folgenden Dinge sagt, ist sie veraltet:

| Veraltetes Signal | Aktuell |
|---|---|
| `codex mcp-server` starten | Plugin `openai/codex-plugin-cc` |
| Codex per Hand in `.mcp.json` eintragen | Plugin erledigt das |
| Eigenen Wrapper / Shell-Exec bauen | Plugin kapselt genau das |

Das gilt ausdrücklich auch für zwei frühere Antworten in diesem Repo — beide
nannten die MCP-Variante, beide lagen falsch. Diese Datei ist die Korrektur.

---

## Was du am Ende hast

Drei Verbindungen, die zusammen mehr sind als ihre Teile:

```
   ┌──────────────┐   Plugin    ┌──────────────┐
   │ Claude Code  │ ──────────► │    Codex     │
   │              │  delegiert  │              │
   └───────┬──────┘             └──────┬───────┘
           │                           │
           │      derselbe Ordner      │
           └───────────┬───────────────┘
                       ▼
              ┌─────────────────┐
              │  Obsidian-Vault │   CLAUDE.md  ← Claude
              │   + Repo        │   AGENTS.md  ← Codex
              └─────────────────┘
```

1. **Claude → Codex** über das offizielle Plugin (Delegation, Review)
2. **Beide → derselbe Ordner** (Vault und Repo als gemeinsame Substanz)
3. **Beide → dieselben Regeln** (`CLAUDE.md` / `AGENTS.md`)

Die dritte ist die, die am häufigsten vergessen wird — und ohne die Codex im
Vault ohne Anleitung arbeitet.

---

## Voraussetzungen

| Was | Warum |
|---|---|
| **Node.js 18.18+** | Plugin-Laufzeit |
| **ChatGPT-Abo (Free genügt) oder OpenAI-API-Key** | Codex braucht ein eigenes Konto |
| **Codex CLI, lokal angemeldet** | Das Plugin umschließt deine lokale CLI |

> **Wichtig, und oft falsch verstanden:** Dein Claude-Abo gilt nicht für Codex.
> Das Plugin startet keine fremde Cloud-Instanz, sondern deine **lokale**
> Codex-CLI — mit deiner Anmeldung, deiner `config.toml`, deinen
> Umgebungsvariablen. Zwei Konten, ein Werkzeugkasten.

---

## Schritt 1 — Vault-Pfad festlegen

Zuerst, weil Schritt 3 darauf aufbaut.

`/watch` sucht den Vault in dieser Reihenfolge, erster Treffer gewinnt:

1. `$WATCH_VAULT_DIR`
2. `~/Second brain`
3. `~/Documents/Obsidian`
4. `~/Obsidian`

Liegt dein Vault woanders oder willst du es explizit:

```bash
echo 'export WATCH_VAULT_DIR="$HOME/Second brain"' >> ~/.zshrc
source ~/.zshrc
```

**Prüfen:**
```bash
echo "$WATCH_VAULT_DIR" && ls "$WATCH_VAULT_DIR"
```
Du solltest deine Vault-Ordner sehen. Falls nicht, stimmt der Pfad nicht —
nicht weitermachen, Schritt 3 hängt daran.

---

## Schritt 2 — Codex-Plugin in Claude Code

In Claude Code:

```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

Beim `install` fragt Claude Code nach dem **Scope** — `user` wählen, dann steht
das Plugin in allen Projekten zur Verfügung.

`/codex:setup` prüft, ob Codex einsatzbereit ist, und installiert es bei Bedarf
per npm nach („install codex?" → ja). Danach **öffnet sich der Browser** für die
Anmeldung; am Ende bestätigt Claude Code mit *„Signed in to Codex"*.

Falls die Anmeldung übersprungen wurde:
```
!codex login
```

**Prüfen:** `/codex:status` muss antworten, ohne zu meckern.

---

## Schritt 3 — Codex die Vault-Regeln geben

Der Baustein, den fast jede Anleitung auslässt.

**Claude liest `CLAUDE.md`. Codex liest `AGENTS.md`.** Dein Vault hat
vermutlich nur ersteres. Ohne diesen Schritt arbeitet Codex dort blind und
kennt deine Ingest-Konventionen nicht.

```bash
cd "$WATCH_VAULT_DIR"
ln -s CLAUDE.md AGENTS.md
```

**Warum Symlink und nicht Kopie:** Eine Kopie driftet auseinander, sobald du
eine der beiden Dateien änderst — und du merkst es erst, wenn Codex nach alten
Regeln arbeitet. Der Symlink kann das nicht.

Falls Codex dem Symlink nicht folgt oder du für Codex bewusst abweichende
Regeln willst: eigenständige Vorlage unter
[`templates/vault-AGENTS.md`](templates/vault-AGENTS.md).

**Dasselbe fürs Repo**, falls du Codex auch hier arbeiten lässt:
```bash
cd /pfad/zu/claude-watch
ln -s CLAUDE.md AGENTS.md   # nur falls eine CLAUDE.md existiert
```

**Prüfen:**
```bash
cd "$WATCH_VAULT_DIR" && cat AGENTS.md | head -5
```

---

## Schritt 4 — Die Gegenrichtung (optional)

`/watch` in Codex nutzen. Das Repo hat `.codex-plugin/plugin.json`, der Weg ist
vorgesehen:

```bash
git clone https://github.com/taoufik123-collab/claude-watch.git ~/.codex/skills/watch
```

Danach ist die Brücke in beide Richtungen offen.

---

## Wofür du was benutzt

Ein zweiter Agent, der dasselbe tut wie der erste, bringt nichts. Der Gewinn
entsteht nur bei inhaltlicher Trennung.

| | **Claude** | **Codex** |
|---|---|---|
| **Stärke** | Recherche, Analyse, Strategie, Architektur, Skripte | abgegrenzte Implementierung, unabhängiges Review |
| **Im Repo** | Features bauen, Entscheidungen treffen | Review, Render-Pipelines, Tooling |
| **Im Vault** | `/watch` → Report → Ingest | Aufräumen, Umstrukturieren, Batch-Arbeit |

### Die Befehle

| Befehl | Wofür |
|---|---|
| `/codex:review` | Review der uncommitteten Änderungen |
| `/codex:adversarial-review` | Review, das Designannahmen gezielt angreift |
| `/codex:rescue` | Aufgabe delegieren (Debugging, Fixes, Untersuchungen) |
| `/codex:transfer` | Persistenten Codex-Thread aus der Session erzeugen |
| `/codex:status` | Laufende und kürzliche Jobs |
| `/codex:result` | Ergebnis eines abgeschlossenen Jobs |
| `/codex:cancel` | Hintergrund-Job abbrechen |

### Use Case 1 — Usage-Limits ausweichen

Der Weg, den man leicht übersieht: **Opus plant, Codex führt aus.**

```
/codex:rescue <Aufgabe>
```

Statt einen teuren Plan *und* die Ausführung über dasselbe Kontingent laufen zu
lassen, macht Opus die Architektur- und Planungsarbeit und reicht die
Implementierung an Codex weiter — die gegen dein ChatGPT-Kontingent läuft, nicht
gegen dein Anthropic-Kontingent. `/codex:rescue` nimmt Flags, u. a. für das
Effort-Level.

Das ist kein Qualitätskompromiss, sondern eine Aufteilung nach Kostenstelle:
Planung ist der Teil, bei dem das stärkere Modell zählt; Ausführung eines
klaren Plans ist der Teil, bei dem Volumen zählt.

### Use Case 2 — Adversarial Review (der wertvollere)

**`/codex:adversarial-review`** — nicht `/codex:review`.

Ein normales Review findet Tippfehler. Das adversarial Review baut einen
strukturierten Angriffs-Prompt über **sieben Flächen** — Auth, Data Loss,
Rollback, Race Conditions, Null/Timeout, Version Skew, Observability — schickt
ihn an Codex in einer **read-only Sandbox** und liefert strukturiertes JSON mit
Severity-Einstufung zurück.

Warum ein zweites Modell und nicht dasselbe nochmal: Es hat deine Annahmen
nicht gemacht.

> **Es gibt dafür harte Zahlen.** Im Vergleichstest des unten verlinkten Videos
> — gleiche Codebase, gleicher Prompt — fand Codex **4 High-Severity-Findings**,
> Opus **7 zusätzliche**, und nur **ein einziges** überlappte. Codex fand drei,
> die Opus verpasste.
>
> Die Lehre ist nicht „Codex ist besser" oder „Opus ist besser", sondern:
> **die beiden finden verschiedene Dinge.** Wer nur eines laufen lässt, sieht
> rund die Hälfte. Deshalb ist der Cross-Check der eigentliche Gewinn der
> Anbindung — nicht der Ersatz des einen durch das andere.

Konkret hier: `scripts/youtube.py`. Der Netzwerkpfad ist inzwischen gegen die
echten Google-Endpunkte geprüft — Request-Aufbau, Formularkodierung und die
401/403-Fehlerbehandlung funktionieren. **Nicht** geprüft sind der
OAuth-Zustimmungsflow (braucht Browser und echte Credentials) und das Parsen
echter Antwortdaten. Genau diese Stellen von einem anderen Modell prüfen zu
lassen, ist mehr wert als das nächste Feature.

```
/codex:adversarial-review scripts/youtube.py
```

---

## Fallstricke

**Nicht beide Agenten gleichzeitig am selben Repo.** Zwei Agenten, die
gleichzeitig committen oder Branches wechseln, treten sich auf die Füße. Codex
arbeitet delegiert, also im Hintergrund — `/codex:status` prüfen, bevor du
selbst weiterschreibst.

**Das ChatGPT-Abo ist separat.** Siehe Voraussetzungen. Kein Claude-Abo der
Welt meldet dich bei Codex an.

**Keine blockierten Aufgaben weiterreichen.** Was Claude aus Berechtigungs-
gründen nicht darf, gehört nicht an Codex delegiert, damit es doch passiert.
Das hebelt die Entscheidung aus, die du selbst getroffen hast.

**Ältere Tutorials gegenprüfen.** Wenn eine Anleitung `codex mcp-server` sagt,
ist sie vor dem 24. August 2026 entstanden. Siehe oben.

---

## Reihenfolge in Kurzform

```bash
# 1  Vault-Pfad
echo 'export WATCH_VAULT_DIR="$HOME/Second brain"' >> ~/.zshrc && source ~/.zshrc

# 3  Vault-Regeln für Codex
cd "$WATCH_VAULT_DIR" && ln -s CLAUDE.md AGENTS.md
```

```
# 2  Plugin (in Claude Code)
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup

# 4  Erster echter Einsatz
/codex:adversarial-review scripts/youtube.py
```

Schritte 1 und 3 dauern zusammen eine Minute. Ohne sie funktioniert Schritt 2
zwar, aber Codex ist im Vault blind.

---

## Quellen

- [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc) — offizielles Plugin
- [From codex mcp-server to App Server and Codex Plugin: v0.149.1 Deprecation](https://codex.danielvaughan.com/2026/08/25/codex-mcp-server-deprecated-app-server-migration-claude-code-plugin-v0149/)
- [Codex App Server — OpenAI Developers](https://developers.openai.com/codex/app-server)
- [Introducing Codex Plugin for Claude Code — OpenAI Developer Community](https://community.openai.com/t/introducing-codex-plugin-for-claude-code/1378186)
- Vault-Mechanik: `SKILL.md` in diesem Repo, Abschnitt *Configuration* und Schritte 4.4/4.5

- [Claude Code + Codex = AI GOD](https://www.youtube.com/watch?v=L7NPhaUBpZE) —
  ausgewertet via `/watch`, Report unter
  [`playbooks/nfl-shorts/analysis/video-codex-report.md`](../playbooks/nfl-shorts/analysis/video-codex-report.md)

> **Korrektur einer früheren Einschätzung:** Ich hatte vermutet, das Video zeige
> den abgekündigten `codex mcp-server`-Weg — gestützt auf ein Datum (31. März
> 2026) aus einer Suchergebnis-Zusammenfassung, das ich nicht prüfen konnte,
> weil YouTube in dieser Session gesperrt ist. **Die Vermutung war falsch.**
> Das Video zeigt exakt den aktuellen Weg (`openai/codex-plugin-cc`); das Datum
> aus der Suche stimmte nicht. Die Wörter `mcp`, `config.toml` und `AGENTS.md`
> kommen im gesamten Transkript nicht vor.
>
> Was das Video **nicht** behandelt: den Vault. Teil 2 dieser Anleitung —
> gemeinsamer Ordner und `AGENTS.md` — hat dort keine Entsprechung.
