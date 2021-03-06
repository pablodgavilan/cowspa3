import datetime
import csv
import cStringIO
import commonlib.shared.constants
import be.repository.access as dbaccess
import commonlib.helpers as helpers
import be.apis.activities as activitylib
import be.apis.user as userlib
import be.apis.role as rolelib
import commonlib.shared.static as data_lists
import be.apis.invoicepref as invoicepreflib

user_store = dbaccess.stores.user_store
member_store = dbaccess.stores.member_store
contact_store = dbaccess.stores.contact_store
profile_store = dbaccess.stores.memberprofile_store
memberpref_store = dbaccess.stores.memberpref_store

class MemberCollection:
    def new(self, email, username=None, password=None, first_name=None, enabled=True, language='en', last_name=None, name=None, interests=None, expertise=None, address=None, city=None, province=None, country=None, pincode=None, work=None, home=None, mobile=None, fax=None, skype=None, website=None, short_description=None, long_description=None, twitter=None, facebook=None, blog=None, linkedin=None, use_gravtar=None, theme="default", mtype="individual", organization=None, company_no=None, number=None, created=None, enc_password=None,  biz_type='', introduced_by='', tariff_id=None, bizplace_id=0):

        if not name: name = first_name + ' ' + (last_name or '')
        created = created if created else datetime.datetime.now() # migration specific
        user_id = userlib.new(username, password, enabled, enc_password)

        data = dict(member=user_id, language=language, theme=theme)
        memberpref_store.add(**data)

        #owner = user_id
        data = dict(member=user_id, first_name=first_name, last_name=last_name, name=name, short_description=short_description, long_description=long_description, interests=interests, expertise=expertise, website=website, twitter=twitter, facebook=facebook, blog=blog, linkedin=linkedin, use_gravtar=use_gravtar, id=user_id, email=email, address=address, city=city, country=country, pincode=pincode, work=work, home=home, mobile=mobile, fax=fax, skype=skype, created=created, enabled=enabled, type=mtype, province=province, biz_type=biz_type, introduced_by=introduced_by)

        if number: data['number'] = number # migration specific
        member_store.add(**data)

        search_d = dict(id=user_id, name=name, short_description=short_description, long_description=long_description, username=username)
        #searchlib.add(search_d)

        invoicepreflib.invoicepref_collection.new(**dict(owner=user_id))

        new_roles = ['member'] if bizplace_id else ['registered']
        rolelib.new_roles(user_id=user_id, roles=['member'], context=bizplace_id)

        data = dict(name=name, id=user_id)
        member_activities = dict(individual=dict(category='member_management', name='member_created'),
                                 organization=dict(category='organization_management', name='organization_created'))
        activity_id = activitylib.add(member_activities[mtype]['category'], member_activities[mtype]['name'], data, created)

        return user_id

    def delete(self, member_id):
        contact_store.remove_by(owner=member_id)
        member_store.remove(member_id)
        raise NotImplemented

    def list(self, formember_id, bizplace_ids=[], hashrows=True):
        my_bizplace_ids = [ms.bizplace_id for ms in dbaccess.find_memberships(formember_id)]
        if bizplace_ids:
            bizplace_ids = set(my_bizplace_ids).intersection(bizplace_ids)
        member_list = []
        for m_dict in dbaccess.find_bizplace_members(bizplace_ids, ['member', 'name', 'email'], hashrows):
            if isinstance(m_dict, dict): m_dict['id'] = m_dict.pop('member')
            member_list.append(m_dict)
        return member_list

    def search_deprecated(self, q, options={'mybizplace': False}, limit=5, mtype="member"):
        """
        q: (first or last name or both) or member_id or email or organization. N members whose respective properties starts with provided word (q) where N is limit.
        options:
            mybizplace:
                if True only members having membership in the bizplaces where the current user has membership are returned
                if False membership is not considered
                membership check is not required if current user has admin role
        limit: number of results to return
        return -> list of tuples containing member's display name and member id
        """
        query_parts = q.split()
        return dbaccess.search_member(query_parts, options, limit, mtype)

    def search(self, q, context, options={}, limit=10):
        """
        q: partial/full first name or last name or both # TODO search email
        options:
            enabled: True/False (True)
            type: member/organization (None). None ignores type
        limit: number of results to return
        return -> list of tuples containing member's display name and member id
        """
        words = q.split()
        options_default = dict(enabled=True, type=None)
        options = dict((k, options.get(k, v)) for k,v in options_default.items())
        return dbaccess.search_members(words, context, options, limit)

    def export(self, context, extra_fields=[], format=None):
        """
        extra_fields: list of more fields to include. Options: organzation, website, long_description
        format: None, csv
        """
        header, data = dbaccess.get_members_data(context, extra_fields)
        contents = (header, data)
        if format == 'csv':
            out = cStringIO.StringIO()
            writer = csv.writer(out, lineterminator='\n', quoting=csv.QUOTE_ALL)
            writer.writerow(header)
            writer.writerows(data)
            contents = out.getvalue()
            out.close()
        return contents

