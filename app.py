import os
import json
from datetime import datetime

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

import gspread
from google.oauth2.service_account import Credentials


app = Flask(__name__)

CORS(app)


# ============================================================
# GOOGLE SHEETS CONFIGURATION
# ============================================================

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS")


if not SPREADSHEET_ID:
    raise RuntimeError("SPREADSHEET_ID environment variable is missing")

if not GOOGLE_CREDENTIALS:
    raise RuntimeError("GOOGLE_CREDENTIALS environment variable is missing")


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


# ============================================================
# GOOGLE AUTHENTICATION
# ============================================================

credentials_info = json.loads(GOOGLE_CREDENTIALS)

credentials = Credentials.from_service_account_info(
    credentials_info,
    scopes=SCOPES
)


# ============================================================
# GOOGLE SHEETS CONNECTION
# ============================================================

client = gspread.authorize(credentials)

spreadsheet = client.open_by_key(SPREADSHEET_ID)

worksheet = spreadsheet.sheet1


# ============================================================
# WEBSITE
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return render_template("index.html")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "service": "VVS-MUN Registration",
        "status": "online",
        "google_sheets": "connected"
    })


# ============================================================
# REGISTER DELEGATE
# ============================================================

@app.route("/register", methods=["POST"])
def register():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No registration data received."
            }), 400


        # ----------------------------------------------------
        # Get submitted fields
        # ----------------------------------------------------

        name = str(
            data.get("name", "")
        ).strip()

        classsec = str(
            data.get("classsec", "")
        ).strip()

        committee = str(
            data.get("committee", "")
        ).strip()

        country = str(
            data.get("country", "")
        ).strip()

        phone = str(
            data.get("phone", "")
        ).strip()


        # ----------------------------------------------------
        # Validate required fields
        # ----------------------------------------------------

        if not name:
            return jsonify({
                "success": False,
                "message": "Full name is required."
            }), 400


        if not classsec:
            return jsonify({
                "success": False,
                "message": "Class and section are required."
            }), 400


        if not committee:
            return jsonify({
                "success": False,
                "message": "Committee is required."
            }), 400


        if not country:
            return jsonify({
                "success": False,
                "message": "Country is required."
            }), 400


        if not phone:
            return jsonify({
                "success": False,
                "message": "Phone number is required."
            }), 400


        # ----------------------------------------------------
        # Timestamp
        # ----------------------------------------------------

        timestamp = datetime.now().strftime(
            "%d/%m/%Y %I:%M:%S %p"
        )


        # ----------------------------------------------------
        # Add registration to Google Sheet
        # ----------------------------------------------------

        worksheet.append_row(
            [
                timestamp,
                name,
                classsec,
                committee,
                country,
                phone
            ],
            value_input_option="USER_ENTERED"
        )


        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        return jsonify({
            "success": True,
            "message": "Registration successfully recorded."
        }), 200


    except Exception as e:

        print(
            "REGISTRATION ERROR:",
            str(e)
        )

        return jsonify({
            "success": False,
            "message": "Unable to save registration."
        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
