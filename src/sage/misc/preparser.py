"""
SAGE pre-parser.

AUTHOR:
    -- William Stein (2006-02-19): fixed bug when loading .py files.
    -- William Stein (2006-03-09): * fixed crash in parsing exponentials
                                   * precision of real literals now determined
                                     by digits of input (like mathematica).
    -- Joe Wetherell (2006-04-14): * added MAGMA-style constructor preparsing.
    -- Bobby Moretti (2007-01-25): * added preliminary function assignment
                                     notation
    -- Robert Bradshaw (2007-09-19): * strip_string_literals, containing_block 
                                       utility functions. Arrr!
                                     * Add [1,2,..,n] notation. 
    -- Robert Bradshaw (2008-01-04): * Implicit multiplication (off by default)
    -- Robert Bradshaw (2008-09-23): * Factor out constants.
    -- Robert Bradshaw (2000-01):    * Simplify preparser by making it modular 
                                       and using regular expressions. Also bug 
                                       fixes, complex numbers, and binary input. 

EXAMPLES:

PREPARSE:
    sage: preparse('2/3')
    'Integer(2)/Integer(3)'
    sage: preparse('2.5')
    "RealNumber('2.5')"
    sage: preparse('2^3')
    'Integer(2)**Integer(3)'
    sage: preparse('a^b')            # exponent
    'a**b'
    sage: preparse('a**b')           
    'a**b'
    sage: preparse('G.0')            # generator
    'G.gen(0)'
    sage: preparse('a = 939393R')    # raw
    'a = 939393'
    sage: implicit_multiplication(True)
    sage: preparse('a b c in L')     # implicit multiplication
    'a*b*c in L'
    sage: preparse('2e3x + 3exp(y)')
    "RealNumber('2e3')*x + Integer(3)*exp(y)"

A string with escaped quotes in it (the point here is that the
preparser doesn't get confused by the internal quotes):
    sage: "\"Yes,\" he said."
    '"Yes," he said.'
    sage: s = "\\"; s
    '\\'


A hex literal:
    sage: preparse('0x2a3')
    'Integer(0x2a3)'
    sage: 0xA
    10

Raw and hex works correctly:
    sage: type(0xa1)
    <type 'sage.rings.integer.Integer'>
    sage: type(0xa1r)
    <type 'int'>
    sage: type(0Xa1R)
    <type 'int'>
    

In SAGE methods can also be called on integer and real literals (note
that in pure Python this would be a syntax error).
    sage: 16.sqrt()
    4
    sage: 87.factor()
    3 * 29
    sage: 15.10.sqrt()
    3.88587184554509
    sage: preparse('87.sqrt()')
    'Integer(87).sqrt()'
    sage: preparse('15.10.sqrt()')
    "RealNumber('15.10').sqrt()"

Note that calling methods on int literals in pure Python is a
syntax error, but SAGE allows this for SAGE integers and reals,
because users frequently request it.

    sage: eval('4.__add__(3)')
    Traceback (most recent call last):
    ...
    SyntaxError: invalid syntax

SYMBOLIC FUNCTIONAL NOTATION:
    sage: a=10; f(theta, beta) = theta + beta; b = x^2 + theta
    sage: f
    (theta, beta) |--> theta + beta
    sage: a
    10
    sage: b
    x^2 + theta
    sage: f(theta,theta)
    2*theta
    
    sage: a = 5; f(x,y) = x*y*sqrt(a)
    sage: f
    (x, y) |--> sqrt(5)*x*y

This involves an =-, but should still be turned into a symbolic expression:
    sage: preparse('a(x) =- 5')
    '__tmp__=var("x"); a = symbolic_expression(- Integer(5)).function(x)'
    sage: f(x)=-x
    sage: f(10)
    -10

This involves -=, which should not be turned into a symbolic
expression (of course a(x) isn't an identifier, so this will never be
valid):
    sage: preparse('a(x) -= 5')
    'a(x) -= Integer(5)'

RAW LITERALS:

Raw literals are not preparsed, which can be useful from an efficiency
point of view.  Just like Python ints are denoted by an L, in SAGE raw
integer and floating literals are followed by an"r" (or "R") for raw,
meaning not preparsed.

We create a raw integer.
    sage: a = 393939r
    sage: a
    393939
    sage: type(a)
    <type 'int'>
    
We create a raw float:    
    sage: z = 1.5949r
    sage: z
    1.5949
    sage: type(z)
    <type 'float'>

You can also use an upper case letter:
    sage: z = 3.1415R
    sage: z
    3.1415000000000002
    sage: type(z)
    <type 'float'>

This next example illustrates how raw literals can be very useful in
certain cases.  We make a list of even integers up to 10000. 
    sage: v = [ 2*i for i in range(10000)]

This talkes a noticeable fraction of a second (e.g., 0.25 seconds).
After preparsing, what Python is really executing is the following:

    sage: preparse('v = [ 2*i for i in range(10000)]')
    'v = [ Integer(2)*i for i in range(Integer(10000))]'

If instead we use a raw 2 we get executation that is ``instant'' (0.00 seconds):
    sage: v = [ 2r * i for i in range(10000r)]

Behind the scenes what happens is the following:
    sage: preparse('v = [ 2r * i for i in range(10000r)]')
    'v = [ 2 * i for i in range(10000)]'

WARNING: The result of the above two expressions is different.  The
first one computes a list of SAGE integers, whereas the second creates
a list of Python integers.  Python integers are typically much more
efficient than SAGE integers when they are very small; large SAGE
integers are much more efficient than Python integers, since they are
implemented using the GMP C library.


    
"""



