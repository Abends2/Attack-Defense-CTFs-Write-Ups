#!/bin/bash
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432;
do
	sleep 1
done
echo "PostgreSQL started"
sleep 1
./app &> /var/log/skychat.txt
