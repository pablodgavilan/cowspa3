import inspect
import commonlib.helpers
import be.repository.access as dbaccess

member_store = dbaccess.stores.member_store

def make_date_element(date):
    return "<c class='date'>%s</c> " % commonlib.helpers.date4human(date)


class BaseEvent(object):
    name = "base"
    category = ""
    def __init__(self, actor, created, data):
        self.created = created
        self.actor = actor
        self.data = commonlib.helpers.odict(**data)
    @property
    def msg_tmpl(self):
        return self._msg_tmpl()
    @property
    def tags(self):
        return self._tags()
    @property
    def message(self):
        data = self.data
        data.update(created=self.created, actor=self.actor)
        return self.msg_tmpl % data
    @property
    def access(self):
        return self._access()
    def _tags(self):
        return []
    def _msg_tmpl(self):
        return ''
    def _access(self):
        return dict(roles=[(0, 'admin')], member_ids=[self.actor])

class MemberCreated(BaseEvent):
    name = "member_created"
    category = "member_management"
    def _msg_tmpl(self):
        return make_date_element(self.data.created) + " New member <a href='./member/edit/#/%(id)s/profile'>%(name)s</a> created by %(actor_name)s."

class MemberInvited(BaseEvent):
    name = "member_invited"
    category = "member_management"
    def _msg_tmpl(self):
        return make_date_element(self.data.created) + ' %(actor_name)s has send membership invitaion to "%(first_name)s %(last_name)s"'

class MemberUpdated(BaseEvent):
    name = "member_updated"
    category = "member_management"
    def _msg_tmpl(self):
        if self.actor == self.data.id:
            tmpl = "You have updated profile."
        else:
            tmpl = "%(actor_name)s has updated %(name)s's profile."
        return make_date_element(self.data.created) + tmpl
    def _access(self):
        return dict(member_ids=[self.actor])

class MemberDeleted(BaseEvent):
    name = "member_deleted"
    category = "member_management"
    def _msg_tmpl(self):
        return "%(name)s account is removed by %(actor_name)s."

class PasswordChanged(BaseEvent):
    name = "password_changed"
    category = "security"
    def _msg_tmpl(self):
        return "Password changed for %(name)s by %(actor_name)s."

class BizplaceCreated(BaseEvent):
    name = "bizplace_created"
    category = "bizplace_management"
    def _msg_tmpl(self):
        return make_date_element(self.data.created) + " New place <a href='./bizplaces/#/%(id)s'>%(name)s</a> created by %(actor_name)s."

class BizplaceUpdated(BaseEvent):
    name = "bizplace_updated"
    category = "bizplace_management"
    def _msg_tmpl(self):
        if self.actor == self.data.id:
            tmpl = " You have updated %(name)s place's profile."
        else:
            tmpl = " %(actor_name)s has updated %(name)s place's profile."
        return make_date_element(self.data.created) + tmpl

class ResourceCreated(BaseEvent):
    name = "resource_created"
    category = "resource_management"
    def _msg_tmpl(self):
        return make_date_element(self.data.created) + " New resource (%(type)s) <a href='./resources/#/%(id)s/edit/profile'>%(name)s</a> created by %(actor_name)s for %(bizplace_name)s."
    def _access(self):
        return dict(member_ids = [self.actor], roles=[(self.data.bizplace_id, 'host'), (self.data.bizplace_id, 'director')])

class TariffCreated(BaseEvent):
    name = "tariff_created"
    category = "tariff_management"
    def _msg_tmpl(self):
        return make_date_element(self.data.created) + " New tariff %(name)s created by %(actor_name)s for %(bizplace_name)s."
    def _access(self):
        return dict(member_ids = [self.actor], roles=[(self.data.bizplace_id, 'host'), (self.data.bizplace_id, 'director')])

class InvoiceCreated(BaseEvent):
    name = "invoice_created"
    category = "invoice_management"
    def _msg_tmpl(self):
        return make_date_element(self.data.created) + " Invoice No.<a href='./invoice/%(invoice_id)s/html'>%(invoice_id)s</a> issued for <a href='./member/edit/#/%(member_id)s/profile'>%(name)s</a> by %(actor_name)s."
    def _access(self):
        return dict(member_ids=[self.actor])

class InvoiceprefUpdated(BaseEvent):
    name = "invoicepref_updated"
    category = "invoicepref_management"
    def _msg_tmpl(self):
        return make_date_element(self.data.created) + " Invoice Preferences %(attrs)s updated for Place %(name)s by %(actor_name)s."
    def _access(self):
        return dict(member_ids=[self.actor])

class BillingprefUpdated(BaseEvent):
    name = "billingpref_updated"
    category = "billingpref_management"
    def _msg_tmpl(self):
        return make_date_element(self.data.created) + " Billing Preferences updated for <a href='./member/edit/#/%(member_id)s/profile'>%(name)s</a> by %(actor_name)s."

class Categories(dict):
    """
    subclassing dict to guarantee uniqueness of event name
    """
    def add_event(self, event):
        if not event.category in self:
            self[event.category] = {}
        elif event.name in self[event.category]:
            raise Exception("Event name not unique: " + event.name)
        self[event.category][event.name] = event
    def eventnames_for_role(self, roles):
        return tuple(itertools.chain(*(tuple(role_categories[role].values()) for role in roles)))

all_events = [o for o in globals().values() if inspect.isclass(o) and issubclass(o, BaseEvent)]
categories = Categories()

for event in all_events:
    if inspect.isclass(event) and issubclass(event, BaseEvent):
        categories.add_event(event)

role_categories = dict(
    admin = dict(
        member_management = ['member_created', 'member_updated'],
        bizplace_management = ['bizplace_created', 'bizplace_updated'],
        security = [],
        resource_management = ['resource_created'] ),
    host = dict(
        member_management = ['member_created', 'member_updated'],
        bizplace_management = ['bizplace_created'],
        security = [],
        resource_management = ['resource_created'] ),
    member = dict(
        member_management = ['member_updated'],
        security = ['password_changed'])
    )
