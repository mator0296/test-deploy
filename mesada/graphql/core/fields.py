import json
from functools import partial

from django.db.models.query import QuerySet
from graphene.relay import PageInfo
from graphene_django.fields import DjangoConnectionField
from graphql_relay.connection.arrayconnection import connection_from_list_slice
from promise import Promise

from graphql.error import GraphQLError


class PrefetchingConnectionField(DjangoConnectionField):
    @classmethod
    def connection_resolver(
        cls,
        resolver,
        connection,
        default_manager,
        max_limit,
        enforce_first_or_last,
        root,
        info,
        **args,
    ):

        # Disable `enforce_first_or_last` if not querying for `edges`.
        values = [
            field.name.value for field in info.field_asts[0].selection_set.selections
        ]
        if "edges" not in values:
            enforce_first_or_last = False

        return super().connection_resolver(
            resolver,
            connection,
            default_manager,
            max_limit,
            enforce_first_or_last,
            root,
            info,
            **args,
        )

    @classmethod
    def resolve_connection(cls, connection, default_manager, iterable, *args, **kwargs):
        if iterable is None:
            iterable = default_manager

        if isinstance(iterable, QuerySet):
            _len = iterable.count()
        else:
            _len = len(iterable)

        connection = connection_from_list_slice(
            iterable,
            args,
            slice_start=0,
            list_length=_len,
            list_slice_length=_len,
            connection_type=connection,
            edge_type=connection.Edge,
            pageinfo_type=PageInfo,
        )
        connection.iterable = iterable
        connection.length = _len
        return connection


class FilterInputConnectionField(PrefetchingConnectionField):
    def __init__(self, *args, **kwargs):
        self.filter_field_name = kwargs.pop("filter_field_name", "filter")
        self.filter_input = kwargs.get(self.filter_field_name)
        self.filterset_class = None
        if self.filter_input:
            self.filterset_class = self.filter_input.filterset_class
        super().__init__(*args, **kwargs)

    @classmethod
    def connection_resolver(
        cls,
        resolver,
        connection,
        default_manager,
        queryset_resolver,
        max_limit,
        enforce_first_or_last,
        filterset_class,
        filters_name,
        root,
        info,
        **args,
    ):
        # Disable `enforce_first_or_last` if not querying for `edges`.
        values = [
            field.name.value for field in info.field_asts[0].selection_set.selections
        ]
        if "edges" not in values:
            enforce_first_or_last = False

        first = args.get("first")
        last = args.get("last")

        if enforce_first_or_last and not (first or last):
            raise GraphQLError(
                f"You must provide a `first` or `last` value to properly paginate "
                f"the `{info.field_name}` connection."
            )

        if max_limit:
            if first:
                assert first <= max_limit, (
                    "Requesting {} records on the `{}` connection exceeds the "
                    "`first` limit of {} records."
                ).format(first, info.field_name, max_limit)
                args["first"] = min(first, max_limit)

            if last:
                assert last <= max_limit, (
                    "Requesting {} records on the `{}` connection exceeds the "
                    "`last` limit of {} records."
                ).format(last, info.field_name, max_limit)
                args["last"] = min(last, max_limit)

        iterable = resolver(root, info, **args)

        if iterable is None:
            iterable = default_manager
        # thus the iterable gets refiltered by resolve_queryset
        # but iterable might be promise
        iterable = queryset_resolver(connection, iterable, info, args)

        on_resolve = partial(
            cls.resolve_connection, connection, args, max_limit=max_limit
        )

        filter_input = args.get(filters_name)
        if filter_input and filterset_class:
            instance = filterset_class(
                data=dict(filter_input), queryset=iterable, request=info.context
            )
            # Make sure filter input has valid values
            if not instance.is_valid():
                raise GraphQLError(json.dumps(instance.errors.get_json_data()))
            iterable = instance.qs

        if Promise.is_thenable(iterable):
            return Promise.resolve(iterable).then(on_resolve)
        return on_resolve(iterable)

    def get_resolver(self, parent_resolver):
        return partial(
            super().get_resolver(parent_resolver),
            self.filterset_class,
            self.filter_field_name,
        )
