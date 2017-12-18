// select right db

//db = db.getSiblingDB(dbName)

var indexes = [ 
    { 
        'index': {
            'streams.indexedMeta.key': 1,
            'streams.indexedMeta.val': 1
        },
        'collection': 'lineage',
        'name': 'lineage indexedMeta'
    },
    { 
        'index': {
            'parameters.key': 1,
            'parameters.val': 1
        },
        'collection': 'lineage',
        'name': 'lineage parameters'
    },    
    { 
        'index': {
            'streams.id': 1
        },
        'collection': 'lineage',
        'name': 'lineage streamsId'
    },
    { 
        'index': {
            'derivationId.DerivedFromDatasetID': 1
        },
        'collection': 'lineage',
        'name': 'lineage DerivedFromDatasetID'
    },
    { 
        'index': {
            'runId': 1
        },
        'collection': 'lineage',
        'name': 'lineage runId'
    },
    {
        'index': {
            'streams.format': 1
        },
        'collection': 'lineage',
        'name': 'lineage streams format'
    }
]
print('start indexing')
for (let index of indexes) {
    print('creating index: ', index.name)
    db[index.collection].createIndex(index.index)
}
print('end indexing')

    