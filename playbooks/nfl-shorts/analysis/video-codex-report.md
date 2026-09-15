---
source: https://www.youtube.com/watch?v=L7NPhaUBpZE
title: Claude Code + Codex = AI GOD
duration: 09:43
watched_at: 2026-09-16T00:04:12.763997+02:00
intent: was zeigt das Video zur Codex-Anbindung?
hero_frames: [frame_0001.jpg, frame_0017.jpg, frame_0033.jpg, frame_0049.jpg, frame_0065.jpg]
transcript_source: captions
---

# Claude Code + Codex = AI GOD

## TL;DR

- Das Video zeigt live die Installation des `openai/codex-plugin-cc` in Claude Code: Marketplace hinzufügen → `/plugin install codex` → `/reload-plugins` → `/codex:setup` (Browser-Login gegen den ChatGPT-Account).
- Das Plugin bringt 4 Befehlsgruppen: Reviews (`/codex:review`, `/codex:adversarial-review`), Task Delegation (`/codex:rescue`), Job Management (`/codex:status`/`result`/`cancel`), Setup (`/codex:setup`) — visualisiert als Excalidraw-Mindmap.
- Kern-Demo ist `/codex:adversarial-review`: Codex bekommt einen strukturierten Angriffs-Prompt mit 7 Fokus-Bereichen (Auth, Data Loss, Rollback, Race Conditions, Null/Timeout, Version Skew, Observability) und liefert JSON mit Severity-Findings zurück.
- Im Vergleichstest gegen Opus 4.6 (gleiche Codebase, gleicher Prompt) findet Codex 4 High-Severity-Issues, Opus 7 zusätzliche — die Anbindung wird also auch als Cross-Check zwischen zwei Modellen genutzt, nicht nur als Ersatz.
- Nebenbei wird klar: Codex-Nutzung läuft über den ChatGPT-Account (auch Free-Tier), unabhängig vom Anthropic-Plan.

## Key moments

- **[00:00] Ankündigung** — X-Post von Vaibhav Srivastav (OpenAI) kündigt Codex-Support in Claude Code an, zeigt die drei Kernbefehle (frame_0001).
- **[00:46] Feature-Überblick vor dem Install** — Erklärt Reviews, adversarial review, Codex rescue und Status-Befehle, bevor überhaupt installiert wird.
- **[01:57] Excalidraw-Mindmap "Codex Plugin for Claude Code"** — visuelle Übersicht aller 4 Befehlsgruppen (hero_frame_0017).
- **[02:00–02:41] Live-Installation** — `/plugin marketplace add`, `/plugin install codex@openai-codex` (Scope: User), `/reload-plugins`, `/codex:setup`, Browser-Login-Bestätigung "Signed in to Codex" (frame_0018–0023).
- **[02:53] Zwei Haupt-Use-Cases genannt** — (1) Usage-Limits umgehen: Opus plant, Codex führt aus via `/codex:rescue`; (2) adversarial review als zweites Augenpaar.
- **[03:33] Zielobjekt der Demo** — sein Twitter-Engagement-/Research-Bot ("tweetgod"), Architektur per Excalidraw erklärt (Apify-Scraper → Quality Filter → Dedup/Supabase → Scoring → Telegram-Approval → Post) (frame_0033–0048).
- **[04:24] `/codex:adversarial-review` gestartet** — offener Prompt "take a look at the codebase and let me know what you think" (hero_frame_0049).
- **[04:47–05:39] Interner Ablauf erklärt** — Parse Args → Estimate Review Size → Resolve Target → Collect Context → Build Adversarial Prompt (7 Attack Surfaces) → Send to Codex (read-only Sandbox) → Structured JSON Output (frame_0057–0064).
- **[05:53] Codex-Ergebnis** — 4 Findings, alle Severity HIGH: Dedup-Logic, Telegram-Polling-Race, Schema Drift, Dashboard-Build-Fehler (frame_0065–0068).
- **[06:32–08:58] Vergleich mit Opus** — Opus bekommt denselben (von Codex formulierten) Prompt; 1 gemeinsamer Fund (Telegram, Codex=HIGH/Opus=CRITICAL), Opus findet 7 zusätzliche High/Critical-Issues, Codex 3, die Opus verpasst (frame_0069–0080).

