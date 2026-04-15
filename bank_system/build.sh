#!/bin/bash
echo "Compiling SQLite and C++ Backend..."

# Compile sqlite3 into an object file (fast if not changed)
if [ ! -f sqlite3.o ]; then
  gcc -c sqlite3.c -o sqlite3.o -fPIC -Wall -O2
fi

# Compile backend as a shared library
g++ -fPIC -shared bank_backend.cpp sqlite3.o -o libbank.so -O2 -Wall

echo "Done! Produced libbank.so"