###########################################################################
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
###########################################################################
import os, re
import pdb

implicit_mul_level = False
numeric_literal_prefix = '_sage_const_'

def implicit_multiplication(level=None):
    """
    Turn implicit multiplication on or off, optionally setting a specific level.
    Returns the current value if no argument is given. 
    
    EXAMPLES: 
      sage: implicit_multiplication(True)
      sage: implicit_multiplication()
      5
      sage: preparse('2x')
      'Integer(2)*x'
      sage: implicit_multiplication(False)
      sage: preparse('2x')
      '2x'
    """
    from sage.plot.plot import EMBEDDED_MODE
    if EMBEDDED_MODE:
        raise NotImplementedError, "Implicit multiplication not implemented for the notebook."
    global implicit_mul_level
    if level is None:
        return implicit_mul_level
    elif level is True:
        implicit_mul_level = 5
    else:
        implicit_mul_level = level

def isalphadigit_(s):
    return s.isalpha() or s.isdigit() or s=="_"

keywords = """
and       del       from      not       while    
as        elif      global    or        with     
assert    else      if        pass      yield    
break     except    import    print              
class     exec      in        raise              
continue  finally   is        return             
def       for       lambda    try
""".split()

in_single_quote = False
in_double_quote = False
in_triple_quote = False

def in_quote():
    return in_single_quote or in_double_quote or in_triple_quote
    

def strip_string_literals(code, state=None):
    r"""
    Returns a string with all literal quotes replaced with 
    labels and a dict of labels for re-subsitution. This makes
    parsing much easier. 
    
    EXAMPLES: 
        sage: from sage.misc.preparser import strip_string_literals
        sage: s, literals, state = strip_string_literals(r'''['a', "b", 'c', "d\""]''')
        sage: s
        '[%(L1)s, %(L2)s, %(L3)s, %(L4)s]'
        sage: literals
        {'L4': '"d\\""', 'L2': '"b"', 'L3': "'c'", 'L1': "'a'"}
        sage: print s % literals
        ['a', "b", 'c', "d\""]
        sage: print strip_string_literals(r'-"\\\""-"\\"-')[0]
        -%(L1)s-%(L2)s-
        
    Triple-quotes are handled as well.
        sage: s, literals, state = strip_string_literals("[a, '''b''', c, '']")
        sage: s
        '[a, %(L1)s, c, %(L2)s]'
        sage: print s % literals
        [a, '''b''', c, '']

    Comments are subsituted too:
        sage: s, literals, state = strip_string_literals("code '#' # ccc 't'"); s
        'code %(L1)s #%(L2)s'
        sage: s % literals
        "code '#' # ccc 't'"
        
    A state is returned so one can break strings across multiple calls to 
    this function:
        sage: s, literals, state = strip_string_literals('s = "some'); s
        's = %(L1)s'
        sage: s, literals, state = strip_string_literals('thing" * 5', state); s
        '%(L1)s * 5'
    """
    new_code = []
    literals = {}
    counter = 0
    start = q = 0
    if state is None:
        in_quote = False
        raw = False
    else:
        in_quote, raw = state
    while True:
        sig_q = code.find("'", q)
        dbl_q = code.find('"', q)
        hash_q = code.find('#', q)
        q = min(sig_q, dbl_q)
        if q == -1: q = max(sig_q, dbl_q)
        if not in_quote and hash_q != -1 and (q == -1 or hash_q < q):
            # it's a comment
            newline = code.find('\n', hash_q)
            if newline == -1: newline = len(code)
            counter += 1
            label = "L%s" % counter
            literals[label] = code[hash_q+1:newline]
            new_code.append(code[start:hash_q].replace('%','%%'))
            new_code.append("#%%(%s)s" % label)
            start = q = newline
        elif q == -1:
            if in_quote:
                counter += 1
                label = "L%s" % counter
                literals[label] = code[start:]
                new_code.append("%%(%s)s" % label)
            else:
                new_code.append(code[start:].replace('%','%%'))
            break
        elif in_quote:
            if not raw and code[q-1] == '\\':
                k = 2
                while code[q-k] == '\\':
                    k += 1
                if k % 2 == 0:
                    q += 1
            if code[q:q+len(in_quote)] == in_quote:
                counter += 1
                label = "L%s" % counter
                literals[label] = code[start:q+len(in_quote)]
                new_code.append("%%(%s)s" % label)
                q += len(in_quote)
                start = q
                in_quote = False
            else:
                q += 1
        else:
            raw = q>0 and code[q-1] in 'rR'
            if len(code) >= q+3 and (code[q+1] == code[q] == code[q+2]):
                in_quote = code[q]*3
            else:
                in_quote = code[q]
            new_code.append(code[start:q].replace('%', '%%'))
            start = q
            q += len(in_quote)
    
    return "".join(new_code), literals, (in_quote, raw)


