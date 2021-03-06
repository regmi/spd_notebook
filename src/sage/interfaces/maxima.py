r"""
Interface to Maxima

Maxima is a free GPL'd general purpose computer algebra system
whose development started in 1968 at MIT. It contains symbolic
manipulation algorithms, as well as implementations of special
functions, including elliptic functions and generalized
hypergeometric functions. Moreover, Maxima has implementations of
many functions relating to the invariant theory of the symmetric
group `S_n`. (However, the commands for group invariants,
and the corresponding Maxima documenation, are in French.) For many
links to Maxima documentation see
http://maxima.sourceforge.net/docs.shtml/.

AUTHORS:

- William Stein (2005-12): Initial version

- David Joyner: Improved documentation

- William Stein (2006-01-08): Fixed bug in parsing

- William Stein (2006-02-22): comparisons (following suggestion of
  David Joyner)

- William Stein (2006-02-24): *greatly* improved robustness by adding
  sequence numbers to IO bracketing in _eval_line

If the string "error" (case insensitive) occurs in the output of
anything from maxima, a RuntimeError exception is raised.

EXAMPLES: We evaluate a very simple expression in maxima.

::

    sage: maxima('3 * 5')
    15

We factor `x^5 - y^5` in Maxima in several different ways.
The first way yields a Maxima object.

::

    sage: F = maxima.factor('x^5 - y^5')
    sage: F
    -(y-x)*(y^4+x*y^3+x^2*y^2+x^3*y+x^4)
    sage: type(F)
    <class 'sage.interfaces.maxima.MaximaElement'>

Note that Maxima objects can also be displayed using "ASCII art";
to see a normal linear representation of any Maxima object x. Just
use the print command: use ``str(x)``.

::

    sage: print F
                               4      3    2  2    3      4
                   - (y - x) (y  + x y  + x  y  + x  y + x )

You can always use ``repr(x)`` to obtain the linear
representation of an object. This can be useful for moving maxima
data to other systems.

::

    sage: repr(F)
    '-(y-x)*(y^4+x*y^3+x^2*y^2+x^3*y+x^4)'
    sage: F.str()
    '-(y-x)*(y^4+x*y^3+x^2*y^2+x^3*y+x^4)'

The ``maxima.eval`` command evaluates an expression in
maxima and returns the result as a *string* not a maxima object.

::

    sage: print maxima.eval('factor(x^5 - y^5)')
    -(y-x)*(y^4+x*y^3+x^2*y^2+x^3*y+x^4)

We can create the polynomial `f` as a Maxima polynomial,
then call the factor method on it. Notice that the notation
``f.factor()`` is consistent with how the rest of Sage
works.

::

    sage: f = maxima('x^5 - y^5')
    sage: f^2
    (x^5-y^5)^2
    sage: f.factor()
    -(y-x)*(y^4+x*y^3+x^2*y^2+x^3*y+x^4)

Control-C interruption works well with the maxima interface,
because of the excellent implementation of maxima. For example, try
the following sum but with a much bigger range, and hit control-C.

::

    sage: maxima('sum(1/x^2, x, 1, 10)')
    1968329/1270080

Tutorial
--------

We follow the tutorial at
http://maxima.sourceforge.net/docs/intromax/.

::

    sage: maxima('1/100 + 1/101')
    201/10100

::

    sage: a = maxima('(1 + sqrt(2))^5'); a
    (sqrt(2)+1)^5
    sage: a.expand()
    29*sqrt(2)+41

::

    sage: a = maxima('(1 + sqrt(2))^5')
    sage: float(a)                
    82.012193308819747
    sage: a.numer()
    82.01219330881975

::

    sage: maxima.eval('fpprec : 100')
    '100'
    sage: a.bfloat()
    8.20121933088197564152489730020812442785204843859314941221237124017312418754011041266612384955016056b1

::

    sage: maxima('100!')
    93326215443944152681699238856266700490715968264381621468592963895217599993229915608941463976156518286253697920827223758251185210916864000000000000000000000000

::

    sage: f = maxima('(x + 3*y + x^2*y)^3')
    sage: f.expand()
    x^6*y^3+9*x^4*y^3+27*x^2*y^3+27*y^3+3*x^5*y^2+18*x^3*y^2+27*x*y^2+3*x^4*y+9*x^2*y+x^3
    sage: f.subst('x=5/z')
    (5/z+25*y/z^2+3*y)^3
    sage: g = f.subst('x=5/z')
    sage: h = g.ratsimp(); h
    (27*y^3*z^6+135*y^2*z^5+(675*y^3+225*y)*z^4+(2250*y^2+125)*z^3+(5625*y^3+1875*y)*z^2+9375*y^2*z+15625*y^3)/z^6
    sage: h.factor()
    (3*y*z^2+5*z+25*y)^3/z^6

::

    sage: eqn = maxima(['a+b*c=1', 'b-a*c=0', 'a+b=5'])
    sage: s = eqn.solve('[a,b,c]'); s
    [[a=(25*sqrt(79)*%i+25)/(6*sqrt(79)*%i-34),b=(5*sqrt(79)*%i+5)/(sqrt(79)*%i+11),c=(sqrt(79)*%i+1)/10],[a=(25*sqrt(79)*%i-25)/(6*sqrt(79)*%i+34),b=(5*sqrt(79)*%i-5)/(sqrt(79)*%i-11),c=-(sqrt(79)*%i-1)/10]]

Here is an example of solving an algebraic equation::

    sage: maxima('x^2+y^2=1').solve('y')
    [y=-sqrt(1-x^2),y=sqrt(1-x^2)]
    sage: maxima('x^2 + y^2 = (x^2 - y^2)/sqrt(x^2 + y^2)').solve('y')
    [y=-sqrt((-y^2-x^2)*sqrt(y^2+x^2)+x^2),y=sqrt((-y^2-x^2)*sqrt(y^2+x^2)+x^2)]

You can even nicely typeset the solution in latex::

    sage: latex(s)
    \left[ \left[ a={{25\,\sqrt{79}\,i+25}\over{6\,\sqrt{79}\,i-34}} ,   b={{5\,\sqrt{79}\,i+5}\over{\sqrt{79}\,i+11}} , c={{\sqrt{79}\,i+1  }\over{10}} \right]  , \left[ a={{25\,\sqrt{79}\,i-25}\over{6\,  \sqrt{79}\,i+34}} , b={{5\,\sqrt{79}\,i-5}\over{\sqrt{79}\,i-11}} ,   c=-{{\sqrt{79}\,i-1}\over{10}} \right]  \right] 

To have the above appear onscreen via ``xdvi``, type
``view(s)``. (TODO: For OS X should create pdf output
and use preview instead?)

::

    sage: e = maxima('sin(u + v) * cos(u)^3'); e
    cos(u)^3*sin(v+u)
    sage: f = e.trigexpand(); f
    cos(u)^3*(cos(u)*sin(v)+sin(u)*cos(v))
    sage: f.trigreduce()
    (sin(v+4*u)+sin(v-2*u))/8+(3*sin(v+2*u)+3*sin(v))/8
    sage: w = maxima('3 + k*%i')
    sage: f = w^2 + maxima('%e')^w
    sage: f.realpart()
    %e^3*cos(k)-k^2+9

::

    sage: f = maxima('x^3 * %e^(k*x) * sin(w*x)'); f
    x^3*%e^(k*x)*sin(w*x)
    sage: f.diff('x')
    k*x^3*%e^(k*x)*sin(w*x)+3*x^2*%e^(k*x)*sin(w*x)+w*x^3*%e^(k*x)*cos(w*x)
    sage: f.integrate('x')
    (((k*w^6+3*k^3*w^4+3*k^5*w^2+k^7)*x^3+(3*w^6+3*k^2*w^4-3*k^4*w^2-3*k^6)*x^2+(-18*k*w^4-12*k^3*w^2+6*k^5)*x-6*w^4+36*k^2*w^2-6*k^4)*%e^(k*x)*sin(w*x)+((-w^7-3*k^2*w^5-3*k^4*w^3-k^6*w)*x^3+(6*k*w^5+12*k^3*w^3+6*k^5*w)*x^2+(6*w^5-12*k^2*w^3-18*k^4*w)*x-24*k*w^3+24*k^3*w)*%e^(k*x)*cos(w*x))/(w^8+4*k^2*w^6+6*k^4*w^4+4*k^6*w^2+k^8)

::

    sage: f = maxima('1/x^2')
    sage: f.integrate('x', 1, 'inf')
    1
    sage: g = maxima('f/sinh(k*x)^4')
    sage: g.taylor('x', 0, 3)
    f/(k^4*x^4)-2*f/(3*k^2*x^2)+11*f/45-62*k^2*f*x^2/945

::

    sage: maxima.taylor('asin(x)','x',0, 10)
    x+x^3/6+3*x^5/40+5*x^7/112+35*x^9/1152

Examples involving matrices
---------------------------

We illustrate computing with the matrix whose `i,j` entry
is `i/j`, for `i,j=1,\ldots,4`.

::

    sage: f = maxima.eval('f[i,j] := i/j')
    sage: A = maxima('genmatrix(f,4,4)'); A
    matrix([1,1/2,1/3,1/4],[2,1,2/3,1/2],[3,3/2,1,3/4],[4,2,4/3,1])
    sage: A.determinant()
    0
    sage: A.echelon()
    matrix([1,1/2,1/3,1/4],[0,0,0,0],[0,0,0,0],[0,0,0,0])
    sage: A.eigenvalues()
    [[0,4],[3,1]]
    sage: A.eigenvectors()
    [[[0,4],[3,1]],[1,0,0,-4],[0,1,0,-2],[0,0,1,-4/3],[1,2,3,4]]

We can also compute the echelon form in Sage::

    sage: B = matrix(QQ, A)
    sage: B.echelon_form()
    [  1 1/2 1/3 1/4]
    [  0   0   0   0]
    [  0   0   0   0]
    [  0   0   0   0]
    sage: B.charpoly('x').factor()
    (x - 4) * x^3

Laplace Transforms
------------------

We illustrate Laplace transforms::

    sage: _ = maxima.eval("f(t) := t*sin(t)")
    sage: maxima("laplace(f(t),t,s)")
    2*s/(s^2+1)^2

::

    sage: maxima("laplace(delta(t-3),t,s)") #Dirac delta function
    %e^-(3*s)

::

    sage: _ = maxima.eval("f(t) := exp(t)*sin(t)")
    sage: maxima("laplace(f(t),t,s)")
    1/(s^2-2*s+2)

::

    sage: _ = maxima.eval("f(t) := t^5*exp(t)*sin(t)")
    sage: maxima("laplace(f(t),t,s)")
    360*(2*s-2)/(s^2-2*s+2)^4-480*(2*s-2)^3/(s^2-2*s+2)^5+120*(2*s-2)^5/(s^2-2*s+2)^6
    sage: print maxima("laplace(f(t),t,s)")
                                             3                 5
               360 (2 s - 2)    480 (2 s - 2)     120 (2 s - 2)
              --------------- - --------------- + ---------------
                2           4     2           5     2           6
              (s  - 2 s + 2)    (s  - 2 s + 2)    (s  - 2 s + 2)

::

    sage: maxima("laplace(diff(x(t),t),t,s)")
    s*?%laplace(x(t),t,s)-x(0)

::

    sage: maxima("laplace(diff(x(t),t,2),t,s)")
    -?%at('diff(x(t),t,1),t=0)+s^2*?%laplace(x(t),t,s)-x(0)*s

It is difficult to read some of these without the 2d
representation::

    sage: print maxima("laplace(diff(x(t),t,2),t,s)")
                         !
                d        !         2
              - -- (x(t))!      + s  laplace(x(t), t, s) - x(0) s
                dt       !
                         !t = 0

Even better, use
``view(maxima("laplace(diff(x(t),t,2),t,s)"))`` to see
a typeset version.

Continued Fractions
-------------------

A continued fraction `a + 1/(b + 1/(c + \cdots))` is
represented in maxima by the list `[a, b, c, \ldots]`.

::

    sage: maxima("cf((1 + sqrt(5))/2)")
    [1,1,1,1,2]
    sage: maxima("cf ((1 + sqrt(341))/2)")
    [9,1,2,1,2,1,17,1,2,1,2,1,17,1,2,1,2,1,17,2]

Special examples
----------------

In this section we illustrate calculations that would be awkward to
do (as far as I know) in non-symbolic computer algebra systems like
MAGMA or GAP.

We compute the gcd of `2x^{n+4} - x^{n+2}` and
`4x^{n+1} + 3x^n` for arbitrary `n`.

::

    sage: f = maxima('2*x^(n+4) - x^(n+2)')
    sage: g = maxima('4*x^(n+1) + 3*x^n')
    sage: f.gcd(g)
    x^n

You can plot 3d graphs (via gnuplot)::

    sage: maxima('plot3d(x^2-y^2, [x,-2,2], [y,-2,2], [grid,12,12])')  # not tested
    [displays a 3 dimensional graph]

You can formally evaluate sums (note the ``nusum``
command)::

    sage: S = maxima('nusum(exp(1+2*i/n),i,1,n)')
    sage: print S
                            2/n + 3                   2/n + 1
                          %e                        %e
                   ----------------------- - -----------------------
                      1/n         1/n           1/n         1/n
                   (%e    - 1) (%e    + 1)   (%e    - 1) (%e    + 1)

We formally compute the limit as `n\to\infty` of
`2S/n` as follows::

    sage: T = S*maxima('2/n')
    sage: T.tlimit('n','inf')
    %e^3-%e

Miscellaneous
-------------

Obtaining digits of `\pi`::

    sage: maxima.eval('fpprec : 100')
    '100'
    sage: maxima(pi).bfloat()
    3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117068b0

Defining functions in maxima::

    sage: maxima.eval('fun[a] := a^2')
    'fun[a]:=a^2'
    sage: maxima('fun[10]')
    100

Interactivity
-------------

Unfortunately maxima doesn't seem to have a non-interactive mode,
which is needed for the Sage interface. If any Sage call leads to
maxima interactively answering questions, then the questions can't be
answered and the maxima session may hang. See the discussion at
http://www.ma.utexas.edu/pipermail/maxima/2005/011061.html for some
ideas about how to fix this problem. An example that illustrates this
problem is ``maxima.eval('integrate (exp(a*x), x, 0, inf)')``.

Latex Output
------------

To tex a maxima object do this::

    sage: latex(maxima('sin(u) + sinh(v^2)'))
    \sinh v^2+\sin u

Here's another example::

    sage: g = maxima('exp(3*%i*x)/(6*%i) + exp(%i*x)/(2*%i) + c')
    sage: latex(g)
    -{{i\,e^{3\,i\,x}}\over{6}}-{{i\,e^{i\,x}}\over{2}}+c

Long Input
----------

The MAXIMA interface reads in even very long input (using files) in
a robust manner, as long as you are creating a new object.

.. note::

   Using ``maxima.eval`` for long input is much less robust, and is
   not recommended.

::

    sage: t = '"%s"'%10^10000   # ten thousand character string.
    sage: a = maxima(t)

TESTS: This working tests that a subtle bug has been fixed::

    sage: f = maxima.function('x','gamma(x)')
    sage: g = f(1/7)
    sage: g
    gamma(1/7)
    sage: del f
    sage: maxima(sin(x))
    sin(x)

This tests to make sure we handle the case where Maxima asks if an
expression is positive or zero.

::

    sage: var('Ax,Bx,By')
    (Ax, Bx, By)
    sage: t = -Ax*sin(sqrt(Ax^2)/2)/(sqrt(Ax^2)*sqrt(By^2 + Bx^2))
    sage: t.limit(Ax=0,dir='above')
    Traceback (most recent call last):
    ...
    TypeError: Computation failed since Maxima requested additional constraints (try the command 'assume(By^2+Bx^2>0)' before integral or limit evaluation, for example):
    Is By^2+Bx^2  positive or zero?

A long complicated input expression::

    sage: maxima._eval_line('((((((((((0) + ((1) / ((n0) ^ (0)))) + ((1) / ((n1) ^ (1)))) + ((1) / ((n2) ^ (2)))) + ((1) / ((n3) ^ (3)))) + ((1) / ((n4) ^ (4)))) + ((1) / ((n5) ^ (5)))) + ((1) / ((n6) ^ (6)))) + ((1) / ((n7) ^ (7)))) + ((1) / ((n8) ^ (8)))) + ((1) / ((n9) ^ (9)));')
    '1/n9^9+1/n8^8+1/n7^7+1/n6^6+1/n5^5+1/n4^4+1/n3^3+1/n2^2+1/n1+1'
"""

