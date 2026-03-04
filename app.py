from flask import Flask, request, jsonify, render_template
from datetime import datetime
import uuid, json, os

app = Flask(__name__)

# ─────────────────────────────────────────────
# Simple JSON file persistence
# ─────────────────────────────────────────────
DB_FILE = "db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            return data.get("donors", {}), data.get("volunteers", {}), data.get("donations", {})
    return {}, {}, {}

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump({"donors": donors, "volunteers": volunteers, "donations": donations}, f, indent=2)

donors, volunteers, donations = load_db()

def new_id(): return str(uuid.uuid4())
def now():    return datetime.utcnow().isoformat() + "Z"

@app.route("/")
def index():
    return render_template("index.html")

# ── Donors ──
@app.route("/donors", methods=["GET"])
def list_donors():
    return jsonify(list(donors.values())), 200

@app.route("/donors/<donor_id>", methods=["GET"])
def get_donor(donor_id):
    d = donors.get(donor_id)
    return (jsonify(d), 200) if d else (jsonify({"error": "Donor not found"}), 404)

@app.route("/donors", methods=["POST"])
def create_donor():
    data = request.get_json() or {}
    missing = [f for f in ["first_name", "last_name", "email"] if not data.get(f)]
    if missing: return jsonify({"error": f"Missing required fields: {missing}"}), 400
    did = new_id()
    donors[did] = {"id": did, "first_name": data["first_name"], "last_name": data["last_name"],
        "email": data["email"], "phone": data.get("phone",""), "address": data.get("address",""),
        "notes": data.get("notes",""), "created_at": now(), "updated_at": now()}
    save_db()
    return jsonify(donors[did]), 201

@app.route("/donors/<donor_id>", methods=["PUT"])
def update_donor(donor_id):
    d = donors.get(donor_id)
    if not d: return jsonify({"error": "Donor not found"}), 404
    data = request.get_json() or {}
    for f in ["first_name","last_name","email","phone","address","notes"]:
        if f in data: d[f] = data[f]
    d["updated_at"] = now(); save_db()
    return jsonify(d), 200

@app.route("/donors/<donor_id>", methods=["DELETE"])
def delete_donor(donor_id):
    if donor_id not in donors: return jsonify({"error": "Donor not found"}), 404
    del donors[donor_id]; save_db()
    return jsonify({"message": "Donor deleted"}), 200

# ── Volunteers ──
@app.route("/volunteers", methods=["GET"])
def list_volunteers():
    return jsonify(list(volunteers.values())), 200

@app.route("/volunteers/<vid>", methods=["GET"])
def get_volunteer(vid):
    v = volunteers.get(vid)
    return (jsonify(v), 200) if v else (jsonify({"error": "Volunteer not found"}), 404)

@app.route("/volunteers", methods=["POST"])
def create_volunteer():
    data = request.get_json() or {}
    missing = [f for f in ["first_name", "last_name", "email"] if not data.get(f)]
    if missing: return jsonify({"error": f"Missing required fields: {missing}"}), 400
    vid = new_id()
    volunteers[vid] = {"id": vid, "first_name": data["first_name"], "last_name": data["last_name"],
        "email": data["email"], "phone": data.get("phone",""), "skills": data.get("skills",[]),
        "availability": data.get("availability",""), "notes": data.get("notes",""),
        "created_at": now(), "updated_at": now()}
    save_db()
    return jsonify(volunteers[vid]), 201

@app.route("/volunteers/<vid>", methods=["PUT"])
def update_volunteer(vid):
    v = volunteers.get(vid)
    if not v: return jsonify({"error": "Volunteer not found"}), 404
    data = request.get_json() or {}
    for f in ["first_name","last_name","email","phone","skills","availability","notes"]:
        if f in data: v[f] = data[f]
    v["updated_at"] = now(); save_db()
    return jsonify(v), 200

@app.route("/volunteers/<vid>", methods=["DELETE"])
def delete_volunteer(vid):
    if vid not in volunteers: return jsonify({"error": "Volunteer not found"}), 404
    del volunteers[vid]; save_db()
    return jsonify({"message": "Volunteer deleted"}), 200

# ── Donations ──
@app.route("/donations", methods=["GET"])
def list_donations():
    df = request.args.get("donor_id")
    result = list(donations.values())
    if df: result = [d for d in result if d["donor_id"] == df]
    return jsonify(result), 200

@app.route("/donations/<did>", methods=["GET"])
def get_donation(did):
    d = donations.get(did)
    return (jsonify(d), 200) if d else (jsonify({"error": "Donation not found"}), 404)

@app.route("/donations", methods=["POST"])
def create_donation():
    data = request.get_json() or {}
    if not data.get("donor_id") or data.get("amount") is None:
        return jsonify({"error": "donor_id and amount are required"}), 400
    if data["donor_id"] not in donors:
        return jsonify({"error": "Donor not found. Create the donor first."}), 404
    try:
        amount = float(data["amount"]); assert amount > 0
    except:
        return jsonify({"error": "amount must be a positive number"}), 400
    did = new_id()
    donations[did] = {"id": did, "donor_id": data["donor_id"], "amount": amount,
        "campaign": data.get("campaign","General"), "payment_method": data.get("payment_method",""),
        "notes": data.get("notes",""), "date": data.get("date", now()),
        "created_at": now(), "updated_at": now()}
    save_db()
    return jsonify(donations[did]), 201

@app.route("/donations/<did>", methods=["PUT"])
def update_donation(did):
    d = donations.get(did)
    if not d: return jsonify({"error": "Donation not found"}), 404
    data = request.get_json() or {}
    for f in ["campaign","payment_method","notes","date"]:
        if f in data: d[f] = data[f]
    if "amount" in data:
        try: d["amount"] = float(data["amount"])
        except: return jsonify({"error": "amount must be a number"}), 400
    d["updated_at"] = now(); save_db()
    return jsonify(d), 200

@app.route("/donations/<did>", methods=["DELETE"])
def delete_donation(did):
    if did not in donations: return jsonify({"error": "Donation not found"}), 404
    del donations[did]; save_db()
    return jsonify({"message": "Donation deleted"}), 200

# ── Utility ──
@app.route("/summary", methods=["GET"])
def summary():
    total = sum(d["amount"] for d in donations.values())
    return jsonify({"total_donors": len(donors), "total_volunteers": len(volunteers),
        "total_donations": len(donations), "total_amount_usd": round(total, 2)}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
