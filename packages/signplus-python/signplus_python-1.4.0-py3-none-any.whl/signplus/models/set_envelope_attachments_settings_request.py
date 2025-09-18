from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .attachment_settings import AttachmentSettings


@JsonMap({})
class SetEnvelopeAttachmentsSettingsRequest(BaseModel):
    """SetEnvelopeAttachmentsSettingsRequest

    :param settings: settings
    :type settings: AttachmentSettings
    """

    def __init__(self, settings: AttachmentSettings, **kwargs):
        """SetEnvelopeAttachmentsSettingsRequest

        :param settings: settings
        :type settings: AttachmentSettings
        """
        self.settings = self._define_object(settings, AttachmentSettings)
        self._kwargs = kwargs
