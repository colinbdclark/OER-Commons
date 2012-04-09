

class OERViewMixin(object):

    page_title = None
    breadcrumbs = None

    def get_page_title(self):
        return self.page_title

    def get_breadcrumbs(self):
        return self.breadcrumbs

    def get_context_data(self, **kwargs):
        #noinspection PyUnresolvedReferences
        data = super(OERViewMixin, self).get_context_data(**kwargs)
        data["page_title"] = self.get_page_title()
        data["breadcrumbs"] = self.get_breadcrumbs()
        return data
