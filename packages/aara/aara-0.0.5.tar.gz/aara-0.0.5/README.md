# An arXiv Reading App (aara)

A super simple [Textual](https://github.com/Textualize/textual) application for reading the latest posts on the arXiv in the terminal. This scrapes the arXiv "new" page from the category you specify. I found the arXiv search API to be lacking in functionality and the RSS feeds are blank if there was no update that day (e.g. like on a Saturday or Sunday). So, I wrote my own terminal app to read the arXiv.

## Installation

To install:

``` sh
pip install aara
```

For development only (using `uv`):

``` sh
git clone https://github.com/jsnguyen/aara
cd aara
uv run aara astro-ph
```

## Usage

Just run:

``` sh
# For astro-ph
aara astro-ph
```

More generally:

``` sh
aara <arXiv category>
```

## Config

Configs are stored at `~/.config/aara/aara.ini`.

You can change the save name parameter by changing `num_words`, which currently takes the first 4 words of the title by default.

You can also change the save directory by modifying the `downloads_folder` variable to a valid path.

## Bindings

Basic vim bindings are implemented, `hjkl`, `g`, `G`, and `{}`. The arrow keys can also be used for navigation. Note that scrolling in abstract window using the vim bindings doesn't work quite yet, but this is a pretty rare occurrence.

`a` opens the abstract of the article using your web browser

`s` will save the pdf to the location specified in the config, but if you haven't set anything it goes to `~/Downloads` by default. The naming scheme is `<arxiv id>_<year>_<first author last name>_<first four words title>.pdf`.

`d` will open the pdf of the article directly

`q` to quit

## Misc

There is also a state file stored at `~/.config/aara/state.ini` that tracks what pdf files you have already saved. This is not designed to be human-editable and is automatically loaded if it exists. It will overwrite every time you close the application.
