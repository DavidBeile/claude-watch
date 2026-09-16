# Wettbewerbsanalyse — Protokoll

> ✅ **Einmal durchgeführt am 16.09.2026.** Ergebnisse und was sie an diesem
> Protokoll widerlegt haben: [`findings.md`](findings.md). Lies das zuerst —
> drei Annahmen unten sind gemessen falsch und unten entsprechend markiert.

Ziel: nicht raten, welche Hooks funktionieren, sondern es an 15–20 echten
NFL-Shorts messen. Ergebnis ist ein **Hookboard** — eine Tabelle plus
Musterauswertung, die zeigt, was die erfolgreichen Shorts anders machen als
die erfolglosen.

Kanalsprache laut Entscheidung: **Englisch**. Die Kandidatenliste unten ist
entsprechend auf den englischsprachigen Markt ausgerichtet.

---

## Warum das hier nicht in der Cloud-Session lief

`/watch` braucht `yt-dlp` und `ffmpeg` und muss YouTube erreichen. In der
Remote-Session, in der dieses Playbook entstanden ist, fehlten beide Tools und
`www.youtube.com` war durch die Egress-Policy der Organisation gesperrt
(403 beim CONNECT). Die Analyse läuft deshalb **lokal bei dir** — dort, wo
`/watch` ohnehin installiert ist.

Dieses Verzeichnis enthält alles, was die Handarbeit dabei abnimmt.

---

## Ablauf

### Schritt 1 — Kandidaten sammeln (15–20 Shorts)

Nicht wahllos. Die Auswahl entscheidet, ob die Auswertung etwas aussagt:

- **Zwei Drittel Gewinner, ein Drittel Ausreißer nach unten.** Ein Board aus
  lauter Hits zeigt nur, was Hits gemeinsam haben — nicht, was sie von Flops
  unterscheidet. Der Kontrast ist die Information.
- **Gleiche Nische.** NFL-Analyse und NFL-Comedy haben verschiedene
  Hook-Ökonomien. Mischen verwässert das Ergebnis.
- **Aktuell.** Nichts älter als ~6 Monate; Shorts-Konventionen drehen schnell.
- **Verschiedene Kanalgrößen.** Sonst misst man Kanal-Reichweite statt Hook.

⚠️ **Die Keyword-Suche funktioniert nicht — gemessen.** Diese sechs Anfragen
lieferten 282 Videos, davon 53 in Shorts-Länge, und darin Madden-Gameplay,
Helm-Redesigns und Trainer-Drill-Clips, also drei verschiedene Nischen. Genau
**ein** Treffer über 100k Views. `#shorts` im Suchtext ist das falsche Werkzeug,
weil Shorts über den Shorts-Feed ausgespielt werden, nicht über das Hashtag.

```
# funktioniert nicht:
nfl film breakdown    nfl explained    nfl film study
why <team> <verb>     nfl route concept    nfl all 22
```

**Was stattdessen funktioniert — kanalweise über den Shorts-Tab:**

```bash
yt-dlp --flat-playlist -j "https://www.youtube.com/channel/<id>/shorts"
```

Vier Aufrufe ergaben 202 echte Shorts mit View-Zahlen. Vorteil darüber hinaus:
Die View-Spannweite liegt **innerhalb** eines Kanals, damit misst der Vergleich
den Hook statt der Kanalreichweite.

