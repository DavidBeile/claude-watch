# NFL-Shorts Playbook

Stand: 15. September 2026 · Saison 2026/27 läuft (Week 2 startet Do, 17.09.)

Nachfolge-Projekt zur WM 2026. Dieses Playbook ist die Entscheidungsgrundlage:
Marktlage, Rechtelage, Formate, Produktionssystem.

---

## Die Kurzfassung

**1. Der Umstieg NFL ist richtig — aber es ist ein anderes Spiel als die WM.**
Die WM war ein vierwöchiger Rausch: ein globaler Peak, K.-o.-Drama, jeder
Zuschauer war Zielgruppe. Die NFL ist ein 21-Wochen-Marathon von September bis
Februar mit festem Wochenrhythmus. Das heißt: weniger Chance auf den einen
Zufallstreffer, dafür ein planbares wöchentliches Format — und das ist für
Kanalaufbau die deutlich bessere Kurve.

**2. Entschieden: Englischsprachig.**
Meine Empfehlung war Deutsch (Begründung steht weiterhin in
[`01-marktanalyse.md`](01-marktanalyse.md) — sie dokumentiert, warum die Wahl
knapp war). Die Entscheidung ist Englisch, und das Playbook ist darauf
ausgerichtet. Zwei Konsequenzen, die daraus folgen und die Planung prägen:
Die Konkurrenz ist erheblich dichter und wird von Kanälen mit Lizenzzugang
dominiert — Differenzierung muss deshalb über Substanz und Format laufen,
nicht über Aktualität. Und die München-/St.-Brown-Achse rutscht vom
Saison-Kern zum Nischenthema.

**3. Der Copyright-Kern in einem Satz:**
Es gibt keine "7-Sekunden-Regel", Deutschland kennt kein Fair Use, und die NFL
betreibt eines der aggressivsten Content-ID-Setups im Sport — **aber** ein
Claim ist kein Strike, und ein geclaimtes Short schadet dem Kanal nicht. Details
und Risiko-Stufen in [`02-copyright.md`](02-copyright.md).

**4. Die Saison hat zwei Peaks — beide sind planbar.**
Der erste ist **München, 15. November** (Patriots vs. Lions, Allianz Arena):
für einen englischsprachigen Kanal kein Saison-Kern, aber ein sauber
bespielbares International-Series-Thema, angereichert durch **Amon-Ra
St. Brown** — halb-deutsch, Mutter aus Leverkusen, fließend Deutsch, und für
ihn ist das Spiel eine Heimkehr. Das trägt auch auf Englisch als Story.
Der zweite und größere Peak sind **Playoffs und Super Bowl im Januar/Februar**.
Ein Kanal, der jetzt startet, hat für beide Vorlauf. Produziert wird **aus der
Ferne** — eigenes Stadionmaterial entfällt, alles andere bleibt.

---

## Die Dokumente

| Datei | Inhalt |
|---|---|
| [`01-marktanalyse.md`](01-marktanalyse.md) | Warum NFL ≠ WM, Sprachentscheidung, Wettbewerb, Saisonkalender |
| [`02-copyright.md`](02-copyright.md) | Die drei Ebenen (Recht / Content ID / Monetarisierung), Risikostufen A–D |
| [`03-formate.md`](03-formate.md) | 14 Formatideen, nach Rechtestufe sortiert, mit Hook-Struktur |
| [`04-integration-plan.md`](04-integration-plan.md) | YouTube ↔ Claude und Claude ↔ Codex — Architektur & Umsetzungsplan |
| [`05-quellen.md`](05-quellen.md) | Belegliste zur Recherche, mit Hinweis auf blockierte Quellen |
| [`analysis/`](analysis/README.md) | Wettbewerbsanalyse — Protokoll, Kandidatenliste, `hookboard.py` |

---

## Entscheidungsstand

| Frage | Stand |
|---|---|
| **Sprache** | ✅ Englisch |
| **München vor Ort** | ✅ Nein — Produktion aus der Ferne |
| **Gesicht oder faceless** | ⬜ offen |

Zur offenen Frage: Talking-Head bindet stärker und ist rechtlich am saubersten;
faceless skaliert besser, kollidiert aber härter mit YouTubes "Inauthentic
Content"-Erkennung auf Kanalebene — und die greift seit 2026 auf **Kanalebene**
statt pro Video. Für einen englischsprachigen Kanal in einem dichten Feld
spricht zusätzlich einiges für ein Gesicht: Es ist das einzige Merkmal, das
sich nicht kopieren lässt.

## Nächster Schritt

Die Wettbewerbsanalyse ist vorbereitet und läuft lokal:
[`analysis/README.md`](analysis/README.md). `/watch` konnte in der
Cloud-Session nicht laufen (YouTube durch Egress-Policy gesperrt, `yt-dlp` und
`ffmpeg` nicht installiert) — das Protokoll, die Kandidatenvorlage und der
Auswertungs-Aggregator `hookboard.py` liegen deshalb fertig bereit.

---

> **Hinweis:** [`02-copyright.md`](02-copyright.md) ist eine recherchierte
> Einschätzung, keine Rechtsberatung. Bei kommerziellem Rollout im Zweifel
> einmal anwaltlich gegenprüfen lassen — insbesondere die Stufe-C-Formate.
