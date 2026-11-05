# Patient no-show rates by clinic setting

Published patient no-show rates, each linked to its source. Read it at https://puppeteer-ai.github.io/no-show-rates/

- `data/no-show-rates.csv` and `data/no-show-rates.json` hold the data.
- `build.py` regenerates the CSV and `index.html` from the JSON. It uses only the Python standard library.

Compiled by [Recupra](https://recupra.com/), which sells no-show recovery software to clinics. None of these figures are Recupra's, and no patient data is included.

## Fields

`rate_pct` is the headline figure. `rate_low` and `rate_high` are a confidence interval or a range across clinics, where the source gives one. `kind` is `measured`, `pooled` (a review or meta-analysis) or `target` (guidance, not a measurement). `checked_against` says which text the figure was checked against on `checked_on`.

Studies define the rate differently, so do not rank the rows against each other.

## Corrections

Open an issue with the row `id` and a link to the source.

## License

The data and page are CC BY 4.0, see `LICENSE`. Cite the original study for any single figure.
