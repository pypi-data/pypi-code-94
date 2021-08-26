import os
import re
from pathlib import Path
from dsocli.logger import Logger
from dsocli.config import Configs
from dsocli.providers import Providers
from dsocli.templates import TemplateProvider
from dsocli.stages import Stages
from dsocli.constants import *
from dsocli.exceptions import DSOException
from dsocli.contexts import Contexts
from dsocli.local_utils import *
from dsocli.settings import *


_default_spec = {
    'path': os.path.join(Configs.config_dir, 'templates')
}


def get_default_spec():
    return _default_spec.copy()


class LocalTemplateProvider(TemplateProvider):


    def __init__(self):
        super().__init__('template/local/v1')


    @property
    def root_dir(self):
        return Configs.template_spec('path')


    def get_path_prefix(self):
        return self.root_dir + os.sep


    def list(self, project, application, stage, uninherited=False, include_contents=False, filter=None):
        templates = load_context_templates(stage, path_prefix=self.get_path_prefix(), uninherited=uninherited, include_contents=include_contents, filter=filter)
        result = {'Templates': []}
        for key, details in templates.items():
            item = {'Key': key}
            item.update(details)
            result['Templates'].append(item)
        return result



    def add(self, project, application, stage, key, contents, render_path=None):
        if not Stages.is_default(stage) and not ALLOW_STAGE_TEMPLATES:
            raise DSOException(f"Templates may not be added to stage scopes, as the feature is currently disabled. It may be enabled by adding 'ALLOW_STAGE_TEMPLATES=yes' to the DSO global settings, or adding environment variable 'DSO_ALLOW_STAGE_TEMPLATES=yes'.")
        response = add_local_template(stage, key, path_prefix=self.get_path_prefix(), contents=contents)
        result = {
                'Key': key,
                'Stage': Stages.shorten(stage),
                'Path': response['Path'],
            }
        return result


    def get(self, project, application, stage, key, revision=None):
        if revision:
            raise DSOException(f"Template provider 'local/v1' does not support versioning.")
        Logger.debug(f"Getting template: stage={stage}, key={key}")
        found = locate_template_in_context_hierachy(stage=stage, key=key, path_prefix=self.get_path_prefix(), include_contents=True)
        if not found:
            raise DSOException(f"Template '{key}' not found nor inherited in the given context: stage={Stages.shorten(stage)}")
        result = {
                'Key': key, 
            }
        result.update(found[key])
        return result


    def delete(self, project, application, stage, key):
        Logger.debug(f"Locating template: stage={stage}, key={key}")
        ### only parameters owned by the context can be deleted, hence uninherited=True
        found = locate_template_in_context_hierachy(stage=stage, key=key, path_prefix=self.get_path_prefix(), uninherited=True)
        if not found:
            raise DSOException(f"Template '{key}' not found in the given context: stage={Stages.shorten(stage)}")
        Logger.info(f"Deleting template: path={found[key]['Path']}")
        delete_local_template(path=found[key]['Path'])
        result = {
                'Key': key,
                'Stage': Stages.shorten(stage),
                'Path': found[key]['Path'],
            }
        return result


    def history(self, project, application, stage, key, include_contents=False):
        raise DSOException(f"Template provider 'local/v1' does not support versioning.")



def register():
    Providers.register(LocalTemplateProvider())