#*****************************************************************************
#       Copyright (C) 2005 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from __future__ import with_statement

import os, re, sys, subprocess
import pexpect
cygwin = os.uname()[0][:6]=="CYGWIN"

from expect import Expect, ExpectElement, FunctionElement, ExpectFunction, gc_disabled, AsciiArtString
from pexpect import EOF

from random import randrange

##import sage.rings.all
import sage.rings.complex_number

from sage.misc.misc import verbose, DOT_SAGE, SAGE_ROOT

from sage.misc.multireplace import multiple_replace

COMMANDS_CACHE = '%s/maxima_commandlist_cache.sobj'%DOT_SAGE

import sage.server.support

# The Maxima "apropos" command, e.g., apropos(det) gives a list
# of all identifiers that begin in a certain way.  This could
# maybe be useful somehow... (?)  Also maxima has a lot for getting
# documentation from the system -- this could also be useful.

class Maxima(Expect):
    """
    Interface to the Maxima interpreter.
    """
    def __init__(self, script_subdirectory=None, logfile=None, server=None,
                 init_code = None):
        """
        Create an instance of the Maxima interpreter.
        
        EXAMPLES::
        
            sage: maxima == loads(dumps(maxima))
            True
        """
        # TODO: Input and output prompts in maxima can be changed by
        # setting inchar and outchar..
        eval_using_file_cutoff = 256
        self.__eval_using_file_cutoff = eval_using_file_cutoff
        STARTUP = '%s/local/bin/sage-maxima.lisp'%SAGE_ROOT
        if not os.path.exists(STARTUP):
            raise RuntimeError, 'You must get the file local/bin/sage-maxima.lisp'
        if init_code is None:
            # display2d -- no ascii art output
            # keepfloat -- don't automatically convert floats to rationals
            init_code = ['display2d : false', 'keepfloat : true']
        Expect.__init__(self,
                        name = 'maxima',
                        prompt = '\(\%i[0-9]+\)',
                        command = 'maxima -p "%s"'%STARTUP, 
                        maxread = 10000, 
                        script_subdirectory = script_subdirectory,
                        restart_on_ctrlc = False,
                        verbose_start = False,
                        init_code = init_code,
                        logfile = logfile,
                        eval_using_file_cutoff=eval_using_file_cutoff)
        self._display_prompt = '<sage-display>'  # must match what is in the file local/ibn/sage-maxima.lisp!!
        self._output_prompt_re = re.compile('\(\%o[0-9]+\)')
        self._ask = ['zero or nonzero?', 'an integer?', 'positive, negative, or zero?', 
                     'positive or negative?', 'positive or zero?']
        self._prompt_wait = [self._prompt] + [re.compile(x) for x in self._ask] + \
                            ['Break [0-9]+'] #note that you might need to change _expect_expr if you
                                             #change this
        self._error_re = re.compile('(Principal Value|debugmode|Incorrect syntax|Maxima encountered a Lisp error)')
        self._display2d = False


    def _function_class(self):
        """
        EXAMPLES::
        
            sage: maxima._function_class()
            <class 'sage.interfaces.maxima.MaximaExpectFunction'>
        """
        return MaximaExpectFunction

    def _start(self):
        """
        Starts the Maxima interpreter.
        
        EXAMPLES::
        
            sage: m = Maxima()
            sage: m.is_running()
            False
            sage: m._start()
            sage: m.is_running()
            True
        """
        Expect._start(self)
        self._sendline(r":lisp (defun tex-derivative (x l r) (tex (if $derivabbrev (tex-dabbrev x) (tex-d x '\\partial)) l r lop rop ))")
        self._eval_line('0;')

    def __reduce__(self):
        """
        EXAMPLES::
        
            sage: maxima.__reduce__()
            (<function reduce_load_Maxima at 0x...>, ())
        """
        return reduce_load_Maxima, tuple([])

    def _quit_string(self):
        """
        EXAMPLES::
        
            sage: maxima._quit_string()
            'quit();'
        """
        return 'quit();'

    def _sendline(self, str):
        self._sendstr(str)
        os.write(self._expect.child_fd, os.linesep)

    def _crash_msg(self):
        """
        EXAMPLES::
        
            sage: maxima._crash_msg()
            Maxima crashed -- automatically restarting.
        """
        print "Maxima crashed -- automatically restarting."

    def _expect_expr(self, expr=None, timeout=None):
        """
        EXAMPLES:
            sage: a,b=var('a,b')
            sage: integrate(1/(x^3 *(a+b*x)^(1/3)),x)
            Traceback (most recent call last):
            ...
            TypeError: Computation failed since Maxima requested additional constraints (try the command 'assume(a>0)' before integral or limit evaluation, for example):
            Is  a  positive or negative?
            sage: assume(a>0)
            sage: integrate(1/(x^3 *(a+b*x)^(1/3)),x)
            2*b^2*arctan((2*(b*x + a)^(1/3) + a^(1/3))/(sqrt(3)*a^(1/3)))/(3*sqrt(3)*a^(7/3)) - b^2*log((b*x + a)^(2/3) + a^(1/3)*(b*x + a)^(1/3) + a^(2/3))/(9*a^(7/3)) + 2*b^2*log((b*x + a)^(1/3) - a^(1/3))/(9*a^(7/3)) + (4*b^2*(b*x + a)^(5/3) - 7*a*b^2*(b*x + a)^(2/3))/(6*a^2*(b*x + a)^2 - 12*a^3*(b*x + a) + 6*a^4)
            sage: var('x, n')
            (x, n)
            sage: integral(x^n,x)
            Traceback (most recent call last):
            ...
            TypeError: Computation failed since Maxima requested additional constraints (try the command 'assume(n+1>0)' before integral or limit evaluation, for example):
            Is  n+1  zero or nonzero?
            sage: assume(n+1>0)
            sage: integral(x^n,x)
            x^(n + 1)/(n + 1)
            sage: forget()
        """
        if expr is None:
            expr = self._prompt_wait
        if self._expect is None:
            self._start()
        try:
            if timeout:
                i = self._expect.expect(expr,timeout=timeout)
            else:
                i = self._expect.expect(expr)
            if i > 0:
                v = self._expect.before

                #We check to see if there is a "serious" error in Maxima.
                #Note that this depends on the order of self._prompt_wait
                if expr is self._prompt_wait and i > len(self._ask):
                    self.quit()
                    raise ValueError, "%s\nComputation failed due to a bug in Maxima -- NOTE: Maxima had to be restarted."%v

                j = v.find('Is ')
                v = v[j:]
                k = v.find(' ',4)
                msg = "Computation failed since Maxima requested additional constraints (try the command 'assume(" + v[4:k] +">0)' before integral or limit evaluation, for example):\n" + v + self._ask[i-1]
                self._sendstr(chr(3))
                self._sendstr(chr(3))
                self._expect_expr()
                raise ValueError, msg
        except KeyboardInterrupt, msg:
            #print self._expect.before
            i = 0
            while True:
                try:
                    print "Control-C pressed.  Interrupting Maxima. Please wait a few seconds..."
                    self._sendstr('quit;\n'+chr(3))
                    self._sendstr('quit;\n'+chr(3))
                    self.interrupt()
                    self.interrupt()
                except KeyboardInterrupt:
                    i += 1
                    if i > 10:
                        break
                    pass
                else:
                    break
            raise KeyboardInterrupt, msg


    def _batch(self, s, batchload=True):
        filename = '%s-%s'%(self._local_tmpfile(),randrange(2147483647))
        F = open(filename, 'w')
        F.write(s)
        F.close()
        if self.is_remote():
            self._send_tmpfile_to_server(local_file=filename)
            tmp_to_use = self._remote_tmpfile()
        tmp_to_use = filename
        
        if batchload:
            cmd = 'batchload("%s");'%tmp_to_use
        else:
            cmd = 'batch("%s");'%tmp_to_use

        r = randrange(2147483647)
        s = str(r+1)
        cmd = "%s1+%s;\n"%(cmd,r)

        self._sendline(cmd)
        self._expect_expr(s)
        out = self._before()
        self._error_check(str, out)
        os.unlink(filename)
        return out

    def _error_check(self, str, out):
        r = self._error_re
        m = r.search(out)
        if not m is None:
            self._error_msg(str, out)
            
    def _error_msg(self, str, out):
        raise TypeError, "Error executing code in Maxima\nCODE:\n\t%s\nMaxima ERROR:\n\t%s"%(str, out.replace('-- an error.  To debug this try debugmode(true);',''))

    def _eval_line(self, line, allow_use_file=False,
                   wait_for_prompt=True, reformat=True, error_check=True):
        if len(line) == 0:
            return ''
        line = line.rstrip()
        if line[-1] != '$' and line[-1] != ';':
            line += ';'

        self._synchronize()

        if len(line) > self.__eval_using_file_cutoff:
	    # This implicitly uses the set method, then displays the result of the thing that was set. 
            # This only works when the input line is an expression.   But this is our only choice, since
            # batchmode doesn't display expressions to screen.   
            a = self(line)
            return repr(a)
        else:
            self._sendline(line)

        if not wait_for_prompt:
            return

        self._expect_expr(self._display_prompt)
        self._expect_expr()
        out = self._before()
        if error_check:
            self._error_check(line, out)
        
        if not reformat:
            return out
        
        r = self._output_prompt_re
        m = r.search(out)
        if m is None:
            o = out[:-2]
        else:
            o = out[m.end()+1:-2]
        o = ''.join([x.strip() for x in o.split()])
        return o

        i = o.rfind('(%o')
        return o[:i]


    def _synchronize(self):
        """
        Synchronize pexpect interface.
        
        This put a random integer (plus one!) into the output stream, then
        waits for it, thus resynchronizing the stream. If the random
        integer doesn't appear within 1 second, maxima is sent interrupt
        signals.
        
        This way, even if you somehow left maxima in a busy state
        computing, calling _synchronize gets everything fixed.
        
        EXAMPLES: This makes Maxima start a calculation::
        
            sage: maxima._sendstr('1/1'*500)
        
        When you type this command, this synchronize command is implicitly
        called, and the above running calculation is interrupted::
        
            sage: maxima('2+2')
            4
        """
        marker = '__SAGE_SYNCHRO_MARKER_'
        if self._expect is None: return
        r = randrange(2147483647)
        s = marker + str(r+1)
        cmd = '''sconcat("%s",(%s+1));\n'''%(marker,r)
        self._sendstr(cmd)
        try:
            self._expect_expr(timeout=0.5)
            if not s in self._before():
                self._expect_expr(s,timeout=0.5)
                self._expect_expr(timeout=0.5)
        except pexpect.TIMEOUT, msg:
            self._interrupt()
        except pexpect.EOF:
            self._crash_msg()
            self.quit()


    ###########################################
    # System -- change directory, etc
    ###########################################
    def chdir(self, dir):
        """
        Change Maxima's current working directory.
        
        EXAMPLES::
        
            sage: maxima.chdir('/')
        """
        self.lisp('(ext::cd "%s")'%dir)

    ###########################################
    # Direct access to underlying lisp interpreter. 
    ###########################################
    def lisp(self, cmd):
        """
        Send a lisp command to maxima.
        
        .. note::

           The output of this command is very raw - not pretty.
        
        EXAMPLES::
        
            sage: maxima.lisp("(+ 2 17)")   # random formated output
             :lisp (+ 2 17)
            19
            (
        """
        self._eval_line(':lisp %s\n""'%cmd, allow_use_file=False, wait_for_prompt=False, reformat=False, error_check=False)
        self._expect_expr('(%i)')
        return self._before()

    ###########################################
    # Interactive help
    ###########################################
    def _command_runner(self, command, s, redirect=True):
        """
        Run ``command`` in a new Maxima session and return its
        output as an ``AsciiArtString``.
        
        If redirect is set to False, then the output of the command is not
        returned as a string. Instead, it behaves like os.system. This is
        used for interactive things like Maxima's demos. See maxima.demo?
        
        EXAMPLES::
        
            sage: maxima._command_runner('describe', 'gcd')
            -- Function: gcd (<p_1>, <p_2>, <x_1>, ...)
            ...
        """
        cmd = 'maxima --very-quiet -r "%s(%s);" '%(command, s)
        if sage.server.support.EMBEDDED_MODE:
            cmd += '< /dev/null'

        if redirect:
            p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            res = AsciiArtString(p.stdout.read())
            return res
        else:
            subprocess.Popen(cmd, shell=True)


    def help(self, s):
        """
        EXAMPLES::
        
            sage: maxima.help('gcd')
            -- Function: gcd (<p_1>, <p_2>, <x_1>, ...)
            ...
        """
        return self._command_runner("describe", s)

    def example(self, s):
        """
        EXAMPLES::
        
            sage: maxima.example('arrays')
            a[n]:=n*a[n-1]
                                            a  := n a
                                             n       n - 1
            a[0]:1
            a[5]
                                                  120
            a[n]:=n
            a[6]
                                                   6
            a[4]
                                                  24
                                                 done
        """
        return self._command_runner("example", s)

    describe = help

    def demo(self, s):
        """
        EXAMPLES::
        
            sage: maxima.demo('array') # not tested
            batching /opt/sage/local/share/maxima/5.16.3/demo/array.dem
        
        At the _ prompt, type ';' followed by enter to get next demo
        subscrmap : true _
        """
        return self._command_runner("demo", s, redirect=False)

    def completions(self, s, verbose=True):
        """
        Return all commands that complete the command starting with the
        string s. This is like typing s[tab] in the Maxima interpreter.
        
        EXAMPLES::
        
            sage: maxima.completions('gc', verbose=False)
            ['gc', 'gcd', 'gcdex', 'gcfactor', 'gcprint', 'gctime']
        """
        if verbose:
            print s,
            sys.stdout.flush()
        s = self._eval_line('apropos(%s)'%s, error_check=False).replace('\\ - ','-')
        return [x for x in s[1:-1].split(',') if x[0] != '?']

    def _commands(self, verbose=True):
        """
        Return list of all commands defined in Maxima.
        
        EXAMPLES::
        
            sage: maxima._commands(verbose=False)
            ['a',
             'abconvtest',
             ...
             'Z']
        """
        try:
            return self.__commands
        except AttributeError:
            self.__commands = sum([self.completions(chr(97+n), verbose=verbose) for n in range(26)], [])
        return self.__commands

    def trait_names(self, verbose=True, use_disk_cache=True):
        """
        Return all Maxima commands, which is useful for tab completion.
        
        EXAMPLES::
        
            sage: t = maxima.trait_names(verbose=False)
            sage: 'gcd' in t
            True
            sage: len(t)    # random output
            1743
        """
        try:
            return self.__trait_names
        except AttributeError:
            import sage.misc.persist
            if use_disk_cache:
                try:
                    self.__trait_names = sage.misc.persist.load(COMMANDS_CACHE)
                    return self.__trait_names
                except IOError:
                    pass
            if verbose:
                print "\nBuilding Maxima command completion list (this takes"
                print "a few seconds only the first time you do it)."
                print "To force rebuild later, delete %s."%COMMANDS_CACHE
            v = self._commands(verbose=verbose)
            if verbose:
                print "\nDone!"
            self.__trait_names = v
            sage.misc.persist.save(v, COMMANDS_CACHE)
            return v

    def _object_class(self):
        """
        Return the Python class of Maxima elements.
        
        EXAMPLES::
        
            sage: maxima._object_class()
            <class 'sage.interfaces.maxima.MaximaElement'>
        """
        return MaximaElement

    def _function_element_class(self):
        """      
        EXAMPLES::
        
            sage: maxima._function_element_class()
            <class 'sage.interfaces.maxima.MaximaFunctionElement'>
        """
        return MaximaFunctionElement

    def _true_symbol(self):
        """
        Return the true symbol in Maxima.
        
        EXAMPLES::
        
            sage: maxima._true_symbol()
            'true'
            sage: maxima.eval('is(2 = 2)')
            'true'
        """
        return 'true'

    def _false_symbol(self):
        """
        Return the false symbol in Maxima.
        
        EXAMPLES::
        
            sage: maxima._false_symbol()
            'false'
            sage: maxima.eval('is(2 = 4)')
            'false'
        """
        return 'false'

    def function(self, args, defn, rep=None, latex=None):
        """
        Return the Maxima function with given arguments and definition.
        
        INPUT:
        
        
        -  ``args`` - a string with variable names separated by
           commas
        
        -  ``defn`` - a string (or Maxima expression) that
           defines a function of the arguments in Maxima.
        
        -  ``rep`` - an optional string; if given, this is how
           the function will print.
        
        
        EXAMPLES::
        
            sage: f = maxima.function('x', 'sin(x)')
            sage: f(3.2)
            -.05837414342758009
            sage: f = maxima.function('x,y', 'sin(x)+cos(y)')
            sage: f(2,3.5)
            sin(2)-.9364566872907963
            sage: f
            sin(x)+cos(y)
        
        ::
        
            sage: g = f.integrate('z')
            sage: g
            (cos(y)+sin(x))*z
            sage: g(1,2,3)
            3*(cos(2)+sin(1))
        
        The function definition can be a maxima object::
        
            sage: an_expr = maxima('sin(x)*gamma(x)')
            sage: t = maxima.function('x', an_expr)
            sage: t
            gamma(x)*sin(x)
            sage: t(2)
             sin(2)
            sage: float(t(2))
            0.90929742682568171
            sage: loads(t.dumps())
            gamma(x)*sin(x)
        """
        name = self._next_var_name()
        if isinstance(defn, MaximaElement):
            defn = defn.str()
        elif not isinstance(defn, str):
            defn = str(defn)
        if isinstance(args, MaximaElement):
            args = args.str()
        elif not isinstance(args, str):
            args = str(args)
        cmd = '%s(%s) := %s'%(name, args, defn)
        maxima._eval_line(cmd)
        if rep is None:
            rep = defn
        f = MaximaFunction(self, name, rep, args, latex)
        return f

    def set(self, var, value):
        """
        Set the variable var to the given value.
        
        INPUT:
        
        
        -  ``var`` - string
        
        -  ``value`` - string
        
        
        EXAMPLES::
        
            sage: maxima.set('x', '2')
            sage: maxima.get('x')
            '2'
        """
        if not isinstance(value, str):
            raise TypeError
        cmd = '%s : %s$'%(var, value.rstrip(';'))
        if len(cmd) > self.__eval_using_file_cutoff:
            self._batch(cmd, batchload=True)
        else:
            self._eval_line(cmd)
            #self._sendline(cmd)
            #self._expect_expr()
            #out = self._before()
            #self._error_check(cmd, out)

    def get(self, var):
        """
        Get the string value of the variable var.
        
        EXAMPLES::
        
            sage: maxima.set('x', '2')
            sage: maxima.get('x')
            '2'
        """
        s = self._eval_line('%s;'%var)
        return s
        
    def clear(self, var):
        """
        Clear the variable named var.
        
        EXAMPLES::
        
            sage: maxima.set('x', '2')
            sage: maxima.get('x')
            '2'
            sage: maxima.clear('x')
            sage: maxima.get('x')
            'x'
        """
        try:
            self._expect.send('kill(%s)$'%var)
        except (TypeError, AttributeError):
            pass
        
    def console(self):
        r"""
        Start the interactive Maxima console. This is a completely separate
        maxima session from this interface. To interact with this session,
        you should instead use ``maxima.interact()``.
        
        EXAMPLES::
        
            sage: maxima.console()             # not tested (since we can't)
            Maxima 5.13.0 http://maxima.sourceforge.net
            Using Lisp CLISP 2.41 (2006-10-13)
            Distributed under the GNU Public License. See the file COPYING.
            Dedicated to the memory of William Schelter.
            This is a development version of Maxima. The function bug_report()
            provides bug reporting information.
            (%i1)
        
        ::
        
            sage: maxima.interact()     # this is not tested either
              --> Switching to Maxima <-- 
            maxima: 2+2
            4
            maxima: 
              --> Exiting back to Sage <--
        """
        maxima_console()
    
    def version(self):
        """
        Return the version of Maxima that Sage includes.
        
        EXAMPLES::
        
            sage: maxima.version()
            '5.16.3'
        """
        return maxima_version()

    def cputime(self, t=None):
        r"""
        Returns the amount of CPU time that this Maxima session has used.
        If \var{t} is not None, then it returns the difference between
        the current CPU time and \var{t}.
        
        EXAMPLES:
            sage: t = maxima.cputime()
            sage: _ = maxima.de_solve('diff(y,x,2) + 3*x = y', ['x','y'], [1,1,1])
            sage: maxima.cputime(t) # output random
            0.568913
        """
        if t:
            return float(self.eval('elapsed_run_time()')) - t
        else:
            return float(self.eval('elapsed_run_time()'))