## Hook microscope (0-10s)

- Frames: 20 at 2 fps
- Word-level transcript (29 words):

```
  [  0.00s] So
  [  0.14s] we
  [  0.28s] can
  [  0.44s] now
  [  0.62s] use
  [  0.84s] Codex
  [  1.46s] inside
  [  2.28s] of
  [  2.58s] Cloud
  [  2.88s] Code.
  [  3.80s] OpenAI
  [  4.10s] has
  [  4.48s] made
  [  4.72s] it.
  [  4.84s] So
  [  5.00s] the
  [  5.24s] number
  [  5.64s] one
  [  5.82s] competitor
  [  6.24s] to
  [  6.76s] Opus
  [  7.00s] 4.6
  [  7.88s] is
  [  8.44s] now
  [  8.56s] something
  [  8.78s] you
  [  8.98s] can
  [  9.14s] use
  [  9.60s] inside
```

Kein Schnitt in den ersten 10s — statisches Bild des X-Posts (Ankündigungstext + Screenshot der Install-Befehle) im Hintergrund, Facecam unten rechts. Die Wortfolge "So we can now use Codex inside of Claude Code" (0.0–2.9s) fällt fast synchron mit dem sichtbaren Text auf dem Screenshot zusammen — Hook-Pattern ist **"news drop"**: eine faktische Ankündigung direkt zu Beginn statt Frage oder Cliffhanger, die Neuheit selbst ("Codex jetzt in Claude Code nutzbar") trägt den Hook.

## Editorial profile

_No scene-change data — likely a static/screen-recorded source._

Talking-Head-Screencast ohne harte Schnitte: durchgehende Terminal-/Browser-Aufnahme mit Facecam-Overlay, Erklärungen per handgezeichneten Excalidraw-Diagrammen statt Text-Overlays — Tutorial-Tempo, keine Fireship-artige Schnittdichte.

## Quotable moments

- [01:35] "Other than that, we can also use Codex rescue, which allows us to have Codex create something all on its own, just like you would do with Opus inside of Claude Code."
- [02:34] "The usage rates are tied to your ChatGPT account, even if you're on the free account, apparently."
- [06:03] "There is some sort of fundamental flaw, I think, with having the same AI system do the planning, the generating, and the evaluating."
- [08:31] "If you're already paying for ChatGPT ... what's the downside to this, really?"
- [09:33] "Codex really is a great value play."

## Entities mentioned

- People: [[vaibhav-srivastav]]
- Companies: [[openai]], [[anthropic]], [[supabase]], [[xai]]
- Tools / products: [[claude-code]], [[codex]], [[codex-plugin-cc]], [[opus-4-6]], [[excalidraw]], [[telegram]], [[apify]], [[grok]]

## Concepts surfaced

adversarial-review: Ein Modell wird explizit angewiesen, den Output eines anderen Modells mit "discerning eye" zu challengen statt neutral zu prüfen — deckt Blindspots auf, die eine Selbstbewertung (Opus prüft Opus) verpasst.
cross-model-evaluation: Zwei unterschiedliche LLM-Systeme (Codex, Opus) bekommen denselben Prompt auf derselben Codebase, um Findings gegenzuprüfen statt einem Modell blind zu vertrauen.
usage-tier-arbitrage: Ein zweites Abo (ChatGPT/Codex) wird gezielt als günstigere Rechenkapazität neben Anthropics Plänen genutzt, um Usage-Limits zu umgehen, ohne auf den teureren 100-200-Dollar-Tier zu wechseln.
plugin-marketplace-install: Claude-Code-Erweiterungen werden über `/plugin marketplace add` + `/plugin install` als Drittanbieter-Plugins eingebunden, inkl. Scope-Wahl (user/project/local) und Reload-Schritt.

## Transcript

_Source: captions._

