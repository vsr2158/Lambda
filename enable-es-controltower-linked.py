import boto3
from botocore.exceptions import ClientError


#Case CC email needs to be updated below to ensure customer recieves a copy of the support case via email
case_cc_emails = "distribution-list@company-example.com"

def lambda_handler(event, context):
    """
    Creates a support case requesting to enable Enterprise Support.
    Get the newly created account IF from cloudwatch event/ ControlTower Lifecycle event
    """
    account_id = event.get("detail").get("serviceEventDetails").get("createManagedAccountStatus").get("account").get(
        "accountId")
    support_client = boto3.client('support', region_name='us-east-1')
    print(f' Event passed form CloudWatch Event is : {event}')
    print(f' Extracted Account ID : {account_id}')

    case_subject = f'Enable Enterprise Support on the new account {account_id}'
    case_severity_code = 'low'
    case_category_code = 'other-account-issues'
    case_service_code = 'customer-account'
    accounts = str(account_id)
    case_issue_type = 'customer-service'
    case_communication_body = f'Hi AWS! Please enable Enterprise Support on new account ID {account_id} with the same ' \
                              f'support plan as this payer account. This case was created automatically after the new account was created, responses to this may go unnoticed, please resolve when done.'

    response = support_client.create_case(
        subject=case_subject,
        severityCode=case_severity_code,
        categoryCode=case_category_code,
        serviceCode=case_service_code,
        communicationBody=case_communication_body,
        ccEmailAddresses=[case_cc_emails],
        language='en',
        issueType=case_issue_type
    )
    # Print Case ID to return.
    case_id = response['caseId']
    case = support_client.describe_cases(
        caseIdList=[case_id])
    display_id = case['cases'][0]['displayId']

    print(f'Case {display_id} opened for accounts {accounts}.')