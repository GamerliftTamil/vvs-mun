import os
import json
import secrets
from datetime import datetime

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

import gspread
from google.oauth2.service_account import Credentials


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

CORS(app)


# ============================================================
# GOOGLE SHEETS CONFIGURATION
# ============================================================

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS")


if not SPREADSHEET_ID:
    raise RuntimeError(
        "SPREADSHEET_ID environment variable is missing"
    )

if not GOOGLE_CREDENTIALS:
    raise RuntimeError(
        "GOOGLE_CREDENTIALS environment variable is missing"
    )


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


# ============================================================
# GOOGLE AUTHENTICATION
# ============================================================

try:

    credentials_info = json.loads(
        GOOGLE_CREDENTIALS
    )

    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=SCOPES
    )

except Exception as e:

    raise RuntimeError(
        f"Google credentials could not be loaded: {e}"
    )


# ============================================================
# GOOGLE SHEETS CONNECTION
# ============================================================

try:

    client = gspread.authorize(
        credentials
    )

    spreadsheet = client.open_by_key(
        SPREADSHEET_ID
    )

    worksheet = spreadsheet.sheet1

except Exception as e:

    raise RuntimeError(
        f"Could not connect to Google Sheets: {e}"
    )


# ============================================================
# WEBSITE
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return render_template(
        "index.html"
    )


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
# GENERATE REGISTRATION ID
# ============================================================

def generate_registration_id():

    random_part = secrets.token_hex(3).upper()

    return f"VVS26-{random_part}"


# ============================================================
# REGISTER DELEGATE
# ============================================================

@app.route("/register", methods=["POST"])
def register():

    try:

        # ----------------------------------------------------
        # RECEIVE JSON DATA
        # ----------------------------------------------------

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "message":
                    "No registration data received."

            }), 400


        # ----------------------------------------------------
        # GET ALL FORM FIELDS
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # VALIDATE REQUIRED FIELDS
        # ----------------------------------------------------

        if not name:

            return jsonify({

                "success": False,

                "message":
                    "Full name is required."

            }), 400


        if not classsec:

            return jsonify({

                "success": False,

                "message":
                    "Class and section are required."

            }), 400


        if not email:

            return jsonify({

                "success": False,

                "message":
                    "Email address is required."

            }), 400


        if not phone:

            return jsonify({

                "success": False,

                "message":
                    "Contact number is required."

            }), 400


        if not parent_name:

            return jsonify({

                "success": False,

                "message":
                    "Parent/Guardian name is required."

            }), 400


        if not parent_phone:

            return jsonify({

                "success": False,

                "message":
                    "Parent/Guardian contact is required."

            }), 400


        if not committee:

            return jsonify({

                "success": False,

                "message":
                    "Committee preference is required."

            }), 400


        if not participated:

            return jsonify({

                "success": False,

                "message":
                    "Please select whether you have participated before."

            }), 400


        if not mun_count:

            return jsonify({

                "success": False,

                "message":
                    "Please select the number of MUNs attended."

            }), 400


        if not awards:

            return jsonify({

                "success": False,

                "message":
                    "Please select whether you have won an MUN award."

            }), 400


        if not why_participate:

            return jsonify({

                "success": False,

                "message":
                    "Please explain why you want to participate."

            }), 400


        if not strengths:

            return jsonify({

                "success": False,

                "message":
                    "Please select at least one strength."

            }), 400


        # ----------------------------------------------------
        # BASIC EMAIL VALIDATION
        # ----------------------------------------------------

        if "@" not in email or "." not in email:

            return jsonify({

                "success": False,

                "message":
                    "Please enter a valid email address."

            }), 400


        # ----------------------------------------------------
        # TIMESTAMP
        # ----------------------------------------------------

        timestamp = datetime.now().strftime(
            "%d/%m/%Y %I:%M:%S %p"
        )


        # ----------------------------------------------------
        # REGISTRATION ID
        # ----------------------------------------------------

        registration_id = generate_registration_id()


        # ----------------------------------------------------
        # PAYMENT
        # ----------------------------------------------------
        #
        # Payment has intentionally been left out.
        #
        # Column C will contain:
        #
        # NOT REQUIRED
        #
        # No Razorpay information is collected.
        #
        # ----------------------------------------------------

        payment_status = "NOT REQUIRED"


        # ----------------------------------------------------
        # BUILD A-Q ROW
        # ----------------------------------------------------
        #
        # A  Timestamp
        # B  Registration ID
        # C  Payment Status
        # D  Name
        # E  Class & Section
        # F  Email
        # G  Phone
        # H  Parent/Guardian Name
        # I  Parent/Guardian Phone
        # J  Committee
        # K  Country Representing
        # L  Participated Before
        # M  MUN Experience
        # N  Awards Before
        # O  Previous Awards
        # P  Why Participate
        # Q  Strengths
        #
        # ----------------------------------------------------

        row = [

            timestamp,            # A
            registration_id,      # B
            payment_status,       # C
            name,                 # D
            classsec,             # E
            email,                # F
            phone,                # G
            parent_name,          # H
            parent_phone,         # I
            committee,            # J
            country,              # K
            participated,         # L
            mun_count,            # M
            awards,               # N
            previous_awards,      # O
            why_participate,      # P
            strengths             # Q

        ]


        # ----------------------------------------------------
        # SAVE TO GOOGLE SHEETS
        # ----------------------------------------------------

        worksheet.append_row(

            row,

            value_input_option="USER_ENTERED"

        )


        # ----------------------------------------------------
        # SUCCESS RESPONSE
        # ----------------------------------------------------

        return jsonify({

            "success": True,

            "message":
                "Registration successfully recorded.",

            "registration_id":
                registration_id

        }), 200


    # ========================================================
    # ERROR HANDLING
    # ========================================================

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


# ============================================================
# START SERVER
# ============================================================

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
