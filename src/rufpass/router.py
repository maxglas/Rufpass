"""Targeted phonebook access; never replaces or restores a whole phonebook."""

from dataclasses import dataclass
from xml.etree import ElementTree as ET

from fritzconnection import FritzConnection
from fritzconnection.lib.fritzphonebook import FritzPhonebook
from fritzconnection.core.exceptions import FritzArrayIndexError


SERVICE = "X_AVM-DE_OnTel1"


@dataclass
class Snapshot:
    contacts: dict[int, ET.Element]
    known: set[str]


def select_book(root, name):
    if root.tag not in ("phonebook", "phonebooks"):
        raise ValueError("Unerwartetes Telefonbuch-XML.")
    books = [root] if root.tag == "phonebook" else root.findall("phonebook")
    matching = [book for book in books if book.get("name") == name and book.get("owner") != "255"]
    if len(matching) != 1:
        raise ValueError("Telefonbuch-XML passt nicht eindeutig zum angeforderten Buch.")
    return matching[0]


class Router:
    def __init__(self, config, normalize):
        self.config = config
        self.normalize = normalize
        self.connection = FritzConnection(address=config.host, user=config.user,
                                          password=config.password, timeout=10, redact_debug_log=True)

    def snapshot(self):
        books = FritzPhonebook(fc=self.connection)
        contacts, known = {}, set()
        found = False
        for book_id in books.phonebook_ids:
            info = books.phonebook_info(book_id)
            if book_id == self.config.phonebook_id:
                if info["name"] != self.config.phonebook_name:
                    raise ValueError("Ziel-Telefonbuch-ID und Name passen nicht zusammen.")
                found = True
            with self.connection.session.get(info["url"], timeout=10) as response:
                response.raise_for_status()
                book = select_book(ET.fromstring(response.content), info["name"])
            for contact in book.findall("contact"):
                nodes = contact.findall("telephony/number")
                if nodes and all(node.get("type") == "intern" or (node.text or "").strip().startswith("**")
                                 for node in nodes):
                    continue
                numbers = {self.normalize(node.text or "") for node in contact.findall("telephony/number")}
                known.update(number for number in numbers if number is not None)
                if book_id == self.config.phonebook_id:
                    raw_uid = contact.findtext("uniqueid")
                    if raw_uid is None or not raw_uid.isascii() or not raw_uid.isdecimal():
                        raise ValueError("Ein Kontakt im Zielbuch hat keine gültige UID.")
                    uid = int(raw_uid)
                    if uid in contacts:
                        raise ValueError("Doppelte UID im Zielbuch.")
                    contacts[uid] = contact
        if not found:
            raise ValueError("Ziel-Telefonbuch ist nicht vorhanden.")
        return Snapshot(contacts, known)

    def create(self, marker, number):
        contact = ET.Element("contact")
        ET.SubElement(contact, "category").text = "0"
        ET.SubElement(ET.SubElement(contact, "person"), "realName").text = marker
        ET.SubElement(ET.SubElement(contact, "telephony"), "number", type="work", prio="0").text = number
        result = self.connection.call_action(SERVICE, "SetPhonebookEntryUID",
                                             NewPhonebookID=self.config.phonebook_id,
                                             NewPhonebookEntryData=ET.tostring(contact, encoding="unicode"))
        raw_uid = result.get("NewPhonebookEntryUniqueID")
        if isinstance(raw_uid, bool) or not str(raw_uid).isascii() or not str(raw_uid).isdecimal():
            raise ValueError("Die Box hat keine gültige UID geliefert; Abgleich beim nächsten Durchlauf.")
        return int(raw_uid)

    def delete(self, uid):
        self.connection.call_action(SERVICE, "DeletePhonebookEntryUID",
                                    NewPhonebookID=self.config.phonebook_id,
                                    NewPhonebookEntryUniqueID=uid)

    def get(self, uid):
        try:
            result = self.connection.call_action(SERVICE, "GetPhonebookEntryUID",
                                                 NewPhonebookID=self.config.phonebook_id,
                                                 NewPhonebookEntryUniqueID=uid)
        except FritzArrayIndexError:
            return None
        return ET.fromstring(result["NewPhonebookEntryData"])
