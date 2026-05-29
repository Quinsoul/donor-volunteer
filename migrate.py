import json, boto3, uuid
from datetime import datetime

# Connect to DynamoDB targeting the active Tokyo region
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
donors_table = dynamodb.Table('cloudnine-crm-donor')

# Open your local database source
with open('db.json', 'r') as f:
    database = json.load(f)

# Loop through records and assign fields matching your cloud schema
for donor in database.get('donors', {}).values():
    
    # 1. Set the primary partition key matching your exact schema layout: donor-id
    donor['donor-id'] = donor.get('id', str(uuid.uuid4()))
    
    # Remove any old conflicting underscore key references if they exist
    if 'donor_id' in donor:
        del donor['donor_id']
    if 'id' in donor:
        del donor['id']
    
    # 2. Combine tracking names for your frontend layout display integration
    if 'name' not in donor:
        donor['name'] = f"{donor.get('first_name', '')} {donor.get('last_name', '')}".strip()
        
    # 3. Apply timestamp tracking metadata
    if 'created_at' not in donor:
        donor['created_at'] = datetime.utcnow().isoformat() + "Z"
        
    # Push clean dictionary item directly into your AWS table instance
    donors_table.put_item(Item=donor)
    print(f"Migrated: {donor['name']}")

print('Migration complete!')
