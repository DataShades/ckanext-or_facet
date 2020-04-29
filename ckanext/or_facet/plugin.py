# -*- coding: utf-8 -*-

import re

import ckan.plugins as plugins
import ckantoolkit as tk

_term_pattern = r'(^|(?<=\s)){field}:(\'|")?(?P<term>.+?)(\1|\1|)(?=\s|$)'


def _get_ors():
    return tk.aslist(tk.config.get('or_facet.or_facets'))


def _split_fq(fq, field):
    exp = re.compile(_term_pattern.format(field=field))
    fqs = [
        fq.group(0).strip()
        for fq in
        exp.finditer(fq)
    ]

    if not fqs:
        return None, fq
    fq = exp.sub('', fq).strip()
    extracted = '{!q.op=OR tag=orFq%s}' % field + ' '.join(fqs)
    return extracted, fq


class OrFacetPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IPackageController, inherit=True)

    # IPackageController

    def before_search(self, search_params):
        fl = search_params.setdefault('facet.field', [])
        fq_list = search_params.setdefault('fq_list', [])
        fq = search_params.get('fq', '')
        ors = _get_ors()

        for field in ors:
            extracted, fq = _split_fq(fq, field)
            if extracted:
                fq_list.append(extracted)

        fl[:] = [
            '{!ex=orFq%s}' % field + field
            if field in ors
            else field
            for field in fl
        ]
        search_params['fq'] = fq

        return search_params