##     def display2d(self, flag=True):
##         """
##         Set the flag that determines whether Maxima objects are
##         printed using their 2-d ASCII art representation.  When the
##         maxima interface starts the default is that objects are not
##         represented in 2-d.

##         INPUT:
##             flag -- bool (default: True)

##         EXAMPLES
##             sage: maxima('1/2')
##             1/2
##             sage: maxima.display2d(True)
##             sage: maxima('1/2')
##                                            1
##                                            -
##                                            2
##             sage: maxima.display2d(False)
##         """
##         self._display2d = bool(flag)

    def plot2d(self, *args):
        r"""
        Plot a 2d graph using Maxima / gnuplot.
        
        maxima.plot2d(f, '[var, min, max]', options)
        
        INPUT:
        
        
        -  ``f`` - a string representing a function (such as
           f="sin(x)") [var, xmin, xmax]
        
        -  ``options`` - an optional string representing plot2d
           options in gnuplot format
        
        
        EXAMPLES::
        
            sage: maxima.plot2d('sin(x)','[x,-5,5]')   # not tested
            sage: opts = '[gnuplot_term, ps], [gnuplot_out_file, "sin-plot.eps"]'
            sage: maxima.plot2d('sin(x)','[x,-5,5]',opts)    # not tested
        
        The eps file is saved in the current directory.
        """
        self('plot2d(%s)'%(','.join([str(x) for x in args])))

    def plot2d_parametric(self, r, var, trange, nticks=50, options=None):
        r"""
        Plots r = [x(t), y(t)] for t = tmin...tmax using gnuplot with
        options
        
        INPUT:
        
        
        -  ``r`` - a string representing a function (such as
           r="[x(t),y(t)]")
        
        -  ``var`` - a string representing the variable (such
           as var = "t")
        
        -  ``trange`` - [tmin, tmax] are numbers with tmintmax
        
        -  ``nticks`` - int (default: 50)
        
        -  ``options`` - an optional string representing plot2d
           options in gnuplot format
        
        
        EXAMPLES::
        
            sage: maxima.plot2d_parametric(["sin(t)","cos(t)"], "t",[-3.1,3.1])   # not tested
        
        ::
        
            sage: opts = '[gnuplot_preamble, "set nokey"], [gnuplot_term, ps], [gnuplot_out_file, "circle-plot.eps"]'
            sage: maxima.plot2d_parametric(["sin(t)","cos(t)"], "t", [-3.1,3.1], options=opts)   # not tested
        
        The eps file is saved to the current working directory.
        
        Here is another fun plot::
        
            sage: maxima.plot2d_parametric(["sin(5*t)","cos(11*t)"], "t", [0,2*pi()], nticks=400)    # not tested
        """
        tmin = trange[0]
        tmax = trange[1]
        cmd = "plot2d([parametric, %s, %s, [%s, %s, %s], [nticks, %s]]"%( \
                   r[0], r[1], var, tmin, tmax, nticks)
        if options is None:
            cmd += ")"
        else:
            cmd += ", %s)"%options
        self(cmd)

    def plot3d(self, *args):
        r"""
        Plot a 3d graph using Maxima / gnuplot.
        
        maxima.plot3d(f, '[x, xmin, xmax]', '[y, ymin, ymax]', '[grid, nx,
        ny]', options)
        
        INPUT:
        
        
        -  ``f`` - a string representing a function (such as
           f="sin(x)") [var, min, max]
        
        
        EXAMPLES::
        
            sage: maxima.plot3d('1 + x^3 - y^2', '[x,-2,2]', '[y,-2,2]', '[grid,12,12]')    # not tested
            sage: maxima.plot3d('sin(x)*cos(y)', '[x,-2,2]', '[y,-2,2]', '[grid,30,30]')   # not tested
            sage: opts = '[gnuplot_term, ps], [gnuplot_out_file, "sin-plot.eps"]' 
            sage: maxima.plot3d('sin(x+y)', '[x,-5,5]', '[y,-1,1]', opts)    # not tested
        
        The eps file is saved in the current working directory.
        """
        self('plot3d(%s)'%(','.join([str(x) for x in args])))

    def plot3d_parametric(self, r, vars, urange, vrange, options=None):
        r"""
        Plot a 3d parametric graph with r=(x,y,z), x = x(u,v), y = y(u,v),
        z = z(u,v), for u = umin...umax, v = vmin...vmax using gnuplot with
        options.
        
        INPUT:
        
        
        -  ``x, y, z`` - a string representing a function (such
           as ``x="u2+v2"``, ...) vars is a list or two strings
           representing variables (such as vars = ["u","v"])
        
        -  ``urange`` - [umin, umax]
        
        -  ``vrange`` - [vmin, vmax] are lists of numbers with
           umin umax, vmin vmax
        
        -  ``options`` - optional string representing plot2d
           options in gnuplot format
        
        
        OUTPUT: displays a plot on screen or saves to a file
        
        EXAMPLES::
        
            sage: maxima.plot3d_parametric(["v*sin(u)","v*cos(u)","v"], ["u","v"],[-3.2,3.2],[0,3])     # not tested
            sage: opts = '[gnuplot_term, ps], [gnuplot_out_file, "sin-cos-plot.eps"]'
            sage: maxima.plot3d_parametric(["v*sin(u)","v*cos(u)","v"], ["u","v"],[-3.2,3.2],[0,3],opts)      # not tested
        
        The eps file is saved in the current working directory.
        
        Here is a torus::
        
            sage: _ = maxima.eval("expr_1: cos(y)*(10.0+6*cos(x)); expr_2: sin(y)*(10.0+6*cos(x)); expr_3: -6*sin(x);")  # optional
            sage: maxima.plot3d_parametric(["expr_1","expr_2","expr_3"], ["x","y"],[0,6],[0,6])   # not tested
        
        Here is a Mobius strip::
        
            sage: x = "cos(u)*(3 + v*cos(u/2))"
            sage: y = "sin(u)*(3 + v*cos(u/2))"
            sage: z = "v*sin(u/2)"
            sage: maxima.plot3d_parametric([x,y,z],["u","v"],[-3.1,3.2],[-1/10,1/10])   # not tested
        """
        umin = urange[0]
        umax = urange[1]
        vmin = vrange[0]
        vmax = vrange[1]
        cmd = 'plot3d([%s, %s, %s], [%s, %s, %s], [%s, %s, %s]'%(
            r[0], r[1], r[2], vars[0], umin, umax, vars[1], vmin, vmax)
        if options is None:
            cmd += ')'
        else:
            cmd += ', %s)'%options
        maxima(cmd)

    def de_solve(maxima, de, vars, ics=None):
        """
        Solves a 1st or 2nd order ordinary differential equation (ODE) in
        two variables, possibly with initial conditions.
        
        INPUT:
        
        
        -  ``de`` - a string representing the ODE
        
        -  ``vars`` - a list of strings representing the two
           variables.
        
        -  ``ics`` - a triple of numbers [a,b1,b2] representing
           y(a)=b1, y'(a)=b2
        
        
        EXAMPLES::
        
            sage: maxima.de_solve('diff(y,x,2) + 3*x = y', ['x','y'], [1,1,1])
            y=3*x-2*%e^(x-1)
            sage: maxima.de_solve('diff(y,x,2) + 3*x = y', ['x','y'])
            y=%k1*%e^x+%k2*%e^-x+3*x
            sage: maxima.de_solve('diff(y,x) + 3*x = y', ['x','y'])
            y=(%c-3*(-x-1)*%e^-x)*%e^x
            sage: maxima.de_solve('diff(y,x) + 3*x = y', ['x','y'],[1,1])
            y=-%e^-1*(5*%e^x-3*%e*x-3*%e)
        """
        if not isinstance(vars, str):
            str_vars = '%s, %s'%(vars[1], vars[0])
        else:
            str_vars = vars
        maxima.eval('depends(%s)'%str_vars)
        m = maxima(de)
        a = 'ode2(%s, %s)'%(m.name(), str_vars)
        if ics != None:
            if len(ics) == 3:
                cmd = "ic2("+a+",%s=%s,%s=%s,diff(%s,%s)=%s);"%(vars[0],ics[0], vars[1],ics[1], vars[1], vars[0], ics[2])
                return maxima(cmd)
            if len(ics) == 2:
                return maxima("ic1("+a+",%s=%s,%s=%s);"%(vars[0],ics[0], vars[1],ics[1]))
        return maxima(a+";")

    def de_solve_laplace(self, de, vars, ics=None):
        """
        Solves an ordinary differential equation (ODE) using Laplace
        transforms.
        
        INPUT:
        
        
        -  ``de`` - a string representing the ODE (e.g., de =
           "diff(f(x),x,2)=diff(f(x),x)+sin(x)")
        
        -  ``vars`` - a list of strings representing the
           variables (e.g., vars = ["x","f"])
        
        -  ``ics`` - a list of numbers representing initial
           conditions, with symbols allowed which are represented by strings
           (eg, f(0)=1, f'(0)=2 is ics = [0,1,2])
        
        
        EXAMPLES::
        
            sage: maxima.clear('x'); maxima.clear('f')
            sage: maxima.de_solve_laplace("diff(f(x),x,2) = 2*diff(f(x),x)-f(x)", ["x","f"], [0,1,2])
            f(x)=x*%e^x+%e^x
        
        ::
        
            sage: maxima.clear('x'); maxima.clear('f')            
            sage: f = maxima.de_solve_laplace("diff(f(x),x,2) = 2*diff(f(x),x)-f(x)", ["x","f"])
            sage: f
            f(x)=x*%e^x*('at('diff(f(x),x,1),x=0))-f(0)*x*%e^x+f(0)*%e^x
            sage: print f
                                               !
                                   x  d        !                  x          x
                        f(x) = x %e  (-- (f(x))!     ) - f(0) x %e  + f(0) %e
                                      dx       !
                                               !x = 0
        
        .. note::

           The second equation sets the values of `f(0)` and
           `f'(0)` in Maxima, so subsequent ODEs involving these
           variables will have these initial conditions automatically
           imposed.
        """
        if not (ics is None):
            d = len(ics)
            for i in range(0,d-1):
                ic = 'atvalue(diff(%s(%s), %s, %s), %s = %s, %s)'%(
                    vars[1], vars[0], vars[0], i, vars[0], ics[0], ics[1+i])
                maxima.eval(ic)
        return maxima('desolve(%s, %s(%s))'%(de, vars[1], vars[0]))

    def solve_linear(self, eqns,vars):
        """
        Wraps maxima's linsolve.
        
        INPUT: eqns is a list of m strings, each rperesenting a linear
        question in m = n variables vars is a list of n strings, each
        representing a variable
        
        EXAMPLES::
        
            sage: eqns = ["x + z = y","2*a*x - y = 2*a^2","y - 2*z = 2"]    
            sage: vars = ["x","y","z"]                                      
            sage: maxima.solve_linear(eqns, vars)
            [x=a+1,y=2*a,z=a-1]
        """
        eqs = "["
        for i in range(len(eqns)):
            if i<len(eqns)-1:
                eqs = eqs + eqns[i]+","
            if  i==len(eqns)-1:
                eqs = eqs + eqns[i]+"]"
        vrs = "["
        for i in range(len(vars)):
            if i<len(vars)-1:
                vrs = vrs + vars[i]+","
            if  i==len(vars)-1:
                vrs = vrs + vars[i]+"]"
        return self('linsolve(%s, %s)'%(eqs, vrs))

    def unit_quadratic_integer(self, n):
        r"""
        Finds a unit of the ring of integers of the quadratic number field
        `\mathbb{Q}(\sqrt{n})`, `n>1`, using the qunit maxima
        command.
        
        EXAMPLES::
        
            sage: u = maxima.unit_quadratic_integer(101); u      
            a + 10
            sage: u.parent()                                       
            Number Field in a with defining polynomial x^2 - 101
            sage: u = maxima.unit_quadratic_integer(13)            
            sage: u                                                
            5*a + 18
            sage: u.parent()                                       
            Number Field in a with defining polynomial x^2 - 13
        """
        from sage.rings.all import QuadraticField, Integer
        # Take square-free part so sqrt(n) doesn't get simplified further by maxima
        # (The original version of this function would yield wrong answers if
        # n is not squarefree.)
        n = Integer(n).squarefree_part()  
        if n < 1:
            raise ValueError, "n (=%s) must be >= 1"%n
        s = repr(self('qunit(%s)'%n)).lower()
        r = re.compile('sqrt\(.*\)')
        s = r.sub('a', s)
        a = QuadraticField(n, 'a').gen()
        return eval(s)

    def plot_list(self, ptsx, ptsy, options=None):
        r"""
        Plots a curve determined by a sequence of points.
        
        INPUT:
        
        
        -  ``ptsx`` - [x1,...,xn], where the xi and yi are
           real,
        
        -  ``ptsy`` - [y1,...,yn]
        
        -  ``options`` - a string representing maxima plot2d
           options.
        
        
        The points are (x1,y1), (x2,y2), etc.
        
        This function requires maxima 5.9.2 or newer.
        
        .. note::

           More that 150 points can sometimes lead to the program
           hanging. Why?
        
        EXAMPLES::
        
            sage: zeta_ptsx = [ (pari(1/2 + i*I/10).zeta().real()).precision(1) for i in range (70,150)]  
            sage: zeta_ptsy = [ (pari(1/2 + i*I/10).zeta().imag()).precision(1) for i in range (70,150)]  
            sage: maxima.plot_list(zeta_ptsx, zeta_ptsy)         # not tested
            sage: opts='[gnuplot_preamble, "set nokey"], [gnuplot_term, ps], [gnuplot_out_file, "zeta.eps"]'
            sage: maxima.plot_list(zeta_ptsx, zeta_ptsy, opts)      # not tested
        """
        cmd = 'plot2d([discrete,%s, %s]'%(ptsx, ptsy)
        if options is None:
            cmd += ')'
        else:
            cmd += ', %s)'%options
        self(cmd)
        

    def plot_multilist(self, pts_list, options=None):
        r"""
        Plots a list of list of points pts_list=[pts1,pts2,...,ptsn],
        where each ptsi is of the form [[x1,y1],...,[xn,yn]] x's must be
        integers and y's reals options is a string representing maxima
        plot2d options.
        
        Requires maxima 5.9.2 at least.

        .. note::

           More that 150 points can sometimes lead to the program
           hanging.
        
        EXAMPLES::
        
            sage: xx = [ i/10.0 for i in range (-10,10)]
            sage: yy = [ i/10.0 for i in range (-10,10)]
            sage: x0 = [ 0 for i in range (-10,10)]
            sage: y0 = [ 0 for i in range (-10,10)]
            sage: zeta_ptsx1 = [ (pari(1/2+i*I/10).zeta().real()).precision(1) for i in range (10)]
            sage: zeta_ptsy1 = [ (pari(1/2+i*I/10).zeta().imag()).precision(1) for i in range (10)]
            sage: maxima.plot_multilist([[zeta_ptsx1,zeta_ptsy1],[xx,y0],[x0,yy]])       # not tested
            sage: zeta_ptsx1 = [ (pari(1/2+i*I/10).zeta().real()).precision(1) for i in range (10,150)]
            sage: zeta_ptsy1 = [ (pari(1/2+i*I/10).zeta().imag()).precision(1) for i in range (10,150)]
            sage: maxima.plot_multilist([[zeta_ptsx1,zeta_ptsy1],[xx,y0],[x0,yy]])      # not tested
            sage: opts='[gnuplot_preamble, "set nokey"]'                 
            sage: maxima.plot_multilist([[zeta_ptsx1,zeta_ptsy1],[xx,y0],[x0,yy]],opts)    # not tested
        """
        n = len(pts_list)
        cmd = '['
        for i in range(n):
            if i < n-1:
                cmd = cmd+'[discrete,'+str(pts_list[i][0])+','+str(pts_list[i][1])+'],'
            if i==n-1:
                cmd = cmd+'[discrete,'+str(pts_list[i][0])+','+str(pts_list[i][1])+']]'
        #print cmd
        if options is None:
            self('plot2d('+cmd+')')
        else:
            self('plot2d('+cmd+','+options+')')
    

