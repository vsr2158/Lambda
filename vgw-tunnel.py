import json
import boto3
import datetime
import sys

ec2 = boto3.client('ec2')
cw = boto3.client('cloudwatch')
version = '0.2.0'


def return_value(dict, key):
    for d in dict:
        if d['Key'] == key:
            return d['Value']
        else:
            return "unknown"


def put_cloudwatch_metric(metric_name, value, vgw, cgw):
    cw.put_metric_data(
        Namespace='VPNStatus',
        MetricData=[{
            'MetricName': metric_name,
            'Value': value,
            'Unit': 'Count',
            'Dimensions': [
                {
                    'Name': 'VGW',
                    'Value': vgw
                },
                {
                    'Name': 'CGW',
                    'Value': cgw
                }
            ]
        }]
    )


def lambda_handler(event, context):
    num_connections = 0
    tunnels = ec2.describe_vpn_connections()['VpnConnections']
    for tunnel in tunnels:


if tunnel['State'] == 'available':
    num_connections += 1
    active_tunnels = 0
    if tunnel['VgwTelemetry'][0]['Status'] == 'UP':
        active_tunnels += 1
    if tunnel['VgwTelemetry'][1]['Status'] == 'UP':
        active_tunnels += 1

    put_cloudwatch_metric(
        tunnel['VpnConnectionId'] + '-' + return_value(tunnel['Tags'], 'Name'),
        active_tunnels,
        tunnel['VpnGatewayId'],
        tunnel['CustomerGatewayId'])
print
tunnel['VpnConnectionId']
print(return_value(tunnel['Tags'], 'Name'))
print
"  " + tunnel['State']
print
"    " + tunnel['VgwTelemetry'][0]['Status']
print
"    " + tunnel['VgwTelemetry'][1]['Status']
print
"