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

from __future__ import print_function

from sys import stderr
from traceback import format_exc


def _error(exc=None):
    if exc is None:
        exc = format_exc()
    print('* ConfigMg:', file=stderr)
    for line in exc.split('\n'):
        print('*  ', line, file=stderr)


class ConfigMg(object):
    """
    Configuration manager object.

    .. todo::

       Implement :meth:`do_import`.

    .. todo::

       Implement :meth:`do_export`.

    :param spec: List of instances of subclasses of
     :class:`confspec.options.ConfigOpt`.

    :param files: A list of paths to configuration files. Files are read in the
     given order. The last file is considered the user file. Example:
     ``['/etc/myapp.conf', '~/.myapp/myapp.conf']``

    :param format: The format to export to and import from. Supported formats
     are given by :attr:`ConfigMg.supported_formats`.

    :param bool create: If a file in ``files`` doesn't exists, try to
     create it with the current configuration state exported using the format
     specified by ``format``. Note that if ``safe`` is not enabled and the file
     cannot be created (in case of insufficient permissions, for example) then
     an exception will be raised.

    :param bool notify: Enable notification of configuration changes to the
     registered listeners. Unless required, it is recommended to leave disabled
     this option when configuration files are being imported, and enable it
     later using :meth:`enable_notify`.

    :param bool writeback: Enable writeback mechanism that calls :meth:`save`
     when the user changes the state of the configuration. This setting is
     ignored by :meth:`do_import` so importing (and thus altering the state of
     the configuration) doesn't trigger a file write for each key value change.
     This feature can be enabled or disabled at any time using
     :meth:`enable_writeback`.

    :param bool safe: Enable safe mode. When safe mode is enabled all
     exceptions happening within all methods are written to
     :py:obj:`sys.stderr` instead of raised. Exceptions can happen when a file
     cannot be created, when a file cannot be imported (no read permissions,
     parse error) or when notifying a listener about a option change, among
     others. This feature can be enabled or disabled at any time using
     :meth:`enable_safe`.
    """

    supported_formats = ['ini', 'json', 'dict']
    """
    Supported format to export configuration held by the configuration manager.
    """

    def __init__(self, spec, files=tuple(), format='ini',
            create=True, notify=False, writeback=True, safe=True):

        # Register spec and check uniqueness
        self._spec = spec
        self._keys = {s.key: s for s in spec}
        if len(self._keys) != len(spec):
            raise AttributeError('Keys are not unique.')

        # Register file stack
        self._files = files

        # Register format
        if format not in ConfigMg.supported_formats:
            raise AttributeError('Unknown format \'{}\''.format(format))
        self._format = format

        # Register flags
        self._create = create
        self._notify = notify
        self._writeback = writeback
        self_safe = safe

        # Create map of listeners
        self._listeners = {}

        # Create categories map
        self._categories = {}
        for s in self._spec:
            if s._category in self._categories:
                self._categories[s._category].append(s)
            else:
                self._categories[s._category] = [s]

        # Create proxy
        self._proxy = ConfigProxy(self)

    def enable_notify(self, enable):
        """
        Enable global notification of configuration changes.
        See :class:`ConfigMg`.
        """
        self._notify = enable

    def enable_writeback(self, enable):
        """
        Enable automatic writeback to file when current configuration changes.
        See :class:`ConfigMg`.
        """
        self._writeback = enable

    def enable_safe(self, enable):
        """
        Enable safe mode. See :class:`ConfigMg`.
        """
        self._safe = enable

    def register_listener(self, func, key):
        """
        Register a listener for given key.
        """
        if func is None or not hasattr(func, '__call__'):
            return False

        if not key in self._listeners:
            self._listeners[key] = []

        listeners = self._listeners[key]
        if not func in listeners:
            listeners.append(func)
            return True
        return False

    def unregister_listener(self, func, key):
        """
        Unregister a listener previously registered for the given key.
        """
        if not key in self._listeners:
            return False

        listeners = self._listeners[key]
        if func in listeners:
            del listeners[listeners.index(func)]
            return True
        return False

    def save(self):
        """
        Export current configuration and write it to the last file in the
        file stack.
        """
        if len(self._files) > 0:
            try:
                with open(self._files[-1], 'w') as f:
                    f.write(self.do_export(format=self._format))
            except Exception as e:
                if not self._safe:
                    raise e
                else:
                    _error()

    def load(self):
        """
        Import all files in the file stack.
        """
        for fn in self._files:
            try:
                with open(fn, 'r') as f:
                    self.do_import(f.read(), format=self._format)
            except Exception as e:
                if not self._safe:
                    raise e
                else:
                    _error()

    def do_import(self, conf, format=None):
        """
        Import and validate a configuration written in a standard format.

        :param str conf: A string with a configuration encoded in the specified
         format.
        :param format: See :attr:`ConfigMg.supported_formats`.
         If ``None`` (the default) the format specified in the constructor is
         used.
        :type format: str or None
        """
        if format is None:
            format = self._format
        pass

    def do_export(self, format=None):
        """
        Export current configuration as a standard format.

        :param format: See :attr:`ConfigMg.supported_formats`.
         If ``None`` (the default) the format specified in the constructor is
         used.
        :type format: str or None
        :rtype: A string with the configuration encoded in the specified
         format.
        """
        if format is None:
            format = self._format
        pass

    def get(self, key):
        """
        Get the value of a config key.
        """
        return self._keys[key].value

    def set(self, key, value):
        """
        Validate and set a config key.
        """
        # Get old value and compare
        old_value = self.get(key)
        if value == old_value:
            return

        # Set -validate new value
        self._keys[key].value = value

        # Writeback if enabled
        if self._writeback:
            self.save()

        # Notify all listeners of the change
        if self._notify:
            for listener in self._listeners[keys]:
                try:
                    listener(key, old_value, value)
                except Exception as e:
                    if not self._safe:
                        raise e
                    else:
                        _error()

    def get_proxy(self):
        """
        Return a proxy object for current configuration specification.
        """
        return self._proxy


class ConfigProxy(object):
    """
    Proxy object for application configuration.
    """

    def __init__(self, cfmg):
        self.cfmg = cfmg

    def __delattr__(self, name):
        raise TypeError('Cannot delete configuration keys.')

    def __getattr__(self, name):
        return self.cfmg.get(name)

    def __setattr__(self, name, value):
        self.cfmg.set(name, value)
