
# Demo of sqlalchemy's sharding using the orm.
# ref: http://docs.sqlalchemy.org/en/latest/_modules/examples/sharding/attribute_shard.html

from uuid import uuid4
from sqlalchemy import create_engine, String, Column, Numeric, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.horizontal_shard import ShardedSession
import smhasher
from faker import Faker

common = create_engine('mysql+pymysql://root:root@localhost:3306/test')
shard1 = create_engine('mysql+pymysql://root:root@localhost:3307/test')
shard2 = create_engine('mysql+pymysql://root:root@localhost:3308/test')

create_session = sessionmaker(class_=ShardedSession)

create_session.configure(shards={
    'shard1': shard1,
    'shard2': shard2,
    'common': common
})

shards = (shard1, shard2)

# TODO: how can I use declarative?

Base = declarative_base()


def create_id():
    return str(uuid4())


class User(Base):
    __tablename__ = 'user'
    id = Column(String(50), primary_key=True, default=create_id)
    email = Column(String(100), nullable=False)
    password = Column(String(50), nullable=False)


class Store(Base):
    __tablename__ = 'store'
    id = Column(String(50), primary_key=True, default=create_id)
    name = Column(String(50), nullable=False)


@event.listens_for(Store, "init")
def init_store(target, args, kwargs):
    if target.id is None:
        target.id = str(uuid4())


class Item(Base):
    __tablename__ = 'item'
    id = Column(String(50), primary_key=True, default=create_id)
    store_id = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    price = Column(Numeric(15, 2), nullable=False)


# Could probably make this more elegant using subclass initializer mixins or
# class decorators...
shard_tables = (Store, Item)
shard_dbs = (shard1, shard2)

User.__table__.drop(common)
User.__table__.create(common)

for table in shard_tables:
    for db in shard_dbs:
        if table.__table__.exists(db):
            table.__table__.drop(db)
        table.__table__.create(db)


# Murmur hash has good distribution which is what we need to assign records
# to each shard as evenly as possible.
def shard_from_id(id):
    index = smhasher.murmur3_x64_64(id) % 2
    shard = 'shard' + str(index + 1)
    return shard


def id_chooser(query, ident):
    print('id_chooser:', query, ident)
    return ['shard1', 'shard2']


def shard_chooser(mapper, instance, clause=None):
    print('shard_chooser', mapper, instance)
    if isinstance(instance, Store):
        return shard_from_id(instance.id)
    elif isinstance(instance, User):
        return 'common'
    else:
        return shard_from_id(instance.store_id)


def query_chooser(query):
    return ['shard1', 'shard2']


create_session.configure(
        shard_chooser=shard_chooser,
        query_chooser=query_chooser,
        id_chooser=id_chooser
)

session = create_session()

fake = Faker()
session.add(Store(name=fake.company()))
session.commit()
session.close()
