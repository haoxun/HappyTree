from __future__ import unicode_literals
def gen_models_debug_info(model_set):
    import cgi
    from django.utils.safestring import mark_safe
    def wrap_sth(sth, foot=None):
        if foot == None:
            foot = sth
        def _wrap(target):
            return "<{0}>{1}</{2}>".format(sth, unicode(target), foot)
        return _wrap
    printed_models = []
    for model in model_set:
        field_set = model._meta.get_all_field_names()
        printed_objects = []
        for instance in model.objects.all():
            printed_instance = []
            for field in field_set:
                try:
                    val = getattr(instance, field)
                except:
                    try:
                        val = getattr(instance, field + '_set')
                    except:
                        val = None
                # deal with many-to-many, many-to-one situation
                if val.__class__.__name__ in ['ManyRelatedManager', 'RelatedManager']:
                    related_instances = [cgi.escape(unicode(related_instance)) \
                                            for related_instance in val.all()]
                    val = "<br/>".join(related_instances)
                else:
                    val = cgi.escape(unicode(val))
                printed_instance.append(val)
            printed_objects.append("".join(map(wrap_sth('td'),
                                               printed_instance)))

        # model name
        printed_model_name = wrap_sth('h3')(cgi.escape(unicode(model)))
        # model header
        printed_fields = "".join(map(wrap_sth('th'),
                                     map(cgi.escape, field_set)))
        printed_fields = wrap_sth('tr')(printed_fields)
        printed_fields = wrap_sth('thead')(printed_fields)
        # model instance
        printed_instances = "".join(map(wrap_sth('tr'),
                                        printed_objects))
        printed_instances = wrap_sth('tbody')(printed_instances)
        # table
        printed_table = "".join([
                            printed_model_name,
                            printed_fields, 
                            printed_instances])
        printed_table = wrap_sth('table')(printed_table)
        printed_models.append(printed_table)

    return mark_safe("".join(printed_models))

