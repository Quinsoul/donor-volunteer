from flask import Flask, request, jsonify
import boto3

from db import (
    create_donor, get_all_donors, get_donor, update_donor, delete_donor,
    create_volunteer, get_all_volunteers, get_volunteer, update_volunteer, delete_volunteer, get_all_donations, create_donation_record, delete_donation, get_all_donations, create_donation_record, delete_donation
)

app = Flask(__name__)

s3 = boto3.client('s3', region_name='ap-northeast-1')
BUCKET_NAME = 'cloudnine-bucket1'  # Replace with your actual bucket name


# ─────────────────────────────────────────
# DONOR ROUTES
# ─────────────────────────────────────────

@app.route('/donors', methods=['GET'])
def list_donors():
    return jsonify(get_all_donors()), 200


@app.route('/donors', methods=['POST'])
def add_donor():
    data = request.get_json()
    if not data or not data.get('first_name') or not data.get('email'):
        return jsonify({'error': 'name and email are required'}), 400
    donor = create_donor(data)
    return jsonify(donor), 201


@app.route('/donors/<donor_id>', methods=['GET'])
def get_one_donor(donor_id):
    donor = get_donor(donor_id)
    if not donor:
        return jsonify({'error': 'Donor not found'}), 404
    return jsonify(donor), 200


@app.route('/donors/<donor_id>', methods=['PUT'])
def edit_donor(donor_id):
    donor = get_donor(donor_id)
    if not donor:
        return jsonify({'error': 'Donor not found'}), 404
    data = request.get_json()
    if not data or not data.get('first_name') or not data.get('email'):
        return jsonify({'error': 'name and email are required'}), 400
    update_donor(donor_id, data)
    return jsonify({'message': 'Donor updated successfully'}), 200


@app.route('/donors/<donor_id>', methods=['DELETE'])
def remove_donor(donor_id):
    donor = get_donor(donor_id)
    if not donor:
        return jsonify({'error': 'Donor not found'}), 404
    delete_donor(donor_id)
    return jsonify({'message': 'Donor deleted successfully'}), 200


# ─────────────────────────────────────────
# VOLUNTEER ROUTES
# ─────────────────────────────────────────

@app.route('/volunteers', methods=['GET'])
def list_volunteers():
    return jsonify(get_all_volunteers()), 200


@app.route('/volunteers', methods=['POST'])
def add_volunteer():
    data = request.get_json()
    if not data or not data.get('first_name') or not data.get('email'):
        return jsonify({'error': 'name and email are required'}), 400
    volunteer = create_volunteer(data)
    return jsonify(volunteer), 201


@app.route('/volunteers/<volunteer_id>', methods=['GET'])
def get_one_volunteer(volunteer_id):
    volunteer = get_volunteer(volunteer_id)
    if not volunteer:
        return jsonify({'error': 'Volunteer not found'}), 404
    return jsonify(volunteer), 200


@app.route('/volunteers/<volunteer_id>', methods=['PUT'])
def edit_volunteer(volunteer_id):
    volunteer = get_volunteer(volunteer_id)
    if not volunteer:
        return jsonify({'error': 'Volunteer not found'}), 404
    data = request.get_json()
    if not data or not data.get('first_name') or not data.get('email'):
        return jsonify({'error': 'name and email are required'}), 400
    update_volunteer(volunteer_id, data)
    return jsonify({'message': 'Volunteer updated successfully'}), 200


@app.route('/volunteers/<volunteer_id>', methods=['DELETE'])
def remove_volunteer(volunteer_id):
    volunteer = get_volunteer(volunteer_id)
    if not volunteer:
        return jsonify({'error': 'Volunteer not found'}), 404
    delete_volunteer(volunteer_id)
    return jsonify({'message': 'Volunteer deleted successfully'}), 200


# ─────────────────────────────────────────
# S3 FILE UPLOAD
# ─────────────────────────────────────────

@app.route('/upload-url', methods=['POST'])
def get_upload_url():
    data = request.get_json()
    if not data or not data.get('filename') or not data.get('donor_id'):
        return jsonify({'error': 'filename and donor_id are required'}), 400
    key = f"donors/{data['donor_id']}/{data['filename']}"
    url = s3.generate_presigned_url(
        'put_object',
        Params={'Bucket': BUCKET_NAME, 'Key': key},
        ExpiresIn=300
    )
    return jsonify({'upload_url': url, 'key': key}), 200


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True)

# ── DONATIONS ROUTES ──
@app.route('/donations', methods=['GET'])
def list_donations():
    return jsonify(get_all_donations()), 200

@app.route('/donations', methods=['POST'])
def add_donation():
    data = request.get_json()
    if not data or not data.get('donor_id') or not data.get('amount'):
        return jsonify({'error': 'donor_id and amount are required'}), 400
    donation = create_donation_record(data)
    return jsonify(donation), 201

@app.route('/donations/<donation_id>', methods=['DELETE'])
def remove_donation(donation_id):
    delete_donation(donation_id)
    return jsonify({'message': 'Donation deleted'}), 200

@app.route('/summary', methods=['GET'])
def summary():
    donors = get_all_donors()
    volunteers = get_all_volunteers()
    donations = get_all_donations()
    total = sum(float(d.get('amount', 0)) for d in donations)
    return jsonify({
        'total_donors': len(donors),
        'total_volunteers': len(volunteers),
        'total_donations': len(donations),
        'total_amount_usd': total
    }), 200