```
[00:03] So, we can now use Codex inside of Claude Code. OpenAI has made it so the
[00:05] Claude Code. OpenAI has made it so the number one competitor to Opus 4.6 is now
[00:09] number one competitor to Opus 4.6 is now something you can use inside of the
[00:10] something you can use inside of the Anthropic ecosystem. And this is great
[00:13] Anthropic ecosystem. And this is great news for all Claude Code enjoyers,
[00:15] news for all Claude Code enjoyers, especially if you're someone who has
[00:17] especially if you're someone who has been struggling with usage rates.
[00:19] been struggling with usage rates. Because, frankly, Codex gives you a way
[00:22] Because, frankly, Codex gives you a way better bang for your buck in terms of
[00:24] better bang for your buck in terms of dollar to credit {slash} tokens. And so,
[00:26] dollar to credit {slash} tokens. And so, in this video, I'm going to show you how
[00:28] in this video, I'm going to show you how to set it up, and we're going to go
[00:29] to set it up, and we're going to go through what Codex can actually do with
[00:32] through what Codex can actually do with the Claude Code harness on top of it.
[00:34] the Claude Code harness on top of it. And more importantly, what we can do
[00:36] And more importantly, what we can do using Claude Code with Opus 4.6 and
[00:39] using Claude Code with Opus 4.6 and Codex together, right? How can we play
[00:41] Codex together, right? How can we play these two models off one another to get
[00:44] these two models off one another to get a sum that is greater than their parts.
[00:46] a sum that is greater than their parts. And before we do the install, let's do a
[00:47] And before we do the install, let's do a quick overview of what the Claude Code
[00:49] quick overview of what the Claude Code plugin brings us, because there's a few
[00:51] plugin brings us, because there's a few things. Now, the two most important
[00:54] things. Now, the two most important things, I would argue, are the code
[00:56] things, I would argue, are the code reviews, right? The ability to
[00:57] reviews, right? The ability to essentially have it take a look at
[00:58] essentially have it take a look at something Opus has written. And that
[01:00] something Opus has written. And that goes into stages. First of all, we have
[01:02] goes into stages. First of all, we have the standard Codex review, which is
[01:04] the standard Codex review, which is just, you know, kind of a neutral
[01:06] just, you know, kind of a neutral review, you know, it's taking a look,
[01:07] review, you know, it's taking a look, it's just read only. The second one is
[01:09] it's just read only. The second one is adversarial review, which I love. So,
[01:12] adversarial review, which I love. So, this is essentially telling Codex, like,
[01:14] this is essentially telling Codex, like, "Hey, take a look at what Opus has built
[01:16] "Hey, take a look at what Opus has built or what any coding agent has built, but
[01:18] or what any coding agent has built, but have a very discerning eye. Like, kind
[01:21] have a very discerning eye. Like, kind of assume they screwed up
[01:23] of assume they screwed up and figure out what we can do to make it
[01:25] and figure out what we can do to make it better." So, this is an awesome way to
[01:27] better." So, this is an awesome way to really improve our outputs. Because one
[01:30] really improve our outputs. Because one of the issues with Opus, and really a
[01:32] of the issues with Opus, and really a lot of AI models in general, is they
[01:34] lot of AI models in general, is they tend to do a bad job of evaluating their
[01:36] tend to do a bad job of evaluating their own their own code. This is something
[01:37] own their own code. This is something Anthropic talked about in their
[01:38] Anthropic talked about in their engineering blog that got released last
[01:40] engineering blog that got released last week. So, something like adversarial
[01:42] week. So, something like adversarial review, perfect. Love this. Other than
[01:44] review, perfect. Love this. Other than that, we can also use Codex rescue,
[01:46] that, we can also use Codex rescue, which allows us to have Codex create
[01:48] which allows us to have Codex create something all on its own, just like you
[01:50] something all on its own, just like you would do with Opus inside of Claude
[01:52] would do with Opus inside of Claude Code. And then beyond that, just kind of
[01:53] Code. And then beyond that, just kind of like some status stuff, like, you know,
[01:55] like some status stuff, like, you know, taking a look at where it's at where it
[01:57] taking a look at where it's at where it is in its particular job. So, let's dive
[01:59] is in its particular job. So, let's dive into this and take a look at the
[02:00] into this and take a look at the install. Now, to install this is pretty
[02:02] install. Now, to install this is pretty simple. You're just going to run this
[02:04] simple. You're just going to run this command to add it to the marketplace,
[02:07] command to add it to the marketplace, and I'll have all these commands down in
[02:08] and I'll have all these commands down in the description. And then you're going
[02:09] the description. And then you're going to run this plugin command to install
[02:11] to run this plugin command to install it, codex@openai-codex.
[02:13] it, codex@openai-codex. As usual, ask where you want to install
[02:15] As usual, ask where you want to install it. I'm going to do user scope, and then
[02:16] it. I'm going to do user scope, and then we just need to reload the plugins to
[02:18] we just need to reload the plugins to get it up and working. And then lastly,
[02:19] get it up and working. And then lastly, we want to run codex:setup.
[02:22] we want to run codex:setup. In case you didn't realize, there's also
[02:23] In case you didn't realize, there's also a GitHub repo for this which also goes
[02:26] a GitHub repo for this which also goes over all of the install commands. So,
[02:28] over all of the install commands. So, I'll link that in the description as
[02:29] I'll link that in the description as well. And the usage rates are tied to
[02:31] well. And the usage rates are tied to your chat GPT account, even if you're on
[02:33] your chat GPT account, even if you're on the free account, apparently. So, just
[02:35] the free account, apparently. So, just understand it's going to be pulling from
[02:36] understand it's going to be pulling from your codex usage. It's going to ask if
[02:38] your codex usage. It's going to ask if you want to install codex. Yes, for that
[02:40] you want to install codex. Yes, for that you log in.
[02:41] you log in. And that will send you to the browser
[02:43] And that will send you to the browser where it runs you through the
[02:43] where it runs you through the authentication process. Now, there's
[02:45] authentication process. Now, there's really two obvious use cases for this
[02:47] really two obvious use cases for this codex tool inside of Claude Code. The
[02:49] codex tool inside of Claude Code. The first one is dealing with the usage
[02:52] first one is dealing with the usage limits inside of Claude Code normally.
[02:54] limits inside of Claude Code normally. If you're on the pro plan with Anthropic
[02:56] If you're on the pro plan with Anthropic 5X Max, you can hit those limits very
[02:58] 5X Max, you can hit those limits very quickly, especially with some of the CLI
[03:00] quickly, especially with some of the CLI bugs we've been seeing in the last week.
[03:02] bugs we've been seeing in the last week. If that's the case, what you might want
[03:03] If that's the case, what you might want to do is use Opus 4.6 to plan and codex
[03:07] to do is use Opus 4.6 to plan and codex to execute. And to do that, again, very
[03:09] to execute. And to do that, again, very simple. You're just going to do codex
[03:11] simple. You're just going to do codex rescue, and then from there
[03:13] rescue, and then from there you're going to give it the prompt. And
[03:15] you're going to give it the prompt. And you can also specify a whole bunch of
[03:16] you can also specify a whole bunch of things. Like you see all the flags here,
[03:18] things. Like you see all the flags here, including the effort level and all that.
[03:20] including the effort level and all that. And remember,
[03:21] And remember, codex, the model is very solid. And
[03:25] codex, the model is very solid. And again, the usage isn't even close to
[03:26] again, the usage isn't even close to what Anthropic charges. But I think the
[03:27] what Anthropic charges. But I think the more interesting use case is what I
[03:29] more interesting use case is what I talked about earlier, and that's the
[03:30] talked about earlier, and that's the adversarial review. So, let's put that
[03:31] adversarial review. So, let's put that to the test. So, I'm going to have it
[03:33] to the test. So, I'm going to have it take a look at my Twitter engagement
[03:36] take a look at my Twitter engagement {slash} research bot. This is the web
[03:38] {slash} research bot. This is the web app I had Claude Code build.
[03:39] app I had Claude Code build. Essentially, what it does is it scans
[03:42] Essentially, what it does is it scans tweets in the AI space for every like 30
[03:44] tweets in the AI space for every like 30 to 45 minutes. It has a quality filter.
[03:47] to 45 minutes. It has a quality filter. It has scoring signals based on a number
[03:49] It has scoring signals based on a number of different parameters. It's connected
[03:51] of different parameters. It's connected to Superbase to make sure the tweets
[03:52] to Superbase to make sure the tweets don't get repeated. It has a scoring
[03:54] don't get repeated. It has a scoring system and it integrates Soft Max,
[03:56] system and it integrates Soft Max, picks, everything gets pushed to
[03:57] picks, everything gets pushed to Telegram and I also have AI built in
[03:59] Telegram and I also have AI built in there to help with responses. So,
[04:01] there to help with responses. So, there's a fair amount going on and then
[04:03] there's a fair amount going on and then on top of that it also tracks like all
[04:05] on top of that it also tracks like all of my responses so we can kind of a
[04:07] of my responses so we can kind of a feedback loop. So, this is like a
[04:09] feedback loop. So, this is like a relatively it's not super complicated
[04:11] relatively it's not super complicated but this isn't like a landing page we're
[04:12] but this isn't like a landing page we're having to look at. So,
[04:14] having to look at. So, we're going to see what Codex comes back
[04:17] we're going to see what Codex comes back with when we do an adversarial review on
[04:19] with when we do an adversarial review on the code for this, right? So, let's see
[04:21] the code for this, right? So, let's see how it does. So, we'll keep it pretty
[04:23] how it does. So, we'll keep it pretty open to interpretation so we're telling
[04:24] open to interpretation so we're telling Codex take a look at the code base and
[04:26] Codex take a look at the code base and let me know what you think. The first
[04:28] let me know what you think. The first thing it does is it tells us, "Hey,
[04:29] thing it does is it tells us, "Hey, we're going to estimate the review size
[04:30] we're going to estimate the review size to determine the best mode." And then
[04:32] to determine the best mode." And then from there it says, "Hey, do you want to
[04:33] from there it says, "Hey, do you want to run it in the background or do you just
[04:35] run it in the background or do you just want to wait for the results?" So, we're
[04:36] want to wait for the results?" So, we're just going to wait for the results. And
[04:37] just going to wait for the results. And it's telling us review scope includes
[04:39] it's telling us review scope includes the full code base plus nine working
[04:41] the full code base plus nine working tree changes, one modified file, eight
[04:43] tree changes, one modified file, eight untracked files. So, it knows there's a
[04:45] untracked files. So, it knows there's a kind of there's a lot it needs to take a
[04:46] kind of there's a lot it needs to take a look at. And while that's working, let's
[04:47] look at. And while that's working, let's talk about how adversarial reviews are
[04:49] talk about how adversarial reviews are actually working. So, we just kind of
[04:51] actually working. So, we just kind of saw the first four parts, right? It
[04:53] saw the first four parts, right? It parsed the arguments. We didn't pass any
[04:55] parsed the arguments. We didn't pass any flags so it's just going off its default
[04:57] flags so it's just going off its default settings. And then it estimated the
[04:58] settings. And then it estimated the review size, resolved the target, and
[05:00] review size, resolved the target, and collected some context. That was all
[05:02] collected some context. That was all that text about, "Hey, you know, we have
[05:03] that text about, "Hey, you know, we have these untracked changes and this is
[05:04] these untracked changes and this is going to take a while." Now, after those
[05:06] going to take a while." Now, after those first four steps, it's then going to
[05:07] first four steps, it's then going to build the adversarial prompt. And
[05:10] build the adversarial prompt. And there's seven attack surfaces it's going
[05:12] there's seven attack surfaces it's going to pay special attention to. That's
[05:14] to pay special attention to. That's authentication, data loss, rollbacks,
[05:18] authentication, data loss, rollbacks, race conditions, degraded dependencies,
[05:20] race conditions, degraded dependencies, version skew, and observability gaps.
[05:23] version skew, and observability gaps. Right? So, like seven things that are
[05:25] Right? So, like seven things that are somewhat under the surface that could
[05:27] somewhat under the surface that could really screw us if we try to push this
[05:28] really screw us if we try to push this to production and we don't have a handle
[05:30] to production and we don't have a handle on. From there it's going to send all
[05:31] on. From there it's going to send all that information back to the OpenAI
[05:33] that information back to the OpenAI server so Codex can take a look at it.
[05:35] server so Codex can take a look at it. And then it will give us our structured
[05:37] And then it will give us our structured JSON output and we should expect it to
[05:39] JSON output and we should expect it to look something like this, right? And it
[05:41] look something like this, right? And it will give us some sort of severity of
[05:43] will give us some sort of severity of its findings, right? Versus critical,
[05:44] its findings, right? Versus critical, high, medium, and low.
[05:46] high, medium, and low. As well as recommendations and next
[05:48] As well as recommendations and next steps. But all you have to do is sit
[05:49] steps. But all you have to do is sit there inside of Claude code and wait for
[05:51] there inside of Claude code and wait for the response. So, Codex came back with
[05:53] the response. So, Codex came back with four issues with our code base and all
[05:55] four issues with our code base and all of them had a severity of high and I
[05:57] of them had a severity of high and I pasted this over to Excalidraw, so it's
[05:59] pasted this over to Excalidraw, so it's a little easier for us to go through it.
[06:00] a little easier for us to go through it. So, for each one of these it gives us
[06:02] So, for each one of these it gives us the severity, the area, the actual
[06:05] the severity, the area, the actual issue, the files, as well as the actual
[06:07] issue, the files, as well as the actual lines of code we need to take a look at.
[06:10] lines of code we need to take a look at. And then, importantly, like what's the
[06:11] And then, importantly, like what's the actual impact here as well as the fix.
[06:13] actual impact here as well as the fix. So, number one, it's saying we had an
[06:15] So, number one, it's saying we had an issue with our dead-up logic. Number two
[06:17] issue with our dead-up logic. Number two was how we were dealing with Telegram
[06:18] was how we were dealing with Telegram polling. Third was our schema drift. And
[06:21] polling. Third was our schema drift. And then, lastly, was our actual dashboard
[06:24] then, lastly, was our actual dashboard build. So, this is actually relatively
[06:26] build. So, this is actually relatively important stuff and, luckily, it doesn't
[06:28] important stuff and, luckily, it doesn't look like the fixes would be too
[06:29] look like the fixes would be too difficult to implement. But what I'm
[06:32] difficult to implement. But what I'm interested in is, okay, this is what
[06:34] interested in is, okay, this is what Codex gave us. What would Claude give us
[06:38] Codex gave us. What would Claude give us if we asked for a similar,
[06:40] if we asked for a similar, you know, sort of adversarial review on
[06:43] you know, sort of adversarial review on its own code base because I think that
[06:45] its own code base because I think that would be kind of enlightening to see
[06:46] would be kind of enlightening to see them head-to-head and like what Codex
[06:47] them head-to-head and like what Codex really does differently than the other
[06:49] really does differently than the other cuz for all we know they're the exactly
[06:50] cuz for all we know they're the exactly the same and so the video is pointless.
[06:52] the same and so the video is pointless. So, I'm now having Opus run the same
[06:55] So, I'm now having Opus run the same sort of adversarial code review. I had
[06:57] sort of adversarial code review. I had Codex come up with the particular
[06:59] Codex come up with the particular prompt. So, essentially, it's just
[07:00] prompt. So, essentially, it's just saying, "Hey, I want you to challenge
[07:02] saying, "Hey, I want you to challenge the implementation and design choices.
[07:04] the implementation and design choices. Here's some things I want you to
[07:05] Here's some things I want you to evaluate and then here's the sort of
[07:07] evaluate and then here's the sort of output format." So, let's see what it
[07:09] output format." So, let's see what it comes back with. And so, here's the
[07:10] comes back with. And so, here's the results broken down. So, first of all,
[07:12] results broken down. So, first of all, they did have one shared finding. So,
[07:14] they did have one shared finding. So, they both agreed that the Telegram issue
[07:17] they both agreed that the Telegram issue was a problem. So, this was the one
[07:19] was a problem. So, this was the one issue that they both found and that they
[07:21] issue that they both found and that they said was either high or critical. Codex
[07:23] said was either high or critical. Codex said it was just high and then Opus said
[07:25] said it was just high and then Opus said it was critical. Now, Opus itself found
[07:28] it was critical. Now, Opus itself found seven other additional issues ranked
[07:31] seven other additional issues ranked high or critical that Codex didn't. Now,
[07:33] high or critical that Codex didn't. Now, we're not saying that just by virtue of
[07:36] we're not saying that just by virtue of saying there's more issues that Opus was
[07:38] saying there's more issues that Opus was necessarily better than Codex. Just
[07:40] necessarily better than Codex. Just pointing out it found seven things we
[07:42] pointing out it found seven things we might want to look at that Codex didn't.
[07:44] might want to look at that Codex didn't. Then obviously, on the flip side, we
[07:46] Then obviously, on the flip side, we found three issues with Codex that Opus
[07:48] found three issues with Codex that Opus missed. So, what does this mean if we
[07:49] missed. So, what does this mean if we kind of look at this in totality? Does
[07:50] kind of look at this in totality? Does this mean Opus is better than Codex
[07:52] this mean Opus is better than Codex because it found more, or that Codex is
[07:54] because it found more, or that Codex is better than Opus cuz it narrowed down on
[07:56] better than Opus cuz it narrowed down on four and didn't take us onto a weird
[07:58] four and didn't take us onto a weird path?
[07:59] path? I think what you draw from this is kind
[08:00] I think what you draw from this is kind of whatever you want to draw from this.
[08:01] of whatever you want to draw from this. And that probably is that
[08:04] And that probably is that there is kind of value in having these
[08:05] there is kind of value in having these two systems look at it, right? It's a
[08:06] two systems look at it, right? It's a second pair of eyes versus having Opus
[08:09] second pair of eyes versus having Opus grade Opus all the time. You know, there
[08:11] grade Opus all the time. You know, there is some sort of fundamental flaw, I
[08:13] is some sort of fundamental flaw, I think, with having the same AI system do
[08:16] think, with having the same AI system do the planning, the generating, and the
[08:17] the planning, the generating, and the evaluating. And if we're able to very
[08:19] evaluating. And if we're able to very easily bring in Codex, especially at its
[08:22] easily bring in Codex, especially at its price point, to even just do things like
[08:24] price point, to even just do things like this, like an adversarial review, again,
[08:26] this, like an adversarial review, again, that's like one of the great AI coding
[08:28] that's like one of the great AI coding like on the margin plays, which again is
[08:30] like on the margin plays, which again is like, why not?
[08:31] like, why not? You know, if you're already paying for
[08:33] You know, if you're already paying for ChatGPT, if you're already paying the 20
[08:35] ChatGPT, if you're already paying the 20 bucks a month, and I can now bring in
[08:37] bucks a month, and I can now bring in this and kind of have Codex just take a
[08:38] this and kind of have Codex just take a look at anything this simply, like
[08:41] look at anything this simply, like what's the downside to this, really? I
[08:44] what's the downside to this, really? I mean, I don't think
[08:46] mean, I don't think in a quick test like this, we're going
[08:47] in a quick test like this, we're going to have any definitive answer like, oh,
[08:48] to have any definitive answer like, oh, Codex is better versus Opus. And I think
[08:50] Codex is better versus Opus. And I think that whole conversation sort of misses
[08:52] that whole conversation sort of misses the point. This is just like one more
[08:53] the point. This is just like one more tool in our toolbox, and now we can use
[08:55] tool in our toolbox, and now we can use it. So, I think this is great. Now, we
[08:57] it. So, I think this is great. Now, we can get way more specific with
[08:58] can get way more specific with adversarial review as well, because our
[09:02] adversarial review as well, because our prompt was pretty just like open and out
[09:03] prompt was pretty just like open and out there, and it was able to interpret it
[09:05] there, and it was able to interpret it in a lot of different ways. But just
[09:06] in a lot of different ways. But just based off of the GitHub examples, right?
[09:08] based off of the GitHub examples, right? You can get pretty specific about what
[09:10] You can get pretty specific about what you want Codex to look at. So, overall,
[09:12] you want Codex to look at. So, overall, I think this is a great addition to the
[09:13] I think this is a great addition to the Claude code ecosystem. The more tools,
[09:15] Claude code ecosystem. The more tools, the better, especially if you're someone
[09:16] the better, especially if you're someone who either A is already paying for
[09:18] who either A is already paying for ChatGPT, or B is like on the Anthropic
[09:21] ChatGPT, or B is like on the Anthropic Pro plan, and then maybe you aren't
[09:23] Pro plan, and then maybe you aren't paying for ChatGPT. 100 bucks a month
[09:25] paying for ChatGPT. 100 bucks a month might be a little much, 200 bucks might
[09:27] might be a little much, 200 bucks might certainly be too much. Like, this almost
[09:29] certainly be too much. Like, this almost gives us like this middle ground between
[09:31] gives us like this middle ground between the $20 sub and the $100 sub, because
[09:34] the $20 sub and the $100 sub, because well, Codex really is a great value
[09:36] well, Codex really is a great value play. So,
[09:37] play. So, definitely check it out. Super easy
[09:39] definitely check it out. Super easy setup. Let me know what you thought. And
[09:41] setup. Let me know what you thought. And as always, I'll see you around.
```

