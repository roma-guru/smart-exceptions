import os
import smart_exceptions as se

se.install(lang="russian", proxy="http://35.185.196.38:3128")

#3 / 0
#print({}["asdf"])

def factorial(n):
    return n*factorial(n-1)

print(factorial(100))