def containing_block(code, ix, delimiters=['()','[]','{}'], require_delim=True):
    """
    Returns the smallest range (start,end) such that code[start,end] 
    is delimited by balanced parentheses/brackets/braces. 
    
    EXAMPLES: 
        sage: from sage.misc.preparser import containing_block
        sage: s = "factor(next_prime(L[5]+1))"
        sage: s[22]
        '+'
        sage: start, end = containing_block(s, 22); print start, end
        17 25
        sage: s[start:end]
        '(L[5]+1)'
        sage: s[20]
        '5'
        sage: start, end = containing_block(s, 20); s[start:end]
        '[5]'
        sage: start, end = containing_block(s, 20, delimiters=['()']); s[start:end]
        '(L[5]+1)'
        sage: start, end = containing_block(s, 10); s[start:end]
        '(next_prime(L[5]+1))'
    """
    openings = "".join([d[0] for d in delimiters])
    closings = "".join([d[-1] for d in delimiters])
    levels = [0] * len(openings)
    p = 0
    start = ix
    while start >= 0:
        start -= 1
        if start == -1:
            if require_delim:
                raise SyntaxError, "Unbalanced or missing ()'s"
            else:
                break
        if code[start] in openings:
            p = openings.index(code[start])
            levels[p] -= 1
            if levels[p] == -1:
                break
        elif code[start] in closings:
            p = closings.index(code[start])
            levels[p] += 1
    if start == -1:
        return 0, len(code)
    end = ix
    level = 0
    while end < len(code):
        end += 1
        if end == len(code):
            raise SyntaxError, "Unbalanced or missing ()'s"
        if code[end] == openings[p]:
            level += 1
        elif code[end] == closings[p]:
            level -= 1
            if level == -1:
                break
    return start, end+1
    
    
def parse_ellipsis(code, preparse_step=True):
    """
    Preparse [0,2,..,n] notation. 
    
    EXAMPLES: 
        sage: from sage.misc.preparser import parse_ellipsis
        sage: parse_ellipsis("[1,2,..,n]")
        '(ellipsis_range(1,2,Ellipsis,n))'
        sage: parse_ellipsis("for i in (f(x) .. L[10]):")
        'for i in (ellipsis_iter(f(x) ,Ellipsis, L[10])):'
    """
    ix = code.find('..')
    while ix != -1:
        if ix == 0:
            raise SyntaxError, "Cannot start line with ellipsis."
        elif code[ix-1]=='.':
            # '...' be valid Python in index slices
            code = code[:ix-1] + "Ellipsis" + code[ix+2:]
        elif len(code) >= ix+3 and code[ix+2]=='.':
            # '...' be valid Python in index slices
            code = code[:ix] + "Ellipsis" + code[ix+3:]
        else:
            start_list, end_list = containing_block(code, ix, ['()','[]'])
            arguments = code[start_list+1:end_list-1].replace('...', ',Ellipsis,').replace('..', ',Ellipsis,')
            arguments = re.sub(r',\s*,', ',', arguments)
            if preparse_step:
                arguments = arguments.replace(';', ', step=')
            range_or_iter = 'range' if code[start_list]=='[' else 'iter'
            code = "%s(ellipsis_%s(%s))%s" %  (code[:start_list],
                                               range_or_iter,
                                               arguments,
                                               code[end_list:])
        ix = code.find('..')
    return code

def extract_numeric_literals(code):
    """
    To eliminate the re-parsing and creation of numeric literals (e.g. during
    every iteration of a loop) we wish to pull them out and assign them to 
    global variables. 
    
    This function takes a block of code and returns a new block of code
    with literals replaced by variable names, as well as a dictionary of what
    variables need to be created. 
    
    EXAMPLES: 
        sage: from sage.misc.preparser import extract_numeric_literals
        sage: code, nums = extract_numeric_literals("1.2 + 5")
        sage: print code
        _sage_const_1p2  + _sage_const_5 
        sage: print nums
        {'_sage_const_1p2': "RealNumber('1.2')", '_sage_const_5': 'Integer(5)'}
        
        sage: extract_numeric_literals("[1, 1.1, 1e1, -1e-1, 1.]")[0]
        '[_sage_const_1 , _sage_const_1p1 , _sage_const_1e1 , -_sage_const_1en1 , _sage_const_1p ]'
        
        sage: extract_numeric_literals("[1.sqrt(), 1.2.sqrt(), 1r, 1.2r, R.1, R0.1, (1..5)]")[0]
        '[_sage_const_1 .sqrt(), _sage_const_1p2 .sqrt(), 1 , 1.2 , R.1, R0.1, (_sage_const_1 .._sage_const_5 )]'
    """
    return preparse_numeric_literals(code, True)

all_num_regex = None

