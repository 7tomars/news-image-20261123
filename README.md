# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/7tomars/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/7tomars/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

**The World in One Image** — a one-page newspaper front page that sums up
the world's news of **Monday 23 November 2026** in a single 1024×1024 PNG.

`generate.py` is a pure Python 3 program (standard library only, no
network, no external assets). It draws the page pixel by pixel into an RGB
framebuffer with a built-in 5×7 bitmap font and writes it out with a
hand-rolled PNG encoder (zlib + struct). The render is fully
deterministic: every run produces byte-identical output. The eight
stories and the reporting behind each one are listed in
[sources.md](sources.md).

## Run it

```sh
python3 main.py   # writes entry.png
```

## The eight stories

1. **Russian warship sunk** — sea drones sink the corvette Merkury in
   Benghazi port. *(CNN; Wall Street Journal; Fox News)*
2. **Biggest US House majority since 1992** — Democrats hit 258 seats
   after the Carolina flip. *(The Times; Daily Fox News; BBC)*
3. **Prabowo to name VP candidates today** — two names go to the MPR;
   parliament votes in December. *(Reuters; Jakarta Globe)*
4. **M6.5 quake strikes deep below Vanuatu** — 601 km down; no tsunami
   threat, agencies say. *(Xinhua; Australian Bureau of Meteorology;
   PHIVOLCS)*
5. **Oil slips as AI selloff spreads** — Brent at 92.29 dollars; Gulf
   attacks cap losses. *(Reuters; BigGo Finance)*
6. **Search goes on in Dymer rubble** — boy, 7, pulled alive after 14
   hours under rubble. *(ERR Reflect; The Gaze; BBC)*
7. **FIFA to confirm UK as 2035 hosts** — unopposed four-nation bid;
   first UK cup since 1966. *(GhanaMMA; BigNewsGH)*
8. **New Zealand hold on for draw** — Mitchell and Phillips bat out day
   five to deny India. *(Reuters; ESPNcricinfo)*

---
<sub>Entered on [make.fun](https://make.fun/?ref=xs6hh474&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
