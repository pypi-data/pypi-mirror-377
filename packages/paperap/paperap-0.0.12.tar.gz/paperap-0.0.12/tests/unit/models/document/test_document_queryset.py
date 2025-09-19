

from __future__ import annotations

import os
import unittest
from datetime import datetime, timezone
from typing import Any, Callable, Iterable, override
from unittest.mock import MagicMock, patch

from paperap.exceptions import FilterDisabledError
from paperap.models import (
    Correspondent,
    CorrespondentQuerySet,
    Document,
    DocumentQuerySet,
    DocumentType,
    DocumentTypeQuerySet,
    Profile,
    ProfileQuerySet,
    StoragePath,
    StoragePathQuerySet,
    Tag,
    TagQuerySet,
    User,
    UserQuerySet,
)
from paperap.resources.documents import DocumentResource
from tests.lib import DocumentUnitTest, UnitTestCase, load_sample_data

sample_document_list = load_sample_data('documents_list.json')
sample_document = load_sample_data('documents_item.json')

class BaseTest(DocumentUnitTest):
    @override
    def setUp(self):
        super().setUp()
        self.queryset = self.client.documents()

    def _test_no_results(self, fn : Callable, *args, **kwargs : Any):
        sample_data = load_sample_data('documents___list__no_results.json')
        with patch('paperap.client.PaperlessClient.request') as mock_request:
            mock_request.return_value = sample_data
            qs = fn(*args, **kwargs)
            self.assertIsInstance(qs, DocumentQuerySet)
            self.assertEqual(qs.count(), 0, "Expected 0 results")
            for _ in qs:
                self.fail("Should not have any results")

class TestMethodsProcedural(BaseTest):

    def test_method_with_no_results(self):
        test_cases = [
            (self.queryset.correspondent_id, 1),
            (self.queryset.correspondent_slug, 'example-correspondent'),
            (self.queryset.correspondent_name, 'Example Correspondent'),
            (self.queryset.tag_id, 179),
            #(self.queryset.tag_slug, 'example-tag'),
            (self.queryset.tag_name, 'Example Tag'),
            (self.queryset.title, 'Example Title'),
            (self.queryset.content, 'Example Content'),
            (self.queryset.added_before, '2025-01-01'),
            (self.queryset.added_after, '2025-01-01'),
            (self.queryset.created_before, '2025-01-01'),
            (self.queryset.created_after, '2025-01-01'),
            (self.queryset.document_type_id, 8),
            (self.queryset.storage_path_id, 1),
        ]
        for fn, args in test_cases:
            self._test_no_results(fn, args)

class TestMeta(BaseTest):

    def test_disabled_filters(self):
        disabled_filters = [
            'page_count',
            'deleted_at',
            'is_shared_by_requester'
        ]
        suffixes = [
            "__eq",
            "__range",
            "__lt",
            "__lte",
            "__gt",
            "__gte",
        ]
        for filter_name in disabled_filters:
            for suffix in suffixes:
                with self.subTest(suffix=suffix, filter_name=filter_name):
                    key = f"{filter_name}{suffix}"
                    kwargs = {key: 5}
                    with self.assertRaises(FilterDisabledError, msg=f"Filtering with {suffix} does not raise exception"):
                        self.queryset.filter(**kwargs)

    def test_filtering_fields(self):
        # Non Exhaustive list, just in case the fields change
        expected_fields = [
            # Inherited from StandardModel
            'id',
            'created',
            # Custom Fields for Document
            'content',
            'custom_field_dicts',
            'document_type_id',
            'tag_ids',
            'title',
        ]
        for field_name in expected_fields:
            with self.subTest(field_name=field_name):
                self.assertIn(field_name, Document._meta.filtering_fields) # type: ignore

    def test_read_only_fields(self):
        # Non Exhaustive list, just in case the fields change
        expected_fields = [
            'page_count',
            'deleted_at',
            'is_shared_by_requester',
        ]
        for field_name in expected_fields:
            with self.subTest(field_name=field_name):
                self.assertIn(field_name, Document._meta.read_only_fields) # type: ignore

