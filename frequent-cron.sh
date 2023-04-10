#!/bin/bash

COUNTER=0
while [ $COUNTER -lt $3 ]; do
  $1 &
  sleep $2
  let COUNTER=COUNTER+1
done