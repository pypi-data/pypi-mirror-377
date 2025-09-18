from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL


@JsonMap({})
class AttachmentSettings(BaseModel):
    """AttachmentSettings

    :param visible_to_recipients: Whether the attachment is visible to the recipients, defaults to None
    :type visible_to_recipients: bool, optional
    """

    def __init__(self, visible_to_recipients: bool = SENTINEL, **kwargs):
        """AttachmentSettings

        :param visible_to_recipients: Whether the attachment is visible to the recipients, defaults to None
        :type visible_to_recipients: bool, optional
        """
        if visible_to_recipients is not SENTINEL:
            self.visible_to_recipients = visible_to_recipients
        self._kwargs = kwargs
