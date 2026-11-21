[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Cervus121212/bold-kestrel-46/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

# THE WORLD TODAY — Saturday 21 November 2026

**Saturday 21 November 2026: 9 stories, 7 regions — COP31 overtime, Kyiv strikes, Mercury arrival**

One front page that sums up Saturday 21 November 2026 in 9 stories across
7 regions. Clean, not dense: one big hero, six secondary stories, two
"Also today" lines — every headline readable at 300 pixels across.

## The 9 stories (all sourced, all verified 21 Nov 2026)

| # | Story | Source | Status |
|---|-------|--------|--------|
| 01 | COP31 talks run into overtime in Antalya — no deal, draft names no fossil fuels, $120bn aid target dropped, third draft due Saturday morning | Reuters / AP | CONFIRMED |
| 02 | Russia fires 110+ missiles and 400+ drones at Ukraine; nine killed; missiles also land in Poland; NATO chief heads to Warsaw | Reuters / AFP | CONFIRMED |
| 03 | Denmark expels Russia's defence attache over an alleged plot to kill rapper Kyivstoner; two men charged | AP | REPORTED |
| 04 | Wall Street in freefall as the AI trade cracks — Nasdaq -5.3%, S&P 500 -3.7%, Dow -1.9%, Nvidia -14% in a day | Reuters | CONFIRMED |
| 05 | ESA-JAXA probe BepiColombo enters Mercury orbit, eight years after launch | ESA | CONFIRMED |
| 06 | Cyclone Akvan crosses Odisha at 80 km/h; heavy rain runs on into Saturday | IMD / PTI | CONFIRMED |
| 07 | Saudi defences stop three Houthi missiles aimed at Riyadh | Al Arabiya | REPORTED |
| 08 | Trump, back from Shenzhen, defends his summit with Xi and Putin | Reuters | CONFIRMED |
| 09 | Congress races to avert a shutdown as the Iran war divides lawmakers | Reuters | REPORTED |

Markets strip (Friday close, Reuters): Nasdaq -5.3%, S&P 500 -3.7%,
Dow -1.9%, VIX 36, Anthropic -9%.

## How it is built

`main.py` is stdlib-only (os/struct/zlib) — no PIL, no network. It draws
the whole page with a hand-built 5x7 bitmap font scaled up (nothing below
2x, so every line stays legible at thumbnail size) and writes a
deterministic PNG. The hero illustration (Antalya coast: sun, sea, skyline,
conference hall) is drawn flat in three inks.

```sh
python3 main.py   # writes entry.png (1024x1024, <= 1 MiB)
```

Run it twice: the sha256 is identical. Freshness anchor: drand round
6660020 (`.makefun/freshness.json`).
