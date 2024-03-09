import os
import smart_exceptions as se

se.install(lang="russian")

#3 / 0
#print({}["asdf"])

def factorial(n):
    return n*factorial(n-1)

print(factorial(100))
