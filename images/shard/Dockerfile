FROM mariadb:10.3

COPY ./configuration-entrypoint.sh /configuration-entrypoint.sh

ENTRYPOINT ["/configuration-entrypoint.sh"]

# Seems that I need to limit what I'm replicating as otherwise I
# get conflicts.
CMD ["mysqld", "--replicate-do-db=test"]

