import boto3


def create_polls_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.client('dynamodb', endpoint_url="http://localhost:8000")


    table_name = 'polls'
    existing_tables = dynamodb.list_tables()['TableNames']

    if table_name not in existing_tables:
        try:
            print("Creating table...")
            table = dynamodb.create_table(
                TableName='polls',
                KeySchema=[
                    {
                        'AttributeName': 'pollTimeStamp',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'question',
                        'KeyType': 'RANGE' # Sort key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'pollTimeStamp',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'question',
                        'AttributeType': 'S'
                    },

                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
            print("Finished creating table...")
            return table
        except Exception as e:
            print("error : " + str(e))
            return {"error" : str(e)}
    # print("error : 'polls' table already exists.")
    return {"error": "'polls' table already exists."}

if __name__ == '__main__':
    polls_table = create_polls_table()
    #print("Table status:", polls_table.table_status)
