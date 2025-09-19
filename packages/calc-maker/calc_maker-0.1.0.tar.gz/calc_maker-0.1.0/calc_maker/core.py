def make_calculator(filename="calculator.py"):
    code = """a,b=map(float,input("Enter 2 numbers: ").split())
op=input("Enter + - * /: ")
print(a+b if op=="+" else a-b if op=="-" else a*b if op=="*" else a/b)"""
    with open(filename, "w") as f:
        f.write(code)
    print(f"{filename} created successfully!")
