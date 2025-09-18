from __future__ import annotations
from typing import List
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL
from .attachment_placeholder import AttachmentPlaceholder


@JsonMap({})
class AttachmentPlaceholdersPerRecipient(BaseModel):
    """AttachmentPlaceholdersPerRecipient

    :param recipient_id: ID of the recipient, defaults to None
    :type recipient_id: str, optional
    :param recipient_name: Name of the recipient, defaults to None
    :type recipient_name: str, optional
    :param placeholders: placeholders, defaults to None
    :type placeholders: List[AttachmentPlaceholder], optional
    """

    def __init__(
        self,
        recipient_id: str = SENTINEL,
        recipient_name: str = SENTINEL,
        placeholders: List[AttachmentPlaceholder] = SENTINEL,
        **kwargs,
    ):
        """AttachmentPlaceholdersPerRecipient

        :param recipient_id: ID of the recipient, defaults to None
        :type recipient_id: str, optional
        :param recipient_name: Name of the recipient, defaults to None
        :type recipient_name: str, optional
        :param placeholders: placeholders, defaults to None
        :type placeholders: List[AttachmentPlaceholder], optional
        """
        if recipient_id is not SENTINEL:
            self.recipient_id = recipient_id
        if recipient_name is not SENTINEL:
            self.recipient_name = recipient_name
        if placeholders is not SENTINEL:
            self.placeholders = self._define_list(placeholders, AttachmentPlaceholder)
        self._kwargs = kwargs
