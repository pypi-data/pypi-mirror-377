# -*- coding: utf-8 -*-

"""
Provides utility functions around HERA attributes.

:copyright: The pyHeimdall contributors.
:licence: Afero GPL, see LICENSE for more details.
:SPDX-License-Identifier: AGPL-3.0-or-later
"""
import heimdall
from heimdall.util.tree import get_node, set_language
from xml.etree.ElementTree import Element


def refactor_relationship(tree, relationship, eid, euid, pid, cleanup=True):
    """This function merges an entity into two others.

    :param tree: (:py:class:`heimdall.elements.Root`) -- HERA element tree
    :param relationship: (:py:class:`dict`) -- Description of the relationship entity we want to merge
    :param eid: (:py:class:`str`) -- Identifier of the HERA entity in ``tree`` to which we'll add ``relationship['target']`` as a repeatable field
    :param euid: (:py:class:`str`) -- Property identifier of an attribute which can uniquely identify entity ``eid``
    :param pid: (:py:class:`str`) -- Property identifier of the new attribute to create in entity ``eid`` for ``relationship['target']``
    :param cleanup: (:py:class:`bool`, optional, default: ``True``) -- If ``True`` (default), items in ``tree`` representing ``relationship['eid']`` will be deleted
    :return: None
    :rtype: :py:class:`NoneType`

    This function merges an entity that is in fact a relationship between two other entities, so the corresponding items become repeatable metadata of one of these two entities.
    It performs its modifications "in place".
    In other words, parameter ``tree`` is directly modified,
    and this function returns nothing.

    **Usage example**

    Let's say ``tree`` initialy contains three entities:

    * '`person`' to represents persons.
      Items of entity '`person`' can be uniquely identified by their '`name`' metadata; attribute '`name`' is the concrete use by '`person`' of property '`title`';
    * '`pet`' to represent pets;
    * '`owners2pets`' representing who owns who, via its two only attributes '`owner`' and '`pet`', as a person can have multiple pets.

    This kind of "indirect relation" entity is often found in databases whose original implementations handle repeatable fields like this.
    Problem is: on many databases, there are many of this kind of entity, they clutter the database schema only because of the limitations of the original implementation.
    This makes the whole database intention less readable, thus less accessible, thus more difficult to understand and reuse.

    Here is how a single call to ``refactor_relationship`` can make things simpler: ::

      >>> import heimdall
      >>> tree = heimdall.getDatabase(...)  # load HERA tree
      >>> refactor_relationship(tree,
      >>>     relationship={
      >>>         'eid': 'owners2pets',  # entity we want to get rid of
      >>>         'source': 'owner',  # pointer to 'person'
      >>>         'target': 'pet',  # metadata we want to keep
      >>>         },
      >>>     eid='person',  # entity the new attribute will be added to
      >>>     euid='title',  # unique identifier property for entity 'person'
      >>>     pid='pet')  # property id for the new attribute

    | After ``refactor_relationship`` is called, ``tree`` only contain two entities ('`person`' and '`pet`'), and entity '`person`' has gained a new repeatable field, '`pet`'.
    | As ``cleanup`` was left to ``True``, items previously belonging to now deleted entity '`owners2pets`' are deleted too.
      No data is lost however, as these items only interesting metadata is now hold by metadata '`pet`' in items of entity '`person`'.

    :see also: | :py:class:`heimdall.util.merge_properties` can be used to merge together properties that are semantically the same.
               | :py:class:`heimdall.util.merge_l10n_attributes` can be used to merge together attributes that are translations of one another.
               | :py:class:`heimdall.util.delete_unused_properties` can be used to cleanup what is left after doing this kind of "tree improvement" operations.
    """  # nopep8: E501
    R_ID = relationship['eid']
    R_SOURCE = relationship['source']
    R_TARGET = relationship['target']
    # TODO only create property if not exists
    p = heimdall.createProperty(tree, id=pid)
    e = heimdall.getEntity(tree, lambda n: n.get('id') == eid)
    # TODO only create attribute if not exists
    a = heimdall.createAttribute(e, pid=pid)
    # iterate over all items belonging to the relationship entity
    items = heimdall.getItems(tree, lambda n: n.get('eid') == R_ID)
    for old in items:
        source = heimdall.getMetadata(old, pid=R_SOURCE)[0].text
        target = heimdall.getMetadata(old, pid=R_TARGET)[0].text

        def is_source(item):
            is_of_entity = item.get('eid') == eid
            has_unique_id = False
            # NOTE: Unique id shouldn't be a repeatable attribute,
            # but we know what real world data looks like.
            # Thus, try to not break in this edge case, and
            # let's hope our caller knows what she does.
            for v in heimdall.getValues(item, pid=euid):
                has_unique_id = has_unique_id or (v == source)
            return is_of_entity and has_unique_id

        # get the item which must contain the new repeatable metadata
        now = heimdall.getItem(tree, is_source)
        metadata = Element('metadata', pid=pid)
        metadata.text = target
        now.append(metadata)
        if cleanup:
            # delete `old` relationship item, because it is
            # now represented by new metadata in item `now`
            heimdall.deleteItem(tree, lambda n: n == old)
    if cleanup:
        # delete the `relationship` entity, as there are no more items using it
        heimdall.deleteEntity(tree, lambda n: n.get('id') == R_ID)


