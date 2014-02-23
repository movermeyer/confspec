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

class ConfigMg(object):
    """
    Configuration Manager object.

    :param spec: List of instances of subclasses of
     :class:`confspec.ConfigOpt`.
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
     later using :meth:`ConfigMg.enable_notify`.
    :param bool writeback: Enable writeback mechanism that calls
     :meth:`ConfigMg.save` when the user changes the state of the
     configuration. This setting is ignored by :meth:`ConfigMg.do_import` so
     importing (and thus altering the state of the configuration) doesn't
     trigger a file write for each key value change. This feature can be
     enabled or disabled at any time using :meth:`ConfigMg.enable_writeback`.
    :param bool safe: Enable safe mode. When safe mode is enabled all
     exceptions happening within all methods are logged instead of raised.
     Exceptions can happen when a file cannot be created, when a file cannot be
     imported (no read permissions, parse error), etc. This feature can be
     enabled or disabled at any time using :meth:`ConfigMg.enable_safe`.
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
        for key in self._keys.keys():
            self._listeners[key] = []

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
        listeners = self._listeners[key]
        if not func in listeners:
            listeners.append(func)
            return True
        return False

    def unregister_listener(self, func, key):
        """
        Unregister a listener for given key.
        """
        listeners = self._listeners[key]
        if func in listeners:
            del listeners[listeners.index(func)]
            return True
        return False

    def save(self):
        """
        Export current configuration to the top file in the file stack.
        """
        if len(self._files) > 0:
            with open(self._files[-1], 'w') as f:
                f.write(self.do_export(format=self._format))

    def load(self):
        """
        Import all files in the file stack.
        """
        for fn in self._files:
            with open(fn, 'r') as f:
                self.do_import(f.read(), format=self._format)

    def do_import(self, conf, format='ini'):
        """
        Import - validate a configuration written in a standard format.
        Supported formats: Auto, INI, JSON, Python dict.
        """
        pass

    def do_export(self, format='ini'):
        """
        Export current configuration as a standard format.
        Supported formats: INI, JSON, Python dict.
        """
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
                except:
                    pass

    def get_proxy(self):
        """
        Return a proxy object for current configuration specification.
        """
        return ConfigProxy(self)


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
