# src/minha_calculadora/cli.py
import argparse
from .core import add, sub, mul, div

def main():
    p = argparse.ArgumentParser(prog="minha-calculadora")
    p.add_argument("a", type=float)
    p.add_argument("b", type=float)
    p.add_argument("-o", "--op", choices=["add","sub","mul","div"], default="add")
    args = p.parse_args()
    ops = {"add": add, "sub": sub, "mul": mul, "div": div}
    try:
        print(ops[args.op](args.a, args.b))
    except Exception as e:
        print("Erro:", e)
        raise SystemExit(1)
