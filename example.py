import smart_exceptions as se

se.init(backend="groq")
se.install_handler(dialog=True)

3 / 0
# print({}["asdf"])


def factorial(n):
    return n * factorial(n - 1)


print(factorial(100))