class TestCorrespondent(BaseTest):

    def test_correspondent(self):
        sample_data = load_sample_data('documents___correspondent__21.json')
        self.assert_queryset_callback_patched(
            queryset = lambda: self.queryset.correspondent_id(21),
            sample_data = sample_data,
            callback = lambda doc: doc.correspondent_id == 21
        )
        self.assert_queryset_callback_patched(
            queryset = lambda: self.queryset.correspondent_slug('example-correspondent'),
            sample_data = sample_data,
            callback = lambda doc: doc.correspondent_id == 21
        )
        self.assert_queryset_callback_patched(
            queryset = lambda: self.queryset.correspondent_name('Example Correspondent'),
            sample_data = sample_data,
            callback = lambda doc: doc.correspondent_id == 21
        )

    def test_correspondent_kwargs(self):
        test_cases = [
            {"id": 21},
            {"slug": "example-correspondent"},
            {"name": "Example Correspondent"},
        ]
        sample_data = load_sample_data('documents___correspondent__21.json')
        with patch('paperap.client.PaperlessClient.request') as mock_request:
            mock_request.return_value = sample_data
            for kwargs in test_cases:
                qs = self.queryset.correspondent(**kwargs) # type: ignore
                self.assertIsInstance(qs, DocumentQuerySet)
                for document in qs:
                    self.assertIsInstance(document, Document)
                    self.assertIsInstance(document.correspondent_id, int)
                    self.assertEqual(document.correspondent_id, 21)

    def test_correspondent_args(self):
        test_cases = [
            21,
            "Example Correspondent",
        ]
        sample_data = load_sample_data('documents___correspondent__21.json')
        with patch('paperap.client.PaperlessClient.request') as mock_request:
            mock_request.return_value = sample_data
            for arg in test_cases:
                qs = self.queryset.correspondent(arg)
                self.assertIsInstance(qs, DocumentQuerySet)
                for document in qs:
                    self.assertIsInstance(document, Document)
                    self.assertIsInstance(document.correspondent_id, int)
                    self.assertEqual(document.correspondent_id, 21)

    def test_correspondent_arg_and_kwargs(self):
        sample_data = load_sample_data('documents___correspondent__21.json')
        with patch('paperap.client.PaperlessClient.request') as mock_request:
            mock_request.return_value = sample_data
            qs = self.queryset.correspondent(21, slug="example-correspondent")
            self.assertIsInstance(qs, DocumentQuerySet)
            for document in qs:
                self.assertIsInstance(document, Document)
                self.assertIsInstance(document.correspondent_id, int)
                self.assertEqual(document.correspondent_id, 21)

    def test_correspondent_no_params(self):
        with self.assertRaises(ValueError):
            self.queryset.correspondent()

class BaseQuerySetTest(BaseTest):

    """Base test class with common queryset test logic."""

    def assert_queryset_results(
        self,
        method : Callable[..., DocumentQuerySet],
        arg : Any,
        sample_data : dict[str, Any],
        expected_count : int | None = None,
        key : str | None = None,
        condition : Callable[..., bool] | None = None
    ):
        """
        Generic method to test queryset filtering.

        Args:
            method: The queryset method to call.
            arg: The argument for the method.
            sample_data: Mocked API response data.
            expected_count: Expected count of results.
            key: Attribute to check in documents (optional).
            condition: Callable to apply on key (optional).

        """
        if expected_count is None:
            expected_count = int(sample_data['count'])
        expected_iterations = min(expected_count, 6)

        with patch('paperap.client.PaperlessClient.request') as mock_request:
            mock_request.return_value = sample_data
            qs = method(arg)
            self.assertIsInstance(qs, DocumentQuerySet)
            self.assertEqual(qs.count(), expected_count)

            count = 0
            for document in qs:
                count += 1
                self.assertIsInstance(document, Document)
                if key and condition:
                    value = getattr(document, key)
                    self.assertTrue(condition(value), f"Condition failed for {key} with {value}")

                # Check multiple results, but avoid paging
                if count > 5:
                    break

            self.assertEqual(count, expected_iterations, f"Documents iteration unexpected. Count: {expected_count} -> Expected {expected_iterations} iterations, got {count}.")

    def _test_date_filter(self, method, file, date_str, key, comparator):
        """
        Helper function for date filtering tests.

        Args:
            method: Queryset method for filtering.
            file: Sample data file name.
            date_str: Date string in YYYY-MM-DD format.
            key: Document attribute to check.
            comparator: Function comparing document date to reference date.

        """
        sample_data = load_sample_data(file)
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        self.assert_queryset_results(
            method,
            date_str,
            sample_data,
            sample_data['count'],
            key=key,
            condition=lambda d: comparator(d, date_obj) # type: ignore
        )