def preparse_numeric_literals(code, extract=False):
    """
    This preparses numerical literals into their sage counterparts, 
    e.g. Integer, RealNumber, and ComplexNumber. 
    If extract is true, then it will create names for the literals 
    and return a dict of name-construction pairs along with the 
    processed code. 
    
    EXAMPLES: 
        sage: from sage.misc.preparser import preparse_numeric_literals
        sage: preparse_numeric_literals("5")
        'Integer(5)'
        sage: preparse_numeric_literals("5j")
        "ComplexNumber(0, '5')"
        sage: preparse_numeric_literals("5jr")
        '5J'
        sage: preparse_numeric_literals("5l")
        '5l'
        sage: preparse_numeric_literals("5L")
        '5L'
        sage: preparse_numeric_literals("1.5")
        "RealNumber('1.5')"
        sage: preparse_numeric_literals("1.5j")
        "ComplexNumber(0, '1.5')"
        sage: preparse_numeric_literals(".5j")
        "ComplexNumber(0, '.5')"
        sage: preparse_numeric_literals("5e9j")
        "ComplexNumber(0, '5e9')"
        sage: preparse_numeric_literals("5.")
        "RealNumber('5.')"
        sage: preparse_numeric_literals("5.j")
        "ComplexNumber(0, '5.')"
        sage: preparse_numeric_literals("5.foo()")
        'Integer(5).foo()'
        sage: preparse_numeric_literals("5.5.foo()")
        "RealNumber('5.5').foo()"
        sage: preparse_numeric_literals("5.5j.foo()")
        "ComplexNumber(0, '5.5').foo()"
        sage: preparse_numeric_literals("5j.foo()")
        "ComplexNumber(0, '5').foo()"
        sage: preparse_numeric_literals("1.exp()")
        'Integer(1).exp()'
        sage: preparse_numeric_literals("1e+10")
        "RealNumber('1e+10')"
        sage: preparse_numeric_literals("0x0af")
        'Integer(0x0af)'
        sage: preparse_numeric_literals("0x10.sqrt()")
        'Integer(0x10).sqrt()'
        sage: preparse_numeric_literals('0o100')
        "Integer('100', 8)"
        sage: preparse_numeric_literals('0b111001')
        "Integer('111001', 2)"
    """
    literals = {}
    last = 0
    new_code = []

    global all_num_regex
    if all_num_regex is None:
        dec_num = r"\b\d+"
        hex_num = r"\b0x[0-9a-f]+"
        oct_num = r"\b0o[0-7]+"
        bin_num = r"\b0b[01]+"
        # This is slightly annoying as floating point numbers may start 
        # with a decimal point, but if they do the \b will not match. 
        float_num = r"((\b\d+([.]\d*)?)|([.]\d+))(e[-+]?\d+)?"
        all_num = r"((%s)|(%s)|(%s)|(%s)|(%s))(rj|rL|jr|Lr|j|L|r|)\b" % (float_num, dec_num, hex_num, oct_num, bin_num)
        all_num_regex = re.compile(all_num, re.I)
        
    for m in all_num_regex.finditer(code):
        start, end = m.start(), m.end()
        num = m.group(1)
        postfix = m.groups()[-1].upper()
        
        if 'R' in postfix:
            num_name = num_make = num + postfix.replace('R', '')
        elif 'L' in postfix:
            continue
        else:
        
            # The Sage preparser does extra things with numbers, which we need to handle here. 
            if '.' in num:
                if start > 0 and num[0] == '.':
                    if code[start-1] == '.':
                        # handle Ellipsis
                        start += 1
                        num = num[1:]
                    elif re.match(r'[a-zA-Z0-9_\])]', code[start-1]):
                        # handle R.0
                        continue
                elif end < len(code) and num[-1] == '.':
                    if re.match('[a-zA-Z_]', code[end]):
                        # handle 4.sqrt()
                        end -= 1
                        num = num[:-1]
            elif end < len(code) and code[end] == '.' and not postfix and re.match(r'\d+$', num):
                # \b does not match after the . for floating point
                # two dots in a row would be an ellipsis
                if end+1 == len(code) or code[end+1] != '.':
                    end += 1
                    num += '.'
                
            if '.' in num or 'e' in num or 'E' in num or 'J' in postfix:
                num_name = numeric_literal_prefix + num.replace('.', 'p').replace('-', 'n').replace('+', '')
                if 'J' in postfix:
                    num_make = "ComplexNumber(0, '%s')" % num
                    num_name += 'j'
                else:
                    num_make = "RealNumber('%s')" % num
            else:
                num_name = numeric_literal_prefix + num
                if len(num) > 3:
                    # Py3 oct and bin support
                    if num[1] in 'bB':
                        num_make = "Integer('%s', 2)" % num[2:]
                    elif num[1] in 'oO':
                        num_make = "Integer('%s', 8)" % num[2:]
                    else:
                        num_make = "Integer(%s)" % num
                else:
                    num_make = "Integer(%s)" % num
        
            literals[num_name] = num_make
            
        new_code.append(code[last:start])
        if extract:
            new_code.append(num_name+' ')
        else:
            new_code.append(num_make)
        last = end
        
    new_code.append(code[last:])
    code = ''.join(new_code)
    if extract:
        return code, literals
    else:
        return code


def strip_prompts(line):
    r"""Get rid of leading sage: and >>> prompts so that pasting of examples from
    the documentation works.

    sage: from sage.misc.preparser import strip_prompts
    sage: strip_prompts("sage: 2 + 2")
    '2 + 2'
    sage: strip_prompts(">>>   3 + 2")
    '3 + 2'
    sage: strip_prompts("  2 + 4")
    '  2 + 4'
    """
    for prompt in ['sage:', '>>>']:
        if line.startswith(prompt):
            line = line[len(prompt):].lstrip()
            break
    return line


