
import logging
import os
import types
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Iterable, Iterator, Union, get_args, get_origin, get_type_hints, override
from unittest.mock import patch

from pydantic import ValidationError

from paperap.models.abstract import BaseModel, BaseQuerySet, StandardModel
from paperap.models.correspondent import Correspondent
from paperap.models.custom_field import CustomField
from paperap.models.document import Document
from paperap.models.document_type import DocumentType
from paperap.models.profile import Profile
from paperap.models.saved_view import SavedView
from paperap.models.share_links import ShareLinks
from paperap.models.storage_path import StoragePath
from paperap.models.tag import Tag
from paperap.models.task import Task
from paperap.models.ui_settings import UISettings
from paperap.models.user import Group, User
from paperap.models.workflow import Workflow, WorkflowAction, WorkflowTrigger
from paperap.resources.base import BaseResource, StandardResource
from tests.lib import UnitTestCase
from tests.lib.factories import *

logger = logging.getLogger(__name__)

class ModelTestCase(UnitTestCase):
    MAX_RECURSION_DEPTH = 2
    model_to_resource : dict[type[BaseModel], BaseResource]
    model_to_factories : dict[type[BaseModel], type[PydanticFactory]]

    @override
    def setUp(self):
        super().setUp()
        self.model_to_resource = {
            Correspondent: self.client.correspondents,
            CustomField: self.client.custom_fields,
            Document: self.client.documents,
            DocumentType: self.client.document_types,
            #Profile: self.client.profile,
            SavedView: self.client.saved_views,
            ShareLinks: self.client.share_links,
            StoragePath: self.client.storage_paths,
            Tag: self.client.tags,
            #Task: self.client.tasks,
            User: self.client.users,
            Group: self.client.groups,
            Workflow: self.client.workflows,
            WorkflowAction: self.client.workflow_actions,
            WorkflowTrigger: self.client.workflow_triggers,
        }
        self.model_to_factories = { # type: ignore
            Correspondent: CorrespondentFactory,
            CustomField: CustomFieldFactory,
            Document: DocumentFactory,
            DocumentType: DocumentTypeFactory,
            Profile: ProfileFactory,
            SavedView: SavedViewFactory,
            ShareLinks: ShareLinksFactory,
            StoragePath: StoragePathFactory,
            Tag: TagFactory,
            Task: TaskFactory,
            User: UserFactory,
            Group: GroupFactory,
            Workflow: WorkflowFactory,
            WorkflowAction: WorkflowActionFactory,
            WorkflowTrigger: WorkflowTriggerFactory,
        }

    def get_sample_value(self, type_hint, depth: int = 0) -> Any:
        if depth > self.MAX_RECURSION_DEPTH:
            return None
        if type_hint is None or type_hint is type(None):
            return None
        origin = get_origin(type_hint)
        if origin is Union:
            args = get_args(type_hint)
            for arg in args:
                if arg is not type(None):
                    return self.get_sample_value(arg, depth)
            return None
        if isinstance(type_hint, type) and issubclass(type_hint, BaseModel):
            return self.generate_sample_data_manual(type_hint, depth + 1)
        if type_hint is str:
            return "Sample String"
        elif type_hint is int:
            return 1
        elif type_hint is float:
            return 1.0
        elif type_hint is bool:
            return True
        elif type_hint is datetime:
            return "2025-01-01T12:00:00Z"
        if origin is list:
            item_type = get_args(type_hint)[0]
            if isinstance(item_type, type) and issubclass(item_type, BaseModel):
                return [self.generate_sample_data_manual(item_type, depth + 1)]
            return [self.get_sample_value(item_type, depth)]
        if origin is dict:
            key_type, value_type = get_args(type_hint)
            return {self.get_sample_value(key_type, depth): self.get_sample_value(value_type, depth)}
        return None

    def generate_sample_data(self, model_class : type["BaseModel"], factory : type[PydanticFactory], depth : int = 0) -> dict[str, Any]:
        _instance = factory.build()
        return _instance.to_dict()

    def generate_sample_data_manual(self, model_class, depth: int = 0) -> dict[str, Any]:
        sample_data: dict[str, Any] = {}
        if depth == 0:
            sample_data = {"id": 1}
        try:
            hints = get_type_hints(model_class)
            for attr_name, type_hint in hints.items():
                if attr_name.startswith('_'):
                    continue
                sample_data[attr_name] = self.get_sample_value(type_hint, depth)
        except Exception as ex:
            logger.exception("Error generating sample data for %s: %s", model_class.__name__, ex)
            common_fields = {
                "name": "Sample Name",
                "title": "Sample Title",
                "content": "Sample Content",
                "description": "Sample Description",
                "slug": "sample-slug",
                "enabled": True,
                "active": True,
                "tag_ids": [1, 2, 3],
                "correspondent_id": 1,
                "document_type_id": 1,
                "storage_path": 1,
            }
            sample_data.update(common_fields)
        return sample_data

    def _get_model_fields(self, model: BaseModel) -> dict[str, Iterable[type]]:
        hints = model.__annotations__
        fields = {}
        for field, type_hint in hints.items():
            model_types = []
            if isinstance(type_hint, types.UnionType) or get_origin(type_hint) is Union:
                args = get_args(type_hint)
                model_types.extend(args)
            else:
                model_types.append(type_hint)
            fields[field] = model_types
        return fields