def merge_l10n_attributes(
        tree, eid, languages,
        pid, aid,
        cleanup=True, update_items=True
        ):
    """Merges attributes that are in fact translations of one another.

    :param tree: (:py:class:`heimdall.elements.Root`) -- HERA element tree
    :param eid: (:py:class:`str`) -- Identifier of the HERA entity in ``tree`` containing all attributes to merge
    :param languages: (:py:class:`dict`) -- :py:class:`dict` containing ``eid``'s "translated" attributes identifiers as keys and their actual language codes as values
    :param pid: (:py:class:`str`) -- Property identifier of "merged" attribute
    :param aid: (:py:class:`str`) -- Attribute identifier of "merged" attribute; if ``aid`` does not identify an attribute already present in ``entity``, a new attribute of this identifier and of type ``text`` will be created
    :param cleanup: (:py:class:`bool`, optional, default: ``True``) -- If ``True`` (default), attributes in ``languages`` will be removed from entity identified ``eid`` after they are merged; attribute identified by ``aid`` is of course never removed
    :param update_items: (:py:class:`bool`, optional, default: ``True``) -- If ``True``, metadata items in ``tree`` using attributes listed in ``languages`` will be updated with the new ``pid`` and ``aid``.
    :return: None
    :rtype: :py:class:`NoneType`

    This function merges attributes that are in fact translations of one another in the same entity into one (possibly new) "merged" attribute.
    It performs its modifications "in place".
    In other words, parameter ``tree`` is directly modified,
    and this function returns nothing.

    **Usage example**

    Let's say ``tree`` initialy contains the following '`person`' entity to represents persons: ::

      >>> <entity id='person'>
      >>>   <attribute pid='name_de' id='person.name_de_attr'>
      >>>     <name>Personenname</name>
      >>>   </attribute>
      >>>   <attribute pid='name_en' id='person.name_en_attr'>
      >>>     <name>Name</name>
      >>>     <description>Name of the person</description>
      >>>   </attribute>
      >>>   <attribute pid='name_fr' id='person.name_fr_attr'>
      >>>     <name>Nom</name>
      >>>     <description>Nom de la personne</description>
      >>>   </attribute>
      >>> </entity>

    Such duplication of attributes is often observed in databases implementations where internationalization and repeatability of values are not features that are available or generally used.
    It makes the resulting entity unwieldy, as semantic relations between metadata values are lost in their syntax.
    The resulting database can be seen as less interoperable, as it requires ad-hoc shenahigans to restore proper internationalization.

    The function ``merge_l10n_attributes`` provides an alternative.
    To merge those three attributes of entity '`person`', one could do the following: ::

      >>> import heimdall
      >>> tree = heimdall.getDatabase(...)  # load HERA tree
      >>> # (1) First, give ourselves a new property
      >>> #     for merging human-readable names:
      >>> heimdall.createProperty(
      >>>     tree, 'dc:title', type='text',
      >>>     name={'en': "Title", 'fr': "Titre", },
      >>>     description={
      >>>         'en': "A name given to the resource.",
      >>>         'fr': "Nom de la ressource.",
      >>>         },
      >>>     uri=[
      >>>         'http://purl.org/dc/terms/title',
      >>>         'http://datacite.org/schema/kernel-4/title',
      >>>         ],
      >>>     )
      >>> # (2) Retrieve the 'person' entity we want to work on:
      >>> e = heimdall.getEntity(tree, lambda n: n.get('id') == 'person')
      >>> # (3) Merge all the things !
      >>> merge_l10n_attributes(tree, e, {
      >>>     'person.name_de_attr': 'de',
      >>>     'person.name_en_attr': 'en',
      >>>     'person.name_fr_attr': 'fr',
      >>>     },
      >>>     aid='person.name',
      >>>     pid='dc:title')

    After running the above code, entity '`person`' looks as follows:

      >>> <entity id='person'>
      >>>   <attribute pid='dc:title' id='person.name'>
      >>>     <name xml:lang='de'>Personenname</name>
      >>>     <name xml:lang='en'>Name</name>
      >>>     <name xml:lang='fr'>Nom</name>
      >>>     <description xml:lang='en'>Name of the person</description>
      >>>     <description xml:lang='fr'>Nom de la personne</description>
      >>>   </attribute>
      >>> </entity>

    One can argue entity '`person`' is now leaner and easier to work with, as long as more accessible and reusable, as it is based on scientific standards like `Dublin Core™ <https://www.dublincore.org/specifications/dublin-core/>`_, and doesn't separate anymore attributes that were "the same in a different language".

    **Impact on items**

    | This is further enforced by the update of items in ``tree`` allowed by setting ``update_items`` parameter to ``True`` (the default).
    | In the example above, before calling ``merge_l10n_attributes``, items would look like that: ::

      >>> <item eid='person'>
      >>>   <metadata pid='name_de' aid='person.name_de_attr'>Wilhem</metadata>
      >>>   <metadata pid='name_en' aid='person.name_en_attr'>William</metadata>
      >>>   <metadata pid='name_fr' aid='person.name_fr_attr'>Guillaume</metadata>
      >>> </item>

    | Syntactically speaking, those are three entirely different metadata.
    | After calling ``merge_l10n_attributes``, items would rather contain `one single` metadata, `localized in three languages`, and would look like this: ::

      >>> <item eid='person'>
      >>>   <metadata pid='title' aid='person.name' xml:lang='de'>Wilhem</metadata>
      >>>   <metadata pid='title' aid='person.name' xml:lang='en'>William</metadata>
      >>>   <metadata pid='title' aid='person.name' xml:lang='fr'>Guillaume</metadata>
      >>> </item>

    :see also: | :py:class:`heimdall.util.merge_properties` can be used to merge together properties that are semantically the same (from a scientific metadata standard point of view), although named differently in different entities of the imported ``tree``.
               | :py:class:`heimdall.util.refactor_relationship` can be used to merge a whole entity into two others.
               | :py:class:`heimdall.util.delete_unused_properties` can be used to cleanup what is left after doing this kind of "tree improvement" operations.
               | :py:class:`heimdall.util.get_language` and :py:class:`heimdall.util.set_language` are useful functions related to HERA elements localization.
    """  # nopep8: E501
    entity = heimdall.getEntity(tree, lambda n: n.get('id') == eid)
    if entity is None:
        raise ValueError(f"Entity '{eid}' doesn't exist")
    (base, new) = _get_or_create_attribute(entity, aid, pid)
    base_aid = base.get('id')
    base_pid = base.get('pid')
    _update_attribute(base, entity, languages)
    if new:
        entity.append(base)
    # * ... if `cleanup` delete `language` attributes (except base_atr ofc)
    # * ... if `update_items`, update_items to use id = base_a.id / base_aid
    items = []
    if update_items:
        items = heimdall.getItems(tree, lambda n: n.get('eid') == eid)
    for aid, language in languages.items():
        if cleanup and (aid != base_aid):
            attr = heimdall.getAttribute(entity, lambda a: a.get('id') == aid)
            entity.remove(attr)
        for item in items:
            for metadata in heimdall.getMetadata(item, aid=aid):
                metadata.set('aid', base_aid)
                metadata.set('pid', base_pid)
                set_language(metadata, language)
    return base


