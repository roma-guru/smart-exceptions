import smart_exceptions as se

se.init(lang="russian")
se.install_handler()

# 3 / 0
# print({}["asdf"])


def factorial(n):
    return n * factorial(n - 1)


print(factorial(100))
