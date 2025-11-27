from flask import Flask, request, jsonify
import sqlite3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
TMDB_KEY = os.getenv("TMDB_KEY", "YOUR_TMDB_KEY_HERE")
DB_PATH = os.getenv("DB_PATH", "movies.db")
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def tmdb_get(path, params=None):
    if params is None:
        params = {}
    params["api_key"] = TMDB_KEY
    url = f"https://api.themoviedb.org/3{path}"
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


@app.route("/user/preferences", methods=["POST"])
def save_preferences():
    data = request.get_json(force=True)
    if not data or "user_id" not in data or "favorite_genres" not in data:
        return jsonify({"error": "invalid payload"}), 400

    user_id = int(data["user_id"])
    genres = data.get("favorite_genres", [])
    watched = data.get("watched", [])

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    cur.execute(
        "INSERT OR REPLACE INTO preferences (user_id, genres) VALUES (?, ?)",
        (user_id, ",".join(genres)),
    )

    # optional: store watched as ratings with NULL rating
    for m in watched:
        try:
            cur.execute(
                "INSERT OR IGNORE INTO ratings (user_id, movie_id, rating) VALUES (?, ?, NULL)",
                (user_id, int(m)),
            )
        except Exception:
            pass

    conn.commit()
    conn.close()
    return jsonify({"status": "saved"})


@app.route("/movies/rate", methods=["POST"])
def rate_movie():
    data = request.get_json(force=True)
    if not data or "user_id" not in data or "movie_id" not in data or "rating" not in data:
        return jsonify({"error": "invalid payload"}), 400

    user_id = int(data["user_id"])
    movie_id = int(data["movie_id"])
    rating = int(data["rating"])

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ratings (user_id, movie_id, rating) VALUES (?, ?, ?)",
        (user_id, movie_id, rating),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "rating saved"})


@app.route("/movies/recommend", methods=["GET"])
def recommend():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    user_id = int(user_id)

    conn = get_db()
    cur = conn.cursor()

    pref_row = cur.execute("SELECT genres FROM preferences WHERE user_id=?", (user_id,)).fetchone()
    if not pref_row:
        return jsonify({"error": "preferences not found for user"}), 404

    genres = [g.strip() for g in pref_row["genres"].split(",") if g.strip()]

    watched_rows = cur.execute("SELECT movie_id FROM ratings WHERE user_id=?", (user_id,)).fetchall()
    watched = {r[0] for r in watched_rows}

    recommendations = []
    seen_ids = set()

    # get TMDB mapping of genre name -> id
    try:
        tmdb_genres = tmdb_get("/genre/movie/list").get("genres", [])
    except Exception:
        tmdb_genres = []

    name_to_id = {g["name"].lower(): g["id"] for g in tmdb_genres}

    for genre in genres:
        genre_lower = genre.lower()
        if genre_lower in name_to_id:
            gid = name_to_id[genre_lower]
            try:
                data = tmdb_get("/discover/movie", params={"with_genres": gid, "sort_by": "popularity.desc"})
                results = data.get("results", [])
            except Exception:
                results = []
        else:
            # fallback: search by text
            try:
                data = tmdb_get("/search/movie", params={"query": genre})
                results = data.get("results", [])
            except Exception:
                results = []

        for m in results:
            mid = m.get("id")
            if not mid or mid in watched or mid in seen_ids:
                continue
            seen_ids.add(mid)

            # compute a simple score: vote_average (0-10) weighted + popularity
            vote = m.get("vote_average") or 0
            pop = m.get("popularity") or 0
            score = round(vote * 1.5 + pop / 100.0, 3)

            recommendations.append(
                {
                    "id": mid,
                    "title": m.get("title"),
                    "overview": m.get("overview"),
                    "poster": (TMDB_IMG_BASE + m["poster_path"]) if m.get("poster_path") else None,
                    "vote_average": vote,
                    "popularity": pop,
                    "score": score,
                    "genre_ids": m.get("genre_ids", []),
                }
            )

    # sort by score desc then popularity
    recommendations.sort(key=lambda x: (x["score"], x["popularity"]), reverse=True)

    conn.close()
    return jsonify({"recommendations": recommendations[:10]})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