def _get_or_create_attribute(entity, aid, pid):
    """Retrieve attribute from ``entity``:
    - if one ``aid`` is in ``entity``, return it
    - if ONLY one ``pid`` is in ``entity``, return it
    - else return a new Attribute element, which is NOT added to ``entity`` yet
    """
    new = False
    base = heimdall.getAttribute(entity, lambda n: n.get('id') == aid)
    if base is None:
        base = heimdall.elements.Attribute(id=aid)
        new = True
    if pid is not None:
        base.set('pid', pid)
    return (base, new)


def _update_attribute(base, entity, languages):
    """Update ``base`` attribute with type and pid of
    attributes listed in ``langages``, while checking
    these type and pid are the same.
    """
    base_aid = base.get('id')
    types = list()
    for aid, language in languages.items():
        a = heimdall.getAttribute(entity, lambda n: n.get('id') == aid)
        if a is None:
            raise ValueError(f"Unknown attribute identifier '{aid}'")
        _update_language(base, a, 'name', language)
        _update_language(base, a, 'description', language)
        if a.type is not None:
            types.append(a.type)
    types = list(set(types))
    if len(types) > 1:
        raise ValueError("Attributes don't all have the same type")
    if len(types) > 0:
        base.type = types[0]
    # TODO: check compatibility of types[0] (if exists)
    #       with underlying property
    # TODO: set min and max
    return base


def _update_language(base, attribute, key, language):
    values = getattr(base, key, dict())
    old_values = getattr(attribute, key, dict())
    for k, v in old_values.items():
        if k is not None and k != language:
            continue
        value = values.get(language, list())
        value = list(set(value + v))
        values[language] = value
    values.pop(None, None)
    setattr(base, key, values)
    return values


__copyright__ = "Copyright the pyHeimdall contributors."
__license__ = 'AGPL-3.0-or-later'
