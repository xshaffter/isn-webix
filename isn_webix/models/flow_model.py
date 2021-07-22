from django.apps import apps
from django.conf import settings
from django.db import models, transaction

from isn_webix.models import CommonModel

send_mail = __import__(getattr(settings, 'SEND_MAIL_APPLICATION', 'django.core.mail.send_mail'))


class FlowModel(CommonModel):
    NEXT_MODEL = None

    CREATED = 0
    APPROVAL_REQUESTED = 1
    APPROVED = 2
    REJECTED = 3

    STATES = (
        (CREATED, 'Draft'),
        (APPROVAL_REQUESTED, 'Pending'),
        (APPROVED, 'Active'),
    )

    attendant = models.ForeignKey('auth.User', null=True, blank=False)
    status = models.SmallIntegerField(choices=STATES, default=CREATED)
    name = models.CharField(max_length=50, null=True, blank=False)
    rejection_comment = models.TextField(null=True)

    def __init__(self, *args, **kwargs):
        super(FlowModel, self).__init__(*args, **kwargs)
        if self.pk and self.attendant:
            self.APPROVED_MESSAGE = 'hi, {}. \nThe approval for {} has been accepted.'.format(
                self.attendant.get_full_name(), self.__unicode__())

    def send_approval_message(self):
        User = apps.get_model('auth', 'User')
        approval_permissions = getattr(self, 'APPROVAL_PERMISSIONS', False)
        if not approval_permissions:
            raise ValueError('APPROVAL_PERMISSIONS required to be filled in this model')
        receivers = User.objects.filter(user_permissions__codename__in=approval_permissions).distinct()
        DEFAULT_FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL')

        send_mail(
            subject='Approval request for {}'.format(self.__unicode__().lower()),
            message='Hi, {}.\nYour approval for {} has been requested.'.format(self.attendant.get_full_name(),
                                                                               self.__unicode__()),
            sender=DEFAULT_FROM_EMAIL,
            recipients=[self.attendant.email]
        )
        for receiver in receivers:
            message = 'Hi, {}. {} has requested the approval of the following the {} with the ID : {}'.format(
                receiver.get_full_name(), self.attendant.get_full_name(), self.__unicode__(), self.pk)
            send_mail(
                subject='You have a new approval request',
                message=message,
                sender=DEFAULT_FROM_EMAIL,
                recipients=[receiver.email]
            )

    def send_approved_message(self):
        message = getattr(self, 'APPROVED_MESSAGE', False)
        if not message:
            raise ValueError('A message is required to send a mail.')
        if self.NEXT_MODEL:
            app, model_name = self.NEXT_MODEL.split('.')
            model = apps.get_model(app, model_name)
            message = '{}\n{}'.format(message, 'The project has advanced to {}'.format(model._meta.verbose_name))
        receivers = [(getattr(self, 'attendant', False) or getattr(self, 'lead').attendant).email]
        DEFAULT_FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL')
        send_mail(
            subject='Approval request for {}'.format(self.__unicode__().lower()),
            message=message,
            sender=DEFAULT_FROM_EMAIL,
            recipients=receivers
        )

    def send_rejected_message(self):
        message = 'hi, {}. \nThe approval for {} has been rejected due to:\n{}'.format(self.attendant.get_full_name(),
                                                                                       self.__unicode__(),
                                                                                       self.rejection_comment)
        approval_permissions = getattr(self, 'APPROVAL_PERMISSIONS', False)
        if not message:
            raise ValueError('A message is required to send a mail.')
        receivers = [(getattr(self, 'attendant', False) or getattr(self, 'lead').attendant).email]
        DEFAULT_FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL')
        send_mail(
            subject='Approval request for {}'.format(self.__unicode__().lower()),
            message=message,
            sender=DEFAULT_FROM_EMAIL,
            recipients=receivers
        )

    @transaction.atomic
    def reject(self, comment):
        self.status = self.CREATED
        self.rejection_comment = comment
        self.save()
        self.send_rejected_message()
        return 'Rejected.'

    @transaction.atomic
    def approve(self):
        if self.NEXT_MODEL:
            app, model_name = self.NEXT_MODEL.split('.')
            model = apps.get_model(app, model_name)
            if hasattr(self, 'lead') and not (getattr(self.lead, model().field_name(), None)):
                model.objects.create(lead=self.lead, attendant=self.attendant, name=self.name)
            else:
                model.objects.create(lead=self, attendant=self.attendant, name=self.name)
        self.status = self.APPROVED
        self.save()
        self.send_approved_message()
        return 'Approved'

    @transaction.atomic
    def request_approval(self):
        self.send_approval_message()
        self.status = self.APPROVAL_REQUESTED
        self.save()
        return 'Requested.'

    def __unicode__(self):
        text = '{} {}'.format(self.classname, self.name)
        return text

    class Meta:
        abstract = True
