import os

from toll_booth.obj.graph.trident import TridentDriver

os.environ['GRAPH_DB_ENDPOINT'] = 'leech-cluster.cluster-cnd32dx4xing.us-east-1.neptune.amazonaws.com'
os.environ['GRAPH_DB_READER_ENDPOINT'] = 'leech-cluster.cluster-ro-cnd32dx4xing.us-east-1.neptune.amazonaws.com'

trident_driver = TridentDriver()
results = trident_driver.execute('g.V().limit(1)', read_only=True)
print(results)
