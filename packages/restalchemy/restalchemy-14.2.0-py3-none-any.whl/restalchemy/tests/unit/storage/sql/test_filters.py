# Copyright 2018 Eugene Frolov <eugene@frolov.net.ru>
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from collections import OrderedDict
import uuid

from urllib3._collections import HTTPHeaderDict

from restalchemy.dm import filters as dm_filters
from restalchemy.dm import models
from restalchemy.dm import properties
from restalchemy.dm import relationships
from restalchemy.dm import types
from restalchemy.storage.sql import filters
from restalchemy.storage.sql import orm
from restalchemy.tests.unit import base
from restalchemy.tests.unit.storage.sql import common
from restalchemy.tests import fixtures


TEST_NAME = "FAKE_NAME"
TEST_VALUE = "FAKE_VALUE"
TEST_UUID = uuid.UUID("89d423c5-4365-4be2-bde9-2730909a9af8")


class BaseModel(models.Model):

    name1 = properties.property(types.Integer())
    name2 = properties.property(types.Integer())


class BaseModelWithUUID(BaseModel, models.ModelWithUUID, orm.SQLStorableMixin):
    pass


class BaseModelWithRelation(BaseModel, models.ModelWithUUID):
    parent = relationships.relationship(BaseModelWithUUID)


class EQTestCase(base.BaseTestCase):

    def setUp(self):
        self._expr = filters.EQ(
            column=TEST_NAME,
            value_type=common.AsIsType(),
            value=TEST_VALUE,
            session=fixtures.SessionFixture(),
        )

    def test_construct_expression(self):

        result = self._expr.construct_expression()

        self.assertEqual(TEST_NAME + " = %s", result)

    def test_value_property(self):
        self.assertEqual(self._expr.value, TEST_VALUE)


class NETestCase(base.BaseTestCase):

    def setUp(self):
        self._expr = filters.NE(
            column=TEST_NAME,
            value_type=common.AsIsType(),
            value=TEST_VALUE,
            session=fixtures.SessionFixture(),
        )

    def test_construct_expression(self):

        result = self._expr.construct_expression()

        self.assertEqual(TEST_NAME + " <> %s", result)

    def test_value_property(self):
        self.assertEqual(self._expr.value, TEST_VALUE)


class GTTestCase(base.BaseTestCase):

    def setUp(self):
        self._expr = filters.GT(
            column=TEST_NAME,
            value_type=common.AsIsType(),
            value=TEST_VALUE,
            session=fixtures.SessionFixture(),
        )

    def test_construct_expression(self):

        result = self._expr.construct_expression()

        self.assertEqual(TEST_NAME + " > %s", result)

    def test_value_property(self):
        self.assertEqual(self._expr.value, TEST_VALUE)


class GETestCase(base.BaseTestCase):

    def setUp(self):
        self._expr = filters.GE(
            column=TEST_NAME,
            value_type=common.AsIsType(),
            value=TEST_VALUE,
            session=fixtures.SessionFixture(),
        )

    def test_construct_expression(self):

        result = self._expr.construct_expression()

        self.assertEqual(TEST_NAME + " >= %s", result)

    def test_value_property(self):
        self.assertEqual(self._expr.value, TEST_VALUE)


class LTTestCase(base.BaseTestCase):

    def setUp(self):
        self._expr = filters.LT(
            column=TEST_NAME,
            value_type=common.AsIsType(),
            value=TEST_VALUE,
            session=fixtures.SessionFixture(),
        )

    def test_construct_expression(self):

        result = self._expr.construct_expression()

        self.assertEqual(TEST_NAME + " < %s", result)

    def test_value_property(self):
        self.assertEqual(self._expr.value, TEST_VALUE)


class LETestCase(base.BaseTestCase):

    def setUp(self):
        self._expr = filters.LE(
            column=TEST_NAME,
            value_type=common.AsIsType(),
            value=TEST_VALUE,
            session=fixtures.SessionFixture(),
        )

    def test_construct_expression(self):

        result = self._expr.construct_expression()

        self.assertEqual(TEST_NAME + " <= %s", result)

    def test_value_property(self):
        self.assertEqual(self._expr.value, TEST_VALUE)


