
import os
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import (
    Flask,
    request,
    redirect,
    url_for,
    render_template_string,
    flash,
)
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-change-this")

# MongoDB replica set: primary entry point is port 27016.
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://127.0.0.1:27016/"
    "?replicaSet=libraryRS&retryWrites=true&w=majority"
)

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
)

db = client["DistributedLibrary"]

# Branch IDs map to the fragment collections created in Step 3.
FRAGMENTS = {
    "B001": "Books_B001",
    "B002": "Books_B002",
    "B003": "Books_B003",
}


# -------------------- HTML TEMPLATE --------------------

PAGE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Distributed Library Management</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f6fa;
            color: #202b3c;
        }
        header {
            background: #183153;
            color: white;
            padding: 24px;
        }
        header h1 { margin: 0 0 8px; }
        nav { margin-top: 16px; }
        nav a {
            color: white;
            margin-right: 18px;
            text-decoration: none;
        }
        main {
            max-width: 1100px;
            margin: 24px auto;
            padding: 0 16px;
        }
        .card {
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px #0000000c;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
        }
        input, select, button {
            padding: 10px;
            margin: 5px 0;
            max-width: 100%;
            box-sizing: border-box;
        }
        input, select { border: 1px solid #ccd3df; border-radius: 5px; }
        button {
            background: #2457a7;
            color: white;
            border: 0;
            border-radius: 5px;
            cursor: pointer;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            background: white;
        }
        th, td {
            border-bottom: 1px solid #e1e5ec;
            padding: 10px;
            text-align: left;
        }
        th { background: #edf1f7; }
        .table-wrap { overflow-x: auto; }
        .message {
            background: #e4f6e9;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 12px;
        }
        .error { background: #fde8e7; }
        .muted { color: #68758a; }
        .inline { display: inline-block; }
        footer { text-align: center; padding: 24px; color: #68758a; }
    </style>
</head>
<body>
<header>
    <h1>Distributed Library Management System</h1>
    <div>MongoDB Replication · Fragmentation · ACID Transactions</div>
    <nav>
        <a href="{{ url_for('home') }}">Dashboard</a>
        <a href="{{ url_for('books') }}">Books</a>
        <a href="{{ url_for('students') }}">Students</a>
        <a href="{{ url_for('loans') }}">Loans</a>
        <a href="{{ url_for('health') }}">Health Check</a>
    </nav>
</header>

<main>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for category, message in messages %}
        <div class="message {% if category == 'error' %}error{% endif %}">
          {{ message }}
        </div>
      {% endfor %}
    {% endwith %}

    {{ content | safe }}
</main>
<footer>Distributed Library Project · MongoDB port 27016</footer>
</body>
</html>
"""


def page(content, **context):
    body = render_template_string(content, **context)
    return render_template_string(PAGE, content=body)


def require_database():
    client.admin.command("ping")


def combined_books(search=""):
    """Read and combine the three branch-specific book fragments."""
    result = []

    for branch_id, collection_name in FRAGMENTS.items():
        query = {"branch_id": branch_id}

        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"author": {"$regex": search, "$options": "i"}},
                {"book_id": {"$regex": search, "$options": "i"}},
            ]

        for book in db[collection_name].find(query):
            book["fragment"] = collection_name
            result.append(book)

    return result


def utc_now():
    return datetime.now(timezone.utc)


# -------------------- DASHBOARD --------------------

@app.route("/")
def home():
    try:
        require_database()

        book_count = sum(
            db[name].count_documents({})
            for name in FRAGMENTS.values()
        )
        student_count = db.Students.count_documents({})
        active_loans = db.Loans.count_documents({"status": "BORROWED"})
        branch_count = db.Branches.count_documents({})

        content = """
        <div class="grid">
          <div class="card">
            <h3>Books in fragments</h3>
            <h2>{{ book_count }}</h2>
          </div>
          <div class="card">
            <h3>Students</h3>
            <h2>{{ student_count }}</h2>
          </div>
          <div class="card">
            <h3>Active loans</h3>
            <h2>{{ active_loans }}</h2>
          </div>
          <div class="card">
            <h3>Library branches</h3>
            <h2>{{ branch_count }}</h2>
          </div>
        </div>

        <div class="card">
          <h2>Project Features</h2>
          <ul>
            <li>Horizontal fragmentation by library branch</li>
            <li>MongoDB replica-set replication</li>
            <li>ACID-protected book borrowing and returns</li>
            <li>Combined queries across branch fragments</li>
            <li>Student and borrowing management</li>
          </ul>
          <p class="muted">
            Database: DistributedLibrary · Entry point: localhost:27016
          </p>
        </div>
        """

        return page(
            content,
            book_count=book_count,
            student_count=student_count,
            active_loans=active_loans,
            branch_count=branch_count,
        )

    except PyMongoError as error:
        return page(
            "<div class='card'><h2>Database unavailable</h2>"
            "<p>{{ error }}</p></div>",
            error=str(error),
        ), 503


# -------------------- BOOK SEARCH --------------------

@app.route("/books")
def books():
    search = request.args.get("q", "").strip()

    try:
        require_database()
        records = combined_books(search)

        content = """
        <div class="card">
          <h2>Search Books</h2>
          <form method="get">
            <input name="q" value="{{ search }}"
                   placeholder="Search title, author or book ID">
            <button type="submit">Search</button>
            <a href="{{ url_for('books') }}">Clear</a>
          </form>
          <p class="muted">
            Results are combined from Books_B001, Books_B002 and Books_B003.
          </p>
        </div>

        <div class="card table-wrap">
          <h2>Books ({{ records|length }})</h2>
          <table>
            <tr>
              <th>Book ID</th><th>Title</th><th>Author</th>
              <th>Branch</th><th>Available</th><th>Fragment</th>
            </tr>
            {% for b in records %}
            <tr>
              <td>{{ b.book_id }}</td>
              <td>{{ b.title }}</td>
              <td>{{ b.author }}</td>
              <td>{{ b.branch_id }}</td>
              <td>{{ b.available_copies }}</td>
              <td>{{ b.fragment }}</td>
            </tr>
            {% else %}
            <tr><td colspan="6">No matching books found.</td></tr>
            {% endfor %}
          </table>
        </div>

        <div class="card">
          <h3>Borrow a Book</h3>
          <form method="post" action="{{ url_for('borrow') }}">
            <label>Student ID</label><br>
            <input name="student_id" required placeholder="ST001"><br>
            <label>Book ID</label><br>
            <input name="book_id" required placeholder="BK001"><br>
            <button type="submit">Borrow Book</button>
          </form>
        </div>
        """

        return page(content, records=records, search=search)

    except PyMongoError as error:
        return page(
            "<div class='card'><h2>Book search failed</h2>"
            "<p>{{ error }}</p></div>",
            error=str(error),
        ), 503


# -------------------- STUDENTS --------------------

@app.route("/students")
def students():
    try:
        require_database()
        records = list(db.Students.find().sort("student_id", 1))

        content = """
        <div class="card">
          <h2>Register Student</h2>
          <form method="post" action="{{ url_for('add_student') }}">
            <input name="student_id" required placeholder="Student ID">
            <input name="name" required placeholder="Full name">
            <input name="department" required placeholder="Department">
            <input name="email" type="email" required placeholder="Email">
            <button type="submit">Add Student</button>
          </form>
        </div>

        <div class="card table-wrap">
          <h2>Student Records</h2>
          <table>
            <tr>
              <th>Student ID</th><th>Name</th>
              <th>Department</th><th>Email</th>
            </tr>
            {% for s in records %}
            <tr>
              <td>{{ s.student_id }}</td>
              <td>{{ s.name }}</td>
              <td>{{ s.department }}</td>
              <td>{{ s.email }}</td>
            </tr>
            {% else %}
            <tr><td colspan="4">No students found.</td></tr>
            {% endfor %}
          </table>
        </div>
        """
        return page(content, records=records)

    except PyMongoError as error:
        return page(
            "<div class='card'><h2>Student query failed</h2>"
            "<p>{{ error }}</p></div>",
            error=str(error),
        ), 503


@app.route("/students/add", methods=["POST"])
def add_student():
    student_id = request.form.get("student_id", "").strip()
    name = request.form.get("name", "").strip()
    department = request.form.get("department", "").strip()
    email = request.form.get("email", "").strip()

    if not all([student_id, name, department, email]):
        flash("All student fields are required.", "error")
        return redirect(url_for("students"))

    try:
        db.Students.insert_one({
            "student_id": student_id,
            "name": name,
            "department": department,
            "email": email,
            "created_at": utc_now(),
        })
        flash("Student registered successfully.")

    except PyMongoError as error:
        flash(f"Could not register student: {error}", "error")

    return redirect(url_for("students"))


# -------------------- ACID BORROW TRANSACTION --------------------

@app.route("/borrow", methods=["POST"])
def borrow():
    student_id = request.form.get("student_id", "").strip()
    book_id = request.form.get("book_id", "").strip()

    if not student_id or not book_id:
        flash("Student ID and Book ID are required.", "error")
        return redirect(url_for("books"))

    # Find the source record to determine the correct fragment.
    book = db.Books.find_one({"book_id": book_id})
    student = db.Students.find_one({"student_id": student_id})

    if not student:
        flash("Student not found. Register the student first.", "error")
        return redirect(url_for("books"))

    if not book:
        flash("Book not found in the main Books collection.", "error")
        return redirect(url_for("books"))

    branch_id = book.get("branch_id")
    fragment_name = FRAGMENTS.get(branch_id)

    if not fragment_name:
        flash("No fragment is configured for this book's branch.", "error")
        return redirect(url_for("books"))

    loan_id = "LN" + uuid.uuid4().hex[:12].upper()
    transaction_id = "TX" + uuid.uuid4().hex[:12].upper()
    now = utc_now()

    try:
        def transaction_work(session):
            # Atomically decrement the main book record.
            update_main = db.Books.update_one(
                {
                    "book_id": book_id,
                    "available_copies": {"$gt": 0},
                },
                {"$inc": {"available_copies": -1}},
                session=session,
            )

            if update_main.modified_count != 1:
                raise ValueError("No available copies of this book.")

            # Keep the branch fragment's stock count consistent.
            update_fragment = db[fragment_name].update_one(
                {
                    "book_id": book_id,
                    "available_copies": {"$gt": 0},
                },
                {"$inc": {"available_copies": -1}},
                session=session,
            )

            if update_fragment.modified_count != 1:
                raise ValueError(
                    "The branch fragment is missing the book "
                    "or its stock count is inconsistent."
                )

            db.Loans.insert_one(
                {
                    "loan_id": loan_id,
                    "student_id": student_id,
                    "book_id": book_id,
                    "branch_id": branch_id,
                    "status": "BORROWED",
                    "issue_date": now,
                    "return_date": None,
                },
                session=session,
            )

            db.Transactions.insert_one(
                {
                    "transaction_id": transaction_id,
                    "loan_id": loan_id,
                    "operation": "BOOK_BORROW",
                    "status": "COMPLETED",
                    "created_at": now,
                },
                session=session,
            )

        with client.start_session() as session:
            session.with_transaction(transaction_work)

        flash(f"Book borrowed successfully. Loan ID: {loan_id}")

    except ValueError as error:
        flash(str(error), "error")
    except PyMongoError as error:
        flash(f"Borrowing transaction failed: {error}", "error")

    return redirect(url_for("loans"))


# -------------------- LOAN LIST AND RETURN --------------------

@app.route("/loans")
def loans():
    try:
        require_database()

        records = list(
            db.Loans.find().sort("issue_date", -1).limit(200)
        )

        content = """
        <div class="card table-wrap">
          <h2>Loan Records</h2>
          <table>
            <tr>
              <th>Loan ID</th><th>Student</th><th>Book</th>
              <th>Branch</th><th>Status</th><th>Action</th>
            </tr>
            {% for loan in records %}
            <tr>
              <td>{{ loan.loan_id }}</td>
              <td>{{ loan.student_id }}</td>
              <td>{{ loan.book_id }}</td>
              <td>{{ loan.branch_id }}</td>
              <td>{{ loan.status }}</td>
              <td>
                {% if loan.status == 'BORROWED' %}
                <form method="post"
                      action="{{ url_for('return_book', loan_id=loan.loan_id) }}">
                  <button type="submit">Return</button>
                </form>
                {% else %}
                Returned
                {% endif %}
              </td>
            </tr>
            {% else %}
            <tr><td colspan="6">No loan records found.</td></tr>
            {% endfor %}
          </table>
        </div>
        """
        return page(content, records=records)

    except PyMongoError as error:
        return page(
            "<div class='card'><h2>Loan query failed</h2>"
            "<p>{{ error }}</p></div>",
            error=str(error),
        ), 503


@app.route("/return/<loan_id>", methods=["POST"])
def return_book(loan_id):
    loan = db.Loans.find_one({
        "loan_id": loan_id,
        "status": "BORROWED",
    })

    if not loan:
        flash("Active loan not found, or the book was already returned.", "error")
        return redirect(url_for("loans"))

    book_id = loan["book_id"]
    branch_id = loan["branch_id"]
    fragment_name = FRAGMENTS.get(branch_id)

    if not fragment_name:
        flash("No fragment is configured for this loan's branch.", "error")
        return redirect(url_for("loans"))

    transaction_id = "TX" + uuid.uuid4().hex[:12].upper()
    now = utc_now()

    try:
        def transaction_work(session):
            # Only one concurrent return can change this loan.
            loan_update = db.Loans.update_one(
                {
                    "loan_id": loan_id,
                    "status": "BORROWED",
                },
                {
                    "$set": {
                        "status": "RETURNED",
                        "return_date": now,
                    }
                },
                session=session,
            )

            if loan_update.modified_count != 1:
                raise ValueError("This loan has already been returned.")

            # Increase stock in both the main collection and its fragment.
            main_update = db.Books.update_one(
                {"book_id": book_id},
                {"$inc": {"available_copies": 1}},
                session=session,
            )

            fragment_update = db[fragment_name].update_one(
                {"book_id": book_id},
                {"$inc": {"available_copies": 1}},
                session=session,
            )

            if main_update.modified_count != 1 or fragment_update.modified_count != 1:
                raise ValueError("Book record or fragment record is missing.")

            db.Transactions.insert_one(
                {
                    "transaction_id": transaction_id,
                    "loan_id": loan_id,
                    "operation": "BOOK_RETURN",
                    "status": "COMPLETED",
                    "created_at": now,
                },
                session=session,
            )

        with client.start_session() as session:
            session.with_transaction(transaction_work)

        flash("Book returned successfully.")

    except ValueError as error:
        flash(str(error), "error")
    except PyMongoError as error:
        flash(f"Return transaction failed: {error}", "error")

    return redirect(url_for("loans"))


# -------------------- HEALTH CHECK --------------------

@app.route("/health")
def health():
    try:
        client.admin.command("ping")
        hello = client.admin.command("hello")

        return {
            "mongodb": "connected",
            "database": db.name,
            "replica_set": hello.get("setName"),
            "is_primary": hello.get("isWritablePrimary", False),
        }

    except PyMongoError as error:
        return {
            "mongodb": "connection failed",
            "error": str(error),
        }, 503


if __name__ == "__main__":
    app.run(debug=True)
