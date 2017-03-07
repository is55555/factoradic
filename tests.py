# >>> compatibility with Python 3
from __future__ import print_function, unicode_literals
import sys
if sys.version_info < (3,):  # pragma: no cover
    integer_types = (int, long,)
    # from itertools import imap
    from builtins import range as range3  # requires package future in Python2 (unfortunate, but there's no better way)
else:  # pragma: no cover
    integer_types = (int,)
    # imap = map
    range3 = range
    unicode = str
# I use the names imap and range3 to make it explicit for Python2 programmers and avoid confusion
# <<< compatibility with Python 3

from factoradic import Factoradic, FactoradicException
import unittest
import functools
import time
import random


# >>> profiling
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
        PROF_DATA[fname]['max'] = max_time
        PROF_DATA[fname]['avg'] = avg_time


def print_prof_data():
    for fname, data in PROF_DATA.items():
        max_time = PROF_DATA[fname]['max']
        avg_time = PROF_DATA[fname]['avg']
        print('\nFunction %s called %d times. Execution time max: %.3f, average: %.3f.' % (fname, data['count'],
                                                                                        max_time, avg_time),)


def clear_profile_time():
    global PROF_DATA
    PROF_DATA = {}
# <<< profiling


class TestCaseFactoradicLowlevel(unittest.TestCase):
    def setUp(self):
        print("----- setUp    -----")

    def tearDown(self):
        print("----- tearDown -----")
        clear_profile_time()

    def test_known_cases_and_conversions(self):
        # Wikipedia example: 463 == factoradic_to_number(string_to_factoradic("341010"))
        assert 463 == Factoradic.factoradic_to_number(Factoradic.string_to_factoradic("341010")), "test case ERROR 463"
        assert Factoradic.string_to_factoradic("341010") == Factoradic.number_to_factoradic(463), "test case ERROR 463"
        assert Factoradic.number_to_factoradic(0) == [0], "test case ERROR (0)"
        assert Factoradic.number_to_factoradic(1) == [1, 0], "test case ERROR (1)"
        assert Factoradic.number_to_factoradic(2) == [1, 0, 0], "test case ERROR (2)"
        assert Factoradic.number_to_factoradic(5) == [2, 1, 0], "test case ERROR (5)"
        assert Factoradic.number_to_factoradic(6) == [1, 0, 0, 0], "test case ERROR (6)"  # this is an edge case...
        # ... for carry-over.
        assert Factoradic.number_to_factoradic(7) == [1, 0, 1, 0], "test case ERROR (7)"

    def test_factoradic_iteration(self):
        f_j = Factoradic.number_to_factoradic(0)
        for j in range3(0, 720):
            # print(j, number_to_factoradic(j), "f_j", f_j)
            assert Factoradic.number_to_factoradic(j) == f_j, "ERROR factoradics don't match"
            f_j = Factoradic.next_factoradic(f_j)
            assert Factoradic.number_to_factoradic(j) != f_j, "ERROR consecutive factoradics shouldn't match"

    def test_factoradic_iteration_timed(self):
        start = (2 ** 607) - 1
        start **= 20  # we need a really large number to even get significant times in a modern computer
        end   = start + 100  # avg: 0.011 per iteration in my comp. for number_to_factoradic, 0.001 for next_factoradic
        f_j = Factoradic.number_to_factoradic(start)
        profiled_number_to_factoradic = profile_time(Factoradic.number_to_factoradic)
        profiled_next_factoradic = profile_time(Factoradic.next_factoradic)

        for j in range3(start, end):
            # print(j, number_to_factoradic(j), "f_j", f_j)
            assert profiled_number_to_factoradic(j) == f_j, "ERROR factoradics don't match"
            f_j = profiled_next_factoradic(f_j)
            assert profiled_number_to_factoradic(j) != f_j, "ERROR consecutive factoradics shouldn't match"

        calc_prof_data()
        print_prof_data()


    def test_factoradic_iterate_permutations(self):
        for j in range3(20):
            elements = list(range3(3))
            # factoradic = Factoradic.padded_to_length_s(number_to_factoradic(j), len(elements)) # not required (visual)
            factoradic = Factoradic.number_to_factoradic(j)
            # print j, factoradic, generate_permutation_from_factoradic_inplace(factoradic, elements)
                #  this also works...
                # ... because we regenerate "elements" every loop, but generally we don't want to modify parameters
            print(j, factoradic, Factoradic.generate_permutation_from_factoradic(factoradic, elements))

    def test_cascading(self):
        fx = [463, 0]
        cascaded_fx = Factoradic.cascade_factoradic_digits(fx)
        print(fx, "cascaded =>", cascaded_fx)
        assert str(cascaded_fx) == u"[3, 4, 1, 0, 1, 0]"

        fx = [9999999999, 0]
        cascaded_fx = Factoradic.cascade_factoradic_digits(fx)
        print(fx, "cascaded =>", cascaded_fx)
        assert str(cascaded_fx) == u"[1, 7, 10, 5, 7, 2, 6, 6, 5, 1, 2, 1, 1, 0]"

        Factoradic.cascade_factoradic_digits_inplace(fx)
        print(fx, "to number =>", Factoradic.factoradic_to_number(fx))

    def test_large_permutation(self):
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

        assert len(n_f) == 113

        resL = "[2L, 77L, 30L, 88L, 71L, 102L, 97L, 70L, 4L, 12L, 75L, 71L, 27L, 9L, 91L, 43L, 75L, 58L, 30L, 73L,"
        resL+= " 10L, 11L, 68L, 33L, 77L, 79L, 50L, 80L, 41L, 77L, 48L, 5L, 32L, 78L, 25L, 74L, 0L, 9L, 49L, 3L, 43L,"
        resL+= " 14L, 6L, 20L, 2L, 6L, 61L, 14L, 29L, 7L, 37L, 41L, 5L, 15L, 30L, 54L, 26L, 0L, 41L, 19L, 29L, 50L, 6L,"
        resL+= " 6L, 2L, 25L, 6L, 8L, 44L, 10L, 26L, 13L, 16L, 0L, 14L, 4L, 5L, 24L, 24L, 30L, 22L, 6L, 6L, 29L, 10L,"
        resL+= " 24L, 12L, 23L, 3L, 20L, 15L, 20L, 16L, 11L, 12L, 7L, 2L, 15L, 10L, 5L, 5L, 8L, 6L, 7L, 2L, 0L, 0L,"
        resL+= " 1L, 0L, 1L, 0L, 1L, 0L]"

        res =  "[2, 77, 30, 88, 71, 102, 97, 70, 4, 12, 75, 71, 27, 9, 91, 43, 75, 58, 30, 73,"
        res += " 10, 11, 68, 33, 77, 79, 50, 80, 41, 77, 48, 5, 32, 78, 25, 74, 0, 9, 49, 3, 43,"
        res += " 14, 6, 20, 2, 6, 61, 14, 29, 7, 37, 41, 5, 15, 30, 54, 26, 0, 41, 19, 29, 50, 6,"
        res += " 6, 2, 25, 6, 8, 44, 10, 26, 13, 16, 0, 14, 4, 5, 24, 24, 30, 22, 6, 6, 29, 10,"
        res += " 24, 12, 23, 3, 20, 15, 20, 16, 11, 12, 7, 2, 15, 10, 5, 5, 8, 6, 7, 2, 0, 0,"
        res += " 1, 0, 1, 0, 1, 0]"

        assert str(n_f) == resL or str(n_f) == res # annoying Python2-3 compatibility glitch workaround

        perm_str  = "[2, 78, 31, 91, 73, 107, 102, 72, 5, 14, 82, 77, 30, 11, 104, 49, 87, 65, 36, 88, 13, 16, 84, 42,"
        perm_str += " 98, 101, 61, 106, 52, 103, 60, 7, 43, 111, 34, 108, 0, 17, 69, 6, 63, 24, 12, 35, 4, 18, 99, 28,"
        perm_str += " 53, 20, 67, 75, 15, 37, 58, 105, 54, 1, 85, 45, 64, 110, 22, 23, 9, 62, 26, 32, 112, 39, 74, 46,"
        perm_str += " 51, 3, 50, 25, 29, 83, 86, 96, 80, 38, 40, 109, 55, 94, 59, 95, 21, 92, 76, 97, 81, 66, 70, 47,"
        perm_str += " 19, 100, 71, 44, 48, 79, 57, 89, 27, 8, 10, 41, 33, 68, 56, 93, 90]"

        assert str(perm_n_f) == perm_str

    def test_misc(self):
        print(9999999999, "to factoradic =>", Factoradic.number_to_factoradic(9999999999))

        f_2 = Factoradic("341010")
        print("Factoradic(\"341010\") ->", f_2, '->', f_2.to_number())

    def test_padding_zeroes(self):
        f = Factoradic(5)  # [2,1,0]
        list_no_pad = Factoradic.padded_to_length_s(f.v, f.length())  # should make no change
        assert f == list_no_pad, "ERROR: padding to the same length should make no change"

        list_f = Factoradic.padded_to_length_s(f.v, 5)

        assert list_f == [0,0,2,1,0]
        assert f.v == [2,1,0]
        print("PADDING", list_f, f.v)

        for _ in range3(100):  # tests random paddings and verifies they stay consistent
            f = Factoradic(random.randint(0,100000000))
            f_padding_size = random.randint(0,50)
            list_paddedf = Factoradic.padded_to_length_s(f.v, f.length() + f_padding_size)

            assert len(list_paddedf) == f.length() + f_padding_size
            assert f.v == list_paddedf[f_padding_size:]




