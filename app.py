from datetime import date
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ---------------------------------------------------------------
# Data lives in plain Python lists (no database).
# It is kept in memory, so it RESETS whenever the app restarts.
# ---------------------------------------------------------------
GENRES = ["Romance", "Fiction", "Literary Fiction", "Fantasy",
          "Classic", "Mystery", "Non-fiction", "Poetry"]
STATUSES = ["Want to Read", "Reading", "Completed"]
goal_settings = {"yearly": 10}   # editable on the Goals page

# Reading moods used by the Discover section and the library filter
MOODS = [
    {"key": "romantics", "title": "For the hopeless romantics.", "line": "Slow burns and aching glances."},
    {"key": "midnight",  "title": "For the midnight thinkers.",  "line": "Quiet minds, long nights."},
    {"key": "escapism",  "title": "For a little escapism.",      "line": "Somewhere far from here."},
    {"key": "broken",    "title": "For the beautifully broken.", "line": "Stories that hold you gently."},
    {"key": "sunday",    "title": "For the slow Sunday mornings.", "line": "Tea, light and a good chapter."},
]

books = []


def make_book(title, author, genre, status, total_pages, pages_read, isbn="", mood=""):
    """Build one book dictionary and add it to the list."""
    if status == "Completed":
        pages_read = total_pages
    elif status == "Want to Read":
        pages_read = 0
    book = {
        "title": title,
        "author": author,
        "genre": genre,
        "status": status,
        "total_pages": total_pages,
        "pages_read": pages_read,
        "percent": int(pages_read / total_pages * 100),
        "isbn": isbn,            # used to fetch a cover image
        "mood": mood,
        "tone": len(books) % 5,  # colour of the CSS fallback cover
    }
    books.append(book)
    return book


# Sample shelf
make_book("The Seven Husbands of Evelyn Hugo", "Taylor Jenkins Reid", "Romance", "Reading", 400, 212, "9781501161933", "romantics")
make_book("Normal People", "Sally Rooney", "Literary Fiction", "Completed", 273, 273, "9781984822185", "romantics")
make_book("The Secret History", "Donna Tartt", "Mystery", "Reading", 559, 140, "9781400031702", "midnight")
make_book("Circe", "Madeline Miller", "Fantasy", "Completed", 393, 393, "9780316556347", "escapism")
make_book("A Little Life", "Hanya Yanagihara", "Literary Fiction", "Want to Read", 720, 0, "9780804172707", "broken")
make_book("Pride and Prejudice", "Jane Austen", "Classic", "Completed", 432, 432, "9780141439518", "sunday")
make_book("The Song of Achilles", "Madeline Miller", "Fantasy", "Reading", 378, 90, "9780062060624", "broken")
make_book("Klara and the Sun", "Kazuo Ishiguro", "Literary Fiction", "Want to Read", 303, 0, "9780593318171", "midnight")
make_book("Little Women", "Louisa May Alcott", "Classic", "Want to Read", 449, 0, "9780147514011", "sunday")
make_book("The Midnight Library", "Matt Haig", "Fiction", "Want to Read", 304, 0, "9780525559474", "escapism")

# Reading journal entries (newest first)
journal = [
    {"date": "24 Oct 2026", "title": "Chapter by candlelight", "note": "Reached page 212 of The Seven Husbands of Evelyn Hugo. I did not expect to feel this much."},
    {"date": "19 Oct 2026", "title": "A finished story", "note": "Closed Circe tonight. Quiet, strange and quietly perfect."},
    {"date": "11 Oct 2026", "title": "A new obsession", "note": "Started The Secret History. Everyone warned me. I am not sorry."},
    {"date": "02 Oct 2026", "title": "Sunday ritual", "note": "Re-read the opening of Pride and Prejudice with a pot of tea."},
]


def count(status):
    return len([b for b in books if b["status"] == status])


def get_stats():
    started = [b for b in books if b["status"] != "Want to Read"]
    progress = round(sum(b["percent"] for b in started) / len(started)) if started else 0
    return {
        "total": len(books),
        "reading": count("Reading"),
        "completed": count("Completed"),
        "progress": progress,  # average progress across books you have started
        "pages_read": sum(b["pages_read"] for b in books),
    }


def first_with(status):
    return next((b for b in books if b["status"] == status), books[0])


