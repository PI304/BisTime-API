#!/bin/bash
cd /home/ubuntu
if [ -d "BisTime-API" ] ; then
  rm -rf BisTime-API
fi
mkdir BisTime-API