class TestCaseFactoradicObject(unittest.TestCase):
    def setUp(self):
        print("----- setUp    -----")

    def tearDown(self):
        print("----- tearDown -----")
        clear_profile_time()

    def test_factoradic_init_inc1_next(self):
        f  = Factoradic()
        f0 = Factoradic(0)

        assert f == f0, "ERROR - null factoradic and factoradic zero should be equal"

        f.inc1()
        assert f == Factoradic([1,0])
        f0.inc1()
        assert f0 == Factoradic([1,0])

        assert f == f0, "ERROR - should be the same after both equal factoradics have been inc1'ed"

        f0_alt = Factoradic(f0)  # should make a copy

        assert f0 == f0_alt, "ERROR - factoradic and its copy by constructor should be equal"

        f0.inc1()

        assert f0 != f0_alt, "ERROR - factoradic and its copy should be different after only one is altered"

        assert f0 == f0_alt.next(), "ERROR - should match (inc1 and next())"
        assert f0 != f0_alt, "ERROR - factoradic and copy should be different after only one is altered - after next()"

        f1 = Factoradic([1,0])

        f0_alt = Factoradic(0)
        assert f0_alt.next() == f1, "ERROR - next factoradic to [0] should be equal to [1,0]"

    def test_trailing_zeroes(self):
        f0_00 = Factoradic(0)
        f0_01 = Factoradic([0])
        f0_02 = Factoradic([0,0])

        assert f0_00 == f0_01, "ERROR trailing zeroes should be ignored for equality"
        assert f0_00 == f0_02, "ERROR trailing zeroes should be ignored for equality"

        print("trailing zeroes", f0_00, f0_02, [0] == [0,0], f0_00.v, f0_02.v)

    def test_increment(self):
        f = Factoradic(2)
        f.increment(5)
        f_ = Factoradic(f)  # copy constructor
        f_.increment(0)

        assert f == Factoradic(7)
        assert f == f_

        f0 = Factoradic(0)

        f0.increment(1)
        assert f0 == Factoradic([1,0])
        assert f0 == Factoradic(0).next()

        f0 = Factoradic(0)

        f0.increment(5)
        assert f0 == Factoradic(5)

        for _ in range3(100):
            x = random.randint(0,10000)
            y = random.randint(0,10000)

            f_x = Factoradic(x)
            f_inc = Factoradic(x+y)
            f_x.increment(y)
            assert f_x == f_inc, "ERROR in random increment"
            f_x_pluszero = Factoradic(f_x)
            f_x_pluszero.increment(0)
            assert f_x_pluszero == f_x
            f_x_plusone = Factoradic(f_x)
            f_x_plusone.increment(1)
            assert f_x_plusone == f_x.next()

        with self.assertRaises(FactoradicException):
            f.increment(-1)  # negatives not allowed
        with self.assertRaises(FactoradicException):
            f.increment("five")  # wrong type
        with self.assertRaises(FactoradicException):
            f.increment([1,1,0])  # would be factoradic for 3, but we don't accept this at the moment (convert to int)

    def test_badly_formed_factoradic(self):
        with self.assertRaises(FactoradicException):
            Factoradic([1])  # badly formed factoradic
        with self.assertRaises(FactoradicException):
            Factoradic([2,0])  # badly formed factoradic
        with self.assertRaises(FactoradicException):
            Factoradic((1,0))  # unrecognised value type

    def test_large_permutation(self):
        # example found online, with a big Mersenne prime
        N = (2 ** 607) - 1

        print("with a Factoradic object:")
        print("N = (2 ** 607) - 1 # =>", N)
        f_1 = Factoradic(N)
        print("factoradic(N) =>", f_1)
        print("length of factoradic(N):", f_1.length())
        perm_f1 = f_1.permutation_inplace(list(range3(f_1.length())))
        print("permutation number factoradic(N) of the ordered list from [0, 1, 2, ... 112] =>", perm_f1)

        assert f_1.length() == 113

        resL = "[2L, 77L, 30L, 88L, 71L, 102L, 97L, 70L, 4L, 12L, 75L, 71L, 27L, 9L, 91L, 43L, 75L, 58L, 30L, 73L,"
        resL+= " 10L, 11L, 68L, 33L, 77L, 79L, 50L, 80L, 41L, 77L, 48L, 5L, 32L, 78L, 25L, 74L, 0L, 9L, 49L, 3L, 43L,"
        resL+= " 14L, 6L, 20L, 2L, 6L, 61L, 14L, 29L, 7L, 37L, 41L, 5L, 15L, 30L, 54L, 26L, 0L, 41L, 19L, 29L, 50L, 6L,"
        resL+= " 6L, 2L, 25L, 6L, 8L, 44L, 10L, 26L, 13L, 16L, 0L, 14L, 4L, 5L, 24L, 24L, 30L, 22L, 6L, 6L, 29L, 10L,"
        resL+= " 24L, 12L, 23L, 3L, 20L, 15L, 20L, 16L, 11L, 12L, 7L, 2L, 15L, 10L, 5L, 5L, 8L, 6L, 7L, 2L, 0L, 0L,"
        resL+= " 1L, 0L, 1L, 0L, 1L, 0L]"

        res =  "[2, 77, 30, 88, 71, 102, 97, 70, 4, 12, 75, 71, 27, 9, 91, 43, 75, 58, 30, 73,"
        res += " 10, 11, 68, 33, 77, 79, 50, 80, 41, 77, 48, 5, 32, 78, 25, 74, 0, 9, 49, 3, 43,"
        res += " 14, 6, 20, 2, 6, 61, 14, 29, 7, 37, 41, 5, 15, 30, 54, 26, 0, 41, 19, 29, 50, 6,"
        res += " 6, 2, 25, 6, 8, 44, 10, 26, 13, 16, 0, 14, 4, 5, 24, 24, 30, 22, 6, 6, 29, 10,"
        res += " 24, 12, 23, 3, 20, 15, 20, 16, 11, 12, 7, 2, 15, 10, 5, 5, 8, 6, 7, 2, 0, 0,"
        res += " 1, 0, 1, 0, 1, 0]"

        assert str(f_1) == resL or str(f_1) == res # annoying Python2-3 compatibility glitch workaround

        perm_str  = "[2, 78, 31, 91, 73, 107, 102, 72, 5, 14, 82, 77, 30, 11, 104, 49, 87, 65, 36, 88, 13, 16, 84, 42,"
        perm_str += " 98, 101, 61, 106, 52, 103, 60, 7, 43, 111, 34, 108, 0, 17, 69, 6, 63, 24, 12, 35, 4, 18, 99, 28,"
        perm_str += " 53, 20, 67, 75, 15, 37, 58, 105, 54, 1, 85, 45, 64, 110, 22, 23, 9, 62, 26, 32, 112, 39, 74, 46,"
        perm_str += " 51, 3, 50, 25, 29, 83, 86, 96, 80, 38, 40, 109, 55, 94, 59, 95, 21, 92, 76, 97, 81, 66, 70, 47,"
        perm_str += " 19, 100, 71, 44, 48, 79, 57, 89, 27, 8, 10, 41, 33, 68, 56, 93, 90]"

        assert str(perm_f1) == perm_str

        # test the not-in-place permutation method
        assert perm_f1 == f_1.permutation(list(range3(f_1.length())))

    def test_comparison_against_unsupported_type(self):
        with self.assertRaises(FactoradicException):
            f = Factoradic(0)
            f == 0
        with self.assertRaises(FactoradicException):
            f = Factoradic("0")
            f == "0"
        with self.assertRaises(FactoradicException):
            f = Factoradic([1, 0, 0])
            f == "[1, 0, 0]"
        with self.assertRaises(FactoradicException):
            f = Factoradic([1, 0, 0])
            f == (1, 0, 0)

def suite():
    my_suite = unittest.TestSuite()
    my_suite.addTest(unittest.makeSuite(TestCaseFactoradicLowlevel, 'tests for Factoradic as a bare list'))
    my_suite.addTest(unittest.makeSuite(TestCaseFactoradicObject, 'tests for Factoradic as class object'))

    return my_suite


if __name__ == '__main__':  # pragma: no cover
    # from coverage import coverage
    #
    # cov = coverage()
    # cov.start()

    unittest.main()
    #
    # cov.stop()
    # cov.save()
    #
    # cov.html_report()
