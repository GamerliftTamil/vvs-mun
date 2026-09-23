import os
import json
import secrets
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

import gspread
from google.oauth2.service_account import Credentials


app = Flask(__name__)
CORS(app)

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS")

if not SPREADSHEET_ID:
    raise RuntimeError("SPREADSHEET_ID environment variable is missing")

if not GOOGLE_CREDENTIALS:
    raise RuntimeError("GOOGLE_CREDENTIALS environment variable is missing")


# ---------------------------------------------------------
# GOOGLE SHEETS
# ---------------------------------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

try:
    credentials_info = json.loads(GOOGLE_CREDENTIALS)

    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=SCOPES
    )

except Exception as e:
    raise RuntimeError(
        f"Google credentials could not be loaded: {e}"
    )


try:
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    worksheet = spreadsheet.sheet1

except Exception as e:
    raise RuntimeError(
        f"Could not connect to Google Sheets: {e}"
    )


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/payment", methods=["GET"])
def payment():
    registration_id = request.args.get("id", "").strip()

    if not registration_id:
        return render_template(
            "payment.html",
            registration_id="Not available"
        )

    return render_template(
        "payment.html",
        registration_id=registration_id
    )


@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "service": "VVS-MUN Registration",
        "status": "online",
        "google_sheets": "connected"
    })


# ---------------------------------------------------------
# REGISTRATION ID
# ---------------------------------------------------------

def generate_registration_id():

    random_part = secrets.token_hex(3).upper()

    return f"VVS26-{random_part}"


# ---------------------------------------------------------
# REGISTRATION
# ---------------------------------------------------------

@app.route("/register", methods=["POST"])
def register():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No registration data received."
            }), 400


        # -------------------------------------------------
        # GET FORM DATA
        # -------------------------------------------------

        name = str(
            data.get("name", "")
        ).strip()

        classsec = str(
            data.get("classsec", "")
        ).strip()

        email = str(
            data.get("email", "")
        ).strip()

        phone = str(
            data.get("phone", "")
        ).strip()

        parent_name = str(
            data.get("parentName", "")
        ).strip()

        parent_phone = str(
            data.get("parentPhone", "")
        ).strip()

        committee = str(
            data.get("committee", "")
        ).strip()

        country = str(
            data.get("country", "")
        ).strip()

        participated = str(
            data.get("participated", "")
        ).strip()

        mun_count = str(
            data.get("munCount", "")
        ).strip()

        awards = str(
            data.get("awards", "")
        ).strip()

        previous_awards = str(
            data.get("previousAwards", "")
        ).strip()

        why_participate = str(
            data.get("whyParticipate", "")
        ).strip()

        strengths = str(
            data.get("strengths", "")
        ).strip()


        # -------------------------------------------------
        # REQUIRED FIELD VALIDATION
        # -------------------------------------------------

        required_fields = {
            "Name": name,
            "Class & Section": classsec,
            "Email": email,
            "Phone": phone,
            "Parent/Guardian Name": parent_name,
            "Parent/Guardian Phone": parent_phone,
            "Committee": committee,
            "Participated Before": participated,
            "MUN Experience": mun_count,
            "Awards Before": awards,
            "Why Participate": why_participate,
            "Strengths": strengths
        }

        for field, value in required_fields.items():

            if not value:

                return jsonify({
                    "success": False,
                    "message": f"{field} is required."
                }), 400


        # -------------------------------------------------
        # EMAIL CHECK
        # -------------------------------------------------

        if "@" not in email or "." not in email:

            return jsonify({
                "success": False,
                "message": "Please enter a valid email address."
            }), 400


        # -------------------------------------------------
        # WHY PARTICIPATE LENGTH
        # -------------------------------------------------

        if len(why_participate) > 600:

            return jsonify({
                "success": False,
                "message": "Why Participate must be 600 characters or less."
            }), 400


        # -------------------------------------------------
        # GENERATE REGISTRATION DETAILS
        # -------------------------------------------------

        timestamp = datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).strftime(
            "%d/%m/%Y %I:%M:%S %p"
        )

        registration_id = generate_registration_id()


        # -------------------------------------------------
        # PAYMENT
        # -------------------------------------------------

        amount_paid = ""

        payment_status = "PENDING"


        # -------------------------------------------------
        # GOOGLE SHEETS ROW
        #
        # A = Timestamp
        # B = Registration ID
        # C = Name
        # D = Class & Section
        # E = Email
        # F = Phone
        # G = Parent/Guardian Name
        # H = Parent/Guardian Phone
        # I = Committee
        # J = Country Representing
        # K = Participated Before
        # L = MUN Experience
        # M = Awards Before
        # N = Previous Awards
        # O = Why Participate
        # P = Strengths
        # Q = Amount Paid
        # R = Payment Status
        # -------------------------------------------------

        row = [

            timestamp,
            registration_id,
            name,
            classsec,
            email,
            phone,
            parent_name,
            parent_phone,
            committee,
            country,
            participated,
            mun_count,
            awards,
            previous_awards,
            why_participate,
            strengths,
            amount_paid,
            payment_status

        ]


        worksheet.append_row(
            row,
            value_input_option="USER_ENTERED"
        )


        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "message": "Registration successfully recorded.",

            "registration_id": registration_id,

            "payment_url": f"/payment?id={registration_id}"

        }), 200


    except Exception as e:

        print(
            "REGISTRATION ERROR:",
            str(e)
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to save registration. Please try again."

        }), 500


# ---------------------------------------------------------
# LOCAL DEVELOPMENT
# ---------------------------------------------------------

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )