# Copyright (C) 2014 Carlos Jenkins <carlos@jenkins.co.cr>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


def in_range(bottom, top):
    """
    Validate that a number is in the given range.

    >>> f = in_range(-10, 100)
    >>> f(-10)
    True
    >>> f(100)
    True
    >>> f(50)
    True
    >>> f(200)
    False
    >>> f(-20)
    False

    :param int bottom: bottom interval delimiter.
    :param int top: top interval delimiter.
    :rtype: A validator function.
    """
    def validator(num):
        if bottom <= num <= top:
            return True
        return False
    return validator


def is_one_of(options):
    """
    Validate that the given attribute is member of the given list.

    >>> f = is_one_of(['foo', 'bar'])
    >>> f('ham')
    False
    >>> f('foo')
    True
    >>> f('Foo')
    False
    >>> f = is_one_of([10, 15, 20])
    >>> f(20)
    True

    :param list options: The options that the attribute can be.
    :rtype: A validator function.
    """
    def validator(item):
        return item in options
    return validator


def is_subset_of(main):
    """
    Validate that the given set is subset of the main given set.

    >>> f = is_subset_of(set(['a', 'b', 'c', 'd']))
    >>> f(set(['b', 'd']))
    True
    >>> f(set(['a', 'b', 'c', 'd']))
    True
    >>> f(set(['a', 'f']))
    False

    :param set main: The main set to compare to.
    :rtype: A validator function.
    """
    def validator(sub):
        return sub <= main
    return validator


def multiple_of(multi):
    """
    Validate that the given number is multiple of the given multiple.

    >>> f = multiple_of(10)
    >>> f(10)
    True
    >>> f(100)
    True
    >>> f(20)
    True
    >>> f(35)
    False
    >>> f(4)
    False

    :param int multi: Multiple to check against.
    :rtype: A validator function.
    """
    def validator(num):
        return (num % multi) == 0
    return validator


def is_even():
    """
    Validate that the given number is even.

    >>> f = is_even()
    >>> f(10)
    True
    >>> f(2)
    True
    >>> f(0)
    True
    >>> f(-1)
    False
    >>> f(3)
    False

    :rtype: A validator function.
    """
    def validator(num):
        return (num % 2) == 0
    return validator


def is_odd():
    """
    Validate that the given number is odd.

    >>> f = is_odd()
    >>> f(3)
    True
    >>> f(-1)
    True
    >>> f(10)
    False
    >>> f(2)
    False
    >>> f(0)
    False

    :rtype: A validator function.
    """
    def validator(num):
        return (num % 2) == 1
    return validator