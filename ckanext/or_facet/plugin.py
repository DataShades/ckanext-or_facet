# -*- coding: utf-8 -*-

import re
import os
import ckan.plugins as plugins
import ckantoolkit as tk


try:
    from ckan.lib.search.query import _parse_local_params
    from pyparsing.exceptions import ParseException
    from pyparsing import (
        Word, QuotedString, Suppress, OneOrMore, Group, alphanums
    )
    try:
        _parse_local_params('{!edismax q.op=OR}')
    except ParseException:

        def _patch(local_params):
            # type: (str) -> list[object]
            key = Word(alphanums + "_.")
            value = QuotedString('"') | QuotedString("'") | Word(alphanums + "_$")
            pair = Group(key + Suppress("=") + value)
            expression = Suppress("{!") + OneOrMore(pair | key) + Suppress("}")
            return expression.parse_string(local_params).as_list()

        if not tk.asbool(os.getenv("CKANEXT_OR_FACET_NOPATCH")):
            _parse_local_params.__code__ = _patch.__code__

except ImportError:
    pass

_term_pattern = (
    r"(^|(?<=\s))"  # begining of the line or space after facet
    r"{field}:"  # fixed field name(must be replaced)
    r"(?P<quote>\'|\")?"  # optional open-quote
    r"(?P<term>.+?)"  # facet value
    r"(?(quote)(?P=quote))"  # optional closing quote
    r"(?=\s|$)"  # end of the line or space before facet
)

_extra_or_prefix = "ext_or_facet_extra_or_"

CONFIG_ORS = "ckanext.or_facet.optional"
CONFIG_LEGACY_ORS = "or_facet.or_facets"


def or_facet_switcher_prefix():
    return _extra_or_prefix


def or_facet_or_enabled(type, params={}):
    state = _get_extra_ors_state(params)
    return state.get(type, type in _get_default_ors())


def _get_default_ors():
    return tk.aslist(tk.config.get(CONFIG_ORS) or tk.config.get(CONFIG_LEGACY_ORS))


def _get_extra_ors_state(extras):
    padding = len(_extra_or_prefix)
    return {
        key[padding:]: tk.asbool(v)
        for key, v in extras.items()
        if key.startswith(_extra_or_prefix)
    }


def _split_fq(fq, field):
    exp = re.compile(_term_pattern.format(field=field))
    fqs = [match.group(0).strip() for match in exp.finditer(fq)]

    if not fqs:
        return None, fq
    fq = exp.sub("", fq).strip()
    extracted = "{!edismax q.op=OR tag=orFq%s}" % field + " ".join(fqs)
    return extracted, fq


class OrFacetPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, "templates")

    # ITemplateHelpers

    def get_helpers(self):
        return {
            "or_facet_switcher_prefix": or_facet_switcher_prefix,
            "or_facet_or_enabled": or_facet_or_enabled,
        }

    # IPackageController

    def before_dataset_search(self, search_params):
        fl = search_params.setdefault("facet.field", [])
        fq_list = search_params.setdefault("fq_list", [])
        fq = search_params.get("fq", "")
        ors = set(_get_default_ors())

        for field, enabled in _get_extra_ors_state(
            search_params.get("extras", {})
        ).items():
            if enabled:
                ors.add(field)
            elif field in ors:
                ors.remove(field)

        for field in ors:
            extracted, fq = _split_fq(fq, field)
            if extracted:
                fq_list.append(extracted)

        search_params["facet.field"] = [
            "{!edismax ex=orFq%s}" % field + field if field in ors else field for field in fl
        ]
        search_params["fq"] = fq

        return search_params

    before_search = before_dataset_search


if tk.check_ckan_version("2.10"):
    tk.blanket.config_declarations(OrFacetPlugin)
