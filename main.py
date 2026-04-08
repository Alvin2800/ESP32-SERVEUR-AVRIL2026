from flask import Flask, request, jsonify
from datetime import datetime
import mysql.connector
import os   

app = Flask(__name__)

db_config = {
    "host": os.getenv("MYSQLHOST"),
    "port": os.getenv("MYSQLPORT"),
    "user": os.getenv("MYSQLUSER"),
    "password": os.getenv("MYSQLPASSWORD"),
    "database": os.getenv("MYSQLDATABASE")  # ⚡ corrigé
}

def db_connection():
    return mysql.connector.connect(**db_config)

def init_db():
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS measuring2(
                id INT PRIMARY KEY AUTO_INCREMENT,
                timestamp DATETIME NOT NULL,
                distance FLOAT NOT NULL,
                alert INT NOT NULL
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Table créée avec succès", flush=True)
    except Exception as e:
        print("Erreur base de données:", e, flush=True)

init_db()

def insert_data(timestamp, distance, alert):
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO measuring2 (timestamp, distance, alert) 
            VALUES (%s, %s, %s)
        """, (timestamp, distance, alert))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Erreur insertion:", e, flush=True)

@app.route("/")
def home():
    return "API IS RUNNING"

@app.route("/data")
def data():
    try:
        timestamp = datetime.now()
        distance = float(request.args.get("distance", 0))
        alert = int(request.args.get("alert", 0))
        insert_data(timestamp, distance, alert)
        print("Données reçues:", {"distance": distance, "alert": alert})
        return "ok", 200
    except Exception as e:
        print("Erreur data:", e, flush=True)
        return "erreur data", 500

@app.route("/status")
def status():
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT distance, alert FROM measuring
            ORDER BY timestamp DESC LIMIT 1
        """)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return jsonify({"distance": row[0], "alert": row[1]})
        else:
            return jsonify({"distance": 0, "alert": 0})
    except Exception as e:
        print("Erreur status:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/logs")
def logs():
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, distance, alert 
            FROM measuring 
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
        print("Erreur logs:", e, flush=True)
        return jsonify({"erreur": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