class TestTag(BaseQuerySetTest):
    def test_tag(self):
        sample_data = load_sample_data('documents___tags__179.json')
        self.assert_queryset_callback_patched(
            queryset = lambda: self.queryset.tag_id(179),
            sample_data = sample_data,
            callback = lambda doc: 179 in doc.tag_ids
        )
        self.assert_queryset_callback_patched(
            queryset = lambda: self.queryset.tag_name('Example Tag'),
            sample_data = sample_data,
            callback = lambda doc: 179 in doc.tag_ids
        )

class TestTitle(BaseQuerySetTest):
    def test_title_iexact(self):
        sample_data = load_sample_data('documents___title__example-title.json')
        self.assert_queryset_callback_patched(
            queryset = lambda: self.queryset.title("example-title"),
            sample_data = sample_data,
            callback = lambda doc: doc.title.lower() == "example-title"
        )

class TestDocumentType(BaseQuerySetTest):
    def test_document_type_id(self):
        sample_data = load_sample_data('documents___document_type__8.json')
        self.assert_queryset_callback_patched(
            queryset = lambda: self.queryset.document_type_id(8),
            sample_data = sample_data,
            callback = lambda doc: doc.document_type_id == 8
        )

class TestStoragePath(BaseQuerySetTest):
    def test_storage_path_id(self):
        sample_data = load_sample_data('documents___storage_path__52.json')
        self.assert_queryset_callback_patched(
            queryset = lambda: self.queryset.storage_path_id(52),
            callback = lambda doc: doc.storage_path_id == 52,
            sample_data = sample_data
        )

class TestContent(BaseQuerySetTest):
    def test_content_contains(self):
        sample_data = load_sample_data('documents___content__contains.json')
        search_string = "ample-cont"
        self.assert_queryset_results(
            self.queryset.content,
            search_string,
            sample_data,
            sample_data['count'],
            key="content",
            condition=lambda content: search_string in (content or '') # type: ignore
        )

class TestAdded(BaseQuerySetTest):
    def test_added_before(self):
        self._test_date_filter(
            method=self.queryset.added_before,
            file='documents___added__lt__20250101.json',
            date_str='2025-01-01',
            key="added",
            comparator=lambda d, ref: d < ref # type: ignore
        )

    def test_added_after(self):
        self._test_date_filter(
            method=self.queryset.added_after,
            file='documents___added__gt__20250101.json',
            date_str='2025-01-01',
            key="added",
            comparator=lambda d, ref: d > ref # type: ignore
        )

class TestCreated(BaseQuerySetTest):
    def test_created_before(self):
        self._test_date_filter(
            method=self.queryset.created_before,
            file='documents___created__lt__20250101.json',
            date_str='2025-01-01',
            key="created",
            comparator=lambda d, ref: d < ref # type: ignore
        )

    def test_created_after(self):
        self._test_date_filter(
            method=self.queryset.created_after,
            file='documents___created__gt__20250101.json',
            date_str='2025-01-01',
            key="created",
            comparator=lambda d, ref: d > ref # type: ignore
        )

