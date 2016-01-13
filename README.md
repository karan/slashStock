# slashStock

Get stock quotes in Twitter. (@slashStock GOOG)

[![](http://i.imgur.com/w68AXmh.png?1)](https://twitter.com/slashStock/status/684970654714626052)

### Usage

The bot understand commands in this format:

    @slashStock SYMBOL TIME_SPAN

* `SYMBOL` - Any stock symbol. Can contain `$` symbol. Can specify the exchange.
* `TIME_SPAN` (optional) - Time span to pull the chart for.
    * Defaults to `1d` if not specifed
    * Possible values: one of `1d`, `5d`, `3m`, `6m`, `1y`, `2y`, `5y`, `my` (max)

### Example

* Amazon - `@slashStock AMZN`
* Netflix - `Netflix is now in 190 countries. Damn! @slashStock $NFLX`
* S&P 500 - `@slashStock SPY 5y`
* Greece ETF - `@slashStock GREK 2y`

### Where is this bot running?

Currently I'm running this bot on a 1GB [DigitalOcean](https://www.digitalocean.com/?refcode=422889a8186d) instance (Use that link to get a free VPS for 2 months). The bot is not resource-intensive and uses a couple dozen MBs of RAM.

## Running

#### Requirements

- Python 2+
- pip

#### Instructions 

Create a file called `config.py` that looks like `config_example.py`. Fill in the necessary values.

For Twitter config:

1. Register your app
2. Get your app's key and secret.
3. Create token and get the token and secret by running `oauth.py`

Then, to run the bot:

```bash
$ pip install -r requirements.txt
$ python bot.py
```

## License 

Apache 2.0
