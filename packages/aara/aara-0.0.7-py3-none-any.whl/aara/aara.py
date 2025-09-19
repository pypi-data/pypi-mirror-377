from pathlib import Path
import argparse
from configparser import ConfigParser
import re
import urllib.request
import aiohttp

from bs4 import BeautifulSoup

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, ListView, ListItem, Static
from textual.containers import VerticalGroup, Horizontal, VerticalScroll

def get_arxiv_articles(category):

    url = f"https://arxiv.org/list/{category}/new"

    response = urllib.request.urlopen(url)
    response_text = response.read().decode("utf-8")

    soup = BeautifulSoup(response_text, "html.parser")

    date_content = soup.find("h3", string=lambda s: s and "Showing new listings for" in s)
    date_str = date_content.text.strip()[len("Showing new listings for "):] if date_content else "Date header not found."

    new_articles = soup.find_all("dl")[0]

    dts = new_articles.find_all("dt")
    dds = new_articles.find_all("dd")

    articles = []

    for dt, dd in zip(dts, dds):
        arxiv_id = dt.find("a", title="Abstract")
        arxiv_id = arxiv_id.text.strip().split(":")[1] if arxiv_id else "N/A"

        title = dd.find("div", class_="list-title mathjax")
        title = title.text.replace("Title:", "").strip() if title else "N/A"

        authors = dd.find("div", class_="list-authors")
        authors = authors.text.replace("Authors:", "").strip() if authors else "N/A"

        abstract = dd.find("p", class_="mathjax")
        abstract = abstract.text.strip() if abstract else "N/A"

        comments = dd.find("div", class_="list-comments")
        comments = comments.text.replace("Comments:", "").strip() if comments else ""

        subjects = dd.find("div", class_="list-subjects")
        subjects = subjects.text.replace("Subjects:", "").strip() if subjects else ""

        articles.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "comments": comments,
            "subjects": subjects
        })

    return date_str, articles

