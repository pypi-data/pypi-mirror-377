import os
from xml.etree import ElementTree

import polars as pl

from fairyex.kernel.qcc import KlangEx


SYSTEM_KEYS = {"objects", "attributes", "memberships", "properties"}


def _is_system(system: dict) -> bool:
   system_keys = map(lambda key: key.lower(), system.keys())
   return set(system_keys) <= SYSTEM_KEYS


class DarkSys:
    def __init__(self, system: dict):
        assert _is_system(system)
        self.objects = None
        self.attributes = None
        self.memberships = None
        self.properties = None
        for key in system.keys():
            setattr(self, key.lower(), system[key])

    @classmethod
    def from_excel(self, path: str):
        system = pl.read_excel(path, sheet_id=0)
        return self(system)

    @classmethod
    def from_folder(self, path: str):
        list_of_files = os.listdir(path)
        system = {key: [] for key in SYSTEM_KEYS}
        for excel_file in list_of_files:
            subpath = os.path.join(path, excel_file)
            subsystem = pl.read_excel(subpath, sheet_id=0)
            for key, value in subsystem.items():
                cast_c_as_str = [pl.col(column).cast(str) for column in value.columns]
                system[key.lower()].append(value.with_columns(cast_c_as_str))
        system = {key: pl.concat(value) for key, value in system.items()}
        return self(system)

    @classmethod
    def from_ods(self, path: str):
        system = pl.read_ods(path, sheet_id=0)
        return self(system)

    @classmethod
    def from_software(self, path: str):
        raise NotImplementedError("You died")

    @classmethod
    def from_xml(self, path: str):
        parser = KlangEx(ElementTree.parse(path))
        system = {
            "objects": pl.DataFrame(list(parser.findall_object())),
            "attributes": pl.DataFrame(list(parser.findall_attribute())),
            "memberships": pl.DataFrame(list(parser.findall_membership())),
            "properties": pl.DataFrame(list(parser.findall_property())),
        }
        return self(system)

    def query_category(self, children_class: str) -> list:
        """Return the list of all available categories.

        Parameters
        __________
        children_class
            From which class are the categories.
        """
        is_category_class = pl.col("class") == children_class
        return self.objects.filter(is_category_class).unique("category")["category"].to_list()

    def query_class(self) -> list:
        """Return all the list of available classes."""
        return self.objects.unique("class")["class"].sort(in_place=False).to_list()

    def query_children(self, children_class: list, category: str = None) -> list:
        """Return the list of all children.

        Parameters
        __________
        children_class
            Which objects to query.

        category
            Filter children from a category listed in self.query_category(children_class).
            Default is None which means no filtering.
        """
        is_children_class = pl.col("class") == children_class
        if category is not None:
            is_category = pl.col("category") == category
            return self.objects.filter(is_children_class & is_category)["name"].sort(in_place=False).to_list()
        return self.objects.filter(is_children_class)["name"].sort(in_place=False).to_list()

    def query_property(self, children_class: str) -> list:
        """Return the list of all properties of a class.

        Parameters
        __________
        children_class
            From which class are the properties.
        """
        is_children_class = pl.col("child_class") == children_class
        return self.properties.filter(is_children_class)["property"].sort(in_place=False).to_list()

    def extract_objects(self, children_class: list, children: list) -> pl.DataFrame:
        is_children_class = pl.col("class") == children_class
        is_in_children = pl.col("name").is_in(children)
        return self.objects.filter(is_children_class & is_in_children)

    def extract_attributes(self, children_class: str, children: list) -> pl.DataFrame:
        is_children_class = pl.col("class") == children_class
        is_in_children = pl.col("name").is_in(children)
        return self.attributes.filter(is_children_class & is_in_children)

    def extract_memberships(self, children_class: str, children: list) -> pl.DataFrame:
        is_children_class = (pl.col("child_class") == children_class) | (pl.col("parent_class") == children_class)
        is_in_children = pl.col("child_object").is_in(children) | pl.col("parent_object").is_in(children)
        return self.memberships.filter(is_children_class & is_in_children)

    def extract_properties(self, children_class: str, children: list, properties: list = None) -> pl.DataFrame:
        is_children_class = pl.col("child_class") == children_class
        is_in_children = pl.col("child_object").is_in(children)
        if properties is not None:
            is_in_properties = pl.col("property").is_in(properties)
            return self.properties.filter(is_children_class & is_in_children & is_in_properties)
        return self.properties.filter(is_children_class & is_in_children)