⚠️ **Zwei Fallstricke des Shorts-Tabs:** Er liefert **kein `duration`**, und der
Kanal steht nicht unter `channel`, sondern unter **`playlist_channel`**. Die
`view_count`-Werte sind gerundet („31000"). Wer auf `duration` filtert, bekommt
eine leere Liste.

Verifizierbare Startpunkte aus der Recherche: der offizielle NFL-Kanal
(~16,3 Mio. Abonnenten) sowie die namentlich bekannten Creator aus dem NFL
Access Pass — **Brett Kollmann** (zwei n), **Tom Grossi**, **Peighton Tubre**.

⚠️ **Nur Kollmann trifft das Zielformat.** Peighton Tubre macht Fan-Reaction und
Memes vor der Kamera (Top-Video: eine WM-Reaktion), Tom Grossi Spielreaktionen
als Fan-Persona. Für die Faceless-Film-Analyse sind beide **keine**
Hook-Referenz. Weitere Kanäle der richtigen Nische: **The QB School**,
**MatchQuarters**, **Ted Nguyen** — aber alle klein (Median 1,3k–3,5k, Decke
12k–29k). Die sind
als Referenz nützlich, aber Vorsicht: Access-Pass-Creator arbeiten mit
lizenziertem Material (Stufe B) und sind bei der Materialfrage **kein**
Vorbild für einen Start ohne Lizenz. Für die Hook-Mechanik taugen sie trotzdem.

Kandidaten in `candidates.md` eintragen (Vorlage liegt dort).

### Schritt 2 — Jedes Short mit `/watch` durchlaufen

```
/watch <URL> --out-dir ~/nfl-analysis/<slug> \
  Hook-Analyse: womit öffnet das Video, was steht im Bild während der
  ersten Worte, wie ist das Pacing?
```

⚠️ **Beim Batch `</dev/null` hinter den Aufruf setzen.** In einer
`while read`-Schleife liest `watch.py` sonst vom selben stdin und frisst Zeichen
weg: drei Video-IDs verloren ihr erstes Zeichen (`gYjncbJ8Jgg` → `YjncbJ8Jgg`
→ 404) und eine vierte Zeile wurde still verschluckt — der Lauf zählte 27 statt
28 und meldete trotzdem Erfolg.

Wichtig: `--out-dir` pro Short auf ein **eigenes** Verzeichnis setzen. Das
Hookboard erwartet genau diese Struktur:

```
~/nfl-analysis/
├── mahomes-audible/
│   ├── report.md        ← von /watch
│   └── coding.json      ← du bzw. Claude, Schritt 3
├── why-cover2-dead/
│   ├── report.md
│   └── coding.json
└── ...
```

> **Behoben:** Bis September 2026 übersprang das Hook-Mikroskop Videos unter
> 30 Sekunden — bei Shorts im Zielband 15–35 s also die Mehrheit. Seitdem
> bekommen kurze Videos das wortgenaue Whisper-Transkript, nur der
> 2-fps-Frame-Repass entfällt (der reguläre Durchlauf sampelt so kurze Videos
> ohnehin dicht genug). Im `report.md` steht dann *"Frames: N reused from the
> main pass"*. Der *Caveat*-Abschnitt des Hookboards sollte bei Shorts-Boards
> jetzt leer bleiben.
>
> Voraussetzung dafür ist ein gesetzter Whisper-Key (`GROQ_API_KEY` oder
> `OPENAI_API_KEY`). ⚠️ Der Key wird in dieser Reihenfolge gesucht: Umgebung →
> `~/.config/watch/.env` → `./.env`. Wer nur `echo $GROQ_API_KEY` prüft, hält
> ihn fälschlich für fehlend. Ohne Key gibt es bei kurzen Videos nichts zu gewinnen —
> dann weist der Report das explizit aus.

### Schritt 3 — Codieren

`/watch` liefert die harten Zahlen (Dauer, Shots, Cuts/min). Was ein Mensch
entscheiden muss, kommt in `coding.json` pro Short:

```json
{
  "channel":       "Beispielkanal",
  "views":         1830000,
  "hook_type":     "contrarian",
  "first_words":   "Everyone got this play wrong.",
  "material_tier": "C",
  "text_density":  "high",
  "ending":        "loop",
  "notes":         "Telestration ab 0:04, Beleg-Clip nur 2s"
}
```

| Feld | Werte | Bedeutung |
|---|---|---|
| `views` | Zahl | **Der wichtigste Wert.** Ohne ihn kann das Board Gewinner nicht von Verlierern trennen. |
| `hook_type` | `superlative-play` `question` `number` `contrarian` `conflict` `visual` `other` | Muster der ersten zwei Sekunden. ⚠️ `superlative-play` wurde nach der ersten Runde ergänzt — es ist das einzige Muster, das Gewinner von Verlierern trennt (Faktor 4,4), fehlte aber im ursprünglichen Vokabular, sodass 18 von 28 auf `other` landeten. |
| `first_words` | Text | Die tatsächlich ersten gesprochenen Worte |
| `material_tier` | `A` `B` `C` `D` | Rechtestufe laut [`../02-copyright.md`](../02-copyright.md) |
| `text_density` | `none` `low` `medium` `high` | Wie viel wird gelesen statt gehört |
| `ending` | `loop` `cliffhanger` `hard_cut` `cta` | Wie das Short schließt |

Unbekannte Felder werden durchgereicht und ignoriert — eigene Spalten sind
also unproblematisch. Fehlende Felder werden als `?` dargestellt; ein
halb codiertes Board ist immer noch auswertbar.

### Schritt 4 — Board erzeugen

```bash
python3 hookboard.py ~/nfl-analysis -o hookboard.md
python3 hookboard.py ~/nfl-analysis --json -o hookboard.json
```

Reine Stdlib, kein `pip install`.

### Schritt 5 — Auswerten

Der Abschnitt **"Above vs. below median views"** ist der eigentliche Zweck.
Er beantwortet die einzige Frage, die zählt:

> Machen die erfolgreichen Shorts systematisch etwas anders — schneller
> geschnitten, kürzer, anderer Hook-Typ?

Ab vier codierten `views`-Werten wird er berechnet. Was daraus abzuleiten ist:

- **Hook-Typ-Verteilung oben vs. unten** → welcher Hook-Typ in dieser Nische
  trägt. Das steuert Schritt ④ der Pipeline (Skripterstellung).
- ~~**Cuts/min oben vs. unten**~~ → ⚠️ **in dieser Nische nicht messbar.**
  26 von 28 Reports melden „No scene-change data — likely a static/screen-recorded
  source" — Broadcast-Footage mit Telestration erzeugt offenbar keine erkennbaren
  Szenenwechsel. Entweder die Erkennung nachbessern oder die Achse streichen.
- ~~**Dauer oben vs. unten**~~ → ⚠️ **beantwortet: das Band stimmt nicht, und
  Dauer trennt nichts.** 2 von 28 im 15–35-s-Band, Median 58,5 s, und oben wie
  unten identisch 58,5 s.
- **Materialstufen-Verteilung** → wie stark das Feld auf Broadcast-Footage
  setzt. Wenn die Top-Shorts durchweg Stufe C sind, ist das eine strategische
  Information: Der Wettbewerb nimmt Claims in Kauf, und ein reiner
  Stufe-A-Kanal muss den Nachteil über Substanz ausgleichen.

---

## Dateien hier

| Datei | Zweck |
|---|---|
| `hookboard.py` | Aggregator — viele `report.md` → ein Musterboard |
| `test_hookboard.py` | 26 Tests, `python3 -m unittest test_hookboard` |
| `candidates.md` | Arbeitsliste der zu analysierenden Shorts |
| `coding.example.json` | Kopiervorlage |
