import sys
import botocore
import boto3
import datetime as datetime
# Get list of regions
ec2_client = boto3.client("ec2")

regions = [region['RegionName']
           for region in ec2_client.describe_regions()['Regions']]

print ("######### List of all regions to be iterated #########")
print(regions)
for region in regions:
    cloudwatch = boto3.resource('cloudwatch', region)
    metric = cloudwatch.Metric('AWS/EC2', 'CPUUtilization')
    print(f'######### Going to check {region} #########')
    ec2 = boto3.resource('ec2', region_name=region)
    test_instance_ids = []
    other_instance_ids = []
    all_instance_ids = []
    # Get list of Ec2 instances
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name',
                  'Values': ['running']}])
    print(type(instances))
    current_utc_time = datetime.datetime.utcnow()
    past_utc_time = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    print (past_utc_time)
    print (current_utc_time)
    for instance in instances:
        print (instance.id)
        metric_response = metric.get_statistics(
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance.id
                },
            ],
            StartTime= past_utc_time,
            EndTime= current_utc_time,
            Period=3600,
            Statistics=[
                'Average',
            ]
        )
        print (metric_response)
        all_instance_ids.append(instance.id)
        other_instance_ids = set(all_instance_ids) - (set(test_instance_ids))
    print('ALL INSTANCES', all_instance_ids)