class InTestCase(base.BaseTestCase):

    TEST_LIST_VALUES = [1, 2, 3]

    def setUp(self):
        self._expr = filters.MySqlIn(
            column=TEST_NAME,
            value_type=common.AsIsType(),
            value=self.TEST_LIST_VALUES,
            session=fixtures.SessionFixture(),
        )

    def test_construct_expression(self):

        result = self._expr.construct_expression()

        self.assertEqual(TEST_NAME + " IN %s", result)

    def test_value_property(self):
        self.assertEqual(self._expr.value, self.TEST_LIST_VALUES)


class NotInTestCase(base.BaseTestCase):

    TEST_LIST_VALUES = [1, 2, 3]

    def setUp(self):
        self._expr = filters.MySqlNotIn(
            column=TEST_NAME,
            value_type=common.AsIsType(),
            value=self.TEST_LIST_VALUES,
            session=fixtures.SessionFixture(),
        )

    def test_construct_expression(self):

        result = self._expr.construct_expression()

        self.assertEqual(TEST_NAME + " NOT IN %s", result)

    def test_value_property(self):
        self.assertEqual(self._expr.value, self.TEST_LIST_VALUES)


class InEmptyListTestCase(base.BaseTestCase):

    def setUp(self):
        self._expr = filters.MySqlIn(
            column=TEST_NAME,
            value_type=common.AsIsType(),
            value=[],
            session=fixtures.SessionFixture(),
        )

    def test_construct_expression(self):

        result = self._expr.construct_expression()

        self.assertEqual(TEST_NAME + " IN %s", result)

    def test_value_property(self):
        self.assertEqual(self._expr.value, [None])


class IsTestCase(base.BaseTestCase):

    def setUp(self):
        self._expr = filters.Is(
            column=TEST_NAME,
            value_type=common.AsIsType(),
            value=TEST_VALUE,
            session=fixtures.SessionFixture(),
        )

    def test_construct_expression(self):

        result = self._expr.construct_expression()

        self.assertEqual(TEST_NAME + " IS %s", result)

    def test_value_property(self):
        self.assertEqual(self._expr.value, TEST_VALUE)


class IsNotTestCase(base.BaseTestCase):

    def setUp(self):
        self._expr = filters.IsNot(
            column=TEST_NAME,
            value_type=common.AsIsType(),
            value=TEST_VALUE,
            session=fixtures.SessionFixture(),
        )

    def test_construct_expression(self):

        result = self._expr.construct_expression()

        self.assertEqual(TEST_NAME + " IS NOT %s", result)

    def test_value_property(self):
        self.assertEqual(self._expr.value, TEST_VALUE)


class IsPgTestCase(base.BaseTestCase):

    def setUp(self):
        self._expr = filters.PostgreSqlIs(
            column=TEST_NAME,
            value_type=common.AsIsType(),
            value=TEST_VALUE,
            session=fixtures.SessionFixture(),
        )

    def test_construct_expression(self):

        result = self._expr.construct_expression()

        self.assertEqual(TEST_NAME + " IS NOT DISTINCT FROM (%s)", result)

    def test_value_property(self):
        self.assertEqual(self._expr.value, TEST_VALUE)


class IsNotPgTestCase(base.BaseTestCase):

    def setUp(self):
        self._expr = filters.PostgreSqlIsNot(
            column=TEST_NAME,
            value_type=common.AsIsType(),
            value=TEST_VALUE,
            session=fixtures.SessionFixture(),
        )

    def test_construct_expression(self):

        result = self._expr.construct_expression()

        self.assertEqual(TEST_NAME + " IS DISTINCT FROM (%s)", result)

    def test_value_property(self):
        self.assertEqual(self._expr.value, TEST_VALUE)


class LikeTestCase(base.BaseTestCase):

    def setUp(self):
        self._expr = filters.Like(
            column=TEST_NAME,
            value_type=common.AsIsType(),
            value=TEST_VALUE,
            session=fixtures.SessionFixture(),
        )

    def test_construct_expression(self):

        result = self._expr.construct_expression()

        self.assertEqual(TEST_NAME + " LIKE %s", result)

    def test_value_property(self):
        self.assertEqual(self._expr.value, TEST_VALUE)


