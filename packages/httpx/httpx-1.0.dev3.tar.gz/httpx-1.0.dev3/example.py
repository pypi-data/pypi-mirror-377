import os
import tokenize

def count_sloc(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith(".py"):
                with open(os.path.join(root, f), "rb") as fh:
                    for tok_type, _, _, _, _ in tokenize.tokenize(fh.readline):
                        # Tokenize gives you structured info:
                        # NAME, OP, STRING, COMMENT, NL, NEWLINE, etc.
                        if tok_type == tokenize.NEWLINE:
                            total += 1
    return total

print(count_sloc("src/httpx"))
print(count_sloc("src/ahttpx"))
print(count_sloc("../httpx/httpx"), 'httpx')
print(count_sloc("../httpcore/httpcore"), 'httpcore')
print(count_sloc("../h11/h11"), 'h11')
print(count_sloc("../anyio/src"), 'anyio')
print(count_sloc("../requests/src"), 'requests')
print(count_sloc("../urllib3/src"), 'urllib3')
print(count_sloc("../flask/src"), 'flask')
