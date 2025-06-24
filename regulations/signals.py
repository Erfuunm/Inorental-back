from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
import os
from .models import Regulation

@receiver(pre_save, sender=Regulation)
def update_regulation_file(sender, instance, **kwargs):
    """
    Delete old file when updating the regulation document.
    """
    if not instance.pk:
        return False

    try:
        old_file = Regulation.objects.get(pk=instance.pk).document
    except Regulation.DoesNotExist:
        return False

    new_file = instance.document
    if not old_file == new_file and old_file and os.path.isfile(old_file.path):
        default_storage.delete(old_file.path)

@receiver(pre_delete, sender=Regulation)
def delete_regulation_file(sender, instance, **kwargs):
    """
    Delete file when the regulation is deleted.
    """
    if instance.document and os.path.isfile(instance.document.path):
        default_storage.delete(instance.document.path)
        
        # Try to remove the directory if it's empty
        directory = os.path.dirname(instance.document.path)
        try:
            if os.path.exists(directory) and not os.listdir(directory):
                os.rmdir(directory)
        except OSError:
            # Directory not empty or other error, ignore
            pass
