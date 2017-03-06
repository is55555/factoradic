
# >>> compatibility with Python 3
from __future__ import print_function, unicode_literals
import sys
if sys.version_info < (3,):
    integer_types = (int, long,)
    from itertools import imap
    from builtins import range as range3  # requires package future in Python2 (unfortunate, but there's no better way)
else:
    integer_types = (int,)
    imap = map
    range3 = range
    unicode = str
# I use the names imap and range3 to make it explicit for Python2 programmers and avoid confusion
# <<< compatibility with Python 3

from math import factorial as fact


class FactoradicException(Exception):
    pass


class Factoradic(object):
    def __init__(self, value):  # constructs either from a number, a list, a string or a Factoradic object (copy)
        if value is None:
            self.v = [0]  # no value creates a [0] by default
        elif isinstance(value, integer_types):
            self.v = Factoradic.number_to_factoradic(value)
        elif isinstance(value, Factoradic):
            self.v = value.v[:]  # copy
        elif isinstance(value, list):
            if Factoradic.is_well_formed_factoradic(value):
                self.v = value[:]  # copy -- if creation time is critical, use the static method interface instead ...
                # ... and work with naked lists.
            else:
                raise FactoradicException('Factoradic __init__ failed: value not well formed')
        elif isinstance(value, unicode):  # would be basestring in Python2 if not for the __future__ import
            l = Factoradic.string_to_factoradic(value)
            if Factoradic.is_well_formed_factoradic(l):
                self.v = l
        else: raise FactoradicException('Factoradic __init__ failed - could not deal with value ' + repr(value))

    def __str__(self):
        # return "".join(imap(lambda x: str(x), self.v)) # would only work for small factoradics
        # a representation based on base64 would get us further but still not fit for the general case, so just print
        # the list.
        return str(self.v)

    def length(self):
        return len(self.v)

    def well_formed(self):
        return Factoradic.is_well_formed_factoradic(self.v)

    def to_number(self):
        return Factoradic.factoradic_to_number(self.v)

    def next(self):  # returns a copy, does not modify the object
        return Factoradic.next_factoradic(self.v)

    def inc1(self):  # modifies the object (increases the factoradic value by one)
        self.v[len(self.v) - 2] += 1
        Factoradic.cascade_factoradic_digits_inplace(self.v)

    def increment(self, inc):  # modifies the object (increases the factoradic value ) - verifies the parameter
        if isinstance(inc, integer_types):
            if inc == 0:
                return
            if inc < 0:
                raise FactoradicException('Factoradic increment failed: negative value (decrement not supported)')
                #  just convert to integer and back to subtract - since I'm not supporting negative values this is ...
                #  ... not a useful feature in this lib. If I add negatives in the future I'll add direct subtraction.
            self.v[len(self.v) - 2] += inc
            Factoradic.cascade_factoradic_digits_inplace(self.v)
        else:
            raise FactoradicException('Factoradic increment failed: expected integer type argument')

    def permutation(self, elements):  # returns the permutation number Factoradic.v from elements
        return Factoradic.generate_permutation_from_factoradic(self.v, elements)

    def permutation_inplace(self, elements):  # destroys the given list, only use if the list is no longer required
        return Factoradic.generate_permutation_from_factoradic_inplace(self.v, elements)

    def padded_to_length(self, n):  # returns a 0-padded version of the Factoradic up to length n
        return Factoradic(Factoradic.padded_to_length_s(self.v, n))

    @staticmethod
    def number_to_factoradic(value):  # the one I want, with zero as [0], one as [1, 0], no carriage errors
        digits = []
        count = 1
        while value >= count:
            digits.insert(0, value % count)
            value //= count
            count += 1
        digits.insert(0, value)
        return digits

    @staticmethod
    def cascade_factoradic_digits_inplace(factoradic_value): # in-place. Makes the factoradic well-formed
        reversed_place = 1
        factoradic_value[len(factoradic_value)-1] = 0
        for i in range3(len(factoradic_value)-2, 0, -1):
            reversed_place += 1
            if factoradic_value[i] >= reversed_place:
                factoradic_value[i-1] += factoradic_value[i] // reversed_place
                factoradic_value[i] %= reversed_place

        reversed_place += 1
        while factoradic_value[0] >= reversed_place:
            factoradic_value.insert(0, factoradic_value[0] // reversed_place)
            factoradic_value[1] %= reversed_place
            reversed_place += 1
        return factoradic_value

    @staticmethod
    def cascade_factoradic_digits(factoradic_value): # helper so it doesn't modify the parameter in-place
        res = factoradic_value[:]
        return Factoradic.cascade_factoradic_digits_inplace(res)

    @staticmethod
    def next_factoradic(factoradic_value):
        if len(factoradic_value) < 2:  # only 0 can be represented in less than 2 digits
            return [1,0]
        result = factoradic_value[:]  # copy
        result[len(factoradic_value) - 2] += 1
        return Factoradic.cascade_factoradic_digits_inplace(result)
        # this can be optimised if we deal only with well-formed factoradic_value inputs, because ...
        # ... cascade_factoradic_digits does not make any assumptions. With well-formed factoradics, we can ...
        # ... stop the cascading at the first digit that doesn't overflow. However in the general case the ...
        # ... improvement is negligible.

    @staticmethod
    def is_well_formed_factoradic(factoradic_value):
        for i in range3(len(factoradic_value)):
            if int(factoradic_value[i]) >= (len(factoradic_value) - i):
                return False
        return True

    @staticmethod
    def factoradic_to_number(factoradic_value):
        res = 0
        for i in range3(len(factoradic_value) - 1):
            res += factoradic_value[i] * fact(len(factoradic_value) - 1 - i)

        return res

    @staticmethod
    def string_to_factoradic(s):
        return list(imap(lambda x: int(x), list(s)))

    @staticmethod
    def generate_permutation_from_factoradic_inplace(factoradic_value, elements):  # modifies 'elements' in place
        res = []

        # this bit makes the permutations cycle through:
        # permutation number [1, 0, 0, 0] <=> permutation number [0, 0, 0]
        size_diff = len(factoradic_value) - len(elements)
        if size_diff > 0:
            factoradic_value = factoradic_value[size_diff:]

        # factoradic_value needs to be padded to the length of "elements"
        if size_diff < 0:
            factoradic_value = Factoradic.padded_to_length_s(factoradic_value, len(elements))

        # at this point, lengths must match
        for i in range3(len(factoradic_value)):
            res.append(elements.pop(factoradic_value[i]))
        return res

    @staticmethod
    def generate_permutation_from_factoradic(factoradic_value, elements): # helper to avoid modifying any parameters
        return Factoradic.generate_permutation_from_factoradic_inplace(factoradic_value, elements[:])

    @staticmethod
    def padded_to_length_s(factoradic_value, new_len):
        if len(factoradic_value) < new_len:
            diff = new_len - len(factoradic_value)
            padding = [0] * diff
            padding.extend(factoradic_value)
            return padding
        return factoradic_value


if __name__ == "__main__":
    import tests

    suite = tests.unittest.TestLoader().loadTestsFromTestCase(tests.TestCaseFactoradicLowlevel)
    suite.addTests(tests.unittest.TestLoader().loadTestsFromTestCase(tests.TestCaseFactoradicObject))
    tests.unittest.TextTestRunner(verbosity=2).run(suite)

    tests.unittest.TestSuite(tests.suite())
