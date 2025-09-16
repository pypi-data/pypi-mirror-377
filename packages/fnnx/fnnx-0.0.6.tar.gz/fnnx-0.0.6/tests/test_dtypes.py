import unittest
from fnnx.dtypes import FlatList, DtypesManager, NDContainer, BUILTINS

class TestFlatList(unittest.TestCase):

    def test_initialization_with_list(self):
        fl = FlatList([1, 2, 3])
        self.assertEqual(fl.data, [1, 2, 3])

    def test_initialization_with_non_list(self):
        with self.assertRaises(ValueError):
            FlatList("not a list")  # type: ignore

    def test_get_item(self):
        fl = FlatList(["a", "b", "c"])
        self.assertEqual(fl[0], "a")
        self.assertEqual(fl[2], "c")

    def test_set_item(self):
        fl = FlatList([1, 2, 3])
        fl[1] = 200
        self.assertEqual(fl[1], 200)

    def test_append(self):
        fl = FlatList([])
        fl.append(10)
        self.assertEqual(fl.data, [10])

    def test_repr(self):
        fl = FlatList([1, 2])
        self.assertEqual(repr(fl), "FlatList([1, 2])")


class TestDtypesManager(unittest.TestCase):

    def setUp(self):
        self.external_dtypes = {
            "Person": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
                "required": ["name", "age"],
            }
        }
        self.builtins = BUILTINS
        self.manager = DtypesManager(self.external_dtypes, self.builtins)

    def test_get_dtype_existing(self):
        dtype = self.manager.get_dtype("Person")
        self.assertEqual(dtype, self.external_dtypes["Person"])

    def test_get_dtype_non_existing(self):
        with self.assertRaises(ValueError):
            self.manager.get_dtype("UnknownType")

    def test_validate_dtype_valid_data(self):
        data = {"name": "Alice", "age": 30}
        self.manager.validate_dtype("Person", data)

    def test_validate_dtype_invalid_data(self):
        data = {"name": "Alice", "age": "thirty"}
        with self.assertRaises(ValueError):
            self.manager.validate_dtype("Person", data)

    def test_validate_dtype_list_of_data(self):
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        self.manager.validate_dtype("Person", data)

    def test_validate_dtype_flatlist(self):
        data = FlatList([{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}])
        self.manager.validate_dtype("Person", [data])
        self.manager.validate_dtype("Person", [data, data])
        self.manager.validate_dtype("Person", [[data], [data]])

    def test_invalid_dtype_name(self):
        with self.assertRaises(ValueError):
            DtypesManager({"Invalid[Name]": {}}, {})


class TestNDContainer(unittest.TestCase):

    def setUp(self):
        self.dtype_manager = DtypesManager(
            {},
            {
                "Number": {
                    "type": "object",
                    "properties": {"num": {"type": "number"}},
                    "required": ["num"],
                }
            },
        )

    def test_initialization_with_valid_data(self):
        data = [{"num": 1}, {"num": 2}, {"num": 3}]
        nd = NDContainer(data, "Number", self.dtype_manager)
        self.assertEqual(nd.data, data)
        self.assertEqual(nd.shape, (3,))

    def test_initialization_with_invalid_data(self):
        data = [{"num": 1}, {"num": "two"}, {"num": 3}]
        with self.assertRaises(ValueError):
            NDContainer(data, "Number", self.dtype_manager)

    def test_initialization_with_ndcontainer_dtype(self):
        data = [[{"num": 1}, {"num": 1}], [{"num": 1}, {"num": 1}]]
        nd = NDContainer(data, "NDContainer[Number]", self.dtype_manager)
        self.assertEqual(nd.shape, (2, 2))

    def test_get_item_single_index(self):
        data = [1, 2, 3]
        nd = NDContainer(data, "Number", None)  # type: ignore
        self.assertEqual(nd[1], 2)

    def test_get_item_multiple_indices(self):
        data = [[1, 2], [3, 4]]
        nd = NDContainer(data, "NDContainer[Number]", None)  # type: ignore
        self.assertEqual(nd[0, 1], 2)

    def test_reshape_valid(self):
        data = [1, 2, 3, 4]
        nd = NDContainer(data, "Number", None)  # type: ignore
        reshaped = nd.reshape(2, 2)
        self.assertEqual(reshaped.shape, (2, 2))
        self.assertEqual(reshaped.data, [[1, 2], [3, 4]])
        reshaped = nd.reshape(1, 4)
        self.assertEqual(reshaped.shape, (1, 4))
        self.assertEqual(reshaped.data, [[1, 2, 3, 4]])

    def test_reshape_invalid_shape(self):
        data = [1, 2, 3]
        nd = NDContainer(data, "Number", None)  # type: ignore
        with self.assertRaises(ValueError):
            nd.reshape(2, 2)

    def test_flatten(self):
        data = ([[1, 2], [3, 4]], [[1, 2, 3, 4]], [[1], [2], [3], [4]])
        for d in data:
            nd = NDContainer(d, "NDContainer[Number]", None)  # type: ignore
            flat = nd.flatten()
            self.assertEqual(flat.data, [1, 2, 3, 4])

    def test_dtype_property(self):
        data = [1, 2, 3]
        nd = NDContainer(data, "Number", None)  # type: ignore
        self.assertEqual(nd.dtype, "Number")
        with self.assertRaises(AttributeError):
            nd.dtype = "NewType"

    def test_repr(self):
        data = [1, 2, 3]
        nd = NDContainer(data, "Number", None)  # type: ignore
        expected = "NDContainer(shape=(3,), dtype=Number, data=[1, 2, 3])"
        self.assertEqual(repr(nd), expected)

    def test_flatlist_in_ndcontainer(self):
        data = [[1, 2], [3, 4]]
        nd = NDContainer(data, "FlatList[Number]", None)  # type: ignore
        self.assertIsInstance(nd.data[0], FlatList)
        self.assertEqual(nd.shape, (2,))

        data = [[1, 2], [3, 4]]
        nd = NDContainer(data, "NDContainer[FlatList[Number]]", None)  # type: ignore
        self.assertIsInstance(nd.data[0], FlatList)
        self.assertEqual(nd.shape, (2,))

        data = [[1, 2, 3, 4]]
        nd = NDContainer(data, "NDContainer[FlatList[Number]]", None)  # type: ignore
        self.assertIsInstance(nd.data[0], FlatList)
        self.assertEqual(nd.shape, (1,))

        data = [[1], [2], [3], [4]]
        nd = NDContainer(data, "NDContainer[FlatList[Number]]", None)  # type: ignore
        self.assertIsInstance(nd.data[0], FlatList)
        self.assertEqual(nd.shape, (4,))

        data = [1]
        nd = NDContainer(data, "NDContainer[FlatList[Number]]", None)  # type: ignore
        self.assertIsInstance(nd.data[0], FlatList)
        self.assertEqual(nd.data[0].data, [1])
        self.assertEqual(nd.shape, (1,))


if __name__ == "__main__":
    unittest.main()
 