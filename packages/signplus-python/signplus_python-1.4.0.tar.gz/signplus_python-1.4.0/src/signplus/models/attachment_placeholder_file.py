from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL


@JsonMap({"id_": "id"})
class AttachmentPlaceholderFile(BaseModel):
    """AttachmentPlaceholderFile

    :param id_: ID of the file, defaults to None
    :type id_: str, optional
    :param name: Name of the file, defaults to None
    :type name: str, optional
    :param size: Size of the file in bytes, defaults to None
    :type size: int, optional
    :param mimetype: MIME type of the file, defaults to None
    :type mimetype: str, optional
    """

    def __init__(
        self,
        id_: str = SENTINEL,
        name: str = SENTINEL,
        size: int = SENTINEL,
        mimetype: str = SENTINEL,
        **kwargs
    ):
        """AttachmentPlaceholderFile

        :param id_: ID of the file, defaults to None
        :type id_: str, optional
        :param name: Name of the file, defaults to None
        :type name: str, optional
        :param size: Size of the file in bytes, defaults to None
        :type size: int, optional
        :param mimetype: MIME type of the file, defaults to None
        :type mimetype: str, optional
        """
        if id_ is not SENTINEL:
            self.id_ = id_
        if name is not SENTINEL:
            self.name = name
        if size is not SENTINEL:
            self.size = size
        if mimetype is not SENTINEL:
            self.mimetype = mimetype
        self._kwargs = kwargs
