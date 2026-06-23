from werkzeug.utils import secure_filename
import os


from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)

app.secret_key = "freefire2026"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tournament.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    team_name = db.Column(db.String(100), nullable=False)

    kills = db.Column(db.Integer, default=0)

    points = db.Column(db.Integer, default=0)

    round_name = db.Column(
        db.String(50),
        default="Round 1"
    )

    team_image = db.Column(db.String(255))


with app.app_context():
    db.create_all()


@app.route("/")
def leaderboard():

    teams = Team.query.order_by(
        Team.points.desc(),
        Team.kills.desc()
    ).all()

    for team in teams:
        print(
            "TEAM =", team.team_name,
            "KILLS =", team.kills,
            "POINTS =", team.points
        )

    return render_template(
        "leaderboard.html",
        teams=teams
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["admin"] = True
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


@app.route("/dashboard")
def dashboard():

    if not session.get("admin"):
        return redirect("/login")

    total_teams = Team.query.count()

    total_kills = db.session.query(
        func.sum(Team.kills)
    ).scalar() or 0

    total_points = db.session.query(
        func.sum(Team.points)
    ).scalar() or 0

    return render_template(
        "dashboard.html",
        total_teams=total_teams,
        total_kills=total_kills,
        total_points=total_points
    )


@app.route("/add", methods=["GET", "POST"])
def add_team():

    if request.method == "POST":

        filename = ""

        image = request.files.get("team_image")

        if image and image.filename != "":

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        team = Team(
    team_name=request.form["team_name"],
    kills=int(request.form["kills"]),
    points=int(request.form["points"]),
    round_name=request.form["round_name"],
    team_image=filename
)

        db.session.add(team)
        db.session.commit()

        return redirect("/")

    return render_template("add_team.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_team(id):

    team = Team.query.get_or_404(id)

    if request.method == "POST":

        team.team_name = request.form["team_name"]
        team.kills = int(request.form["kills"])
        team.points = int(request.form["points"])

        image = request.files.get("team_image")

        if image and image.filename != "":

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

            team.team_image = filename

        db.session.commit()

        return redirect("/")

    return render_template(
        "edit_team.html",
        team=team
    )


@app.route("/delete/<int:id>")
def delete_team(id):

    team = Team.query.get_or_404(id)

    db.session.delete(team)
    db.session.commit()

    return redirect("/")


@app.route("/reset")
def reset():

    Team.query.delete()
    db.session.commit()

    return redirect("/")

print("BASE_DIR =", BASE_DIR)
print("UPLOAD_FOLDER =", UPLOAD_FOLDER)

if __name__ == "__main__":

    app.run(debug=True)