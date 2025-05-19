import boto3
import json

ses = boto3.client('ses', region_name='ap-southeast-2')

def lambda_handler(event, context):
    email = event['email']
    item_name = event['item_name']

    response = ses.send_email(
        Source='adityajaiswal9820@gmail.com',
        Destination={'ToAddresses': [email]},
        Message={
            'Subject': {'Data': f'Purchase Confirmation: {item_name}'},
            'Body': {
                'Text': {
                    'Data': f"Thank you for purchasing {item_name} during your flight."
                }
            }
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Email sent successfully!')
    }