class MaximaElement(ExpectElement):
    def __str__(self):
        """
        Printing an object explicitly gives ASCII art:
        
        EXAMPLES::
        
            sage: f = maxima('1/(x-1)^3'); f
            1/(x-1)^3
            sage: print f
                                                  1
                                               --------
                                                      3
                                               (x - 1)
        """
        return self.display2d(onscreen=False)

    def bool(self):
        """
        EXAMPLES::
        
            sage: maxima(0).bool()
            False
            sage: maxima(1).bool()
            True
        """
        P = self._check_valid()
        return P.eval('is(%s = 0);'%self.name()) == P._false_symbol()

    def __cmp__(self, other):
        """
        EXAMPLES::
        
            sage: a = maxima(1); b = maxima(2)
            sage: a == b
            False
            sage: a < b
            True
            sage: a > b
            False
            sage: b < a
            False
            sage: b > a
            True
        
        We can also compare more complicated object such as functions::
        
            sage: f = maxima('sin(x)'); g = maxima('cos(x)')
            sage: -f == g.diff('x')
            True
        """

        # thanks to David Joyner for telling me about using "is".
        P = self.parent()
        try:
            if P.eval("is (%s < %s)"%(self.name(), other.name())) == P._true_symbol():
                return -1
            elif P.eval("is (%s > %s)"%(self.name(), other.name())) == P._true_symbol():
                return 1
            elif P.eval("is (%s = %s)"%(self.name(), other.name())) == P._true_symbol():
                return 0
        except TypeError:
            pass
        return cmp(repr(self),repr(other))
                   # everything is supposed to be comparable in Python, so we define
                   # the comparison thus when no comparable in interfaced system.

    def _sage_(self):
        """
        Attempt to make a native Sage object out of this maxima object.
        This is useful for automatic coercions in addition to other
        things.
        
        EXAMPLES::
        
            sage: a = maxima('sqrt(2) + 2.5'); a
            sqrt(2)+2.5
            sage: b = a._sage_(); b
            sqrt(2) + 2.5
            sage: type(b)
            <class 'sage.calculus.calculus.SymbolicArithmetic'>
        
        We illustrate an automatic coercion::
        
            sage: c = b + sqrt(3); c
            sqrt(3) + sqrt(2) + 2.5
            sage: type(c)
            <class 'sage.calculus.calculus.SymbolicArithmetic'>
            sage: d = sqrt(3) + b; d
            sqrt(3) + sqrt(2) + 2.5
            sage: type(d)
            <class 'sage.calculus.calculus.SymbolicArithmetic'>
        """
        from sage.calculus.calculus import symbolic_expression_from_maxima_string
        #return symbolic_expression_from_maxima_string(self.name(), maxima=self.parent())
        return symbolic_expression_from_maxima_string(repr(self))

    def __complex__(self):
        """
        EXAMPLES::
        
            sage: complex(maxima('sqrt(-2)+1'))
            (1+1.4142135623730951j)
        """
        return complex(self._sage_())

    def _complex_mpfr_field_(self, C):
        """
        EXAMPLES::
        
            sage: CC(maxima('1+%i'))
             1.00000000000000 + 1.00000000000000*I
            sage: CC(maxima('2342.23482943872+234*%i'))
             2342.23482943872 + 234.000000000000*I
            sage: ComplexField(10)(maxima('2342.23482943872+234*%i'))
             2300. + 230.*I
            sage: ComplexField(200)(maxima('1+%i'))
            1.0000000000000000000000000000000000000000000000000000000000 + 1.0000000000000000000000000000000000000000000000000000000000*I
            sage: ComplexField(200)(maxima('sqrt(-2)'))
            1.4142135623730950488016887242096980785696718753769480731767*I
            sage: N(sqrt(-2), 200)
            1.4142135623730950488016887242096980785696718753769480731767*I
        """
        return C(self._sage_())

    def _mpfr_(self, R):
        """
        EXAMPLES::
        
            sage: RealField(100)(maxima('sqrt(2)+1'))
            2.4142135623730950488016887242
        """
        return R(self._sage_())

    def _complex_double_(self, C):
        """
        EXAMPLES::
        
            sage: CDF(maxima('sqrt(2)+1'))
            2.41421356237
        """
        return C(self._sage_())

    def _real_double_(self, R):
        """
        EXAMPLES::
        
            sage: RDF(maxima('sqrt(2)+1'))
            2.41421356237
        """
        return R(self._sage_())

    def real(self):
        """
        Return the real part of this maxima element.
        
        EXAMPLES::
        
            sage: maxima('2 + (2/3)*%i').real()
            2
        """
        return self.realpart()

    def imag(self):
        """
        Return the imaginary part of this maxima element.
        
        EXAMPLES::
        
            sage: maxima('2 + (2/3)*%i').imag()
            2/3
        """
        return self.imagpart()

    def numer(self):
        """
        Return numerical approximation to self as a Maxima object.
        
        EXAMPLES::
        
            sage: a = maxima('sqrt(2)').numer(); a
            1.414213562373095
            sage: type(a)
            <class 'sage.interfaces.maxima.MaximaElement'>
        """
        return self.comma('numer')

    def str(self):
        """
        Return string representation of this maxima object.
        
        EXAMPLES::
        
            sage: maxima('sqrt(2) + 1/3').str()
            'sqrt(2)+1/3'
        """
        P = self._check_valid()
        return P.get(self._name)

    def __repr__(self):
        """
        Return print representation of this object.
        
        EXAMPLES::
        
            sage: maxima('sqrt(2) + 1/3').__repr__()
            'sqrt(2)+1/3'
        """
        P = self._check_valid()
        try:
            return self.__repr
        except AttributeError:
            pass
        r = P.get(self._name)
        self.__repr = r
        return r

    def display2d(self, onscreen=True):
        """
        EXAMPLES::
        
            sage: F = maxima('x^5 - y^5').factor()  
            sage: F.display2d ()              
                                   4      3    2  2    3      4
                       - (y - x) (y  + x y  + x  y  + x  y + x )
        """
        self._check_valid()
        P = self.parent()
        with gc_disabled():
            s = P._eval_line('display2d : true; %s'%self.name(), reformat=False)
            P._eval_line('display2d : false;', reformat=False)

        r = P._output_prompt_re

        m = r.search(s)
        s = s[m.start():]
        i = s.find('\n')
        s = s[i+1 + len(P._display_prompt):]
        m = r.search(s)
        if not m is None:
            s = s[:m.start()] + ' '*(m.end() - m.start()) + s[m.end():].rstrip()
        # if ever want to dedent, see
        # http://mail.python.org/pipermail/python-list/2006-December/420033.html
        if onscreen:
            print s
        else:
            return s

    def diff(self, var='x', n=1):
        """
        Return the n-th derivative of self.
        
        INPUT:
        
        
        -  ``var`` - variable (default: 'x')
        
        -  ``n`` - integer (default: 1)
        
        
        OUTPUT: n-th derivative of self with respect to the variable var
        
        EXAMPLES::
        
            sage: f = maxima('x^2')                          
            sage: f.diff()                                   
            2*x
            sage: f.diff('x')                                
            2*x
            sage: f.diff('x', 2)                             
            2
            sage: maxima('sin(x^2)').diff('x',4)
            16*x^4*sin(x^2)-12*sin(x^2)-48*x^2*cos(x^2)
        
        ::
        
            sage: f = maxima('x^2 + 17*y^2')                 
            sage: f.diff('x')
            34*y*'diff(y,x,1)+2*x
            sage: f.diff('y')                                
            34*y
        """
        return ExpectElement.__getattr__(self, 'diff')(var, n)

    derivative = diff

    def nintegral(self, var='x', a=0, b=1,
                  desired_relative_error='1e-8',
                  maximum_num_subintervals=200):
        r"""
        Return a numerical approximation to the integral of self from a to
        b.
        
        INPUT:
        
        
        -  ``var`` - variable to integrate with respect to
        
        -  ``a`` - lower endpoint of integration
        
        -  ``b`` - upper endpoint of integration
        
        -  ``desired_relative_error`` - (default: '1e-8') the
           desired relative error
        
        -  ``maximum_num_subintervals`` - (default: 200)
           maxima number of subintervals
        
        
        OUTPUT:
        
        
        -  approximation to the integral
        
        -  estimated absolute error of the
           approximation
        
        -  the number of integrand evaluations
        
        -  an error code:
        
            -  ``0`` - no problems were encountered

            -  ``1`` - too many subintervals were done

            -  ``2`` - excessive roundoff error

            -  ``3`` - extremely bad integrand behavior

            -  ``4`` - failed to converge

            -  ``5`` - integral is probably divergent or slowly convergent

            -  ``6`` - the input is invalid
        
        
        EXAMPLES::
        
            sage: maxima('exp(-sqrt(x))').nintegral('x',0,1)
            (.5284822353142306, 4.163314137883845E-11, 231, 0)
        
        Note that GP also does numerical integration, and can do so to very
        high precision very quickly::
        
            sage: gp('intnum(x=0,1,exp(-sqrt(x)))')            
            0.5284822353142307136179049194             # 32-bit
            0.52848223531423071361790491935415653021   # 64-bit
            sage: _ = gp.set_precision(80)
            sage: gp('intnum(x=0,1,exp(-sqrt(x)))')
            0.52848223531423071361790491935415653021675547587292866196865279321015401702040079
        """
        from sage.rings.all import Integer
        v = self.quad_qags(var, a, b, epsrel=desired_relative_error,
                           limit=maximum_num_subintervals)
        return v[0], v[1], Integer(v[2]), Integer(v[3])

    def integral(self, var='x', min=None, max=None):
        r"""
        Return the integral of self with respect to the variable x.
        
        INPUT:
        
        
        -  ``var`` - variable
        
        -  ``min`` - default: None
        
        -  ``max`` - default: None
        
        
        Returns the definite integral if xmin is not None, otherwise
        returns an indefinite integral.
        
        EXAMPLES::
        
            sage: maxima('x^2+1').integral()                   
            x^3/3+x
            sage: maxima('x^2+ 1 + y^2').integral('y')         
            y^3/3+x^2*y+y
            sage: maxima('x / (x^2+1)').integral()             
            log(x^2+1)/2
            sage: maxima('1/(x^2+1)').integral()               
            atan(x)
            sage: maxima('1/(x^2+1)').integral('x', 0, infinity) 
            %pi/2
            sage: maxima('x/(x^2+1)').integral('x', -1, 1)     
            0
        
        ::
        
            sage: f = maxima('exp(x^2)').integral('x',0,1); f   
            -sqrt(%pi)*%i*erf(%i)/2
            sage: f.numer()         # I wonder how to get a real number (~1.463)??
            -.8862269254527579*%i*erf(%i)
        """
        I = ExpectElement.__getattr__(self, 'integrate')
        if min is None:
            return I(var)
        else:
            if max is None:
                raise ValueError, "neither or both of min/max must be specified."
            return I(var, min, max)

    integrate = integral

    def __float__(self):
        """
        Return floating point version of this maxima element.
        
        EXAMPLES::
        
            sage: float(maxima("3.14"))
            3.1400000000000001
            sage: float(maxima("1.7e+17"))
            1.7e+17
            sage: float(maxima("1.7e-17"))
            1.6999999999999999e-17
        """
        try:
            return float(repr(self.numer()))
        except ValueError:
            raise TypeError, "unable to coerce '%s' to float"%repr(self)

    def __len__(self):
        """
        Return the length of a list.
        
        EXAMPLES::
        
            sage: v = maxima('create_list(x^i,i,0,5)')         
            sage: len(v)                                       
            6
        """
        P = self._check_valid()        
        return int(P.eval('length(%s)'%self.name()))

    def dot(self, other):
        """
        Implements the notation self . other.
        
        EXAMPLES::
        
            sage: A = maxima('matrix ([a1],[a2])')
            sage: B = maxima('matrix ([b1, b2])')
            sage: A.dot(B)
            matrix([a1*b1,a1*b2],[a2*b1,a2*b2])
        """
        P = self._check_valid()
        Q = P(other)
        return P('%s . %s'%(self.name(), Q.name()))

    def __getitem__(self, n):
        r"""
        Return the n-th element of this list.
        
        .. note::

           Lists are 0-based when accessed via the Sage interface, not
           1-based as they are in the Maxima interpreter.
        
        EXAMPLES::
        
            sage: v = maxima('create_list(i*x^i,i,0,5)'); v    
            [0,x,2*x^2,3*x^3,4*x^4,5*x^5]
            sage: v[3]                                         
            3*x^3
            sage: v[0]                                           
            0
            sage: v[10]                                          
            Traceback (most recent call last):
            ...
            IndexError: n = (10) must be between 0 and 5
        """
        n = int(n)
        if n < 0 or n >= len(self):
            raise IndexError, "n = (%s) must be between %s and %s"%(n, 0, len(self)-1)
        # If you change the n+1 to n below, better change __iter__ as well.
        return ExpectElement.__getitem__(self, n+1)

    def __iter__(self):
        """
        EXAMPLE::
        
            sage: v = maxima('create_list(i*x^i,i,0,5)')
            sage: list(v)
            [0, x, 2*x^2, 3*x^3, 4*x^4, 5*x^5]
        """
        for i in range(len(self)):
            yield self[i]

    def subst(self, val):
        """
        Substitute a value or several values into this Maxima object.
        
        EXAMPLES::
        
            sage: maxima('a^2 + 3*a + b').subst('b=2')
            a^2+3*a+2
            sage: maxima('a^2 + 3*a + b').subst('a=17')
            b+340
            sage: maxima('a^2 + 3*a + b').subst('a=17, b=2')
            342
        """
        return self.comma(val)

    def comma(self, args):
        """
        Form the expression that would be written 'self, args' in Maxima.
        
        EXAMPLES::
        
            sage: maxima('sqrt(2) + I').comma('numer')
            I+1.414213562373095
            sage: maxima('sqrt(2) + I*a').comma('a=5')
            5*I+sqrt(2)
        """
        self._check_valid()
        P = self.parent()
        return P('%s, %s'%(self.name(), args))

    def _latex_(self):
        """
        Return Latex representation of this Maxima object.
        
        This calls the tex command in Maxima, then does a little
        post-processing to fix bugs in the resulting Maxima output.
        
        EXAMPLES::
        
            sage: maxima('sqrt(2) + 1/3 + asin(5)')._latex_()
            '\\sin^{-1}\\cdot5+\\sqrt{2}+{{1}\\over{3}}'

            sage: y,d = var('y,d')
            sage: latex(maxima(derivative(ceil(x*y*d), d,x,x,y)))
            {{{\it \partial}^4}\over{{\it \partial}\,d\,{\it \partial}\,x^2\,  {\it \partial}\,y}}\,\left \lceil d\,x\,y \right \rceil

            sage: latex(maxima(d/(d-2)))
            {{d}\over{d-2}}
        """
        self._check_valid()
        P = self.parent()
        s = P._eval_line('tex(%s);'%self.name(), reformat=False)
        if not '$$' in s:
            raise RuntimeError, "Error texing maxima object."
        i = s.find('$$')
        j = s.rfind('$$')
        s = s[i+2:j]
        s = multiple_replace({'\r\n':' ',
                              '\\%':'', 
                              '\\arcsin ':'\\sin^{-1} ',
                              '\\arccos ':'\\cos^{-1} ',
                              '\\arctan ':'\\tan^{-1} '}, s)

        # Fix a maxima bug, which gives a latex representation of multiplying
        # two numbers as a single space. This was really bad when 2*17^(1/3)
        # gets TeXed as '2 17^{\frac{1}{3}}'
        #
        # This regex matches a string of spaces preceeded by either a '}', a
        # decimal digit, or a ')', and followed by a decimal digit. The spaces
        # get replaced by a '\cdot'.
        s = re.sub(r'(?<=[})\d]) +(?=\d)', '\cdot', s)

        return s

    def trait_names(self, verbose=False):
        """
        Return all Maxima commands, which is useful for tab completion.
        
        EXAMPLES::
        
            sage: m = maxima(2)
            sage: 'gcd' in m.trait_names()
            True
        """
        return self.parent().trait_names(verbose=False)

    def _matrix_(self, R):
        r"""
        If self is a Maxima matrix, return the corresponding Sage matrix
        over the Sage ring `R`.
        
        This may or may not work depending in how complicated the entries
        of self are! It only works if the entries of self can be coerced as
        strings to produce meaningful elements of `R`.
        
        EXAMPLES::
        
            sage: _ = maxima.eval("f[i,j] := i/j")              
            sage: A = maxima('genmatrix(f,4,4)'); A             
            matrix([1,1/2,1/3,1/4],[2,1,2/3,1/2],[3,3/2,1,3/4],[4,2,4/3,1])
            sage: A._matrix_(QQ)                                
            [  1 1/2 1/3 1/4]
            [  2   1 2/3 1/2]
            [  3 3/2   1 3/4]
            [  4   2 4/3   1]
        
        You can also use the ``matrix`` command (which is
        defined in ``sage.misc.functional``)::
        
            sage: matrix(QQ, A)
            [  1 1/2 1/3 1/4]
            [  2   1 2/3 1/2]
            [  3 3/2   1 3/4]
            [  4   2 4/3   1]
        """
        from sage.matrix.all import MatrixSpace
        self._check_valid()
        P = self.parent()
        nrows = int(P.eval('length(%s)'%self.name()))
        if nrows == 0:
            return MatrixSpace(R, 0, 0)(0)
        ncols = int(P.eval('length(%s[1])'%self.name()))
        M = MatrixSpace(R, nrows, ncols)
        s = self.str().replace('matrix','').replace(',',"','").\
            replace("]','[","','").replace('([',"['").replace('])',"']")
        s = eval(s)
        return M([R(x) for x in s])
        
    def partial_fraction_decomposition(self, var='x'):
        """
        Return the partial fraction decomposition of self with respect to
        the variable var.
        
        EXAMPLES::
        
            sage: f = maxima('1/((1+x)*(x-1))')            
            sage: f.partial_fraction_decomposition('x')    
            1/(2*(x-1))-1/(2*(x+1))
            sage: print f.partial_fraction_decomposition('x')
                                 1           1
                             --------- - ---------
                             2 (x - 1)   2 (x + 1)
        """
        return self.partfrac(var)

    def _operation(self, operation, right):
        r"""
        Note that right's parent should already be Maxima since this should
        be called after coercion has been performed.
        
        If right is a ``MaximaFunction``, then we convert
        ``self`` to a ``MaximaFunction`` that takes
        no arguments, and let the
        ``MaximaFunction._operation`` code handle everything
        from there.
        
        EXAMPLES::
        
            sage: f = maxima.cos(x)
            sage: f._operation("+", f)
            2*cos(x)
        """
        P = self._check_valid()

        if isinstance(right, MaximaFunction):
            fself = P.function('', repr(self))
            return fself._operation(operation, right)

        try:
            return P.new('%s %s %s'%(self._name, operation, right._name))
        except Exception, msg:
            raise TypeError, msg


        
