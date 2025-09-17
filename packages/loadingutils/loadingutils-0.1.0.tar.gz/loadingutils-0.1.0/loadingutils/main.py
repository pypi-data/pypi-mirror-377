import sys, time

# ANSI color codes
GREEN = "\033[92m"
RESET = "\033[0m"

def spinner(message: str, cycles: int, delay: float):
    spinner = "|/-\\"
    for i in range(cycles):
        sys.stdout.write(f"\r{message} {spinner[i % len(spinner)]}   ")
        sys.stdout.flush()
        time.sleep(delay)
    print()

def dots(message: str, cycles: int, delay: float):
    for i in range(cycles):
        dots = "." * (i % 4)
        sys.stdout.write(f"\r{message}{dots}   ")
        sys.stdout.flush()
        time.sleep(delay)
    print()

def bar(message: str, sign: str, delay: float):
    for i in range(101):
        bar = f"{sign}" * i + " " * (100 - i)
        sys.stdout.write(f"\r{message}: [{GREEN}{bar}{RESET}] {i}%{RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()