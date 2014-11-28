# -*- coding: UTF-8 -*-
import os
import cPickle as pickle
import warnings

from importlib import import_module
from os.path import join, dirname, abspath, isabs, exists

from scrapy.utils.conf import closest_scrapy_cfg, get_config, init_env
from scrapy.settings import CrawlerSettings
from scrapy.exceptions import NotConfigured

ENVVAR = 'SCRAPY_SETTINGS_MODULE'
DATADIR_CFG_SECTION = 'datadir'

def inside_project():
    scrapy_module = os.environ.get('SCRAPY_SETTINGS_MODULE')
    if scrapy_module is not None:
        try:
            import_module(scrapy_module)
        except ImportError as exc:
            warnings.warn("Cannot import scrapy settings module %s: %s" % (scrapy_module, exc))
        else:
            return True
    return bool(closest_scrapy_cfg())

def project_data_dir(project='default'):
    """Return the current project data dir, creating it if it doesn't exist"""
    if not inside_project():
        raise NotConfigured("Not inside a project")
    cfg = get_config()
    if cfg.has_option(DATADIR_CFG_SECTION, project):
        d = cfg.get(DATADIR_CFG_SECTION, project)
    else:
        scrapy_cfg = closest_scrapy_cfg()
        if not scrapy_cfg:
            raise NotConfigured("Unable to find scrapy.cfg file to infer project data dir")
        d = abspath(join(dirname(scrapy_cfg), '.scrapy'))
    if not exists(d):
        os.makedirs(d)
    return d

def data_path(path, createdir=False):
    """If path is relative, return the given path inside the project data dir,
    otherwise return the path unmodified
    """
    if not isabs(path):
        path = join(project_data_dir(), path)
    if createdir and not exists(path):
        os.makedirs(path)
    return path

def get_project_settings():

#     指定设定(Designating the settings)
# ENVVAR = 'SCRAPY_SETTINGS_MODULE'
# 当您使用Scrapy时，您需要声明您所使用的设定。这可以通过使用环境变量: SCRAPY_SETTINGS_MODULE 来完成。
#
# SCRAPY_SETTINGS_MODULE 必须以Python路径语法编写, 如 myproject.settings 。 注意，设定模块应该在 Python import search path 中。
    if ENVVAR not in os.environ:
        project = os.environ.get('SCRAPY_PROJECT', 'default')
        init_env(project)
    settings_module_path = os.environ.get(ENVVAR)
    if settings_module_path:
        settings_module = import_module(settings_module_path)
    else:
        settings_module = None
    settings = CrawlerSettings(settings_module)

    # XXX: remove this hack
    pickled_settings = os.environ.get("SCRAPY_PICKLED_SETTINGS_TO_OVERRIDE")
    settings.overrides = pickle.loads(pickled_settings) if pickled_settings else {}

    # XXX: deprecate and remove this functionality
    for k, v in os.environ.items():
        if k.startswith('SCRAPY_'):
            settings.overrides[k[7:]] = v

    return settings