class MaximaFunctionElement(FunctionElement):
    def _sage_doc_(self):
        """
        EXAMPLES::
        
            sage: m = maxima(4)
            sage: m.gcd._sage_doc_()
            -- Function: gcd (<p_1>, <p_2>, <x_1>, ...)
            ...
        """
        return self._obj.parent().help(self._name)

class MaximaExpectFunction(ExpectFunction):
    def _sage_doc_(self):
        """
        EXAMPLES::
        
            sage: maxima.gcd._sage_doc_()
            -- Function: gcd (<p_1>, <p_2>, <x_1>, ...)
            ...
        """
        M = self._parent
        return M.help(self._name)


class MaximaFunction(MaximaElement):
    def __init__(self, parent, name, defn, args, latex):
        """
        EXAMPLES::
        
            sage: f = maxima.function('x,y','sin(x+y)')
            sage: f == loads(dumps(f))
            True
        """
        MaximaElement.__init__(self, parent, name, is_name=True)
        self.__defn = defn
        self.__args = args
        self.__latex = latex

    def __reduce__(self):
        """
        EXAMPLES::
        
            sage: f = maxima.function('x,y','sin(x+y)')
            sage: f.__reduce__()
            (<function reduce_load_Maxima_function at 0x...>,
             (Maxima, 'sin(x+y)', 'x,y', None))
        """
        return reduce_load_Maxima_function, (self.parent(), self.__defn, self.__args, self.__latex)
        
    def __call__(self, *x):
        """
        EXAMPLES::
        
            sage: f = maxima.function('x,y','sin(x+y)')
            sage: f(1,2)
            sin(3)
            sage: f(x,x)
            sin(2*x)
        """
        P = self._check_valid()
        if len(x) == 1:
            x = '(%s)'%x
        return P('%s%s'%(self.name(), x))

    def __repr__(self):
        """
        EXAMPLES::
        
            sage: f = maxima.function('x,y','sin(x+y)')
            sage: repr(f)
            'sin(x+y)'
        """
        return self.definition()

    def _latex_(self):
        """
        EXAMPLES::
        
            sage: f = maxima.function('x,y','sin(x+y)')
            sage: latex(f)
            \mathrm{sin(x+y)}
        """
        if self.__latex is None:
            return r'\mathrm{%s}'%self.__defn
        else:
            return self.__latex

    def arguments(self, split=True):
        r"""
        Returns the arguments of this Maxima function.
        
        EXAMPLES::
        
            sage: f = maxima.function('x,y','sin(x+y)')
            sage: f.arguments()
            ['x', 'y']
            sage: f.arguments(split=False)
            'x,y'
            sage: f = maxima.function('', 'sin(x)')
            sage: f.arguments()
            []
        """
        if split:
            return self.__args.split(',') if self.__args != '' else []
        else:
            return self.__args

    def definition(self):
        """
        Returns the definition of this Maxima function as a string.
        
        EXAMPLES::
        
            sage: f = maxima.function('x,y','sin(x+y)')
            sage: f.definition()
            'sin(x+y)'
        """
        return self.__defn

    def integral(self, var):
        """
        Returns the integral of self with respect to the variable var.
        
        Note that integrate is an alias of integral.
        
        EXAMPLES::
        
            sage: x,y = var('x,y')
            sage: f = maxima.function('x','sin(x)')
            sage: f.integral(x)
            -cos(x)
            sage: f.integral(y)
            sin(x)*y
        """
        var = str(var)
        P = self._check_valid()
        f = P('integrate(%s(%s), %s)'%(self.name(), self.arguments(split=False), var))

        args = self.arguments()
        if var not in args:
            args.append(var)
        return P.function(",".join(args), repr(f))

    integrate = integral

    def _operation(self, operation, f=None):
        r"""
        This is a utility function which factors out much of the
        commonality used in the arithmetic operations for
        ``MaximaFunctions``.
        
        INPUT:
        
        
        -  ``operation`` - A string representing the operation
           being performed. For example, '\*', or '1/'.
        
        -  ``f`` - The other operand. If f is
           ``None``, than the operation is assumed to be unary
           rather than binary.
        
        
        EXAMPLES::
        
            sage: f = maxima.function('x,y','sin(x+y)')
            sage: f._operation("+", f)
            2*sin(y+x)
            sage: f._operation("+", 2)
            sin(y+x)+2
            sage: f._operation('-')
            -sin(y+x)
            sage: f._operation('1/')
            1/sin(y+x)
        """
        P = self._check_valid()
        if isinstance(f, MaximaFunction):
            tmp = list(sorted(set(self.arguments() + f.arguments())))
            args = ','.join(tmp)
            defn = "(%s)%s(%s)"%(self.definition(), operation, f.definition())
        elif f is None:
            args = self.arguments(split=False)
            defn = "%s(%s)"%(operation, self.definition())
        else:
            args = self.arguments(split=False)
            defn = "(%s)%s(%s)"%(self.definition(), operation, repr(f))

        return P.function(args,P.eval(defn))

    def _add_(self, f):
        """
        MaximaFunction as left summand.
        
        EXAMPLES::
        
            sage: x,y = var('x,y')
            sage: f = maxima.function('x','sin(x)')
            sage: g = maxima.function('x','-cos(x)')
            sage: f+g
            sin(x)-cos(x)
            sage: f+3
            sin(x)+3
        
        ::
        
            sage: (f+maxima.cos(x))(2)
            sin(2)+cos(2)
            sage: (f+maxima.cos(y)) # This is a function with only ONE argument!
            cos(y)+sin(x)  
            sage: (f+maxima.cos(y))(2)
            cos(y)+sin(2)
        
        ::
        
            sage: f = maxima.function('x','sin(x)')
            sage: g = -maxima.cos(x)
            sage: g+f
            sin(x)-cos(x)
            sage: (g+f)(2) # The sum IS a function
            sin(2)-cos(2)  
            sage: 2+f
            sin(x)+2
        """
        return self._operation("+", f)

    def _sub_(self, f):
        r"""
        ``MaximaFunction`` as minuend.
        
        EXAMPLES::
        
            sage: x,y = var('x,y')
            sage: f = maxima.function('x','sin(x)')
            sage: g = -maxima.cos(x) # not a function
            sage: f-g
            sin(x)+cos(x)
            sage: (f-g)(2)
            sin(2)+cos(2) 
            sage: (f-maxima.cos(y)) # This function only has the argument x!
            sin(x)-cos(y)
            sage: _(2)
            sin(2)-cos(y) 
        
        ::
        
            sage: g-f
            -sin(x)-cos(x)
        """
        return self._operation("-", f)
        
    def _mul_(self, f):
        r"""
        ``MaximaFunction`` as left factor.
        
        EXAMPLES::
        
            sage: f = maxima.function('x','sin(x)')
            sage: g = maxima('-cos(x)') # not a function!
            sage: f*g
            -cos(x)*sin(x)
            sage: _(2)
            -cos(2)*sin(2)
        
        ::
        
            sage: f = maxima.function('x','sin(x)')
            sage: g = maxima('-cos(x)')
            sage: g*f
            -cos(x)*sin(x)
            sage: _(2)
            -cos(2)*sin(2)
            sage: 2*f
            2*sin(x)
        """
        return self._operation("*", f)

    def _div_(self, f):
        r"""
        ``MaximaFunction`` as dividend.
        
        EXAMPLES::
        
            sage: f=maxima.function('x','sin(x)')
            sage: g=maxima('-cos(x)')
            sage: f/g
            -sin(x)/cos(x)
            sage: _(2)
            -sin(2)/cos(2)
        
        ::
        
            sage: f=maxima.function('x','sin(x)')
            sage: g=maxima('-cos(x)')
            sage: g/f
            -cos(x)/sin(x)
            sage: _(2)
            -cos(2)/sin(2)
            sage: 2/f
            2/sin(x)
        """
        return self._operation("/", f)

    def __neg__(self):
        r"""
        Additive inverse of a ``MaximaFunction``.
        
        EXAMPLES::
        
            sage: f=maxima.function('x','sin(x)')
            sage: -f
            -sin(x)
        """
        return self._operation('-')

    def __inv__(self):
        r"""
        Multiplicative inverse of a ``MaximaFunction``.
        
        EXAMPLES::
        
            sage: f = maxima.function('x','sin(x)')
            sage: ~f
            1/sin(x)
        """
        return self._operation('1/')

    def __pow__(self,f):
        r"""
        ``MaximaFunction`` raised to some power.
        
        EXAMPLES::
        
            sage: f=maxima.function('x','sin(x)')
            sage: g=maxima('-cos(x)')
            sage: f^g
            1/sin(x)^cos(x)
        
        ::
        
            sage: f=maxima.function('x','sin(x)')
            sage: g=maxima('-cos(x)') # not a function
            sage: g^f
            (-cos(x))^sin(x)
        """
        return self._operation("^", f)