class MemberResource:

    get_attributes = ['id', 'created', 'enabled', 'hidden', 'first_name', 'last_name', 'name', 'short_description', 'long_description', 'interests', 'expertise', 'website', 'blog', 'twitter', 'facebook', 'linkedin', 'use_gravtar', 'organization', 'address', 'city', 'province', 'country', 'pincode', 'phone', 'mobile', 'fax', 'email', 'skype']
    set_attributes = ['enabled', 'hidden', 'first_name', 'last_name', 'name', 'short_description', 'long_description', 'interests', 'expertise', 'website', 'blog', 'twitter', 'facebook', 'linkedin', 'use_gravtar', 'organization', 'address', 'city', 'country', 'province', 'pincode', 'work', 'home', 'mobile', 'fax', 'email', 'skype']

    def update(self, member_id, **mod_data):
        if 'username' in mod_data or 'password' in mod_data:
            userlib.update(member_id, **mod_data)
        elif 'theme' in mod_data or 'language' in mod_data:
            memberpref_store.update_by(dict(member=member_id), **mod_data)
        else:
            member_store.update(member_id, **mod_data)

        name, mtype = member_store.get(member_id, fields=['name', 'type'], hashrows=False)
        data = dict(id=member_id, name=name, attrs=', '.join(attr for attr in mod_data))
        member_activities = dict(individual=dict(category='member_management', name='member_updated'),\
                                 organization=dict(category='organization_management', name='organization_updated'))
        activity_id = activitylib.add(member_activities[mtype]['category'], member_activities[mtype]['name'], data)

    def info(self, member_id):
        info = member_store.get(member_id, ['id', 'number', 'enabled', 'name'])
        return info

    def details(self, member_id, bizplace_ids=[]):
        member = member_store.get(member_id, ['type', 'number'])
        profile = profile_store.get_by(dict(member=member_id))[0]
        contact = contact_store.get_by(dict(id=member_id))[0]
        account = dict(username=user_store.get(member_id, ['username']), password="") if member.type == "individual" else []
        preferences = memberpref_store.get_by(dict(member=member_id), ['theme', 'language'])[0] if member.type == "individual" else []
        memberships = dbaccess.get_member_current_memberships(member_id, bizplace_ids)
        return dict(number=member.number, mtype=member.type, profile=profile, contact=contact, account=account, preferences=preferences, memberships=memberships)

    def contact(self, member_id):
        return contact_store.get_by(dict(id=member_id))[0]

    def get(self, member_id, attrname):
        if not attrname in self.get_attributes: return
        return member_store.get(member_id, fields=[attrname])

    def set(self, member_id, attrname, v):
        if not attrname in self.set_attributes: return
        self.update(member_id, **{attrname: v})

member_resource = MemberResource()
member_collection = MemberCollection()
