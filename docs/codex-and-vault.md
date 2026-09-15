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

`/codex:setup` prüft, ob Codex einsatzbereit ist, und installiert es bei Bedarf
per npm nach. Es verwaltet außerdem ein optionales Review-Gate.

Falls Codex nicht angemeldet ist:
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

### Der wertvollste Einsatz

**`/codex:adversarial-review`** — nicht `/codex:review`.

Ein normales Review findet Tippfehler. Das adversarial Review greift
Designannahmen an, und das ist der Teil, den ein zweites Modell tatsächlich
besser kann als dasselbe Modell nochmal: Es hat deine Annahmen nicht gemacht.

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

> **Nicht ausgewertet:** [Claude Code + Codex = AI GOD](https://www.youtube.com/watch?v=L7NPhaUBpZE)
> (31. März 2026). YouTube ist in der Session, in der diese Datei entstand,
> durch die Egress-Policy gesperrt — das Video wurde **nicht** gesehen. Sein
> Veröffentlichungsdatum liegt rund fünf Monate vor der Abkündigung von
> `codex mcp-server`; falls es eine Verdrahtung zeigt, ist sie mit hoher
> Wahrscheinlichkeit die veraltete. Gegen die Tabelle oben prüfen.
