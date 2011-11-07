import cPickle
import datetime
import psycopg2
import be.repository.stores as stores_mod
import bases.persistence

ctxsep = ':'

PGBinary = bases.persistence.PGBinary

user_store = stores_mod.User()
contact_store = stores_mod.Contact()
member_store = stores_mod.Member()
memberpref_store = stores_mod.MemberPref()
memberprofile_store = stores_mod.MemberProfile()
registered_store = stores_mod.Registered()
session_store = stores_mod.Session()
userpermission_store = stores_mod.UserPermission()
userrole_store = stores_mod.UserRole()
bizplace_store = stores_mod.BizPlace()
bizplaceprofile_store = stores_mod.BizplaceProfile()
request_store = stores_mod.Request()
requestpermission_store = stores_mod.RequestPermission()
plan_store = stores_mod.Plan()
subscription_store = stores_mod.Subscription()
resource_store = stores_mod.Resource()
resourcerelation_store = stores_mod.ResourceRelation()
usage_store = stores_mod.Usage()
invoice_store = stores_mod.Invoice()
pricing_store = stores_mod.Pricing()
activity_store = stores_mod.Activity()
activityaccess_store = stores_mod.ActivityAccess()
invoicepref_store = stores_mod.InvoicePref()
billingpref_store = stores_mod.BillingPref()
oidgen_store = stores_mod.OidGen()

class RStore(object): pass

def make_rstore(store):
    rstore = RStore()
    for attr in ('setup', 'add', 'add_many', 'remove', 'remove_by', 'remove_many', 'get', 'get_many', 'get_by', 'get_one_by', 'get_all', 'update', 'update_many', 'update_by', 'count'):
        method = getattr(store, attr)
        setattr(rstore, attr, method)
    return rstore

class stores: pass

stores_by_type = {}

for name, store in stores_mod.known_stores.items():
    setattr(stores, name, make_rstore(store))
    stores_by_type[store.__class__.__name__] = store

def find_memberships(member_id):
    return subscription_store.get_by(crit=dict(subscriber_id=member_id))

def biz_info(biz_id):
    return biz_store.get(biz_id, ['name', 'state', 'short_description', 'tags', 'website', 'blog', 'address', 'city', 'country', 'email'])

bizplace_info_fields = ['id', 'name', 'state', 'short_description', 'tags', 'website', 'blog', 'address', 'city', 'country', 'email']

def bizplace_info(bizplace_id):
    return bizplace_store.get(bizplace_id, bizplace_info_fields)

class Resource(object):
    store = resource_store
    info_fields = ['id', 'name', 'short_description']
    def info(self):
        return self.store.get(self.id, self.info_fields)
    def dependencies(self):
        deps = self.store.get(self.id, ['contains', 'contains_opt', 'requires', 'suggests', 'contained_by', 'required_by', 'suggested_by'])
        dep_ids = list(itertools.chain(*deps.values()))
        return resource_store.get_many(dep_ids, self.info_fields)


def list_activities_by_categories(catesgories, from_date, to_date, limit=20):
    clause = '( category IN %(categories)s) AND created >= %(from_date)s AND created <= %(to_date)s ORDER BY created DESC LIMIT %(limit)s'
    clause_values = dict(categories=tuple(categories), from_date=from_date, to_date=to_date, limit=limit)
    return activity_store.get_by_clause(clause, clause_values, fields=None, hashrows=True)

def list_activities_by_names(names, from_date, to_date, limit=20):
    clause = '(name IN %(names)s) AND created >= %(from_date)s AND created <= %(to_date)s ORDER BY created DESC LIMIT %(limit)s'
    clause_values = dict(names=tuple(names), from_date=from_date, to_date=to_date ,limit=limit)
    return activity_store.get_by_clause(clause, clause_values, fields=None, hashrows=True)

def list_activities_by_roles(roles, limit=15):
    clause = 'role IN %(roles)s GROUP BY created, a_id ORDER BY created DESC LIMIT %(limit)s '
    clause_values = dict(roles=tuple(roles), limit=limit)
    a_ids = [row[0] for row in activityaccess_store.get_by_clause(clause, clause_values, fields=['a_id'], hashrows=False)]
    clause = '(id IN %(a_ids)s) ORDER BY created DESC'
    clause_values = dict(a_ids = tuple(a_ids))
    return activity_store.get_by_clause(clause, clause_values, fields=[], hashrows=True) if len(a_ids)!=0 else []

def list_resources_in_order(owner, fields):
    clause = "owner = %(owner)s ORDER BY name"
    clause_values = dict(owner=owner)
    return resource_store.get_by_clause(clause, clause_values, fields)

def oid2name(oid):
    store = stores_by_type[OidGenerator.get_otype(oid)]
    attr = 'name' if 'name' in store.schema else 'display_name'
    return store.get(oid, [attr], hashrows=False)

def oid2o(oid):
    store = stores_by_type[OidGenerator.get_otype]
    return store.get(int(oid))

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

plan_info_fields = ['id', 'name', 'bizplace', 'description']

