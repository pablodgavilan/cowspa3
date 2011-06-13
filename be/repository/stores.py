import bases.persistence

PGStore = bases.persistence.PGStore

cursor_getter = lambda x: env.context.pgcursor

class PGStore(PGStore):
    cursor_getter = cursor_getter

class User(PGStore):
    table_name = "account"
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    state INTEGER default 1 NOT NULL
    """

class Contact(PGStore):
    table_name = "contact"
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    owner TEXT NOT NULL,
    address TEXT,
    city TEXT,
    country TEXT,
    pincode TEXT,
    homephone TEXT,
    mobile TEXT,
    fax TEXT,
    email TEXT NOT NULL,
    skype TEXT,
    sip TEXT
    """

class MemberPref(PGStore):
    table_name = "member_pref"
    create_sql = """
    member INTEGER NOT NULL,
    theme TEXT DEFAULT 'default',
    language TEXT DEFAULT 'en'
    """

class MemberServices(PGStore):
    table_name = "member_service"
    create_sql = """
    member TEXT NOT NULL,
    webpage boolean default false NOT NULL
    """

#class MemberProfileSecurity(PGStore):
#    #membership_id = IntegerField(required=True)
#    property_name = Attribute(required=True)
#    #level = ListField(required=True) # 0 off 1 on: [anonymous access][all locations][same location][private]

class MemberProfile(PGStore):
    table_name = "member_profile"
    create_sql = """
    member INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT,
    display_name TEXT,
    short_description TEXT,
    long_description TEXT,
    interests TEXT[],
    expertise TEXT[],
    website TEXT,
    blog TEXT,
    twitter TEXT[2],
    facebook TEXT[2],
    linkedin TEXT[2],
    use_gravtar boolean default false
    """

# Container objects
class Member(PGStore):
    table_name = "member"
    create_sql = """
    id INTEGER NOT NULL,
    contact INTEGER NOT NULL,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    state INTEGER default 1 NOT NULL
    """

class Registered(PGStore):
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    activation_key TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT,
    email TEXT NOT NULL,
    ipaddr inet
    """

class Session(PGStore):
    create_sql = """
    token TEXT NOT NULL,
    user_id integer NOT NULL UNIQUE,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    last_seen TIMESTAMP WITHOUT TIME ZONE
    """

class Permission(PGStore):
    table_name = "permission"
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    label TEXT,
    description TEXT
    """

class Role(PGStore):
    table_name = "role"
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    label TEXT,
    description TEXT,
    permissions smallint[] NOT NULL
    """

class UserRole(PGStore):
    create_sql = """
    user_id integer NOT NULL,
    role_id TEXT NOT NULL
    """

class UserPermission(PGStore):
    create_sql = """
    user_id integer NOT NULL,
    permission_id TEXT NOT NULL
    """

class BizProfile(PGStore):
    create_sql = """
    short_description TEXT,
    long_description TEXT,
    tags TEXT[],
    website TEXT,
    blog TEXT,
    twitter TEXT[2],
    facebook TEXT[2],
    linkedin TEXT[2]
    """

class BizplaceProfile(PGStore):
    create_sql = """
    short_description TEXT,
    long_description TEXT,
    tags TEXT[],
    website TEXT,
    blog TEXT,
    twitter TEXT[2],
    facebook TEXT[2],
    linkedin TEXT[2]
    """

#class BizInvoicingPref(PGStore):
#    invoice_logo = Attribute()
#
class Biz(PGStore):
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    name TEXT NOT NULL,
    enabled boolean default true NOT NULL,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    logo TEXT,
    contact INTEGER
    """

class BizPlace(PGStore):
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    name TEXT NOT NULL,
    enabled boolean default true NOT NULL,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    contact INTEGER,
    langs TEXT[],
    tz TEXT,
    holidays smallint[],
    biz TEXT
    """

class Request(PGStore):
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    acted_at TIMESTAMP WITHOUT TIME ZONE,
    requestor_id integer,
    request_note TEXT,
    status smallint default 0 NOT NULL,
    approver_id integer,
    approver_perm TEXT NOT NULL,
    _req_data bytea
    """

class Plan(PGStore):
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    name TEXT NOT NULL,
    bizplace_id integer NOT NULL,
    description TEXT,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    state INTEGER default 1 NOT NULL
    """

class Subscriptions(PGStore):
    create_sql = """
    subscriber_id INTEGER NOT NULL UNIQUE,
    plan_id INTEGER NOT NULL
    """

class Resource(PGStore):
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    name TEXT NOT NULL,
    owner TEXT NOT NULL
    """

class Pricing(PGStore):
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    name TEXT NOT NULL,
    starts TIMESTAMP WITHOUT TIME ZONE NOT NULL
    """

class Price(PGStore):
    create_sql = """
    pricing_id INTEGER NOT NULL,
    plan_id INTEGER NOT NULL,
    resource_id INTEGER NOT NULL,
    cost NUMERIC(16, 2),
    state INTEGER default 1 NOT NULL
    """

class Usage(PGStore):
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    resource_id INTEGER,
    resource_name TEXT,
    calculated_cost NUMERIC(16, 2),
    cost NUMERIC(16, 2)
    """

class Invoice(PGStore):
    create_sql = """
    id SERIAL NOT NULL UNIQUE,

#class Activity(PGStore):
#    name = Attribute(required=True)
#    created = DateTimeField(auto_now_add=False)