def preparse_calculus(code):
    """
    Support for calculus-like function assignment, the line
    "f(x,y,z) = sin(x^3 - 4*y) + y^x"
    gets turnd into
    '__tmp__=var("x,y,z"); f = symbolic_expression(sin(x**3 - 4*y) + y**x).function(x,y,z)'
   
    AUTHORS:
        -- Bobby Moretti: initial version - 02/2007
        -- William Stein: make variables become defined if they aren't already defined.
        -- Robert Bradshaw: rewrite using regular expressions (01/2009)
        
    EXAMPLES: 
        sage: preparse("f(x) = x^3-x")
        '__tmp__=var("x"); f = symbolic_expression(x**Integer(3)-x).function(x)'
        sage: preparse("f(u,v) = u - v")
        '__tmp__=var("u,v"); f = symbolic_expression(u - v).function(u,v)'
        sage: preparse("f(x) =-5")
        '__tmp__=var("x"); f = symbolic_expression(-Integer(5)).function(x)'
        sage: preparse("f(x) -= 5")
        'f(x) -= Integer(5)'
        sage: preparse("f(x_1, x_2) = x_1^2 - x_2^2")
        '__tmp__=var("x_1,x_2"); f = symbolic_expression(x_1**Integer(2) - x_2**Integer(2)).function(x_1,x_2)'
        
    For simplicity, this function assumes all statements begin and end with a semicolon.
        sage: from sage.misc.preparser import preparse_calculus
        sage: preparse_calculus(";f(t,s)=t^2;")
        ';__tmp__=var("t,s"); f = symbolic_expression(t^2).function(t,s);'
        sage: preparse_calculus(";f( t , s ) = t^2;")
        ';__tmp__=var("t,s"); f = symbolic_expression(t^2).function(t,s);'
    """
    new_code = []
    last_end = 0
    #                                   f         (  vars  )   =      expr
    for m in re.finditer(r";(\s*)([a-zA-Z_]\w*) *\(([^()]+)\) *= *([^;#=][^;#]*)", code):
        ident, func, vars, expr = m.groups()
        vars = ','.join(v.strip() for v in vars.split(','))
        new_code.append(code[last_end:m.start()])
        new_code.append(';%s__tmp__=var("%s"); %s = symbolic_expression(%s).function(%s)' % (ident, vars, func, expr, vars))
        last_end = m.end()

    if last_end == 0:
        return code
    else:
        new_code.append(code[m.end():])
        return ''.join(new_code)


def preparse_generators(code):
    r"""Parse R.<a, b> in line[start_index:].

    Returns preparsed code.

    Support for generator construction syntax:
    "obj.<gen0,gen1,...,genN> = objConstructor(...)"
    is converted into
    "obj = objConstructor(..., names=("gen0", "gen1", ..., "genN")); \
     (gen0, gen1, ..., genN,) = obj.gens()"

    Also, obj.<gen0,gen1,...,genN> = R[interior] is converted into
    "obj = R[interior]; (gen0, gen1, ..., genN,) = obj.gens()"

    LIMITATIONS:
       - The entire constructor *must* be on one line.

    AUTHORS:
        -- 2006-04-14: Joe Wetherell (jlwether@alum.mit.edu)
        -- 2006-04-17: William Stein - improvements to allow multiple statements.
        -- 2006-05-01: William -- fix bug that Joe found
        -- 2006-10-31: William -- fix so obj doesn't have to be mutated
        -- 2009-01-27: Robet Bradshaw -- rewrite using regular expressions

    TESTS:
        sage: from sage.misc.preparser import preparse, preparse_generators

        Vanilla:
        
        sage: preparse("R.<x> = ZZ['x']")
        "R = ZZ['x']; (x,) = R._first_ngens(1)"
        sage: preparse("R.<x,y> = ZZ['x,y']")
        "R = ZZ['x,y']; (x, y,) = R._first_ngens(2)"

        No square brackets:

        sage: preparse("R.<x> = PolynomialRing(ZZ, 'x')")
        "R = PolynomialRing(ZZ, 'x', names=('x',)); (x,) = R._first_ngens(1)"
        sage: preparse("R.<x,y> = PolynomialRing(ZZ, 'x,y')")
        "R = PolynomialRing(ZZ, 'x,y', names=('x', 'y',)); (x, y,) = R._first_ngens(2)"

        Names filled in:

        sage: preparse("R.<x> = ZZ[]")
        "R = ZZ['x']; (x,) = R._first_ngens(1)"
        sage: preparse("R.<x,y> = ZZ[]")
        "R = ZZ['x, y']; (x, y,) = R._first_ngens(2)"

        Names given not the same as generator names:

        sage: preparse("R.<x> = ZZ['y']")
        "R = ZZ['y']; (x,) = R._first_ngens(1)"
        sage: preparse("R.<x,y> = ZZ['u,v']")
        "R = ZZ['u,v']; (x, y,) = R._first_ngens(2)"

        Number fields:

        sage: preparse("K.<a> = QQ[2^(1/3)]")
        'K = QQ[Integer(2)**(Integer(1)/Integer(3))]; (a,) = K._first_ngens(1)'
        sage: preparse("K.<a, b> = QQ[2^(1/3), 2^(1/2)]")
        'K = QQ[Integer(2)**(Integer(1)/Integer(3)), Integer(2)**(Integer(1)/Integer(2))]; (a, b,) = K._first_ngens(2)'

        Just the .<> notation:

        sage: preparse("R.<x> = ZZx")
        'R = ZZx; (x,) = R._first_ngens(1)'
        sage: preparse("R.<x, y> = a+b")
        'R = a+b; (x, y,) = R._first_ngens(2)'
        sage: preparse("A.<x,y,z>=FreeAlgebra(ZZ,3)")
        "A = FreeAlgebra(ZZ,Integer(3), names=('x', 'y', 'z',)); (x, y, z,) = A._first_ngens(3)"

        Ensure we don't eat too much:

        sage: preparse("R.<x, y> = ZZ;2")
        'R = ZZ; (x, y,) = R._first_ngens(2);Integer(2)'
        sage: preparse("R.<x, y> = ZZ['x,y'];2")
        "R = ZZ['x,y']; (x, y,) = R._first_ngens(2);Integer(2)"
        sage: preparse("F.<b>, f, g = S.field_extension()")
        "F, f, g  = S.field_extension(names=('b',)); (b,) = F._first_ngens(1)"
    
    For simplicity, this function assumes all statements begin and end with a semicolon.
        preparse_generators(";  R.<x>=ZZ[];")
    """
    new_code = []
    last_end = 0
    #                                  obj       .< gens >      ,  other   =   constructor
    for m in re.finditer(r";(\s*)([a-zA-Z_]\w*)\.<([^>]+)> *((?:,[\w, ]+)?)= *([^;#]+)", code):
        ident, obj, gens, other_objs, constructor = m.groups()
        gens = [v.strip() for v in gens.split(',')]
        constructor = constructor.rstrip()
        if constructor[-1] == ')':
            opening = constructor.rindex('(')
            # Only use comma if there are already arguments to the constructor
            comma = ', ' if constructor[opening+1:-1].strip() != '' else ''
            names = "('%s',)" % "', '".join(gens)
            constructor = constructor[:-1] + comma + "names=%s)" % names
        elif constructor[-1] == ']':
            # Could be nested. 
            opening = constructor.rindex('[')
            closing = constructor.index(']', opening)
            if constructor[opening+1:closing].strip() == '':
                names = "'" + ', '.join(gens) + "'"
                constructor = constructor[:opening+1] + names + constructor[closing:]
        else:
            pass
        gens_tuple = "(%s,)" % ', '.join(gens)
        new_code.append(code[last_end:m.start()])
        new_code.append(";%s%s%s = %s; %s = %s._first_ngens(%s)" % (ident, obj, other_objs, constructor, gens_tuple, obj, len(gens)))
        last_end = m.end()
        
    if last_end == 0:
        return code
    else:
        new_code.append(code[m.end():])
        return ''.join(new_code)