class TestModelFromDict(ModelTestCase):
    def test_all_models_from_dict(self):
        for model_class, factory in self.model_to_factories.items():
            with self.subTest(model=model_class.__name__):
                sample_data = self.generate_sample_data(model_class, factory)
                try:
                    model = model_class.from_dict(sample_data)
                except Exception as ex:
                    logger.exception("from_dict failed for %s with data: %s", model_class.__name__, sample_data)
                    self.fail(f"Failed to instantiate {model_class.__name__}.from_dict: {ex}")

                self.assertIsInstance(model, model_class, f"Expected {model_class.__name__}, got {type(model)}")
                if pk := getattr(model, 'id', None):
                    self.assertEqual(pk, sample_data.get("id"), f"{model_class.__name__} id mismatch")

                model_fields = self._get_model_fields(model)

                for date_field in ['created', 'added']:
                    if hasattr(model, date_field) and date_field in sample_data:
                        # Allow None
                        if sample_data[date_field] is None:
                            continue

                        field_value = getattr(model, date_field)
                        self.assertIsInstance(field_value, datetime, f"{model_class.__name__}.{date_field} should be datetime")

                for attr_name, expected_value in sample_data.items():
                    if attr_name in ['id', 'created', 'added']:
                        continue
                    if hasattr(model, attr_name):
                        field_types = model_fields.get(attr_name, [])
                        if expected_value is None or type(None) in field_types:
                            continue
                        actual_value = getattr(model, attr_name)
                        self.assertIsNotNone(actual_value, f"{model_class.__name__}.{attr_name} was not set correctly. Expected {expected_value}, got {actual_value}")

    def test_invalid_field_types(self):
        for model_class, factory in self.model_to_factories.items():
            with self.subTest(model=model_class.__name__):
                sample_data = self.generate_sample_data(model_class, factory)
                hints = model_class.__annotations__
                for attr, type_hint in hints.items():
                    if attr.startswith('_'):
                        continue
                    # Test only for fields that are not optional
                    field_types = get_args(type_hint) if get_origin(type_hint) is Union else (type_hint,)
                    if type(None) in field_types:
                        continue
                    # For an int field, set a string value
                    if int in field_types:
                        original = sample_data.get(attr)
                        sample_data[attr] = "invalid"
                        with self.assertRaises(ValueError, msg=f"{model_class.__name__} should raise ValueError for field {attr}"):
                            model_class.from_dict(sample_data)
                        sample_data[attr] = original
                        break

    def test_all_models_to_dict(self):
        for model_class, factory in self.model_to_factories.items():
            with self.subTest(model=model_class.__name__):
                sample_data = self.generate_sample_data(model_class, factory)
                model = model_class.from_dict(sample_data)

                model_dict = model.to_dict(exclude_none=False, exclude_unset=False, include_read_only=True)
                missing = set(sample_data.keys()) - set(model_dict.keys())
                self.assertFalse(missing, f"{model_class.__name__}.to_dict missing keys: {missing}")

class TestRequest(ModelTestCase):

    def test_request(self):
        for model_class, resource in self.model_to_resource.items():
            #with self.subTest(model=model_class.__name__):
                models = self.list_resource(resource) # type: ignore
                self.assertIsInstance(models, BaseQuerySet, f"Expected BaseQuerySet after list, got {type(models)}")
                total = models.count()
                self.assertIsInstance(total, int, f"Expected int for count, got {type(total)}")

                count = 0
                for model in models:
                    count += 1
                    self.assertIsInstance(model, model_class, f"Expected {model_class.__name__}, got {type(model)}")
                    if hasattr(model, 'id'):
                        self.assertIsInstance(model.id, int, f"{model_class.__name__}.id should be int")
                    model_fields = self._get_model_fields(model)
                    for date_field in ['created', 'added']:
                        if hasattr(model, date_field):
                            field_value = getattr(model, date_field)
                            if field_value is not None:
                                self.assertIsInstance(field_value, datetime, f"{model_class.__name__}.{date_field} should be datetime")
                    for attr_name, _expected_value in model.to_dict().items():
                        if attr_name in ['id', 'created', 'added']:
                            continue
                        if hasattr(model, attr_name):
                            field_types = model_fields.get(attr_name, [])
                            if type(None) in field_types:
                                continue
                            actual_value = getattr(model, attr_name)
                            self.assertIsNotNone(actual_value, f"{model_class.__name__}.{attr_name} was not set correctly")
                    break

                self.assertGreater(count, 0, f"Expected to iterate over at least one {model_class.__name__}")
                return

    """
    # WIP
    def test_request_item(self):
        for model_class, resource in self.model_to_resource.items():
            with self.subTest(model=model_class.__name__):
                if not (response := request_or_load_data(f"{resource.name}_item.json", resource._request_raw, 1)):
                    self.fail(f"Failed to get sample data for {resource.name}")
                model = resource._handle_response(response)
                self.assertIsInstance(model, model_class, f"Expected {model_class.__name__}, got {type(model)}")
                if hasattr(model, 'id'):
                    self.assertEqual(model.id, 1, f"{model_class.__name__}.id mismatch")
                model_fields = self._get_model_fields(model)
                for date_field in ['created', 'added']:
                    if hasattr(model, date_field):
                        field_value = getattr(model, date_field)
                        self.assertIsInstance(field_value, datetime, f"{model_class.__name__}.{date_field} should be datetime")
                for attr_name, expected_value in model.to_dict().items():
                    if attr_name in ['id', 'created', 'added']:
                        continue
                    if hasattr(model, attr_name):
                        field_types = model_fields.get(attr_name, [])
                        if type(None) in field_types:
                            continue
                        actual_value = getattr(model, attr_name)
                        self.assertIsNotNone(actual_value, f"{model_class.__name__}.{attr_name} was not set correctly")
    """
