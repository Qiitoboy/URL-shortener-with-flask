import random
import string
from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shortened_urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ShortenedURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_code = db.Column(db.String(6), unique=True, nullable=False)
    long_url = db.Column(db.String(200), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    visits = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"ShortenedURL('{self.short_code}', '{self.long_url}')"

# Create database tables within application context
with app.app_context():
    db.create_all()

def generate_short_url(length=6):
    chars = string.ascii_letters + string.digits
    short_url = "".join(random.choice(chars) for _ in range(length))
    return short_url

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        long_url = request.form['long_url']
        short_url = generate_short_url()
        
        new_url = ShortenedURL(short_code=short_url, long_url=long_url)
        db.session.add(new_url)
        db.session.commit()
        
        return f"Shortened URL: {request.url_root}{short_url}"
    return render_template("index.html")

@app.route("/<short_url>")
def redirect_url(short_url):
    url_entry = ShortenedURL.query.filter_by(short_code=short_url).first()
    if url_entry:
        url_entry.visits += 1
        db.session.commit()
        return redirect(url_entry.long_url)
    else:
        return "URL not found", 404

if __name__ == "__main__":
    app.run(debug=True)
