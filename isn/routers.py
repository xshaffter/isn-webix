from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns


class WebixRouter(DefaultRouter):
    # noinspection PyProtectedMember
    def get_urls(self):
        ret = []
        for prefix, viewset, basename in self.registry:
            lookup = self.get_lookup_regex(viewset)
            routes = self.get_routes(viewset)
            for route in routes:
                mapping = self.get_method_map(viewset, route.mapping)
                if not mapping:
                    continue
                regex = route.url.format(
                    prefix=prefix,
                    lookup=lookup,
                    trailing_slash=self.trailing_slash
                )
                if not prefix and regex[:2] == '^/':
                    regex = '^' + regex[2:]
                view = viewset.as_view(mapping, **route.initkwargs)
                name = route.name.format(basename=basename)
                ret.append(url(regex, view, name=name))
            if issubclass(viewset, WebixModelViewSet):
                model = viewset.queryset.model
                ret += [
                    url(u'^{}/choice_field/{}/$'.format(prefix, field.attname),
                        viewset.as_view(
                            dict(get="{}_choice_field_{}".format(model._meta.model_name, field.attname)),
                            **dict()),
                        name="{}-choice_field_{}".format(basename, field.attname)
                        ) for field in model._meta.fields if len(field.choices) > 0
                ]
        if self.include_root_view:
            if hasattr(self, 'schema_title'):
                view = self.get_schema_root_view(api_urls=ret)
            else:
                view = self.get_api_root_view(api_urls=ret)
            root_url = url(r'^$', view, name=self.root_view_name)
            ret.append(root_url)
        if self.include_format_suffixes:
            ret = format_suffix_patterns(ret)
        return ret