from __future__ import annotations
from typing import List
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .attachment_placeholder_request import AttachmentPlaceholderRequest


@JsonMap({})
class SetEnvelopeAttachmentsPlaceholdersRequest(BaseModel):
    """SetEnvelopeAttachmentsPlaceholdersRequest

    :param placeholders: placeholders
    :type placeholders: List[AttachmentPlaceholderRequest]
    """

    def __init__(self, placeholders: List[AttachmentPlaceholderRequest], **kwargs):
        """SetEnvelopeAttachmentsPlaceholdersRequest

        :param placeholders: placeholders
        :type placeholders: List[AttachmentPlaceholderRequest]
        """
        self.placeholders = self._define_list(
            placeholders, AttachmentPlaceholderRequest
        )
        self._kwargs = kwargs