class TestCustomFields(BaseQuerySetTest):
    def test_search_no_response(self):
        self._test_no_results(self.queryset.custom_field_fullsearch, 'Zoom')

    def test_search(self):
        sample_data = load_sample_data('documents___custom_fields__icontains__zoom.json')
        self.assert_queryset_results(
            self.queryset.custom_field_fullsearch,
            'zoom',
            sample_data,
            sample_data['count']
        )

    def test_has_id(self):
        sample_data = load_sample_data('documents___custom_fields__icontains__zoom.json')
        expected_count = sample_data['count']
        with patch('paperap.client.PaperlessClient.request') as mock_request:
            mock_request.return_value = sample_data
            qs = self.queryset.has_custom_field_id(27)
            self.assertIsInstance(qs, DocumentQuerySet)
            self.assertEqual(qs.count(), expected_count)
            count = 0
            for document in qs:
                count += 1
                self.assertIsInstance(document, Document)
                found_ids = document.custom_field_ids
                self.assertIn(27, found_ids)

                # Avoid requesting next url (infinitely)
                break

            self.assertEqual(count, 1, "Documents were not iterated over.")

    def test_has_ids(self):
        sample_data = load_sample_data('documents___custom_fields__id__in__26,27.json')
        expected_count = sample_data['count']
        with patch('paperap.client.PaperlessClient.request') as mock_request:
            mock_request.return_value = sample_data
            qs = self.queryset.has_custom_field_id([26,27])
            self.assertIsInstance(qs, DocumentQuerySet)
            self.assertEqual(qs.count(), expected_count)
            count = 0
            for document in qs:
                count += 1
                self.assertIsInstance(document, Document)
                found_ids = document.custom_field_ids
                self.assertTrue(any([id in found_ids for id in [26,27]]))

                # Avoid requesting next url (infinitely)
                break

            self.assertEqual(count, 1, "Documents were not iterated over.")

    def test_has_only_ids(self):
        sample_data = load_sample_data('documents___custom_fields__id__all__32,11,12,13,25,28,29,30,31,24,26,23.json')
        ids = [32,11,12,13,25,28,29,30,31,24,26,23]
        expected_count = sample_data['count']
        with patch('paperap.client.PaperlessClient.request') as mock_request:
            mock_request.return_value = sample_data
            qs = self.queryset.has_custom_field_id(ids, exact=True)
            self.assertIsInstance(qs, DocumentQuerySet)
            self.assertEqual(qs.count(), expected_count)
            count = 0
            for document in qs:
                count += 1
                self.assertIsInstance(document, Document)
                found_ids = document.custom_field_ids
                self.assertEqual(found_ids, ids)

                # Avoid requesting next url (infinitely)
                break

            self.assertEqual(count, 1, "Documents were not iterated over.")

    def test_has_only_id(self):
        sample_data = load_sample_data('documents___custom_fields__id__all__32.json')
        expected_count = sample_data['count']
        with patch('paperap.client.PaperlessClient.request') as mock_request:
            mock_request.return_value = sample_data
            qs = self.queryset.has_custom_field_id(32, exact=True)
            self.assertIsInstance(qs, DocumentQuerySet)
            self.assertEqual(qs.count(), expected_count)
            count = 0
            for document in qs:
                count += 1
                self.assertIsInstance(document, Document)
                found_ids = document.custom_field_ids
                self.assertEqual(found_ids, [32])

                # Avoid requesting next url (infinitely)
                break

            self.assertEqual(count, 1, "Documents were not iterated over.")

    def test_normalize_custom_field_query_item(self):
        test_cases = [
            (5,                 '5'),
            (27,                '27'),
            (10.5,              '10.5'),
            (2523.501,          '2523.501'),
            ("bob",             '"bob"'),
            ("https://",        '"https://"'),
            ("USD",             '"USD"'),
            ("2024-07-01",      '"2024-07-01"'),
            ("True",            '"True"'),
            (True,              'true'),
            (False,             'false'),
            (["cAt", "doG"],    '["cAt", "doG"]'),
            ([3, 7],            '[3, 7]'),
            ([42],              '[42]'),
            ([10.5, 20.5],      '[10.5, 20.5]'),
            ([10.5, 20.5, 30.5],'[10.5, 20.5, 30.5]'),
            (["astr", 10, True], '["astr", 10, true]'),
        ]
        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = self.queryset._normalize_custom_field_query_item(value) # type: ignore
                self.assertEqual(result, expected, f'Expected {expected}. Got {result} of type {type(result)}')

    def test_normalize_custom_field_query(self):
        test_cases = [
            (("due", "range", ["2024-08-01", "2024-09-01"]),    '["due", "range", ["2024-08-01", "2024-09-01"]]'),
            (("customer", "exact", "bob"),                      '["customer", "exact", "bob"]'),
            (("answered", "exact", True),                       '["answered", "exact", true]'),
            (("favorite animal", "in", ["cat", "dog"]),         '["favorite animal", "in", ["cat", "dog"]]'),
            (("foo", "exists", False),                          '["foo", "exists", false]'),
            (("references", "contains", [3, 7]),                '["references", "contains", [3, 7]]'),
            (("string_field", "icontains", "partial"),          '["string_field", "icontains", "partial"]'),
            (("url_field", "istartswith", "https://"),          '["url_field", "istartswith", "https://"]'),
            (("money_field", "iendswith", "USD"),               '["money_field", "iendswith", "USD"]'),
            (("integer_field", "gt", 5),                        '["integer_field", "gt", 5]'),
            (("float_field", "lte", 10.5),                      '["float_field", "lte", 10.5]'),
            (("date_field", "gte", "2024-07-01"),               '["date_field", "gte", "2024-07-01"]'),
            (("doc_link", "contains", [42]),                    '["doc_link", "contains", [42]]'),
            (("date_field", "range", ["2024-01-01", "2024-12-31"]), '["date_field", "range", ["2024-01-01", "2024-12-31"]]'),
            (("OR", ["address", "isnull", True], ["address", "exact", ""]), '["OR", ["address", "isnull", true], ["address", "exact", ""]]'),
            (("OR", ("address", "isnull", True), ("address", "exact", "")), '["OR", ["address", "isnull", true], ["address", "exact", ""]]'),
        ]

        count = 0
        for query, expected in test_cases:
            count += 1
            with self.subTest(query=query, expected=expected):
                result = self.queryset._normalize_custom_field_query(query) # type: ignore
                self.assertEqual(result, expected, f'Subtest {count}: Expected {expected}')

    def test_query_exact(self):
        sample_data = load_sample_data('documents___custom_field_query__building__exact__52.json')
        expected_count = sample_data['count']
        with patch('paperap.client.PaperlessClient.request') as mock_request:
            mock_request.return_value = sample_data
            qs = self.queryset.custom_field_query("Building #", "exact", 52)
            self.assertIsInstance(qs, DocumentQuerySet)
            self.assertEqual(qs.count(), expected_count)
            count = 0
            for document in qs:
                count += 1
                self.assertIsInstance(document, Document)
                # Avoid requesting next url (infinitely)
                break

            self.assertEqual(count, 1, "Documents were not iterated over.")

    def test_query_icontains(self):
        sample_data = load_sample_data('documents___custom_field_query__building__icontains__52.json')
        expected_count = sample_data['count']
        with patch('paperap.client.PaperlessClient.request') as mock_request:
            mock_request.return_value = sample_data
            qs = self.queryset.custom_field_query("Building #", "icontains", "52")
            self.assertIsInstance(qs, DocumentQuerySet)
            self.assertEqual(qs.count(), expected_count)
            count = 0
            for document in qs:
                count += 1
                self.assertIsInstance(document, Document)
                # Avoid requesting next url (infinitely)
                break

            self.assertEqual(count, 1, "Documents were not iterated over.")

