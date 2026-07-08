from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from models import db, Expense
from datetime import datetime, timedelta
from sqlalchemy import func

app = Flask(__name__)

# ==================================
# Configuration
# ==================================
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Required for flash messages
app.secret_key = "expense_tracker_secret_key"

db.init_app(app)

with app.app_context():
    db.create_all()


# ==================================
# Home Page
# ==================================
@app.route("/", methods=["GET", "POST"])
def home():

    # --------------------------
    # Add Expense
    # --------------------------
    if request.method == "POST":

        product = request.form.get("product_name", "").strip()
        category = request.form.get("category", "").strip()
        amount = request.form.get("amount", "").strip()
        notes = request.form.get("notes", "").strip()

        # Validation
        if not product or not category or not amount:
            flash("Please fill in all required fields.", "warning")
            return redirect(url_for("home"))

        try:
            amount = float(amount)

            if amount <= 0:
                flash("Amount must be greater than zero.", "warning")
                return redirect(url_for("home"))

            expense = Expense(
                product_name=product,
                category=category,
                amount=amount,
                notes=notes,
            )

            db.session.add(expense)
            db.session.commit()

            flash("Expense added successfully.", "success")

        except ValueError:
            flash("Please enter a valid amount.", "danger")

        except Exception:
            db.session.rollback()
            flash("Something went wrong while saving the expense.", "danger")

        return redirect(url_for("home"))

    # --------------------------
    # Fetch Expenses
    # --------------------------
    try:
        expenses = Expense.query.order_by(
            Expense.created_at.desc()
        ).all()

    except Exception:
        expenses = []
        flash("Unable to load expenses.", "danger")

    return render_template(
        "index.html",
        expenses=expenses,
    )


# ==================================
# Delete Single Expense
# ==================================
@app.route("/delete/<int:id>")
def delete_expense(id):

    try:
        expense = Expense.query.get(id)

        if expense is None:
            flash("Expense not found.", "warning")
            return redirect(url_for("home"))

        db.session.delete(expense)
        db.session.commit()

        flash("Expense deleted successfully.", "success")

    except Exception:
        db.session.rollback()
        flash("Unable to delete expense.", "danger")

    return redirect(url_for("home"))


# ==================================
# Delete All Expenses
# ==================================
@app.route("/delete_all")
def delete_all():

    try:
        total = Expense.query.count()

        if total == 0:
            flash("No expenses available to delete.", "info")
            return redirect(url_for("home"))

        Expense.query.delete()
        db.session.commit()

        flash("All expenses have been deleted successfully.", "success")

    except Exception:
        db.session.rollback()
        flash("Failed to delete expenses.", "danger")

    return redirect(url_for("home"))


# ==================================
# Weekly Report
# ==================================
@app.route("/weekly")
def weekly_report():

    try:

        today = datetime.today()

        start_of_week = today - timedelta(days=today.weekday())

        weekly_data = (
            db.session.query(
                func.date(Expense.created_at),
                func.sum(Expense.amount)
            )
            .filter(Expense.created_at >= start_of_week)
            .group_by(func.date(Expense.created_at))
            .order_by(func.date(Expense.created_at))
            .all()
        )

        weekly_total = (
            sum(float(total) for _, total in weekly_data)
            if weekly_data
            else 0
        )

        if not weekly_data:
            flash("No expense data available for this week.", "info")

        return render_template(
            "weekly.html",
            weekly_data=weekly_data,
            weekly_total=weekly_total
        )

    except Exception as e:

        db.session.rollback()

        flash("Unable to generate weekly report.", "danger")

        print(e)

        return render_template(
            "weekly.html",
            weekly_data=[],
            weekly_total=0
        )

# ==================================
# Run Application
# ==================================
if __name__ == "__main__":
    app.run(debug=True)