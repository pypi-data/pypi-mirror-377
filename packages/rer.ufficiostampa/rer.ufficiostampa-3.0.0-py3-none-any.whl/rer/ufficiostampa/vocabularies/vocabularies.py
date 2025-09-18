from Acquisition import aq_base
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.vocabularies.catalog import KeywordsVocabulary
from plone.app.vocabularies.terms import safe_simplevocabulary_from_values
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import json


@implementer(IVocabularyFactory)
class ArgumentsVocabularyFactory:
    def __call__(self, context):
        stored = getattr(aq_base(context), "legislature", "")
        arguments = []
        try:
            legislatures = json.loads(
                api.portal.get_registry_record(
                    "legislatures", interface=IRerUfficiostampaSettings
                )
            )
            if not legislatures:
                pass
            for data in legislatures:
                if data.get("legislature", "") == stored:
                    arguments = data.get("arguments", [])
                    break
            if not arguments:
                arguments = legislatures[-1].get("arguments", [])
        except (KeyError, InvalidParameterError, TypeError):
            arguments = []
        for arg in getattr(context, "arguments", []) or []:
            if arg and arg not in arguments:
                arguments.append(arg)
        terms = [
            SimpleTerm(value=x, token=x.encode("utf-8"), title=x)
            for x in sorted(arguments)
        ]
        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class ChannelsVocabularyFactory:
    def __call__(self, context):
        try:
            subscription_channels = api.portal.get_registry_record(
                "subscription_channels",
                interface=IRerUfficiostampaSettings,
            )
        except (KeyError, InvalidParameterError):
            subscription_channels = []
        return safe_simplevocabulary_from_values(subscription_channels)


@implementer(IVocabularyFactory)
class AttachmentsVocabularyFactory:
    def __call__(self, context):
        terms = []
        for child in context.listFolderContents(
            contentFilter={"portal_type": ["File", "Image"]}
        ):
            terms.append(
                SimpleTerm(
                    value=child.UID(),
                    token=child.UID(),
                    title=child.Title(),
                )
            )
        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class LegislaturesVocabularyFactory:
    def __call__(self, context):
        """
        return a list of legislature names.
        There are all possible index values sorted on reverse order from
        the registry one (last legislature is the first one).
        """
        try:
            registry_val = json.loads(
                api.portal.get_registry_record(
                    "legislatures", interface=IRerUfficiostampaSettings
                )
            )
            registry_legislatures = [x.get("legislature", "") for x in registry_val]
            registry_legislatures.reverse()
        except (KeyError, InvalidParameterError, TypeError):
            registry_legislatures = []

        pc = api.portal.get_tool(name="portal_catalog")
        catalog_legislatures = pc.uniqueValuesFor("legislature")

        legislatures = [x for x in registry_legislatures if x in catalog_legislatures]
        return safe_simplevocabulary_from_values(legislatures)


@implementer(IVocabularyFactory)
class AllArgumentsVocabularyFactory(KeywordsVocabulary):
    keyword_index = "arguments"


AllArgumentsVocabulary = AllArgumentsVocabularyFactory()
ArgumentsVocabulary = ArgumentsVocabularyFactory()
ChannelsVocabulary = ChannelsVocabularyFactory()
AttachmentsVocabulary = AttachmentsVocabularyFactory()
LegislaturesVocabulary = LegislaturesVocabularyFactory()
