
import_fact = True

if import_fact:
    from math import factorial as fact
else:
    def fact(n): # could obviously just import from math - this is just for speed testing
        if n <= 1:
            return 1
        if n < 10:
            return [2, 6, 24, 120, 720, 5040, 40320, 362880][n-2]

        res = 362880

        for i in xrange(10, n+1):
            res *= i

        return res


def number_to_factoradic(value): # the one I want, with zero as [0], one as [1, 0], no carriage errors
    digits = []
    count = 1
    while value >= count:
        digits.insert(0, value % count)
        value //= count
        count += 1
    digits.insert(0, value)
    return digits


def to_factoradic_simple(value):  # zero represented as []
    digits = []
    count = 1
    while value > 0:  # value >= 0 would never finish, as 0 //= x is 0 for any x.
        digits.insert(0, value % count)
        value = value // count
        count += 1
    return digits


def to_factoradic2flaw(value): # flaw : for instance 6 [3, 0, 0] violates the rule ...
        # ... that each digit cannot be larger than its position.
    digits = []
    count = 1
    while value > count:
        digits.insert(0, value % count)
        value //= count
        count += 1
    digits.insert(0, value)
    return digits


def to_factoradic3flaw(value):  # zero represented as [0,0] instead of [0]
    digits = [0]
    count = 2
    while value >= count:
        digits.insert(0, value % count)
        value //= count
        count += 1
    digits.insert(0, value)
    return digits


def cascade_factoradic_digits_inplace(factoradic_value): # in-place. Makes the factoradic well-formed
    reversed_place = 1
    factoradic_value[len(factoradic_value)-1] = 0
    for i in xrange(len(factoradic_value)-2, 0, -1):
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


def cascade_factoradic_digits(factoradic_value): # helper so it doesn't modify the parameter in-place
    res = factoradic_value[:]
    return cascade_factoradic_digits_inplace(res)


def next_factoradic(factoradic_value):
    if len(factoradic_value) < 2:  # only 0 can be represented in less than 2 digits
        return [1,0]
    result = factoradic_value[:]  # copy
    result[len(factoradic_value) - 2] += 1
    return cascade_factoradic_digits_inplace(result)
    # this can be optimised if we deal only with well-formed factoradic_value inputs, because cascade_factoradic_digits
    # does not make any assumptions. With well-formed factoradics, we can stop the cascading at the first digit that
    # doesn't overflow. However in the general case the improvement is negligible.


def well_formed(factoradic_value):
    for i in xrange(len(factoradic_value)):
        if factoradic_value[i] >= (len(factoradic_value) - i):
            return False
    return True


def factoradic_to_number(factoradic_value):
    res = 0
    for i in xrange(len(factoradic_value) - 1):
        res += factoradic_value[i] * fact(len(factoradic_value) - 1 - i)

    return res


def string_to_factoradic(s):
    return list(map(lambda x: int(x), list(s)))


def generate_permutation_from_factoradic_inplace(factoradic_value, elements): # modifies 'elements' in place
    res = []

    # this bit makes the permutations cycle through: permutation number [1, 0, 0, 0] <=> permutation number [0, 0, 0]
    size_diff = len(factoradic_value) - len(elements)
    if size_diff > 0:
        factoradic_value = factoradic_value[size_diff:]

    # factoradic_value needs to be padded to the length of "elements"
    if size_diff < 0:
        factoradic_value = pad_to_length(factoradic_value, len(elements))

    # at this point, lengths must match
    for i in xrange(len(factoradic_value)):
        res.append(elements.pop(factoradic_value[i]))
    return res


def generate_permutation_from_factoradic(factoradic_value, elements): # helper to avoid modifying any parameters
    return generate_permutation_from_factoradic_inplace(factoradic_value, elements[:])


def pad_to_length(factoradic_value, new_len):
    if len(factoradic_value) < new_len:
        diff = new_len - len(factoradic_value)
        padding = [0] * diff
        padding.extend(factoradic_value)
        return padding
    return factoradic_value


if __name__ == "__main__":
    # Wikipedia example: 463 == factoradic_to_number(string_to_factoradic("341010"))
    print 463, '<=> ', factoradic_to_number(string_to_factoradic("341010"))
    print "factoradic", string_to_factoradic("341010"), "<=> factoradic", number_to_factoradic(463)
    assert 463 == factoradic_to_number(string_to_factoradic("341010")), "test case ERROR"
    assert string_to_factoradic("341010") == number_to_factoradic(463), "test case ERROR"

    assert number_to_factoradic(0) == [0], "test case ERROR (0)"
    assert number_to_factoradic(1) == [1, 0], "test case ERROR (1)"
    assert number_to_factoradic(2) == [1, 0, 0], "test case ERROR (2)"
    assert number_to_factoradic(5) == [2, 1, 0], "test case ERROR (5)"
    assert number_to_factoradic(6) == [1, 0, 0, 0], "test case ERROR (6)" # this is an edge case for carry-over
    assert number_to_factoradic(7) == [1, 0, 1, 0], "test case ERROR (7)"

    fj = number_to_factoradic(0)
    for j in xrange(0, 720):
        # print j, number_to_factoradic(j), "fj", fj
        assert number_to_factoradic(j) == fj, "ERROR factoradics don't match"
        fj = next_factoradic(fj)
        assert number_to_factoradic(j) != fj, "ERROR consecutive factoradics shouldn't match"

    for j in xrange(20):
        elements = range(3)
        # factoradic = pad_to_length(number_to_factoradic(j), len(elements)) # not required
        factoradic = number_to_factoradic(j)
        # print j, factoradic, generate_permutation_from_factoradic_inplace(factoradic, elements)  # this also works...
        # ... because we regenerate "elements" every loop, but generally we don't want to modify parameters
        print j, factoradic, generate_permutation_from_factoradic(factoradic, elements)

    fx = [463,0]
    print fx, "cascaded =>", cascade_factoradic_digits(fx)
    fx = [9999999999, 0]
    print fx, "cascaded =>", cascade_factoradic_digits(fx)

    cascade_factoradic_digits_inplace(fx)
    print fx, "to number =>", factoradic_to_number(fx)
    print "341010 to number =>", factoradic_to_number(string_to_factoradic("341010"))

    print 9999999999, "to factoradic =>", number_to_factoradic(9999999999)

    # example found online, with a big Mersenne prime
    N = (2 ** 607) - 1
    print "N = (2 ** 607) - 1 # =>", N
    n_f = number_to_factoradic(N)
    print "factoradic(N) =>", n_f
    print "length of factoradic(N):", len(n_f)

    perm_n_f = generate_permutation_from_factoradic(n_f, range(len(n_f)))

    print "permutation number factoradic(N) of the ordered list from [0, 1, 2, ... 112] =>", perm_n_f
    # observation: by definition, each element of perm_n_f is >= to n_f for every position, ...
    # ... for the canonical [0...len(n_f)] list of elements
