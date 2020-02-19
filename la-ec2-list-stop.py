import sys
import botocore
import boto3


def lambda_handler(event, context):
    # Get list of regions
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName']
               for region in ec2_client.describe_regions()['Regions']]
    print(regions)
    regions = ['us-east-1']
    for region in regions:
        ec2 = boto3.resource('ec2', region_name=region)
        print("Region = ", region)
        test_instance_ids = []
        other_instance_ids = []
        all_instance_ids = []
        # Get list of Ec2 instances
        instances = ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name',
                      'Values': ['running']}])
        # print (str(instances))
        for instance in instances:
            # print (instance.id)
            tags = {}
            # print (instance.tags)
            all_instance_ids.append(instance.id)
            if instance.tags is not None:
                for tag in instance.tags:
                    print(tag)
                    if tag['Key'] == 'ENV' and tag["Value"] == 'TEST':
                        print("match env and TEST")
                        test_instance_ids.append(instance.id)
                        print(instance.id)
        other_instance_ids = set(all_instance_ids) - (set(test_instance_ids))
        print('TEST TAG INSTANCES', test_instance_ids)
        print('TEST TAG MISSING INSTANCES', other_instance_ids)
        print('ALL INSTANCES', all_instance_ids)

        for instance in test_instance_ids:
            instance = ec2.Instance(instance)
            instance.stop()
            print('Stopped instance', instance.id)
