import sys
import botocore
import boto3


def lambda_handler(event, context):
    # Get list of regions
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName']
               for region in ec2_client.describe_regions()['Regions']]
    print(regions)

    for region in regions:
        rds = boto3.client('rds', region_name=region)
        print("Region = ", region)
        test_cluster_arn = []
        test_cluster_id = []
        other_cluster_arn = []
        all_cluster_arn = []
        # Get list of rds clusters
        clusters = rds.describe_db_clusters(
            MaxRecords=100,
            IncludeShared=True | False
        )
        print('####')
        numberofclusters = (len(clusters['DBClusters']))
        i = 0
        ClusterArnList = []
        ClusterIdList = []
        while i < numberofclusters:
            ClusterArnList.append((clusters['DBClusters'][i]['DBClusterArn']))
            i += 1
        print('####')
        for Arn in ClusterArnList:
            print('Getting Tags for :', Arn)
            tags = rds.list_tags_for_resource(
                ResourceName=Arn,
            )
            TagList = (tags['TagList'])
            for Tag in TagList:
                print(Tag)
                if Tag['Key'] == 'ENV' and Tag['Value'] == 'TEST':
                    print("TAG Match Found ENV and TEST")
                    test_cluster_arn.append(Arn)
                    id = Arn.split(':')
                    test_cluster_id.append(id[6])
        print('Final list of DB Clusters Arn to be powered off : ', test_cluster_arn)
        print('Final list of DB Clusters ID to be powered off : ', test_cluster_id)
        # other_instance_ids = list(set(all_instance_ids) - (set(test_instance_ids)))
        # print ('TEST TAG INSTANCES' , test_instance_ids)
        # print ('TEST TAG MISSING INSTANCES' , other_instance_ids)
        # print ('ALL INSTANCES' , all_instance_ids)

        for cluster_id in test_cluster_id:
            try:
                print('+++++++++++++++++++++++++++++++++++++')
                print('Shutting down  :', cluster_id)
                response = rds.stop_db_cluster(
                    DBClusterIdentifier=cluster_id
                )
            except:
                continue
            print(response)
