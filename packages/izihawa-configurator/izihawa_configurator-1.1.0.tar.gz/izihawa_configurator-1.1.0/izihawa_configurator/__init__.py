import json
import os
import os.path
import re
from types import ModuleType

import yaml
from izihawa_configurator.exceptions import UnknownConfigFormatError
from izihawa_utils.common import smart_merge_dicts, unflatten
from jinja2 import Template


class ConfigObject(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(e)


class AnyOf:
    def __init__(self, *args):
        self.args = args


class RichDict(dict):
    def has(self, *args):
        current = self
        for c in args:
            if c not in current:
                return False
            current = current[c]
        return True

    def copy_if_exists(self, source_keys, target_key):
        current = self
        for c in source_keys:
            if c not in current:
                return False
            current = current[c]
        self[target_key] = current
        return True


class Configurator(RichDict):
    def __init__(self, configs: list, env_prefix: str = None, env_key_separator: str = '.'):
        """
        Create Configurator object

        :param configs: list of paths to config files, dicts or modules.
        End filepath with `?` to mark it as optional config.
        """
        super().__init__()

        self._by_basenames = {}
        self._omitted_files = []

        env_dict = {}
        array_dict = {}

        if env_prefix:
            env_prefix = env_prefix.lower()
            for name, value in os.environ.items():
                if name.lower().startswith(env_prefix):
                    stripped_name = name[len(env_prefix):].lstrip('_').lower()
                    
                    # Check for array format: {MAIN_PART}[{index}]
                    array_match = re.match(r'^(.+)\[(\d+)\]$', stripped_name)
                    if array_match:
                        base_name, index_str = array_match.groups()
                        index = int(index_str)
                        if base_name not in array_dict:
                            array_dict[base_name] = {}
                        array_dict[base_name][index] = value
                    else:
                        # Handle legacy [] format for backward compatibility
                        if stripped_name.endswith('[]'):
                            base_name = stripped_name[:-2]
                            if base_name not in env_dict:
                                env_dict[base_name] = []
                            env_dict[base_name].append(value)
                        else:
                            env_dict[stripped_name] = value
            
            # Convert indexed arrays to lists
            for base_name, indexed_values in array_dict.items():
                # Sort by index and convert to list
                max_index = max(indexed_values.keys()) if indexed_values else -1
                array = [None] * (max_index + 1)
                for index, value in indexed_values.items():
                    array[index] = value
                env_dict[base_name] = array
                
            env_dict = unflatten(env_dict, sep=env_key_separator)

        # Create filtered environ that excludes prefix-based variables to avoid duplication
        filtered_environ = {}
        if env_prefix:
            for name, value in os.environ.items():
                if not name.lower().startswith(env_prefix):
                    filtered_environ[name] = value
        else:
            filtered_environ = dict(os.environ)
            
        for config in ([filtered_environ] + configs + [env_dict]):
            file_found = self.update(config)
            if not file_found:
                self._omitted_files.append(config)

    def _config_filename(self, filename):
        return os.path.join(os.getcwd(), filename)

    def walk_and_render(self, c):
        if isinstance(c, str):
            return Template(c).render(**self)
        elif isinstance(c, list):
            return [self.walk_and_render(e) for e in c]
        elif isinstance(c, dict):
            for key in list(c.keys()):
                c[key] = self.walk_and_render(c[key])
                if key.endswith('_filepath'):
                    with open(c[key]) as f:
                        if c[key].endswith('.json'):
                            c[key.replace('_filepath', '')] = json.loads(f.read())
                        elif c[key].endswith('.yaml'):
                            c[key.replace('_filepath', '')] = yaml.safe_load(f.read())
        return c

    def update(self, new_config, basename=None, **kwargs):
        if isinstance(new_config, AnyOf):
            for config in new_config.args:
                try:
                    return self.update(config.rstrip('?'))
                except IOError:
                    pass
            raise IOError('None of %s was found' % ', '.join(new_config.args))
        elif isinstance(new_config, str):
            optional = new_config.endswith('?')
            filename = new_config.rstrip('?')
            basename = basename or os.path.basename(filename)

            config_filename = self._config_filename(filename)

            data = None

            if os.path.exists(config_filename) and os.access(config_filename, os.R_OK):
                with open(config_filename) as f:
                    data = f.read()

            if data is None:
                if optional:
                    return False
                else:
                    raise IOError(f'File {config_filename} not found')

            if filename.endswith('.json'):
                new_config = json.loads(data)
            elif filename.endswith('.yaml'):
                new_config = yaml.safe_load(data)
            else:
                raise UnknownConfigFormatError(filename)

            new_config = self.walk_and_render(new_config)

        elif isinstance(new_config, ModuleType):
            new_config = new_config.__dict__

        elif callable(new_config):
            new_config = new_config(self)

        if not new_config:
            new_config = {}

        for k in new_config:
            if callable(new_config[k]):
                new_config[k] = new_config[k](context=self)

        if 'log_path' in new_config:
            new_config['log_path'] = os.path.expanduser(new_config['log_path']).rstrip('/')

        smart_merge_dicts(self, new_config, list_policy='override', copy=False)
        if basename:
            self._by_basenames[basename] = new_config

        return True

    def get_config_by_basename(self, basename):
        return self._by_basenames[basename]

    def get_object_by_basename(self, basename):
        return ConfigObject(self._by_basenames[basename])

    def has_missed_configs(self):
        return bool(self._omitted_files)

    def has_file(self, basename):
        return basename in self._by_basenames

    def get_files(self):
        return self._by_basenames