quote_state = None

def preparse(line, reset=True, do_time=False, ignore_prompts=False, numeric_literals=True):
    r"""
    EXAMPLES:
        sage: preparse("ZZ.<x> = ZZ['x']")
        "ZZ = ZZ['x']; (x,) = ZZ._first_ngens(1)"
        sage: preparse("ZZ.<x> = ZZ['y']")
        "ZZ = ZZ['y']; (x,) = ZZ._first_ngens(1)"
        sage: preparse("ZZ.<x,y> = ZZ[]")
        "ZZ = ZZ['x, y']; (x, y,) = ZZ._first_ngens(2)"
        sage: preparse("ZZ.<x,y> = ZZ['u,v']")
        "ZZ = ZZ['u,v']; (x, y,) = ZZ._first_ngens(2)"
        sage: preparse("ZZ.<x> = QQ[2^(1/3)]")
        'ZZ = QQ[Integer(2)**(Integer(1)/Integer(3))]; (x,) = ZZ._first_ngens(1)'
        sage: QQ[2^(1/3)]
        Number Field in a with defining polynomial x^3 - 2

        sage: preparse("a^b")
        'a**b'
        sage: preparse("a^^b")
        'a^b'
        sage: 8^1
        8
        sage: 8^^1
        9
        sage: 9^^1
        8
        
        sage: preparse("A \ B")
        'A  * BackslashOperator() * B'
        sage: preparse("A^2 \ B + C")
        'A**Integer(2)  * BackslashOperator() * B + C'
        sage: preparse("a \\ b \\") # There is really only one backslash here, it's just being escaped. 
        'a  * BackslashOperator() * b \\'

        sage: preparse("time R.<x> = ZZ[]", do_time=True)
        '__time__=misc.cputime(); __wall__=misc.walltime(); R = ZZ[\'x\']; print "Time: CPU %.2f s, Wall: %.2f s"%(misc.cputime(__time__), misc.walltime(__wall__)); (x,) = R._first_ngens(1)'
    """
    global quote_state
    if reset:
        quote_state = None

    L = line.lstrip()
    if len(L) > 0 and L[0] in ['#', '!']:
        return line

    if L.startswith('...'):
        i = line.find('...')
        return line[:i+3] + preparse(line[i+3:], reset=reset, do_time=do_time, ignore_prompts=ignore_prompts)

    if ignore_prompts:
        # Get rid of leading sage: and >>> so that pasting of examples from
        # the documentation works.
        line = strip_prompts(line)

    # This part handles lines with semi-colons all at once
    # Then can also handle multiple lines more efficiently, but
    # that optimization can be done later. 
    L, literals, quote_state = strip_string_literals(line, quote_state)
    
    # Ellipsis Range
    # [1..n]
    try:
        L = parse_ellipsis(L, preparse_step=False)
    except SyntaxError:
        pass
        
    if implicit_mul_level:
        # Implicit Multiplication
        # 2x -> 2*x
        L = implicit_mul(L, level = implicit_mul_level)
    
    if numeric_literals:
        # Wrapping
        # 1 + 0.5 -> Integer(1) + RealNumber('0.5')
        L = preparse_numeric_literals(L)
    
    # Generators
    # R.0 -> R.gen(0)
    L = re.sub(r'([_a-zA-Z]\w*|[)\]])\.(\d+)', r'\1.gen(\2)', L)

    # Use ^ for exponentiation and ^^ for xor
    # (A side effect is that **** becomes xor as well.)
    L = L.replace('^', '**').replace('****', '^')
    
    # Make it easy to match statement ends
    L = ';%s;' % L.replace('\n', ';\n;')
    
    if do_time:
        # Separate time statement
        L = re.sub(r';(\s*)time +(\w)', r';time;\1\2', L)
    
    # Construction with generators
    # R.<...> = obj()
    # R.<...> = R[]
    L = preparse_generators(L)
    
    # Calculus functions
    # f(x,y) = x^3 - sin(y)
    L = preparse_calculus(L)
    
    # Backslash
    L = re.sub(r'''\\\s*([^\t ;#])''', r' * BackslashOperator() * \1', L)
    
    if do_time:
        # Time keyword
        L = re.sub(r';time;(\s*)(\S[^;]*)', 
                   r';\1__time__=misc.cputime(); __wall__=misc.walltime(); \2; print ' +
                        '"Time: CPU %%.2f s, Wall: %%.2f s"%%(misc.cputime(__time__), misc.walltime(__wall__))',
                   L)
                    
    # Remove extra ;'s
    L = L.replace(';\n;', '\n')[1:-1]

    line = L % literals
        
    return line
    

