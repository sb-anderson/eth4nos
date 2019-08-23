import pymongo

URL = "mongodb://ara.snu.ac.kr:27017"
DB_NAME = "eth-analysis"


# for test
def checkDBExist(dbname):
    dblist = client.list_database_names()
    if dbname in dblist:
        print("The database exists.")


def checkCollectionExist(dbname, collectionName):
    db = client[dbname]
    collist = db.list_collection_names()
    if collectionName in collist:
        print("The collection exists.")


# API
def findMany(collectionName, keys, values):
    client = pymongo.MongoClient(URL)
    db = client[DB_NAME]
    collection = db[collectionName]
    txs = []

    conditions = dict()
    for i, key in enumerate(keys):
        conditions[key] = values[i]

    for x in collection.find(conditions):
        txs.append(x)
    client.close()
    return txs
