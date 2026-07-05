from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)
app.json.sort_keys = False

DATA_FILE = 'books.json'

def read_json():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

def write_json(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data,file,indent=4)

def rupiah(price):
    return f"Rp{price:,.0f}".replace(",", ".")

def format_book(data):
    return {
        "id": data["id"],
        "items": [
            {
                "title": item["title"],
                "author": item["author"],
                "price": rupiah(item["price"])
            }
            for item in data["items"]
        ]
    }

def check_items(items):
    if not isinstance(items, list) or len(items) == 0:
        return False, "items harus berupa list dan tidak boleh kosong"
    for item in items:
        if "title" not in item or "author" not in item or "price" not in item:
            return False, "field title, author, price wajib ada"
        if not isinstance(item["price"], (int, float)):
            return False, "price harus angka"
        if item["price"] < 0:
            return False, "price tidak boleh negatif"
    return True, None

@app.route("/")
def home():
    return jsonify({
        "message": "Book API sederhana",
        "routes": [
            "GET /book",
            "GET /book/<id>",
            "POST /book",
            "PUT /book/<id>",
            "DELETE /book/<id>"
        ]
    })


@app.route("/book", methods=["GET"])
def get_books():
    books = read_json()
    result = [format_book(b) for b in books]
    return jsonify({
        "status": "success",
        "total": len(result),
        "data": result
    })

@app.route("/book/<int:id>", methods=["GET"])
def get_book(id):
    books = read_json()
    for b in books:
        if b["id"] == id:
            return jsonify({
                "status": "success",
                "data": format_book(b)
            })
    return jsonify({"status": "error", "message": "data tidak ditemukan"}), 404

@app.route("/book", methods=["POST"])
def add_book():
    books = read_json()
    data = request.get_json()

    if not data:
        return jsonify({"message": "body kosong"}), 400

    if "id" not in data or "items" not in data:
        return jsonify({"message": "id dan items wajib"}), 400

    for b in books:
        if b["id"] == data["id"]:
            return jsonify({"message": "id sudah ada"}), 409

    valid, err = check_items(data["items"])
    if not valid:
        return jsonify({"message": err}), 400

    books.append(data)
    write_json(books)

    return jsonify({
        "status": "success",
        "data": format_book(data)
    }), 201

@app.route("/book/<int:id>", methods=["PUT"])
def update_book(id):
    books = read_json()
    data = request.get_json()

    if not data:
        return jsonify({"message": "body kosong"}), 400

    for b in books:
        if b["id"] == id:
            if "items" in data:
                valid, err = check_items(data["items"])
                if not valid:
                    return jsonify({"message": err}), 400
                b["items"] = data["items"]

            write_json(books)

            return jsonify({
                "status": "success",
                "data": format_book(b)
            })

    return jsonify({"message": "data tidak ditemukan"}), 404

@app.route("/book/<int:id>", methods=["DELETE"])
def delete_book(id):
    books = read_json()

    for i, b in enumerate(books):
        if b["id"] == id:
            deleted = books.pop(i)
            write_json(books)
            return jsonify({
                "status": "success",
                "deleted": format_book(deleted)
            })

    return jsonify({"message": "data tidak ditemukan"}), 404


if __name__ == "__main__":
    app.run(debug=True)
