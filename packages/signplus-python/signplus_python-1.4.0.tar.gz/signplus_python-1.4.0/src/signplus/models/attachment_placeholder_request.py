from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL


@JsonMap({"id_": "id"})
class AttachmentPlaceholderRequest(BaseModel):
    """AttachmentPlaceholderRequest

    :param recipient_id: ID of the recipient
    :type recipient_id: str
    :param id_: ID of the attachment placeholder, defaults to None
    :type id_: str, optional
    :param name: name
    :type name: str
    :param hint: Hint of the attachment placeholder, defaults to None
    :type hint: str, optional
    :param required: Whether the attachment placeholder is required
    :type required: bool
    :param multiple: multiple
    :type multiple: bool
    """

    def __init__(
        self,
        recipient_id: str,
        name: str,
        required: bool,
        multiple: bool,
        id_: str = SENTINEL,
        hint: str = SENTINEL,
        **kwargs
    ):
        """AttachmentPlaceholderRequest

        :param recipient_id: ID of the recipient
        :type recipient_id: str
        :param id_: ID of the attachment placeholder, defaults to None
        :type id_: str, optional
        :param name: name
        :type name: str
        :param hint: Hint of the attachment placeholder, defaults to None
        :type hint: str, optional
        :param required: Whether the attachment placeholder is required
        :type required: bool
        :param multiple: multiple
        :type multiple: bool
        """
        self.recipient_id = recipient_id
        if id_ is not SENTINEL:
            self.id_ = id_
        self.name = name
        if hint is not SENTINEL:
            self.hint = hint
        self.required = required
        self.multiple = multiple
        self._kwargs = kwargs
