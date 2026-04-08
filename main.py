from flask import Flask, request, jsonify
from datetime import datetime
import mysql.connector
import os

app = Flask(__name__)

db_config = {
    "host": os.getenv("MYSQLHOST"),
    "port": int(os.getenv("MYSQLPORT", 3306)),
    "user": os.getenv("MYSQLUSER"),
    "password": os.getenv("MYSQLPASSWORD"),
    "database": os.getenv("MYSQLDATABASE")
}

distance = 0.0
alert = 0

# connexion à la base de donnée
def db_connection():
    return mysql.connector.connect(**db_config)

# creation de notre table
def init_dblog():
    try:
        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_distance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            distance FLOAT NOT NULL,
            alert INT NOT NULL
        )
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("creation reussie de votre table", flush=True)

    except Exception as e:
        print("erreur base donnée", e, flush=True)

init_dblog()

# insertion des données dans la table
def inser_data(timestamp, distance, alert):
    try:
        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO log_distance (timestamp, distance, alert)
            VALUES (%s, %s, %s)
        """, (timestamp, distance, alert))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print("pas de donnée disponible", e, flush=True)

@app.route("/")
def home():
    return "API IS RUNNING"

@app.route("/data")
def data():
    global distance, alert
    try:
        timestamp = datetime.now()
        distance = float(request.args.get("distance", 0))
        alert = int(request.args.get("alert", 0))

        inser_data(timestamp, distance, alert)

        print("données recues", {
            "distance": distance,
            "alert": alert
        }, flush=True)

        return "ok", 200

    except Exception as e:
        print("erreur data", e, flush=True)
        return "erreur data", 500

@app.route("/status")
def status():
    return jsonify({
        "distance": distance,
        "alert": alert
    })

@app.route("/logs")
def logs():
    try:
        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, distance, alert
            FROM log_distance
            ORDER BY timestamp DESC
            LIMIT 100
        """)

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        log = []
        for row in rows:
            log.append({
                "timestamp": str(row[0]),
                "distance": row[1],
                "alert": row[2]
            })

        return jsonify(log)

    except Exception as e:
        print("erreur de logs", e, flush=True)
        return jsonify({"erreur": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