def find_bizplace_plans(bizplace_id, fields):
    return plan_store.get_by(crit={'bizplace':bizplace_id}, fields=fields)
    
def list_bizplaces(ids):
    return bizplace_store.get_many(ids,fields=bizplace_info_fields) if ids else []

def list_all_bizplaces():
    return bizplace_store.get_all(fields=bizplace_info_fields)

def find_plan_members(plan_ids, fields=['member', 'display_name'], at_time=None):
    plan_ids = tuple(plan_ids)
    if not at_time: at_time = datetime.datetime.now()
    clause = 'member IN (SELECT subscriber_id FROM subscription WHERE plan_id IN %(plan_ids)s AND starts <= %(at_time)s AND (ends >= %(at_time)s OR ends is NULL))'
    clause_values = dict(plan_ids=plan_ids, at_time=at_time)
    return memberprofile_store.get_by_clause(clause, clause_values, fields)


def find_usage(start, end, res_owner_refs, resource_ids, member_ids, resource_types):
    clauses = []

    if start: clauses.append('start_time >= %(start_time)s')
    if end: clauses.append('start_time <= %(end_time)s')
    if res_owner_refs: clauses.append('(resource_id IN (SELECT id FROM resource WHERE owner IN %(owner_refs)s))')
    if resource_ids: clauses.append('(resource_id IN %(resource_ids)s)')
    if member_ids: clauses.append('(member IN %(member_ids)s)')
    if resource_types: clauses.append('(resource_id IN (SELECT id FROM resource WHERE type IN %(resource_types)s))')

    clauses_s = ' AND '.join(clauses)
    clause_values = dict(start_time=start, end_time=end, resource_ids=tuple(resource_ids), owner_refs=tuple(res_owner_refs), member_id=tuple(member_ids), resource_types=tuple(resource_types))

    return usage_store.get_by_clause(clauses_s, clause_values, fields=None)

def get_member_plan_id(member_id, bizplace_id, date, default=True):
    clause = 'subscriber_id = %(subscriber_id)s AND bizplace_id = %(bizplace_id)s AND starts <= %(date)s AND (ends >= %(date)s OR ends IS NULL)'
    values = dict(subscriber_id=member_id, date=date, bizplace_id=bizplace_id)
    plan_ids = subscription_store.get_by_clause(clause, values, fields=['plan_id'], hashrows=False)
    if plan_ids:
        return plan_ids[0][0]
    elif default:
        return bizplace_store.get(bizplace_id, fields=['default_plan'], hashrows=False)

def get_member_subscription(member_id, bizplace_id, date):
    clause = 'subscriber_id = %(subscriber_id)s AND bizplace_id = %(bizplace_id)s AND starts <= %(date)s AND (ends >= %(date)s OR ends IS NULL)'
    values = dict(subscriber_id=member_id, date=date, bizplace_id=bizplace_id)
    subscriptions = subscription_store.get_by_clause(clause, values)
    if subscriptions:
        return subscriptions[0]

def get_member_tariff_history(member_id, bizplace_ids=[]):
    date = datetime.datetime.now()
    clause = '(subscriber_id = %(subscriber_id)s) AND (ends <= %(date)s)'
    if bizplace_ids:
        clause += ' AND bizplace_id IN %(bizplace_ids)s'
    values = dict(subscriber_id=member_id, date=date, bizplace_ids=bizplace_ids)
    return subscription_store.get_by_clause(clause, values)

def get_member_current_subscriptions(member_id, bizplace_ids=[]):
    date = datetime.datetime.now().date()
    clause = '(subscriber_id = %(subscriber_id)s) AND (starts <= %(date)s) AND (ends IS NULL OR ends >= %(date)s)'
    if bizplace_ids:
        clause += ' AND bizplace_id IN %(bizplace_ids)s'
    values = dict(subscriber_id=member_id, date=date, bizplace_ids=bizplace_ids)
    return subscription_store.get_by_clause(clause, values)

def get_member_subscriptions(member_id, bizplace_ids=[], since=None):
    if not since:
        since = datetime.datetime.now() - datetime.timedelta(365)
    clause = '(subscriber_id = %(subscriber_id)s) AND ((ends >= %(since)s) OR (ends IS NULL))'
    if bizplace_ids:
        clause += ' AND bizplace_id IN %(bizplace_ids)s'
    values = dict(subscriber_id=member_id, since=since, bizplace_ids=bizplace_ids)
    return subscription_store.get_by_clause(clause, values)

def list_invoices(issuer ,limit):
    query = "SELECT invoice.id, member.display_name, invoice.cost::TEXT, DATE(invoice.created)::TEXT as created, invoice.id FROM member, invoice WHERE member.id = invoice.member AND issuer = %(issuer)s ORDER BY created DESC LIMIT %(limit)s"
    values = dict(issuer = issuer, limit = limit) 
    return invoice_store.query_exec(query, values, hashrows=False)
    
