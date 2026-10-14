"""
Vocabulary server with full CRUD for the Flutter app.

Install:   pip install flask flask-cors   (flask-cors is optional, for Flutter web)
Run:       python server_crud.py          (listens on http://0.0.0.0:8000)

Routes
  GET    /health          quick check
  GET    /words           {"words": [...]}
  GET    /words/<id>      one word
  POST   /words           create  -> 201 {"id": ..., "word": {...}}
  PUT    /words/<id>      update  -> 200 {"word": {...}}
  DELETE /words/<id>      delete  -> 200 {"deleted": id}
  GET    /metrics         request counters (simple monitoring)

Data is stored in words.json next to this file. If your existing server.py
already serves /words, copy the POST / PUT / DELETE routes into it instead.
"""
import json
import os
import threading
import time

from flask import Flask, jsonify, request
try:
    from flask_cors import CORS  # only needed for Flutter web
except ImportError:  # mobile apps do not need CORS
    CORS = None

app = Flask(__name__)
if CORS:
    CORS(app)

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocab_250.json")
lock = threading.Lock()
counters = {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "errors": 0}
started = time.time()


def load_words():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("words", []) if isinstance(data, dict) else data


def save_words(words):
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"words": words}, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)


def next_id(words):
    ids = [w.get("id") for w in words if isinstance(w.get("id"), int)]
    return (max(ids) + 1) if ids else 1


def find(words, wid):
    for i, w in enumerate(words):
        if str(w.get("id")) == str(wid):
            return i
    return -1


def clean(body):
    word = str(body.get("word", "")).strip()
    definition = str(body.get("definition", "")).strip()
    meaning = str(body.get("meaning", "")).strip()
    if not word or not (definition or meaning):
        return None, "word and (definition or meaning) are required"
    out = dict(body)
    out["word"] = word
    out["letter"] = (str(body.get("letter", "")).strip() or word[0]).upper()
    syn = body.get("synonyms", [])
    out["synonyms"] = [str(s).strip() for s in syn if str(s).strip()] if isinstance(syn, list) else []
    return out, None


@app.get("/health")
def health():
    return jsonify({"status": "ok", "uptime_s": int(time.time() - started)})


@app.get("/metrics")
def metrics():
    return jsonify({**counters, "words": len(load_words())})


@app.get("/words")
def list_words():
    counters["GET"] += 1
    return jsonify({"words": load_words()})


@app.get("/words/<wid>")
def get_word(wid):
    counters["GET"] += 1
    words = load_words()
    i = find(words, wid)
    if i < 0:
        counters["errors"] += 1
        return jsonify({"error": "not found"}), 404
    return jsonify({"word": words[i]})


@app.post("/words")
def create_word():
    counters["POST"] += 1
    body, err = clean(request.get_json(silent=True) or {})
    if err:
        counters["errors"] += 1
        return jsonify({"error": err}), 400
    with lock:
        words = load_words()
        if any(w.get("word", "").lower() == body["word"].lower() for w in words):
            counters["errors"] += 1
            return jsonify({"error": "word already exists"}), 409
        body["id"] = next_id(words)
        words.append(body)
        save_words(words)
    return jsonify({"id": body["id"], "word": body}), 201


@app.put("/words/<wid>")
def update_word(wid):
    counters["PUT"] += 1
    body, err = clean(request.get_json(silent=True) or {})
    if err:
        counters["errors"] += 1
        return jsonify({"error": err}), 400
    with lock:
        words = load_words()
        i = find(words, wid)
        if i < 0:
            counters["errors"] += 1
            return jsonify({"error": "not found"}), 404
        body["id"] = words[i].get("id")
        words[i] = {**words[i], **body}
        save_words(words)
    return jsonify({"word": words[i]})


@app.delete("/words/<wid>")
def delete_word(wid):
    counters["DELETE"] += 1
    with lock:
        words = load_words()
        i = find(words, wid)
        if i < 0:
            counters["errors"] += 1
            return jsonify({"error": "not found"}), 404
        gone = words.pop(i)
        save_words(words)
    return jsonify({"deleted": gone.get("id")})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)