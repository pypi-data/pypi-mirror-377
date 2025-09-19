"""Query Compiler Collection"""

from xml.etree import ElementTree

from .querxml import _set_query


class KlangEx:
    def __init__(self, xml: ElementTree):
        self.xml = xml
        self.default_namespace = _set_query(self.xml, "", "Master")
        self._action = {
            self.findattr(action, "action_id"): self.findattr(action, "action_symbol")
            for action in self.findall("action")
        }
        self._band = {
            self.findattr(band, "data_id"): self.findattr(band, "band_id")
            for band in self.findall("band")
        }
        self._category = {
            self.findattr(category, "category_id"): self.findattr(category, "name")
            for category in self.findall("category")
        }
        self._class = {
            self.findattr(klass, "class_id"): self.findattr(klass, "name")
            for klass in self.findall("class")
        }
        self._collection = {
            self.findattr(collection, "collection_id"): self.findattr(collection, "name")
            for collection in self.findall("collection")
        }
        self._unit = {
            self.findattr(unit, "unit_id"): self.findattr(unit, "value")
            for unit in self.findall("unit")
        }

        self._object = {
            self.findattr(obj, "object_id"): {
                "class": self._class[self.findattr(obj, "class_id")],
                "name": self.findattr(obj, "name"),
                "category": self._category[self.findattr(obj, "category_id")],
            }
            for obj in self.findall("object")
        }
        self._attribute = {
            self.findattr(attribute, "attribute_id"): self.findattr(attribute, "name")
            for attribute in self.findall("attribute")
        }
        self._membership = {
            self.findattr(memb, "membership_id"): {
                "parent_class": self._class[self.findattr(memb, "parent_class_id")],
                "parent_object": self._object[self.findattr(memb, "parent_object_id")]["name"],
                "collection": self._collection[self.findattr(memb, "collection_id")],
                "child_class": self._class[self.findattr(memb, "child_class_id")],
                "child_object": self._object[self.findattr(memb, "child_object_id")]["name"],
            }
            for memb in self.findall("membership")
        }
        self._property = {
            self.findattr(prop, "property_id"):
                f'{self.findattr(prop, "name")} ({self._unit[self.findattr(prop, "unit_id")]})'
            for prop in self.findall("property")
        }

        self._date_from = {
            self.findattr(date_from, "data_id"): self.findattr(date_from, "date")
            for date_from in self.findall("date_from")
        }
        self._date_to = {
            self.findattr(date_to, "data_id"): self.findattr(date_to, "date")
            for date_to in self.findall("date_to")
        }
        self._tag = self._findall_tag()
        self._text = self._findall_text()

    def find(self, query):
        return self.xml.find(f"{self.default_namespace}t_{query}")

    def findall(self, query):
        return self.xml.findall(f"{self.default_namespace}t_{query}")

    def findattr(self, leaf, attr):
        try:
            return leaf.find(f"{self.default_namespace}{attr}").text
        except AttributeError:
            raise AttributeError(f"{leaf} object has no attribute {attr}")

    def attrget(self, leaf, attr):
        try:
            return self.findattr(leaf, attr)
        except AttributeError:
            return None

    def _findall_tag(self):
        all_tag = {}
        for text in self.findall("tag"):
            key_ids = (self.findattr(text, "data_id"), self._object[self.findattr(text, "object_id")]["class"])
            all_tag[key_ids] = self._object[self.findattr(text, "object_id")]["name"]
            if action_id := self.attrget(text, "action_id"):
                all_tag[(self.findattr(text, "data_id"), "Action")] = self._action[action_id]
        return all_tag

    def _findall_text(self):
        all_text = {}
        for text in self.findall("text"):
            if action_id := self.attrget(text, "action_id"):
                klass = "Action"
                value = self._action[action_id]
            elif object_id := self.attrget(text, "object_id"):
                klass = self._object[object_id]["class"]
                value = self._object[object_id]["name"]
            else:
                class_id = self.findattr(text, "class_id")
                klass = self._class[class_id]
                value = self.findattr(text, "value")
            data_id = self.findattr(text, "data_id")
            all_text[(data_id, klass)] = value
        return all_text

    def _find_tag_text(self, data_id: str, object_class: str):
        key_ids = (data_id, object_class)
        if tag := self._tag.get(key_ids):
            return tag
        elif text := self._text.get(key_ids):
            return text
        return ""

    def findall_attribute(self):
        for attr in self.findall("attribute_data"):
            yield {
                "class": self._object[self.findattr(attr, "object_id")]["class"],
                "name": self._object[self.findattr(attr, "object_id")]["name"],
                "attribute": self._attribute[self.findattr(attr, "attribute_id")],
                "value": self.findattr(attr, "value"),
            }

    def findall_membership(self):
        return self._membership.values()

    def findall_object(self):
        return self._object.values()

    def findall_property(self):
        filename_id = next(key for key in self._class.keys() if self._class[key] == "Data File")
        for data in self.findall("data"):
            data_id = self.findattr(data, "data_id")
            membership_id = self.findattr(data, "membership_id")
            yield {
                "parent_class": self._membership[membership_id]["parent_class"],
                "parent_object": self._membership[membership_id]["parent_object"],
                "child_class": self._membership[membership_id]["child_class"],
                "child_object": self._membership[membership_id]["child_object"],
                "property": self._property[self.findattr(data, "property_id")],
                "band": self._band.get(data_id, "1"),
                "value": self.findattr(data, "value"),
                "date_from": self._date_from.get(data_id, ""),
                "date_to": self._date_to.get(data_id, ""),
                "filename": self._find_tag_text(data_id, "Data File"),
                "action": self._find_tag_text(data_id, "Action"),
                "variable": self._find_tag_text(data_id, "Variable"),
                "pattern": self._find_tag_text(data_id, "Timeslice"),
                "scenario": self._find_tag_text(data_id, "Scenario"),
            }