######################################################
## Apply the preparser to an entire file
######################################################

def preparse_file(contents, attached={}, magic=True,
                  do_time=False, ignore_prompts=False,
                  numeric_literals=True):
    """
    NOTE: Temporarily, if @parallel is in the input, then numeric_literals
    is always set to False. 
    
    TESTS:
        sage: from sage.misc.preparser import preparse_file
        sage: lots_of_numbers = "[%s]" % ", ".join(str(i) for i in range(3000))
        sage: _ = preparse_file(lots_of_numbers)
        sage: preparse_file("type(100r), type(100)")
        '_sage_const_100 = Integer(100)\ntype(100 ), type(_sage_const_100 )'
    """
    if not isinstance(contents, str):
        raise TypeError, "contents must be a string"

    assert isinstance(contents, str)
    # We keep track of which files have been loaded so far
    # in order to avoid a recursive load that would result
    # in creating a massive file and crashing.
    loaded_files = []

    # This is a hack, since when we use @parallel to parallelize code,
    # the numeric literals that are factored out do not get copied
    # to the subprocesses properly.  See trac #4545.
    if '@parallel' in contents:
        numeric_literals = False
    
    if numeric_literals:
        contents, literals, state = strip_string_literals(contents)
        contents, nums = extract_numeric_literals(contents)
        contents = contents % literals
        if nums:
            # Stick the assignments at the top, trying not to shift the lines down. 
            ix = contents.find('\n')
            if ix == -1: ix = len(contents)
            if not re.match(r"^ *(#.*)?$", contents[:ix]):
                contents = "\n"+contents
            assignments = ["%s = %s" % x for x in nums.items()]
            # the preparser recurses on semicolons, so we only attempt to preserve line numbers if there are a few
            if len(assignments) < 500:
                contents = "; ".join(assignments) + contents
            else:
                contents = "\n".join(assignments) + "\n\n" + contents

    F = []
    A = contents.splitlines()
    i = 0
    while i < len(A):
        L = A[i].rstrip()
        if magic and L[:7] == "attach ":
            name = os.path.abspath(_strip_quotes(L[7:]))
            try:
                if not attached.has_key(name):
                    t = os.path.getmtime(name)
                    attached[name] = t
            except IOError, OSError:
                pass
            L = 'load ' + L[7:]

        if magic and L[:5] == "load ":
            try:
                name_load = _strip_quotes(L[5:])
            except:
                name_load = L[5:].strip()
            if name_load in loaded_files:
                i += 1
                continue
            loaded_files.append(name_load)
            if name_load[-3:] == '.py':
                import IPython.ipapi
                # This is a dangerous hack, actually, since it means
                # that if the input file is:
                #     load a.sage
                #     load b.py
                # Then b.py will be loaded while the file is being *parsed*,
                # and *before* a.sage is loaded.  That would be very confusing.
                # This is now Trac ticket #4474.
                IPython.ipapi.get().magic('run -i "%s"'%name_load)
                L = ''
            elif name_load[-5:] == '.sage':
                try:
                    G = open(name_load)
                except IOError:
                    print "File '%s' not found, so skipping load of %s"%(name_load, name_load)
                    i += 1
                    continue
                else:
                    A = A[:i] + G.readlines() + A[i+1:]
                    continue
            elif name_load[-5:] == '.spyx':
                import interpreter
                L = interpreter.load_cython(name_load)
            else:
                #print "Loading of '%s' not implemented (load .py, .spyx, and .sage files)"%name_load
                L = 'load("%s")'%name_load

        M = preparse(L, reset=(i==0), do_time=do_time, ignore_prompts=ignore_prompts, numeric_literals=not numeric_literals)
        F.append(M)
        i += 1
    # end while

    return '\n'.join(F)

