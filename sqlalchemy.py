
# Demo of sqlalchemy's sharding using the orm.
# ref: http://docs.sqlalchemy.org/en/latest/_modules/examples/sharding/attribute_shard.html

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.horizontal_shard import ShardedSession

common = create_engine('mysql+pymysql://root:root@localhost:3306/test')
shard1 = create_engine('mysql+pymysql://root:root@localhost:3307/test')
shard2 = create_engine('mysql+pymysql://root:root@localhost:3308/test')

create_session = sessionmaker(class_=ShardedSession)

create_session.configure(shards={
    'shard1': shard1,
    'shard2': shard2,
    'common': common
})

# TODO: how can I use declarative?