class AARA(App):
    CSS = """
    Horizontal {
        height: 1fr;
    }
    ListView {
        width: 40%;
        border: solid round #888;
    }
    ListView:focus {
        border: solid round white;
    }
    VerticalScroll#abstract {
        padding: 1 2;
        border: solid round #888;
    }
    VerticalScroll#abstract:focus {
        border: solid round white;
    }
    """

    BINDINGS = [
                ("q", "quit()", "Quit"),
                ("{", "jump_five_up()", "Jump Five Up"),
                ("}", "jump_five_down()", "Jump Five Down"),
                ("g", "jump_top()", "Jump to Top"),
                ("G", "jump_bottom()", "Jump to Bottom"),
                ("a", "open_url('abs')", "Open Abstract"),
                ("s", "save_url()", "Save PDF"),
                ("d", "open_url('pdf')", "Open PDF")
               ]

    DEFAULT_CONFIG = {"CONFIG":
                        {"num_words": 4},
                      "FILEPATHS":
                        {"download_folder": Path.home() / "Downloads"}}

    def __init__(self, category, config_path=None):
        super().__init__()
        self.category = category
        self.date_str, self.articles = get_arxiv_articles(self.category)

        if config_path is None:
            self.config_folder = Path.home() / ".config/aara"
        else:
            self.config_folder = Path(config_path)

        self.config_path = self.config_folder / "aara.ini"
        self.saved_state_path = self.config_folder / "state.ini"

        if self.config_path.exists():
            self.load_config()
        else:
            self.make_default_config()
            self.load_config()

        if self.saved_state_path.exists():
            self.load_saved()
        else:
            self.saved = {self.date_str: []}

    def make_default_config(self):
        config = ConfigParser()
        config.read_dict(self.DEFAULT_CONFIG)
        config_folder = self.config_path.parent
        config_folder.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as configfile:
            config.write(configfile)

    def load_config(self):
        config = ConfigParser()
        config.read(self.config_path)
        self.num_words = int(config["CONFIG"]["num_words"])
        self.download_folder = Path(config["FILEPATHS"]["download_folder"])
        if not self.download_folder.exists():
            self.download_folder.mkdir(parents=True, exist_ok=True)

    def load_saved(self):
        config = ConfigParser()
        config.read(self.saved_state_path)
        self.saved = {}
        saved_date = config.sections()[0]
        if saved_date == self.date_str:
            self.saved[saved_date] = config[saved_date]["saved_ids"].split(",")
        else:
            self.saved[self.date_str] = []

    def save_saved(self):
        config = ConfigParser()
        for date, ids in self.saved.items():
            config[date] = {"saved_ids": ",".join(ids).strip(",")}
        with open(self.saved_state_path, "w") as configfile:
            config.write(configfile)

    def compose(self) -> ComposeResult:
        yield Header()

        self.status_bar = Static("Status", id="status_bar")
        yield self.status_bar

        with VerticalGroup():
            yield Static(f"[dim]{self.category} | {self.date_str} | Total Articles: {len(self.articles)}[/dim]")
        with Horizontal():

            titles = []
            for i, article in enumerate(self.articles):
                title = f"[dim][{i+1:>2}][/dim] [b]{article['title']}[/b]"
                if article["arxiv_id"] in self.saved.get(self.date_str, []):
                    title = f"✓ {title}"
                titles.append(title)

            self.list_view = ListView(*[ListItem(Static(title)) for title in titles])
            yield self.list_view

            self.abstract_view = VerticalScroll(Static("Select an article to view its abstract."), id="abstract")
            yield self.abstract_view

        yield Footer()

    def on_mount(self):
        self.list_view.focus()
        if self.articles:
            self.show_abstract(0)

    def action_quit(self):
        self.save_saved()
        self.exit()

    def show_abstract(self, idx):
        info = self.articles[idx]
        self.abstract_view.children[0].update(
            f"[dim]arxiv:{info['arxiv_id']}[/dim]\n"
            +f"[skyblue][b][u]{info['title']}[/u][/b][/skyblue]\n"
            +f"[khaki]{info['authors']}[/khaki]\n"
            +"\n"
            +f"{info['abstract']}\n"
            +"\n"
            +f"[dim]Comments: {info['comments']}[/dim]\n"
            +f"[dim]Subjects: {info['subjects']}[/dim]"
        )

    def on_resize(self, event):
        self.show_abstract(self.list_view.index)

    def on_list_view_highlighted(self, event):
        self.show_abstract(self.list_view.index)

    def action_open_url(self, urltype):
        arxiv_id = self.articles[self.list_view.index]["arxiv_id"]
        arxiv_url = f"https://arxiv.org/{urltype}/{arxiv_id}"
        self.open_url(arxiv_url)

    def action_save_url(self):
        arxiv_id = self.articles[self.list_view.index]["arxiv_id"]
        self.saved[self.date_str].append(arxiv_id)

        # might accidentally get the institutional name, not sure how to fix this
        first_author_lastname = self.articles[self.list_view.index]["authors"].split(",")[0].split()[-1]

        shortened_title = "_".join(self.articles[self.list_view.index]["title"].split()[:self.num_words])
        rejected_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|", "$"]
        shortened_title = "".join(c for c in shortened_title if c not in rejected_chars)
        shortened_title = re.sub(r"[^a-zA-Z0-9]", "_", shortened_title).strip("_")

        year = self.date_str.split()[-1]

        arxiv_url = f"https://arxiv.org/pdf/{arxiv_id}"
        save_path = self.download_folder / f"{arxiv_id}_{year}_{first_author_lastname}_{shortened_title}.pdf"

        home_str = str(Path.home())
        save_path_str = str(save_path)
        
        if save_path_str.startswith(home_str):
           save_path_str = save_path_str.replace(home_str, "~", 1)

        if save_path.exists():
            self.status_bar.update(f"File already exists, at {save_path_str}")
            return

        self.status_bar.update(f"Saving to {save_path_str}")

        current_item = self.list_view.highlighted_child
        if current_item:
            #current_text = self.articles[self.list_view.index]["title"]
            current_text = current_item.children[0].render().plain
            if not current_text.startswith("✓"):
                new_text = f"✓ {current_text}"
                current_item.children[0].update(new_text)

        self.run_worker(self.save_pdf_url(arxiv_url, save_path))

    async def save_pdf_url(self, url, save_path):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                with open(save_path, "wb") as outfile:
                    async for chunk in response.content.iter_chunked(8192):
                        outfile.write(chunk)

    def action_jump_five_up(self):
        for _ in range(5):
            self.list_view.action_cursor_up()

    def action_jump_five_down(self):
        for _ in range(5):
            self.list_view.action_cursor_down()

    def action_jump_top(self):
        for _ in range(self.list_view.index):
            self.list_view.action_cursor_up()

    def action_jump_bottom(self):
        for _ in range(len(self.articles) - 1 - self.list_view.index):
            self.list_view.action_cursor_down()

    def on_key(self, event):
        if event.key in ("h", "left"):
            self.list_view.focus()
        elif event.key in ("j"):
            if self.list_view.has_focus:
                self.list_view.action_cursor_down()
            elif self.abstract_view.has_focus and self.abstract_view.allow_vertical_scroll:
                self.abstract_view.action_scroll_down()
        elif event.key in ("k"):
            if self.list_view.has_focus:
                self.list_view.action_cursor_up()
            elif self.abstract_view.has_focus and self.abstract_view.allow_vertical_scroll:
                self.abstract_view.action_scroll_up()
        elif event.key in ("l", "right"):
            self.abstract_view.focus()

def main():
    parser = argparse.ArgumentParser(description="ArXiv Article Reader")
    parser.add_argument("category", help="ArXiv category to fetch articles from")
    args = parser.parse_args()

    app = AARA(category=args.category)
    app.run()

if __name__ == "__main__":
    main()
