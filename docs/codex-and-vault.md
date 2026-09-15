# Codex ↔ Claude ↔ Vault — der zusammengeführte Weg

Zwei Sessions haben diese Frage getrennt beantwortet. Dieses Dokument führt
beides zusammen und korrigiert, was in beiden veraltet war.

Stand: 15. September 2026.

---

## Was in beiden Sessions falsch war

Session *„Codex mit Claude/Vault verbinden"* nannte drei Wege: (a) gemeinsamer
Vault-/Repo-Ordner, (b) MCP-Bridge, (c) Shell-Exec. Session *„Shorts-Analyse und
NFL-Format"* nannte `codex mcp-server`.

**Beide lagen bei der MCP-Variante daneben.** `codex mcp-server` wurde mit
Codex CLI **v0.149.1 am 24. August 2026 abgekündigt**. Der Befehl stammte aus
der Zeit vor dem Codex **App Server** — einem JSON-RPC-2.0-Daemon, der seit
Anfang 2026 der maßgebliche Integrationspunkt ist.

Für Claude Code gibt es inzwischen einen offiziellen Weg, der besser ist als
jede der drei Varianten: das Plugin **[`openai/codex-plugin-cc`](https://github.com/openai/codex-plugin-cc)**.

Was aus den drei Wegen bleibt:

| Weg | Stand |
|---|---|
| (a) Gemeinsamer Ordner | ✅ richtig — und der Schlüssel zur Vault-Frage, siehe Teil 2 |
| (b) MCP-Bridge | ❌ überholt für Claude Code → Plugin nehmen |
| (c) Shell-Exec | ⚠️ funktioniert, aber das Plugin kapselt genau das sauberer |

Ebenfalls richtig und weiterhin gültig: **Das ChatGPT-Abo überträgt sich
nicht.** Jeder Agent nutzt sein eigenes Konto. Das Plugin umschließt deine
*lokale* Codex-CLI und erbt deren Anmeldung — du brauchst also ein
ChatGPT-Abo (Free genügt) oder einen OpenAI-API-Key, und Codex muss lokal
angemeldet sein (`codex login`).

---

## Teil 1 — Codex in Claude Code

```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

`/codex:setup` prüft die Installation und installiert Codex bei Bedarf per npm
nach. Falls nicht angemeldet: `!codex login`.

**Voraussetzungen:** ChatGPT-Abo (Free genügt) oder OpenAI-API-Key, Node.js
18.18+.

Das Plugin erbt deine vorhandene Codex-Authentifizierung, deine `config.toml`,
deine MCP-Konfiguration und deine Umgebungsvariablen — es gibt keine zweite
Konfiguration zu pflegen.

| Befehl | Zweck |
|---|---|
| `/codex:review` | Review der uncommitteten Änderungen |
| `/codex:adversarial-review` | Review, das Annahmen gezielt angreift |
| `/codex:rescue` | Aufgabe delegieren |
| `/codex:transfer` | Persistenten Codex-Thread aus der Session erzeugen |
| `/codex:status` · `/codex:result` · `/codex:cancel` | Hintergrund-Jobs |

---

## Teil 2 — Der Vault als gemeinsame Substanz

Hier zahlt sich Weg (a) aus der anderen Session aus, und zwar stärker als es
klingt.

**Der Vault ist bereits der gemeinsame Ordner.** `/watch` legt jeden Report
unter `$VAULT_DIR/raw/watched/<slug>/report.md` ab, und `$VAULT_DIR/CLAUDE.md`
definiert die Ingest-Op. Wenn Codex denselben Ordner sieht, lesen und schreiben
beide Agenten dieselben Notizen — **ohne Protokoll, ohne Bridge, ohne Daemon.**
Die Verbindung ist das Dateisystem.

### Vault-Pfad

`/watch` löst ihn in dieser Reihenfolge auf (erster Treffer gewinnt):

1. `$WATCH_VAULT_DIR`
2. `~/Second brain`
3. `~/Documents/Obsidian`
4. `~/Obsidian`

Setzen, falls der Vault woanders liegt:

```bash
echo 'export WATCH_VAULT_DIR="$HOME/Second brain"' >> ~/.zshrc
```

### Der eine fehlende Baustein: `AGENTS.md`

Claude liest `CLAUDE.md`. **Codex liest `AGENTS.md`.** Dein Vault hat
vermutlich nur ersteres — deshalb würde Codex dort ohne Anleitung arbeiten und
die Ingest-Konventionen nicht kennen.

Die Lösung ist eine Datei. Im Vault-Wurzelverzeichnis:

```bash
cd "$WATCH_VAULT_DIR"
ln -s CLAUDE.md AGENTS.md
```

Ein Symlink hält beide automatisch synchron — eine Kopie driftet auseinander,
sobald du eine der beiden änderst. Falls Codex dem Symlink nicht folgt oder du
für Codex bewusst andere Regeln willst, liegt unter
[`templates/vault-AGENTS.md`](templates/vault-AGENTS.md) eine eigenständige
Vorlage.

### Danach

```bash
cd "$WATCH_VAULT_DIR"
codex
```

Codex arbeitet dann im selben Vault, nach denselben Regeln, auf denselben
Reports, die `/watch` dort ablegt.

---

## Die Arbeitsteilung, die sich daraus ergibt

Ein zweiter Agent, der dasselbe tut wie der erste, bringt nichts. Die Trennung
muss inhaltlich sein:

| | Claude | Codex |
|---|---|---|
| **Stärke hier** | Recherche, Analyse, Strategie, Skripte | abgegrenzte Implementierung, unabhängiges Review |
| **Im Vault** | `/watch` → Report → Ingest | Aufräumen, Umstrukturieren, Batch-Arbeit an vielen Notizen |
| **Im Repo** | Features, Architektur | Review, Render-Pipelines, Tooling |

**Erster sinnvoller Einsatz:** `/codex:adversarial-review` auf
`scripts/youtube.py`. Dessen OAuth- und HTTP-Pfad wurde in einer Cloud-Session
geschrieben, in der Google über den Egress-Proxy nicht erreichbar war — live
getestet ist er also nicht. Ein unabhängiges Review genau dieser Stellen ist
mehr wert als das nächste Feature.

---

## Reihenfolge

1. `WATCH_VAULT_DIR` setzen, falls nötig — Voraussetzung für alles Weitere
2. `AGENTS.md` im Vault anlegen (Symlink)
3. Codex-Plugin in Claude Code installieren (Teil 1)
4. `/codex:adversarial-review` auf `scripts/youtube.py` laufen lassen

Schritte 1–2 dauern zusammen eine Minute und sind die Voraussetzung dafür, dass
Schritt 3 überhaupt etwas nützt.
