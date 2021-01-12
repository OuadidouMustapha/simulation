from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from notifications.signals import notify

from .models import Version

@receiver(pre_save, sender=Version)
def send_email_if_review_requested(sender, instance, **kwargs):
    ''' Send email to supervisor uppon review request '''
    try:
        old_instance = Version.objects.get(id=instance.id)
    except Version.DoesNotExist:  # to handle initial object creation
        return None  # just exiting from signal

    if old_instance.approved_by != instance.approved_by and instance.approved_by is not None:
        # Notify the user
        notify.send(sender=instance.created_by, recipient=instance.approved_by, verb='sent',
                    description='a review request', action_object=instance, level='info')
        # Prepare email parameters
        subject = 'Review request for {}'.format(instance.reference)
        message = 'You have received a new request from {} {} ({}) to review a version with the reference "{}".\nPlease login to the app for details.'.format(
            instance.created_by.first_name, instance.created_by.last_name, instance.created_by.username, instance.reference)
        from_email = settings.EMAIL_HOST_USER
        # recipient_list = [old_instance.approved_by.email]
        recipient_list = ['abdeltif.b@gclgroup.com']
        # Send email
        send_mail(subject, message, from_email,
                  recipient_list, fail_silently=False)

@receiver(pre_save, sender=Version)
def send_email_if_review_approved(sender, instance, **kwargs):
    ''' Send email to supervisor uppon review request '''
    try:
        old_instance = Version.objects.get(id=instance.id)
    except Version.DoesNotExist:  # to handle initial object creation
        return None  # just exiting from signal

    if old_instance.status != instance.APPROVED and instance.status == instance.APPROVED:
        # Notify the user
        notify.send(sender=instance.approved_by, recipient=instance.created_by, verb='approved',
                    description='your review request', action_object=instance, level='info')
        # Prepare email parameters
        subject = 'Review request for {} is approved'.format(instance.reference)
        message = 'Your review request to {} {} ({}) for the reference "{}" has been approved.\nPlease login to the app for details.'.format(
            instance.approved_by.first_name, instance.approved_by.last_name, instance.approved_by.username, instance.reference)
        from_email = settings.EMAIL_HOST_USER
        # recipient_list = [old_instance.created_by.email]
        recipient_list = ['abdeltif.b@gclgroup.com']
        # Send email
        send_mail(subject, message, from_email,
                  recipient_list, fail_silently=False)


# @receiver(post_save, sender=Version)
# def my_handler(sender, instance, created, **kwargs):
#     ''' Generating notifications '''
#     notify.send(instance, verb='was saved')

# post_save.connect(my_handler, sender=Version)
