import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
donors_table = dynamodb.Table('cloudnine-crm-donor')
volunteers_table = dynamodb.Table('cloudnine-crm-volunteer')


# ─────────────────────────────────────────
# DONOR FUNCTIONS
# ─────────────────────────────────────────

def create_donor(data):
    item = {
        'donor_id': str(uuid.uuid4()),
        'first_name': data.get('first_name', ''), 
	'last_name': data.get('last_name', ''),
        'email': data['email'],
        'phone': data.get('phone', ''),
        'total_donated': data.get('total_donated', 0),
        'status': data.get('status', 'active'),
        'created_at': datetime.utcnow().isoformat()
    }
    donors_table.put_item(Item=item)
    return item


def get_all_donors():
    response = donors_table.scan()
    return response.get('Items', [])


def get_donor(donor_id):
    response = donors_table.get_item(Key={'donor-id': donor_id})
    return response.get('Item')


def update_donor(donor_id, data):
    donors_table.update_item(
        Key={'donor-id': donor_id},
        UpdateExpression='SET #n = :n, email = :e, phone = :p, status = :s',
        ExpressionAttributeNames={'#n': 'name'},  # 'name' is a reserved word in DynamoDB
        ExpressionAttributeValues={
            ':n': data['name'],
            ':e': data['email'],
            ':p': data.get('phone', ''),
            ':s': data.get('status', 'active')
        }
    )


def delete_donor(donor_id):
    donors_table.delete_item(Key={'donor-id': donor_id})


# ─────────────────────────────────────────
# VOLUNTEER FUNCTIONS
# ─────────────────────────────────────────

def create_volunteer(data):
    item = {
        'volunteer_id': str(uuid.uuid4()),
        'first_name': data.get('first_name', ''),
	'last_name': data.get('last_name', ''),
        'email': data['email'],
        'phone': data.get('phone', ''),
        'skills': data.get('skills', []),
        'availability': data.get('availability', ''),
        'hours_logged': data.get('hours_logged', 0),
        'status': data.get('status', 'active'),
        'created_at': datetime.utcnow().isoformat()
    }
    volunteers_table.put_item(Item=item)
    return item


def get_all_volunteers():
    response = volunteers_table.scan()
    return response.get('Items', [])


def get_volunteer(volunteer_id):
    response = volunteers_table.get_item(Key={'volunteer-id': volunteer_id})
    return response.get('Item')


def update_volunteer(volunteer_id, data):
    volunteers_table.update_item(
        Key={'volunteer-id': volunteer_id},
        UpdateExpression='SET #n = :n, email = :e, phone = :p, availability = :a, status = :s',
        ExpressionAttributeNames={'#n': 'name'},
        ExpressionAttributeValues={
            ':n': data['name'],
            ':e': data['email'],
            ':p': data.get('phone', ''),
            ':a': data.get('availability', ''),
            ':s': data.get('status', 'active')
        }
    )


def delete_volunteer(volunteer_id):
    volunteers_table.delete_item(Key={'volunteer-id': volunteer_id})

# ── DONATION FUNCTIONS ──
donations_table = dynamodb.Table('cloudnine-crm-donation')

def create_donation_record(data):
    item = {
        'donation_id': str(uuid.uuid4()),
        'donor_id': data['donor_id'],
        'amount': str(data['amount']),
        'campaign': data.get('campaign', 'General'),
        'payment_method': data.get('payment_method', ''),
        'notes': data.get('notes', ''),
        'date': data.get('date', datetime.utcnow().isoformat()),
        'created_at': datetime.utcnow().isoformat()
    }
    donations_table.put_item(Item=item)
    return item

def get_all_donations():
    response = donations_table.scan()
    return response.get('Items', [])

def delete_donation(donation_id):
    donations_table.delete_item(Key={'donation_id': donation_id})

# ── DONATION FUNCTIONS ──
donations_table = dynamodb.Table('cloudnine-crm-donation')

def create_donation_record(data):
    item = {
        'donation_id': str(uuid.uuid4()),
        'donor_id': data['donor_id'],
        'amount': str(data['amount']),
        'campaign': data.get('campaign', 'General'),
        'payment_method': data.get('payment_method', ''),
        'notes': data.get('notes', ''),
        'date': data.get('date', datetime.utcnow().isoformat()),
        'created_at': datetime.utcnow().isoformat()
    }
    donations_table.put_item(Item=item)
    return item

def get_all_donations():
    response = donations_table.scan()
    return response.get('Items', [])

def delete_donation(donation_id):
    donations_table.delete_item(Key={'donation_id': donation_id})
