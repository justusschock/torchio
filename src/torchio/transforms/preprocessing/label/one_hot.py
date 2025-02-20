import torch.nn.functional as F  # noqa: N812

from ....data.image import Image
from .label_transform import LabelTransform


class OneHot(LabelTransform):
    r"""Reencode label maps using one-hot encoding.

    Args:
        num_classes: See :func:`~torch.nn.functional.one_hot`.
        **kwargs: See :class:`~torchio.transforms.Transform` for additional
            keyword arguments.
    """
    def __init__(self, num_classes: int = -1, **kwargs):
        super().__init__(**kwargs)
        self.num_classes = num_classes
        self.args_names = ('num_classes',)
        self.invert_transform = False

    def apply_transform(self, subject):
        for image in self.get_images(subject):
            if self.invert_transform:
                self.argmax(image)
            else:
                self.one_hot(image)
        return subject

    @staticmethod
    def argmax(image: Image) -> None:
        data = image.data.argmax(dim=0, keepdim=True)
        image.set_data(data)

    def one_hot(self, image: Image) -> None:
        if image.num_channels > 1:
            message = (
                'The number of input channels must be 1,'
                f' but it is {image.num_channels}'
            )
            raise RuntimeError(message)
        data = image.data[0]
        num_classes = -1 if self.num_classes is None else self.num_classes
        one_hot = F.one_hot(data.long(), num_classes=num_classes)
        image.set_data(one_hot.permute(3, 0, 1, 2).type(data.type()))
