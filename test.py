import os
import smart_exceptions

smart_exceptions.install(os.environ["OPENAI_TOKEN"])

#3 / 0
#print({}["asdf"])

def factorial(n):
    return n*factorial(n-1)

print(factorial(100))