class TestCustomFieldAccess(BaseQuerySetTest):
    def test_custom_field_noparams(self):
        sample_data = load_sample_data('documents___custom_field_query__building__icontains__52.json')
        expected_count = sample_data['count']
        with patch('paperap.client.PaperlessClient.request') as mock_request:
            mock_request.return_value = sample_data
            qs = self.queryset.custom_field("Building #", 52)
            self.assertIsInstance(qs, DocumentQuerySet)
            self.assertEqual(qs.count(), expected_count)
            count = 0
            for document in qs:
                count += 1
                self.assertIsInstance(document, Document)
                # Avoid requesting next url (infinitely)
                break

        self.assertEqual(count, 1, "Documents were not iterated over.")

    def test_custom_field_exact(self):
        sample_data = load_sample_data('documents___custom_field_query__building__exact__52.json')
        expected_count = sample_data['count']
        with patch('paperap.client.PaperlessClient.request') as mock_request:
            mock_request.return_value = sample_data
            qs = self.queryset.custom_field("Building #", 52, exact=True, case_insensitive=False)
            self.assertIsInstance(qs, DocumentQuerySet)
            self.assertEqual(qs.count(), expected_count)
            count = 0
            for document in qs:
                count += 1
                self.assertIsInstance(document, Document)
                # Avoid requesting next url (infinitely)
                break

        self.assertEqual(count, 1, "Documents were not iterated over.")

    def test_custom_field_iexact(self):
        sample_data = load_sample_data('documents___custom_field_query__building__exact__52.json')
        expected_count = sample_data['count']
        with patch('paperap.client.PaperlessClient.request') as mock_request:
            mock_request.return_value = sample_data
            qs = self.queryset.custom_field("Building #", 52, exact=True)
            self.assertIsInstance(qs, DocumentQuerySet)
            self.assertEqual(qs.count(), expected_count)
            count = 0
            for document in qs:
                count += 1
                self.assertIsInstance(document, Document)
                # Avoid requesting next url (infinitely)
                break

        self.assertEqual(count, 1, "Documents were not iterated over.")

if __name__ == "__main__":
    unittest.main()
