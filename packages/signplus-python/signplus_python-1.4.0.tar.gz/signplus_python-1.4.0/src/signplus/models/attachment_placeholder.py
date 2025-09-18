from __future__ import annotations
from typing import List
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL
from .attachment_placeholder_file import AttachmentPlaceholderFile


@JsonMap({"id_": "id"})
class AttachmentPlaceholder(BaseModel):
    """AttachmentPlaceholder

    :param recipient_id: ID of the recipient, defaults to None
    :type recipient_id: str, optional
    :param id_: ID of the attachment placeholder, defaults to None
    :type id_: str, optional
    :param name: Name of the attachment placeholder, defaults to None
    :type name: str, optional
    :param hint: Hint of the attachment placeholder, defaults to None
    :type hint: str, optional
    :param required: Whether the attachment placeholder is required, defaults to None
    :type required: bool, optional
    :param multiple: Whether the attachment placeholder can have multiple files, defaults to None
    :type multiple: bool, optional
    :param files: files, defaults to None
    :type files: List[AttachmentPlaceholderFile], optional
    """

    def __init__(
        self,
        recipient_id: str = SENTINEL,
        id_: str = SENTINEL,
        name: str = SENTINEL,
        hint: str = SENTINEL,
        required: bool = SENTINEL,
        multiple: bool = SENTINEL,
        files: List[AttachmentPlaceholderFile] = SENTINEL,
        **kwargs,
    ):
        """AttachmentPlaceholder

        :param recipient_id: ID of the recipient, defaults to None
        :type recipient_id: str, optional
        :param id_: ID of the attachment placeholder, defaults to None
        :type id_: str, optional
        :param name: Name of the attachment placeholder, defaults to None
        :type name: str, optional
        :param hint: Hint of the attachment placeholder, defaults to None
        :type hint: str, optional
        :param required: Whether the attachment placeholder is required, defaults to None
        :type required: bool, optional
        :param multiple: Whether the attachment placeholder can have multiple files, defaults to None
        :type multiple: bool, optional
        :param files: files, defaults to None
        :type files: List[AttachmentPlaceholderFile], optional
        """
        if recipient_id is not SENTINEL:
            self.recipient_id = recipient_id
        if id_ is not SENTINEL:
            self.id_ = id_
        if name is not SENTINEL:
            self.name = name
        if hint is not SENTINEL:
            self.hint = hint
        if required is not SENTINEL:
            self.required = required
        if multiple is not SENTINEL:
            self.multiple = multiple
        if files is not SENTINEL:
            self.files = self._define_list(files, AttachmentPlaceholderFile)
        self._kwargs = kwargs
