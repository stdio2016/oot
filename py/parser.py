import sys
import pprint

def removeTrailingNewline(line):
    if line[-1] == '\n':
        line = line[:-1]
    return line

def unescapeRule(line):
    i = 0
    parts = []
    part = ""
    f1 = line.find("{{::=}}")
    f2 = line.find("::=")
    while True:
        if f1 == -1 and f2 == -1:
            part += line[i:]
            parts.append(part)
            break
        elif f1 == -1 or (f2 != -1 and f2 < f1):
            # ::= fisrt
            part = part + line[i:f2]
            parts.append(part)
            i = f2 + 3
            part = ""
            f2 = line.find("::=", i)
        else:
            # {{::=}} first
            part += line[i:f1] + "::="
            i = f1 + 7
            if f2 < i:
                f2 = line.find("::=", i)
            f1 = line.find("{{::=}}", i)
    return parts

def parseFile(filename):
    f = open(filename)
    line = f.readline()
    mainClass = {"name": "", "rules": [], "base": []}
    currentClass = mainClass
    classes = {"": mainClass}
    canListSuperclasses = False
    beginning = True
    lineno = 1
    for nextLine in f:
        # remove trailing newline
        line = removeTrailingNewline(line)

        # empty line
        if line == "":
            pass
        # {} comment
        elif line.startswith("{}"):
            pass
        else:
            parts = unescapeRule(line)
            if len(parts) > 2:
                pos = len(parts[0])+3+len(parts[1])+1
                raise SyntaxError("multiple ::=", (filename, lineno, pos, line))

            # lhs ::= rhs
            elif len(parts) == 2:
                currentClass["rules"].append(parts)
                canListSuperclasses = False
                beginning = False
            # { comment
            elif line.startswith('{'):
                pass
            # end of class
            elif line == "}":
                if currentClass is mainClass:
                    raise SyntaxError("unexpected end of class", (filename, lineno, 1, line))
                currentClass = mainClass
                canListSuperclasses = False
                beginning = False
            # import
            elif line.startswith("import "):
                if not beginning:
                    raise SyntaxError("import statement must be at the start of a program",
                        (filename, lineno, 1, line))
                name = parts[0][7:]
                if name.startswith('std'):
                    # TODO import standard library
                    pass
                else:
                    # TODO don't load the same file twice
                    parseFile(name + '.oot')
            # class
            else:
                name = parts[0]
                if name.isdigit():
                    raise SyntaxError("class name must not consist solely of digits",
                        (filename, lineno, 1, line))
                if currentClass is mainClass:
                    if name in classes:
                        raise SyntaxError("class %s is redefined" % name,
                            (filename, lineno, 1, line))
                    currentClass = {"name": name, "rules": [], "base": []}
                    classes[name] = currentClass
                elif canListSuperclasses:
                    currentClass["base"].append(name)
                else:
                    raise SyntaxError("name of the superclasses must be immediately after the class name",
                        (filename, lineno, 1, line))
                canListSuperclasses = True
                beginning = False
        line = nextLine
        lineno += 1
    f.close()
    line = removeTrailingNewline(line)
    initStr = unescapeRule(line)
    if len(initStr) > 1:
        raise SyntaxError("initial string cannot be a rule",
            (filename, lineno, len(initStr[0])+1, line))
    return (classes, initStr[0])

def main():
    if len(sys.argv) < 2:
        print ("usage: python oot.py <oot file>")
        sys.exit()
    inName = sys.argv[1]
    pp = pprint.PrettyPrinter(depth=6)
    classes = parseFile(inName)
    pp.pprint(classes)

main()
