from __future__ import annotations
from typing import List
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL
from .attachment_settings import AttachmentSettings
from .attachment_placeholders_per_recipient import AttachmentPlaceholdersPerRecipient


@JsonMap({})
class EnvelopeAttachments(BaseModel):
    """EnvelopeAttachments

    :param settings: settings, defaults to None
    :type settings: AttachmentSettings, optional
    :param recipients: recipients, defaults to None
    :type recipients: List[AttachmentPlaceholdersPerRecipient], optional
    """

    def __init__(
        self,
        settings: AttachmentSettings = SENTINEL,
        recipients: List[AttachmentPlaceholdersPerRecipient] = SENTINEL,
        **kwargs,
    ):
        """EnvelopeAttachments

        :param settings: settings, defaults to None
        :type settings: AttachmentSettings, optional
        :param recipients: recipients, defaults to None
        :type recipients: List[AttachmentPlaceholdersPerRecipient], optional
        """
        if settings is not SENTINEL:
            self.settings = self._define_object(settings, AttachmentSettings)
        if recipients is not SENTINEL:
            self.recipients = self._define_list(
                recipients, AttachmentPlaceholdersPerRecipient
            )
        self._kwargs = kwargs
