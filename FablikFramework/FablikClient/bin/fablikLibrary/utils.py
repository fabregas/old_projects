

def rw_form_only(func):
    def form_method(form_obj, *args, **kvargs):
        if form_obj.isReadOnly():
            return

        return func(form_obj, *args, **kvargs)
    return form_method

