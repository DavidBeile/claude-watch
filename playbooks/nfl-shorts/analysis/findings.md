# Wettbewerbsanalyse — Befunde (2026-09-16)

28 Shorts, alle mit `/watch` durchlaufen und codiert. Board: `hookboard.md`
(erzeugt nach `~/nfl-analysis/`, nicht im Repo — enthält fremde Videotitel).

**Auswahl:** Brett Kollmann komplett (22 Shorts, 18k–3,8 Mio.) als Kern, dazu je
ein Top- und ein Flop-Short von The QB School, MatchQuarters und Ted Nguyen als
Nischen-Gegenprobe. Kollmann-Kern deshalb, weil die Spannweite **innerhalb eines
Kanals** liegt — damit misst der Vergleich den Hook und nicht die Kanalreichweite.

---

## 1. Der eine Befund mit Signal

Innerhalb von Kollmann, also bei konstantem Kanal:

| Hook-Muster | n | Median-Views |
|---|---|---|
| `superlative-play` | 8 | **539.500** |
| alle anderen | 12 | **123.500** |

**Faktor 4,4.** `superlative-play` heißt: ein **namentlich genannter Spieler** plus
eine **Wertung über genau eine Spielszene**, beides in den ersten Sekunden.

- „This throw from Patrick Mahomes yesterday was **insane**" (1,1 Mio.)
- „We need to take a second to **appreciate** what **Brock Purdy** did" (3,8 Mio.)
- „This throw from **Baker Mayfield** last night was absolutely **outrageous**" (368k)

Dagegen die schwachen Öffnungen desselben Kanals:

- „**A missed field goal on the opening drive** for Chicago…" (46k) — Spielkontext
  statt Spieler
- „**Next up**, we've got Geno Smith" (536) — setzt voraus, dass man die Reihe kennt
- „**It's the same issue though.** We have a free runner…" (29k) — mitten im Gedanken

⚠️ **Wie belastbar ist das?** n=8 gegen n=12, und die Musterzuordnung ist mein
Urteil, keine Messung. Störgrößen, die nicht kontrolliert sind: Bekanntheit des
Spielers (Mahomes zieht auch ohne guten Hook), ob die Szene ohnehin viral ging,
und das Veröffentlichungsdatum. Der Befund ist ein **starker Hinweis, kein Beweis** —
aber der einzige im ganzen Board, der überhaupt trennt.

## 2. Drei Annahmen des Playbooks, die die Messung nicht stützt

**Das Zielband 15–35 s stimmt nicht.** 2 von 28 liegen darin, Median ist **58,5 s**.
Und zwischen oben und unten gibt es **keinen** Unterschied: 58,5 s gegen 58,5 s.
Dauer trennt in dieser Nische gar nichts. Kollmanns schwächstes Short mit Transkript
ist zugleich sein längstes (108 s), sein zweitschwächstes das kürzeste (18 s).

**`cuts/min` ist nicht messbar.** 26 von 28 Reports melden „No scene-change data —
likely a static/screen-recorded source". Die Achse „schneiden Gewinner schneller?"
aus Schritt 5 der README lässt sich hier nicht beantworten. Entweder die
Scene-Change-Erkennung für Broadcast-Footage mit Telestration nachbessern, oder
die Achse streichen und das sagen.

**Das `hook_type`-Vokabular passt nicht.** 18 von 28 landen auf `other`, weil
`question/number/contrarian/conflict/visual` das dominierende Muster dieser Nische
— die Superlativ-Behauptung über eine Einzelszene — nicht abbildet. Deshalb das
Zusatzfeld `hook_pattern`; `hookboard.py` aggregiert es nicht, die Auswertung oben
ist von Hand. **Vorschlag:** `superlative-play` ins offizielle Vokabular aufnehmen.

## 3. Der strategisch unangenehmste Befund

**Null von 28 Shorts sind Stufe A.** 22× Stufe B (Kollmann, NFL Access Pass),
6× Stufe C (All-22 ohne Lizenz). Das gesamte gemessene Feld läuft auf
Broadcast-Material.

`02-copyright.md` empfiehlt „70–80 % Stufe A, 20–30 % Stufe C, Stufe B als
Saisonziel". Die Messung sagt: In dieser Nische gewinnt niemand mit Stufe A. Das
widerlegt die Empfehlung nicht — sie ist eine Risikoentscheidung, keine
Reichweiten-Prognose — aber sie ist teurer, als das Playbook nahelegt, und das
sollte dort stehen.

Dazu passt der zweite Befund aus der Kandidatensuche: In der reinen
Faceless-Film-Analyse skalieren Shorts nicht. QB School, MatchQuarters und
Ted Nguyen liegen bei Median 1,3k–3,5k mit einer Decke von 12k–29k. Kollmann
bricht aus — und zwar mit Emotion über eine Einzelszene, nicht mit Scheme-Erklärung.

## 4. Was offen bleibt

- **`text_density` ist bei allen 28 `?`.** Das Feld braucht einen Blick auf die
  Frames; aus Transkript und Metadaten ist es nicht ableitbar.
- **Vier Shorts ohne verwertbaren Hook-Text** (Musik-Intro, leeres Transkript,
  7-Sekunden-Clip ohne Ton). Bei denen steht `first_words: "?"`.
- **Kein Stufe-A-Kanal im Board.** `candidates.md` verlangt 5–6 Kandidaten ohne
  Lizenzzugang. Für die Hook-Frage unerheblich, für die Materialfrage nicht.
