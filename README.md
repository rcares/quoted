# quoted

Feed your brain with the best random quotes from multiple web portals.

## Features

* Multiple WEB sources
* Rich Text
* Argument options
* Logs

## Requirements

```
git
python 3x
poetry
```

## Installation

### Linux/MacOS

```
$ pip install quoted
```

### Windows


## Usage

```
$ quoted

“Insanity is doing the same thing, over and over again, but expecting different results.”
―― Narcotics Anonymous

tags: humor, insanity, life, misattributed-ben-franklin, misattributed-mark-twain, misattributed-to-einstein
link: https://www.goodreads.com/quotes/5543-insanity-is-doing-the-same-thing-over-and-over-again

© goodreads

Powered by quoted
```
## Development

### Run

```
$ poetry install
$ poetry run quoted
```

### Build

```
$ poetry build
```

The distribution packages are located in `dist` directory.

### Publish

```
$ poetry publish
```

### Spiders

Spider output is a list of dicts with the structure:
```
[
    {
        'author': 'Author Name',
        'text': 'Text of Quote',
        'tags': ['tag1','tag2'],
        'url': 'https://www.quotesource.com/linktoquote'
    }
]
```

## Todo

* Cache
* Supports `bash` and `zsh`
* Output formats

## Contribution

* File bugs, feature requests in [GitHub Issues](https://github.com/rcares/quoted/issues).