def search_member(keys, options, limit):
    fields = ['id', 'display_name']
    query = 'SELECT member.id, member.display_name as name, member.display_name as label, member.email FROM member'
    clause = ""
    if 'global::admin' not in env.context.roles and options['mybizplace']: # TODO: change this post 0.2
        query += ', subscription'
        clause = 'subscription.subscriber_id = Member.id AND subscription.bizplace_id = (SELECT bizplace_id FROM subscription where subscriber_id = %(subscriber_id)s) AND ' 
    if len(keys) == 1:
        try:
            keys[0] = int(keys[0])
            clause += 'Member.id = %(key)s'
        except:
            keys[0] = keys[0] + "%"
            clause += '(Member.first_name ILIKE %(key)s OR Member.last_name ILIKE %(key)s OR Member.email ILIKE %(key)s OR Member.organization ILIKE %(key)s)'
        values = dict(key=keys[0], limit=limit)
    elif len(keys) == 2:
        clause += '((Member.first_name ILIKE %(key1)s AND Member.last_name ILIKE %(key2)s) OR (Member.first_name ILIKE %(key2)s AND Member.last_name ILIKE %(key1)s))'
        values = dict(key1=keys[0], key2=keys[1]+"%", limit=limit)
    query  += ' WHERE '+clause+' LIMIT %(limit)s'  
    values['subscriber_id'] =  env.context.user_id
    
    return member_store.query_exec(query, values)

def search_biz(key, limit):
    fields = ['id', 'name', 'name as label']
    try:
        key = int(key)
        clause = 'id = %(key)s'
    except:
        key = key + "%"
        clause = 'name ILIKE %(key)s OR email ILIKE %(key)s LIMIT %(limit)s'
    clause_values =  dict(key=key, limit=limit)
    return biz_store.get_by_clause(clause, clause_values, fields)

def get_resource_pricing(plan_id, resource_id, usage_time):
    clause = 'plan = %(plan)s AND resource = %(resource)s AND starts <= %(usage_time)s AND (ends >= %(usage_time)s OR ends is NULL)'
    values = dict(plan=plan_id, resource=resource_id, usage_time=usage_time)
    return pricing_store.get_by_clause(clause, values, fields=['id', 'starts', 'ends', 'amount'])

def get_price(resource_id, member_id, usage_time):
    # TODO: if resource owner is not bizplace then?
    bizplace_id = resource_store.get(resource_id, fields=['owner'], hashrows=False)
    plan_id = get_member_plan_id(member_id, bizplace_id, usage_time)
    pricing = get_resource_pricing(plan_id, resource_id, usage_time)
    if pricing:
        return pricing[0].amount

def remove_user_roles(user_id, roles, context):
    clause = 'user_id = %(user_id)s AND context = %(context)s AND role IN %(roles)s'
    userrole_store.remove_by_clause(clause, dict(user_id=user_id, roles=tuple(roles), context=context))

def remove_user_permissions(user_id, permissions, context):
    clause = 'user_id = %(user_id)s AND context = %(context)s AND permission IN %(permissions)s'
    userpermission_store.remove_by_clause(clause, dict(user_id=user_id, permissions=tuple(permissions), context=context))

def search_invoice(keys, options, limit):
    fields = ['id', 'member']
    query = 'SELECT invoice.id, invoice.member FROM invoice, member'
    clause = ""
    if 'global::admin' not in env.context.roles or options['mybizplace']:
        query += ', subscription'
        clause = 'subscription.subscriber_id = Member.id AND subscription.bizplace_id = (SELECT bizplace_id FROM subscription where subscriber_id = %(subscriber_id)s) AND'
    if len(keys) == 1:
        try:
            keys[0] = int(keys[0])
            clause += ' invoice.id = %(key)s'
        except:
            keys[0] = keys[0] + "%"
            clause += ' (member.first_name ILIKE %(key)s OR member.last_name ILIKE %(key)s)'
        values = dict(key=keys[0], limit=limit)
    elif len(keys) == 2:
        clause += '((member.first_name ILIKE %(key1)s AND member.last_name ILIKE %(key2)s) OR (member.first_name ILIKE %(key2)s AND member.last_name ILIKE %(key1)s))'
        values = dict(key1=keys[0], key2=keys[1]+"%", limit=limit)
    query  += ' WHERE '+clause+' AND member.id=invoice.member LIMIT %(limit)s'
    values['subscriber_id'] =  env.context.user_id

    return member_store.query_exec(query, values)

def find_requests_for_approval(perms):
    ctx_perms = tuple((str(c) + ctxsep + p) for c, p in perms)
    clause = " permission IN %(ctx_perms)s"
    values = dict(ctx_perms=ctx_perms)
    req_ids = tuple(row[0] for row in requestpermission_store.get_by_clause(clause, values, fields=['request'], hashrows=False))
    return request_store.get_many(req_ids)

class OidGenerator(object):

    @staticmethod
    def next(otype):
        return oidgen_store.add(**dict(type=otype))

    @staticmethod
    def get_otype(oid):
        return oidgen_store.get(oid, fields=['type'])
