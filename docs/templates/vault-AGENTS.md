# AGENTS.md — Vault-Konventionen für Codex

Kopiervorlage für das Wurzelverzeichnis deines Obsidian-Vaults, falls du Codex
dort eigene Regeln geben willst statt `CLAUDE.md` zu verlinken.

Bevorzugt ist der Symlink (`ln -s CLAUDE.md AGENTS.md`) — er kann nicht
auseinanderdriften. Diese Vorlage ist für den Fall, dass Codex dem Symlink
nicht folgt oder du bewusst abweichende Regeln brauchst.

Die Platzhalter unten an den tatsächlichen Vault anpassen.

---

## Was dieser Ordner ist

Ein Obsidian-Vault. Markdown-Dateien mit `[[Wikilinks]]`, kein Code-Projekt.
Änderungen sind für einen Menschen zum Lesen, nicht für einen Compiler.

## Struktur

| Pfad | Inhalt |
|---|---|
| `raw/watched/<slug>/` | Von `/watch` abgelegte Video-Reports samt Hero-Frames |
| `wiki/entities/` | Personen, Firmen, Tools — je eine Datei |
| `wiki/concepts/` | Frameworks, Ideen, benannte Muster |
| `wiki/sources/` | Quellenseiten mit TL;DR und Zitaten |
| `log.md` | Chronologischer Eintragsverlauf |

> Anpassen, falls der Vault anders geschnitten ist.

## Regeln

1. **Nichts löschen, was ein Mensch geschrieben hat.** Ergänzen, nicht ersetzen.
2. **`[[Wikilinks]]` beim Verweisen benutzen** — sie tragen den Graphen.
3. **Frontmatter erhalten.** Obsidian-Plugins hängen daran.
4. **Keine Dateien umbenennen**, ohne die eingehenden Links mitzuziehen. Ein
   Rename ohne Link-Update zerreißt den Graphen still.
5. **Keine `.obsidian/`-Dateien anfassen** — das ist App-Konfiguration.
6. **Bei Unklarheit fragen**, statt zu raten. Ein falsch strukturierter Eintrag
   kostet mehr Zeit als eine Rückfrage.

## Typische Aufgaben

- **Ingest:** Einen Report aus `raw/watched/<slug>/` lesen, Entities und
  Concepts herausziehen, die entsprechenden Wiki-Seiten anlegen oder ergänzen,
  eine Zeile an `log.md` hängen.
- **Aufräumen:** Verwaiste Links finden, Dubletten zusammenführen, fehlende
  Rückverweise ergänzen.
- **Batch-Arbeit:** Umstrukturierungen über viele Notizen hinweg — die
  Aufgabenart, für die Delegation an Codex sich tatsächlich lohnt.
