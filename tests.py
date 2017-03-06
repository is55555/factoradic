# >>> compatibility with Python 3
from __future__ import print_function, unicode_literals
import sys
if sys.version_info < (3,):
    integer_types = (int, long,)
    # from itertools import imap
    from builtins import range as range3  # requires package future in Python2 (unfortunate, but there's no better way)
else:
    integer_types = (int,)
    # imap = map
    range3 = range
    unicode = str
# I use the names imap and range3 to make it explicit for Python2 programmers and avoid confusion
# <<< compatibility with Python 3

from factoradic import Factoradic
import unittest
import functools
import time
import random


PROF_DATA = {}


def profile_time(fn):
    @functools.wraps(fn)
    def with_profiling(*args, **kwargs):
        start_time = time.time()

        ret = fn(*args, **kwargs)

        elapsed_time = time.time() - start_time

        if fn.__name__ not in PROF_DATA:
            PROF_DATA[fn.__name__] = {'count': 0, 'times': [], 'max': -1, 'avg': -1}
        PROF_DATA[fn.__name__]['count'] += 1
        PROF_DATA[fn.__name__]['times'].append(elapsed_time)

        return ret

    return with_profiling


def calc_prof_data():
    for fname, data in PROF_DATA.items():
        max_time = max(data['times'])
        avg_time = sum(data['times']) / len(data['times'])
        #print "Function %s called %d times. " % (fname, data['count']),
        #print 'Execution time max: %.3f, average: %.3f' % (max_time, avg_time)
        PROF_DATA[fname]['max'] = max_time
        PROF_DATA[fname]['avg'] = avg_time

def print_prof_data():
    for fname, data in PROF_DATA.items():
        max_time = PROF_DATA[fname]['max']
        avg_time = PROF_DATA[fname]['avg']
        print("Function %s called %d times. " % (fname, data['count']),)
        print('Execution time max: %.3f, average: %.3f' % (max_time, avg_time))

def calc_and_print_prof_data():
    for fname, data in PROF_DATA.items():
        max_time = max(data['times'])
        avg_time = sum(data['times']) / len(data['times'])
        print("Function %s called %d times. " % (fname, data['count']),)
        print('Execution time max: %.3f, average: %.3f' % (max_time, avg_time))
        PROF_DATA[fname]['max'] = max_time
        PROF_DATA[fname]['avg'] = avg_time


def clear_profile_time():
    global PROF_DATA
    PROF_DATA = {}



class TestCase_factoradic(unittest.TestCase):
    def setUp(self):
        print("setUp")

    def tearDown(self):
        print("tearDown")
        clear_profile_time()

    def test_misc(self):
        # Wikipedia example: 463 == factoradic_to_number(string_to_factoradic("341010"))
        print(463, '<=> ', Factoradic.factoradic_to_number(Factoradic.string_to_factoradic("341010")))
        print("factoradic", Factoradic.string_to_factoradic("341010"),
              "<=> factoradic", Factoradic.number_to_factoradic(463))
        assert 463 == Factoradic.factoradic_to_number(Factoradic.string_to_factoradic("341010")), "test case ERROR"
        assert Factoradic.string_to_factoradic("341010") == Factoradic.number_to_factoradic(463), "test case ERROR"

        assert Factoradic.number_to_factoradic(0) == [0], "test case ERROR (0)"
        assert Factoradic.number_to_factoradic(1) == [1, 0], "test case ERROR (1)"
        assert Factoradic.number_to_factoradic(2) == [1, 0, 0], "test case ERROR (2)"
        assert Factoradic.number_to_factoradic(5) == [2, 1, 0], "test case ERROR (5)"
        assert Factoradic.number_to_factoradic(6) == [1, 0, 0, 0], "test case ERROR (6)"  # this is an edge case...
        # ... for carry-over.
        assert Factoradic.number_to_factoradic(7) == [1, 0, 1, 0], "test case ERROR (7)"

        fj = Factoradic.number_to_factoradic(0)
        for j in range3(0, 720):
            # print j, number_to_factoradic(j), "fj", fj
            assert Factoradic.number_to_factoradic(j) == fj, "ERROR factoradics don't match"
            fj = Factoradic.next_factoradic(fj)
            assert Factoradic.number_to_factoradic(j) != fj, "ERROR consecutive factoradics shouldn't match"

        for j in range3(20):
            elements = list(range3(3))
            # factoradic = Factoradic.padded_to_length_s(number_to_factoradic(j), len(elements)) # not required (visual)
            factoradic = Factoradic.number_to_factoradic(j)
            # print j, factoradic, generate_permutation_from_factoradic_inplace(factoradic, elements)
                #  this also works...
                # ... because we regenerate "elements" every loop, but generally we don't want to modify parameters
            print(j, factoradic, Factoradic.generate_permutation_from_factoradic(factoradic, elements))

        fx = [463, 0]
        print(fx, "cascaded =>", Factoradic.cascade_factoradic_digits(fx))
        fx = [9999999999, 0]
        print(fx, "cascaded =>", Factoradic.cascade_factoradic_digits(fx))

        Factoradic.cascade_factoradic_digits_inplace(fx)
        print(fx, "to number =>", Factoradic.factoradic_to_number(fx))
        print("341010 to number =>", Factoradic.factoradic_to_number(Factoradic.string_to_factoradic("341010")))

        print(9999999999, "to factoradic =>", Factoradic.number_to_factoradic(9999999999))

        # example found online, with a big Mersenne prime
        N = (2 ** 607) - 1
        print("N = (2 ** 607) - 1 # =>", N)
        n_f = Factoradic.number_to_factoradic(N)
        print("factoradic(N) =>", n_f)
        print("length of factoradic(N):", len(n_f))

        perm_n_f = Factoradic.generate_permutation_from_factoradic(n_f, list(range3(len(n_f))))

        print("permutation number factoradic(N) of the ordered list from [0, 1, 2, ... 112] =>", perm_n_f)
        # observation: by definition, each element of perm_n_f is >= to n_f for every position, ...
        # ... for the canonical [0...len(n_f)] list of elements

        print("same with a Factoradic object:")
        f_1 = Factoradic(N)
        print(N)
        print("->", f_1)
        print(f_1.permutation_inplace(list(range3(f_1.length()))))

        print("-----")

        f_2 = Factoradic("341010")
        print("Factoradic(\"341010\") ->", f_2, '->', f_2.to_number())


def suite():
    my_suite = unittest.TestSuite()
    my_suite.addTest(unittest.makeSuite(TestCase_factoradic, 'tests for Factoradic'))
    return my_suite


if __name__ == '__main__':
    #unittest.TestSuite(suite())
    unittest.main()