from flask import Flask
from config import Config
from models import db, User, Palm
import itertools, string

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Seed palms A1..L26 (A-L = 12 letters * 26 = 312 trees)
        letters = list("ABCDEFGHIJKL")
        for letter in letters:
            for i in range(1, 27):
                code = f"{letter}{i}"
                db.session.add(Palm(code=code))
        db.session.commit()
        print("Database initialized and palms seeded.")