def is_MaximaElement(x):
    """
    Returns True if x is of type MaximaElement.
    
    EXAMPLES::
    
        sage: from sage.interfaces.maxima import is_MaximaElement
        sage: m = maxima(1)
        sage: is_MaximaElement(m)
        True
        sage: is_MaximaElement(1)
        False
    """
    return isinstance(x, MaximaElement)

# An instance
maxima = Maxima(script_subdirectory=None)

def reduce_load_Maxima():
    """
    EXAMPLES::
    
        sage: from sage.interfaces.maxima import reduce_load_Maxima
        sage: reduce_load_Maxima()
        Maxima
    """
    return maxima

def reduce_load_Maxima_function(parent, defn, args, latex):
    return parent.function(args, defn, defn, latex)
    

import os
def maxima_console():
    """
    Spawn a new Maxima command-line session.
    
    EXAMPLES::
    
        sage: from sage.interfaces.maxima import maxima_console
        sage: maxima_console()                    # not tested
        Maxima 5.16.3 http://maxima.sourceforge.net
        ...
    """
    os.system('maxima')

def maxima_version():
    """
    EXAMPLES::
    
        sage: from sage.interfaces.maxima import maxima_version
        sage: maxima_version()
        '5.16.3'
    """
    return os.popen('maxima --version').read().split()[1]

def __doctest_cleanup():
    import sage.interfaces.quit
    sage.interfaces.quit.expect_quitall()


