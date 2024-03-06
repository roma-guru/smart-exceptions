import os
import smart_exceptions as se

se.install()

#3 / 0
#print({}["asdf"])

def factorial(n):
    return n*factorial(n-1)

print(factorial(100))