class NotLikeTestCase(base.BaseTestCase):

    def setUp(self):
        self._expr = filters.NotLike(
            column=TEST_NAME,
            value_type=common.AsIsType(),
            value=TEST_VALUE,
            session=fixtures.SessionFixture(),
        )

    def test_construct_expression(self):

        result = self._expr.construct_expression()

        self.assertEqual(TEST_NAME + " NOT LIKE %s", result)

    def test_value_property(self):
        self.assertEqual(self._expr.value, TEST_VALUE)


class ConvertFiltersTestCase(base.BaseTestCase):

    def test_convert_filters_new(self):
        d = OrderedDict()
        d["name1"] = dm_filters.EQ(1)
        d["name2"] = dm_filters.EQ(2)
        filter_list = dm_filters.AND(d)

        processed = filters.convert_filters(
            BaseModel,
            filter_list,
            session=fixtures.SessionFixture(),
        )

        self.assertEqual(
            "(`name1` = %s AND `name2` = %s)", processed.construct_expression()
        )
        self.assertEqual([1, 2], processed.value)

    def test_convert_filters_new_separate_dicts(self):
        filter_list = dm_filters.AND(
            {"name1": dm_filters.EQ(1)}, {"name2": dm_filters.EQ(2)}
        )

        processed = filters.convert_filters(
            BaseModel,
            filter_list,
            session=fixtures.SessionFixture(),
        )

        self.assertEqual(
            "(`name1` = %s AND `name2` = %s)", processed.construct_expression()
        )
        self.assertEqual([1, 2], processed.value)

    def test_convert_filters_new_nested(self):
        d = OrderedDict()
        d["name1"] = dm_filters.EQ(1)
        d["name2"] = dm_filters.EQ(2)
        filter_list = dm_filters.OR(
            dm_filters.AND(d), dm_filters.AND({"name2": dm_filters.EQ(2)})
        )

        processed = filters.convert_filters(
            BaseModel,
            filter_list,
            session=fixtures.SessionFixture(),
        )

        self.assertEqual(
            "((`name1` = %s AND `name2` = %s) OR `name2` = %s)",
            processed.construct_expression(),
        )
        self.assertEqual([1, 2, 2], processed.value)

    def test_convert_filters_old(self):
        d = OrderedDict()
        d["name1"] = dm_filters.EQ(1)
        d["name2"] = dm_filters.EQ(2)
        filter_list = d

        processed = filters.convert_filters(
            BaseModel,
            filter_list,
            session=fixtures.SessionFixture(),
        )

        self.assertEqual(
            "(`name1` = %s AND `name2` = %s)", processed.construct_expression()
        )
        self.assertEqual([1, 2], processed.value)

    def test_convert_filters_old_multidict(self):
        d = HTTPHeaderDict()
        d.add("name1", dm_filters.EQ(1))
        d.add("name1", dm_filters.EQ(1))
        filter_list = d

        processed = filters.convert_filters(
            BaseModel,
            filter_list,
            session=fixtures.SessionFixture(),
        )

        self.assertEqual(
            "(`name1` = %s AND `name1` = %s)", processed.construct_expression()
        )
        self.assertEqual([1, 1], processed.value)

    def test_convert_filters_new_relationship_by_model(self):
        model = BaseModelWithUUID(name1=1, name2=2, uuid=TEST_UUID)
        filter_list = {"parent": dm_filters.EQ(model)}

        processed = filters.convert_filters(
            BaseModelWithRelation,
            filter_list,
            session=fixtures.SessionFixture(),
        )

        self.assertEqual("`parent` = %s", processed.construct_expression())
        self.assertEqual([str(TEST_UUID)], processed.value)

    def test_convert_filters_new_relationship_by_id(self):
        filter_list = {"parent": dm_filters.EQ(TEST_UUID)}

        processed = filters.convert_filters(
            BaseModelWithRelation,
            filter_list,
            session=fixtures.SessionFixture(),
        )

        self.assertEqual("`parent` = %s", processed.construct_expression())
        self.assertEqual([str(TEST_UUID)], processed.value)