@app.route("/")
def index():
    # Reading books come first, then the rest (sort is stable)
    featured = sorted(books, key=lambda b: b["status"] != "Reading")[:6]
    moods = [dict(m, count=len([b for b in books if b["mood"] == m["key"]])) for m in MOODS]
    return render_template(
        "index.html",
        stats=get_stats(),
        featured=featured,
        moods=moods,
        hero=[b for b in books if b["isbn"]][:3],
        current=first_with("Reading"),
        upnext=first_with("Want to Read"),
        keeper=first_with("Completed"),
    )


@app.route("/library")
def library():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    genre = request.args.get("genre", "")
    mood = request.args.get("mood", "")

    results = books
    if q:
        results = [b for b in results if q.lower() in b["title"].lower() or q.lower() in b["author"].lower()]
    if status:
        results = [b for b in results if b["status"] == status]
    if genre:
        results = [b for b in results if b["genre"] == genre]
    if mood:
        results = [b for b in results if b["mood"] == mood]

    return render_template(
        "library.html",
        books=results,
        q=q, status=status, genre=genre,
        active_mood=next((m for m in MOODS if m["key"] == mood), None),
        statuses=STATUSES,
        genres=sorted({b["genre"] for b in books}),
        added=request.args.get("added", ""),
    )


@app.route("/add", methods=["GET", "POST"])
def add_book():
    form = {"title": "", "author": "", "genre": GENRES[0], "status": "Want to Read",
            "total_pages": "", "pages_read": "", "isbn": ""}
    errors = {}

    if request.method == "POST":
        form = {key: request.form.get(key, "").strip() for key in form}

        if not form["title"]:
            errors["title"] = "Please tell us the title."
        if not form["author"]:
            errors["author"] = "Please add the author."
        if form["genre"] not in GENRES:
            errors["genre"] = "Choose a genre from the list."
        if form["status"] not in STATUSES:
            errors["status"] = "Choose a reading status."

        form["isbn"] = "".join(ch for ch in form["isbn"] if ch.isdigit() or ch in "xX")
        if form["isbn"] and len(form["isbn"]) not in (10, 13):
            errors["isbn"] = "An ISBN has 10 or 13 characters, or leave it empty."

        total = read = 0
        try:
            total = int(form["total_pages"])
            if total < 1:
                raise ValueError
        except ValueError:
            errors["total_pages"] = "Enter the total pages (1 or more)."

        try:
            read = int(form["pages_read"] or 0)
            if read < 0:
                raise ValueError
            if "total_pages" not in errors and read > total:
                errors["pages_read"] = "Pages read cannot be more than the total pages."
        except ValueError:
            errors["pages_read"] = "Enter a whole number, or leave it empty."

        if not errors:
            make_book(form["title"], form["author"], form["genre"], form["status"], total, read, form["isbn"])
            journal.insert(0, {
                "date": date.today().strftime("%d %b %Y"),
                "title": "New on the shelf",
                "note": f"Added {form['title']} by {form['author']} to the collection.",
            })
            return redirect(url_for("library", added=form["title"]))

    return render_template("add_book.html", form=form, errors=errors,
                           genres=GENRES, statuses=STATUSES)


@app.route("/journal")
def journal_page():
    return render_template("journal.html", entries=journal)


@app.route("/goals", methods=["GET", "POST"])
def goals():
    error = ""
    if request.method == "POST":
        try:
            new_goal = int(request.form.get("goal", ""))
            if not 1 <= new_goal <= 365:
                raise ValueError
            goal_settings["yearly"] = new_goal
            return redirect(url_for("goals", saved=1))
        except ValueError:
            error = "Please enter a whole number between 1 and 365."

    stats = get_stats()
    goal = goal_settings["yearly"]
    done = stats["completed"]
    genre_counts = {}
    for b in books:
        genre_counts[b["genre"]] = genre_counts.get(b["genre"], 0) + 1
    top = max(genre_counts.values()) if genre_counts else 1
    by_genre = [{"name": g, "count": c, "pct": int(c / top * 100)}
                for g, c in sorted(genre_counts.items(), key=lambda x: -x[1])]
    return render_template(
        "goals.html",
        stats=stats,
        goal=goal,
        done=done,
        remaining=max(goal - done, 0),
        percent=min(int(done / goal * 100), 100),
        current=[b for b in books if b["status"] == "Reading"],
        finished=[b for b in books if b["status"] == "Completed"],
        by_genre=by_genre,
        saved=request.args.get("saved", ""),
        error=error,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