## All frames

_Total: 80. Hero frames flagged with star._

* `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0001.jpg` (t=00:00)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0002.jpg` (t=00:07)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0003.jpg` (t=00:15)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0004.jpg` (t=00:22)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0005.jpg` (t=00:29)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0006.jpg` (t=00:36)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0007.jpg` (t=00:44)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0008.jpg` (t=00:51)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0009.jpg` (t=00:58)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0010.jpg` (t=01:06)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0011.jpg` (t=01:13)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0012.jpg` (t=01:20)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0013.jpg` (t=01:27)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0014.jpg` (t=01:35)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0015.jpg` (t=01:42)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0016.jpg` (t=01:49)
* `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0017.jpg` (t=01:57)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0018.jpg` (t=02:04)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0019.jpg` (t=02:11)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0020.jpg` (t=02:18)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0021.jpg` (t=02:26)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0022.jpg` (t=02:33)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0023.jpg` (t=02:40)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0024.jpg` (t=02:48)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0025.jpg` (t=02:55)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0026.jpg` (t=03:02)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0027.jpg` (t=03:09)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0028.jpg` (t=03:17)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0029.jpg` (t=03:24)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0030.jpg` (t=03:31)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0031.jpg` (t=03:38)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0032.jpg` (t=03:46)
* `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0033.jpg` (t=03:53)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0034.jpg` (t=04:00)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0035.jpg` (t=04:08)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0036.jpg` (t=04:15)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0037.jpg` (t=04:22)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0038.jpg` (t=04:29)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0039.jpg` (t=04:37)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0040.jpg` (t=04:44)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0041.jpg` (t=04:51)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0042.jpg` (t=04:59)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0043.jpg` (t=05:06)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0044.jpg` (t=05:13)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0045.jpg` (t=05:20)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0046.jpg` (t=05:28)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0047.jpg` (t=05:35)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0048.jpg` (t=05:42)
* `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0049.jpg` (t=05:50)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0050.jpg` (t=05:57)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0051.jpg` (t=06:04)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0052.jpg` (t=06:11)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0053.jpg` (t=06:19)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0054.jpg` (t=06:26)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0055.jpg` (t=06:33)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0056.jpg` (t=06:41)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0057.jpg` (t=06:48)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0058.jpg` (t=06:55)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0059.jpg` (t=07:02)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0060.jpg` (t=07:10)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0061.jpg` (t=07:17)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0062.jpg` (t=07:24)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0063.jpg` (t=07:32)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0064.jpg` (t=07:39)
* `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0065.jpg` (t=07:46)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0066.jpg` (t=07:53)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0067.jpg` (t=08:01)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0068.jpg` (t=08:08)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0069.jpg` (t=08:15)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0070.jpg` (t=08:23)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0071.jpg` (t=08:30)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0072.jpg` (t=08:37)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0073.jpg` (t=08:44)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0074.jpg` (t=08:52)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0075.jpg` (t=08:59)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0076.jpg` (t=09:06)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0077.jpg` (t=09:14)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0078.jpg` (t=09:21)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0079.jpg` (t=09:28)
  `/var/folders/zy/4hjjtsfn05zbtd49tg53588m0000gn/T/watch-f2mb7v22/frames/frame_0080.jpg` (t=09:35)
