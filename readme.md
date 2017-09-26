## Introduction
Just some musings on replication/sharding.

## Databases
- commondb -> user data and other parts which need to be joined on
accross shards. Replicated over to the shards.
- shard1db -> shard based on a certain location range.
- shard2db -> shard based on a certain location range.

## API Requirements
Unfortunately I think this idea would require the api to always have the
unique identifier of the location to access resources under it. Either that or
we'd have to make an extra network call which might not be optimal.

## Setting up the replicas
Unfortunately, I think the only way to get the replicas started is with an
initial backup of the 

```bash
docker-compose up
# Create the slave user...
docker-compose exec common mysql -proot -e " grant replication slave on *.* to 'root'@'%' identified by 'root';"
docker-compose exec shard1 mysql -proot
```

And now from the shard sql client:
```sql
change master to master_host='common', master_user='root', master_password='root';
start slave;
quit;
```

The data will now start to sync from the master to the slave. You will need to
do the same for the `shard2`.

### Testing the replicas

Log back into the `common` server:
```bash
docker-compose exec common mysql -proot test
```

Then create some shared data:
```sql
create table user(email varchar(250) primary key, password text);
insert into user values('foo@bar.com', 'very secure');
-- observe the output
explain select * from user where email = 'foo@bar.com';
quit;
```

Log into the shard:
```bash
docker-compose exec shard1 mysql -proot test
```

Then select from the table:
```sql
-- will be using indexes afaik
explain select * from user where email = 'foo@bar.com';

select * from user;
```

We can also crate our own tables in the replicated database. These tables will
not be pushed to the master, however:

```sql
-- lets suppose our app is a gmail clone
create table email(
	user_email varchar(250) not null,
	subject text,
	body text,
	foreign key (user_email) references user(email)
);
insert into email values('foo@bar.com', 'subject', 'body');
-- observe how the constraint is respected
insert into email values('boo@bar.com', 'subject', 'body');
```

## Shards
TODO