def implicit_mul(code, level=5):
    """
    Insert explicit *'s for implicit multiplication. 

    INPUT: 
        code  -- the code with missing *'s
        level -- how agressive to be in placing *'s
                   0) Do nothing
                   1) numeric followed by alphanumeric
                   2) closing parentheses followed by alphanumeric
                   3) Spaces between alphanumeric
                  10) Adjacent parentheses (may mangle call statements)
                   
    EXAMPLES: 
        sage: from sage.misc.preparser import implicit_mul
        sage: implicit_mul('(2x^2-4x+3)a0')
        '(2*x^2-4*x+3)*a0'
        sage: implicit_mul('a b c in L')
        'a*b*c in L'
        sage: implicit_mul('1r + 1e3 + 5exp(2)')
        '1r + 1e3 + 5*exp(2)'
        sage: implicit_mul('f(a)(b)', level=10)
        'f(a)*(b)'
    """
    def re_no_keyword(pattern, code):
        for _ in range(2): # do it twice in because matches don't overlap
            for m in reversed(list(re.finditer(pattern, code))):
                left, right = m.groups()
                if left not in keywords and right not in keywords:
                    code = "%s%s*%s%s" % (code[:m.start()],
                                          left,
                                          right,
                                          code[m.end():])
        return code
        
    code, literals, state = strip_string_literals(code)
    if level >= 1:
        no_mul_token = " '''_no_mult_token_''' "
        code = re.sub(r'\b0x', r'0%sx' % no_mul_token, code)  # hex digits
        code = re.sub(r'( *)time ', r'\1time %s' % no_mul_token, code)  # first word may be magic 'time'
        code = re.sub(r'\b(\d+(?:\.\d+)?(?:e\d+)?)([rR]\b)', r'\1%s\2' % no_mul_token, code)  # exclude such things as 10r
        code = re.sub(r'\b(\d+(?:\.\d+)?)e([-\d])', r'\1%se%s\2' % (no_mul_token, no_mul_token), code)  # exclude such things as 1e5
        code = re_no_keyword(r'\b((?:\d+(?:\.\d+)?)|(?:%s[0-9eEpn]*\b)) *([a-zA-Z_(]\w*)\b' % numeric_literal_prefix, code)
    if level >= 2:
        code = re.sub(r'(\%\(L\d+\))s', r'\1%ss%s' % (no_mul_token, no_mul_token), code) # literal strings
        code = re_no_keyword(r'(\)) *(\w+)', code)
    if level >= 3:
        code = re_no_keyword(r'(\w+) +(\w+)', code)
    if level >= 10:
        code = re.sub(r'\) *\(', ')*(', code)
    code = code.replace(no_mul_token, '')
    return code % literals



def _strip_quotes(s):
    """
    Strips one set of outer quotes.
    
    INPUT:
        a string s
        
    OUTPUT:
        a string with the single and double quotes on either side of s
        removed, if there are any

    EXAMPLES:
    Both types of quotes work.
        sage: import sage.misc.preparser
        sage: sage.misc.preparser._strip_quotes('"foo.sage"')
        'foo.sage'
        sage: sage.misc.preparser._strip_quotes("'foo.sage'")
        'foo.sage'

    The only thing that is stripped is at most one set of outer quotes:
        sage: sage.misc.preparser._strip_quotes('""foo".sage""')
        '"foo".sage"'
    """
    if len(s) == 0:
        return s
    if s[0] in ["'", '"']:
        s = s[1:]
    if s[-1] in ["'", '"']:
        s = s[:-1]
    return s


class BackslashOperator:
    """
    This implements Matlab-style backslash operator for system solving via A \ b. 
    
    EXAMPLES: 
        sage: preparse("A \ matrix(QQ,2,1,[1/3,'2/3'])")
        "A  * BackslashOperator() * matrix(QQ,Integer(2),Integer(1),[Integer(1)/Integer(3),'2/3'])"
        sage: preparse("A \ matrix(QQ,2,1,[1/3,2*3])")
        'A  * BackslashOperator() * matrix(QQ,Integer(2),Integer(1),[Integer(1)/Integer(3),Integer(2)*Integer(3)])'
        sage: preparse("A \ B + C")
        'A  * BackslashOperator() * B + C'
        sage: preparse("A \ eval('C+D')")
        "A  * BackslashOperator() * eval('C+D')"
        sage: preparse("A \ x / 5")
        'A  * BackslashOperator() * x / Integer(5)'
        sage: preparse("A^3 \ b")
        'A**Integer(3)  * BackslashOperator() * b'
    """
    def __rmul__(self, left):
        """
        EXAMPLES: 
            sage: A = random_matrix(ZZ, 4)
            sage: B = random_matrix(ZZ, 4)
            sage: temp = A * BackslashOperator()
            sage: temp.left is A
            True
            sage: X = temp * B
            sage: A * X == B
            True
        """
        self.left = left
        return self
        
    def __mul__(self, right):
        """
        EXAMPLES: 
            sage: A = matrix(RDF, 5, 5, 2)
            sage: b = vector(RDF, 5, range(5))
            sage: A \ b
            (0.0, 0.5, 1.0, 1.5, 2.0)
            sage: A._backslash_(b)
            (0.0, 0.5, 1.0, 1.5, 2.0)
            sage: A * BackslashOperator() * b
            (0.0, 0.5, 1.0, 1.5, 2.0)
        """
        return self.left._backslash_(right)
