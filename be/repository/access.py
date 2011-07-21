import be.repository.stores as stores_mod
import bases.persistence

user_store = stores_mod.User()
contact_store = stores_mod.Contact()
member_store = stores_mod.Member()
memberpref_store = stores_mod.MemberPref()
memberprofile_store = stores_mod.MemberProfile()
registered_store = stores_mod.Registered()
session_store = stores_mod.Session()
permission_store = stores_mod.Permission()
role_store = stores_mod.Role()
user_perms_store = stores_mod.UserPermission()
user_roles_store = stores_mod.UserRole()
biz_store = stores_mod.Biz()
bizplace_store = stores_mod.BizPlace()
bizprofile_store = stores_mod.BizProfile()
bizplaceprofile_store = stores_mod.BizplaceProfile()
request_store = stores_mod.Request()
plan_store = stores_mod.Plan()
subscription_store = stores_mod.Subscription()
resource_store = stores_mod.Resource()
usage_store = stores_mod.Usage()
invoice_store = stores_mod.Invoice()
pricing_store = stores_mod.Pricing()
price_store = stores_mod.Price()
activity_store = stores_mod.Activity()

class RStore(object): pass

def make_rstore(store):
    rstore = RStore()
    for attr in ('ref', 'setup', 'add', 'remove', 'get', 'get_by', 'get_one_by', 'update'):
        method = getattr(store, attr)
        setattr(rstore, attr, method)
    return rstore

class stores: pass

for name, store in stores_mod.known_stores.items():
    setattr(stores, name, make_rstore(store))

def find_memberships(member_id):
    return subscription_store.get_by(crit=dict(subscriber_id=member_id))

def biz_info(biz_id):
    ref = biz_store.ref(biz_id)
    q = 'SELECT biz.name, biz.state, \
         bizprofile.short_description, bizprofile.tags, bizprofile.website, bizprofile.blog, \
         contact.address, contact.city, contact.country, contact.email \
         from biz \
         INNER JOIN contact ON contact.owner = %(ref)s \
         INNER JOIN bizprofile ON bizprofile.biz = %(biz_id)s \
         WHERE biz.id = %(biz_id)s'
    values = dict(biz_id=biz_id, ref=ref)
    return biz_store.query_exec(q, values)[0]

bizplace_info_sql = 'SELECT bizplace.name, bizplace.state, \
    bizplaceprofile.short_description, bizplaceprofile.tags, bizplaceprofile.website, bizplaceprofile.blog, \
    contact.address, contact.city, contact.country, contact.email \
    from bizplace '

def bizplace_info(bizplace_id):
    ref = bizplace_store.ref(bizplace_id)
    q = bizplace_info_sql + \
    """
    INNER JOIN contact ON contact.owner = %(ref)s
    INNER JOIN bizplaceprofile ON bizplaceprofile.bizplace = %(bizplace_id)s
    WHERE bizplace.id = %(bizplace_id)s
    """
    values = dict(bizplace_id=bizplace_id, ref=ref)
    return bizplace_store.query_exec(q, values)[0]

class Resource(object):
    store = resource_store
    info_fields = ['id', 'name', 'short_description']
    def info(self):
        return self.store.get(self.id, self.info_fields)
    def dependencies(self):
        deps = self.store.get(self.id, ['contains', 'contains_opt', 'requires', 'suggests', 'contained_by', 'required_by', 'suggested_by'])
        dep_ids = list(itertools.chain(*deps.values()))
        return resource_store.get_many(dep_ids, self.info_fields)

# functions

def get_passphrase_by_username(username):
    return user_store.get_by(crit={'username': username})[0].password

def add_membership(member_id, plan_id):
    plan = plan_store.get(plan_id)
    bizplace_name = bizplace_store.get(bizplace_id, fields=['name']).name
    data = dict(plan_id=plan_id, subscriber_id=member_id, plan_name=plan.name, bizplace_id=plan.bizplace_id, bizplace_name=bizplace_name)
    subscription_store.add(**data)
    return True

def find_bizplace_members(bizplace_ids, fields=['member', 'display_name']):
    bizplace_ids = tuple(bizplace_ids)
    clause = 'member IN (SELECT subscriber_id FROM subscription WHERE bizplace_id IN %s)'
    clause_values = (bizplace_ids,)
    return memberprofile_store.get_by_clause(clause, clause_values, fields)

def list_bizplaces():
    q = bizplace_info_sql
    q += """
    INNER JOIN contact ON contact.owner = 'BizPlace:' || bizplace.id
    INNER JOIN bizplaceprofile ON bizplaceprofile.bizplace = bizplace.id
    """
    return bizplace_store.query_exec(q)

def find_plan_members(plan_ids, fields=['member', 'display_name']):
    plan_ids = tuple(plan_ids)
    clause = 'member IN (SELECT subscriber_id FROM subscription WHERE plan_id IN %s)'
    clause_values = (plan_ids,)
    return memberprofile_store.get_by_clause(clause, clause_values, fields)
