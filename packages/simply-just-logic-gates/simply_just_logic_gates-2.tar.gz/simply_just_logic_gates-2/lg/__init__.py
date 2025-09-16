#  ___                   ___           
# | __|_ _ _ _ ___ _ _  |   \ _____ __ 
# | _|| '_| '_/ _ \ '_| | |) / -_) V / 
# |___|_| |_| \___/_|   |___/\___|\_/  
#                                      

# Functions =+--

def credits():
    """
    Shows credits for simply-just-logic-gates.
    """

    print("# simply just logic gates credits")
    print("|")
    print("| author: Error Dev")
    print("|")
    print("> all code and comments in this module/package are created by the author, Error Dev")

def author():
    """
    Lists the author and his contact information.
    """

    print("# contact information")
    print("| name: Error Dev")
    print("> discord: @error_dev")
    print("> email: 3rr0r.d3v@gmail.com")

def gates():
    """
    Lists all the logic gates avaliable.
    """

    print("# logic gates list")
    print("| lg.and_g() # \"g\" represents \"gate\". Cannot redefine 'and'.")
    print("|")
    print("| lg.or_g()  # \"g\" represents \"gate\". Cannot redefine 'or'.")
    print("|")
    print("| lg.not_g()  # \"g\" represents \"gate\". Cannot redefine 'not'.")
    print("|")
    print("| lg.nand()")
    print("|")
    print("| lg.nor()")
    print("|")
    print("| lg.xor()")
    print("| lg.eor()")
    print("| (eor is the same as xor)")

def and_g(x, y):
    if x and y:
        return True
    else:
        return False

def or_g(x, y):
    if x or y:
        return True
    else:
        return False

def not_g(x):
    return not x

def nand(x, y):
    if x and y:
        return not True
    else:
        return not False

def nor(x, y):
    if x or y:
        return not True
    else:
        return not False

def xor(x, y):
    if x and y:
        return False
    elif not x and not y:
        return False
    else:
        return True
def eor(x, y):
    if x and y:
        return False
    elif not x and not y:
        return False
    else:
        return True

#  ___                   ___           
# | __|_ _ _ _ ___ _ _  |   \ _____ __ 
# | _|| '_| '_/ _ \ '_| | |) / -_) V / 
# |___|_| |_| \___/_|   |___/\___|\_/  
#                                      