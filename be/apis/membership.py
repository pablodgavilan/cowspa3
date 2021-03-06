import datetime
import collections
import calendar

import bases.app as applib
import commonlib.helpers
import commonlib.messaging.messages as messages
import be.repository.access as dbaccess
import be.apis.activities as activitylib
import be.apis.usage as usagelib
import be.apis.resource as resourcelib

import be.apis.activities as activitylib

resource_store = dbaccess.stores.resource_store
bizplace_store = dbaccess.stores.bizplace_store
membership_store = dbaccess.stores.membership_store
member_store = dbaccess.stores.member_store

membership = applib.Resource()
memberships = applib.Collection()

def new(tariff_id, member_id, starts, ends, skip_usages=False):
    """
    """
    # TODO skip_usages is there mainly to help migration. If there is no use case if must retire post migration 
    tariff = resource_store.get(tariff_id)
    bizplace = bizplace_store.get(tariff.owner)
    starts_dt = commonlib.helpers.iso2date(starts)
    ends_dt = commonlib.helpers.iso2date(ends)
    overlapping_membership = dbaccess.get_member_membership(member_id, bizplace.id, starts_dt)
    if ends_dt and starts_dt > ends_dt:
        raise Exception("End date should be greater than start date.")
    if overlapping_membership:
        if overlapping_membership['ends'] or overlapping_membership['starts']==starts_dt:
            raise Exception("Start date is overlapping with another membership.")
        update(overlapping_membership['id'], ends=(starts_dt-datetime.timedelta(1)).isoformat())
    overlapping_membership = dbaccess.get_member_membership(member_id, bizplace.id, ends_dt)
    if ends_dt and overlapping_membership:
        raise Exception("End date is overlapping with another membership.")
    elif not ends_dt:
        next_membership = dbaccess.get_member_next_memberships(member_id, starts_dt, [tariff.owner])
        if  next_membership: ends_dt = next_membership[0]['starts'] - datetime.timedelta(1)
    membership_store.add(tariff_id=tariff_id, starts=starts_dt, ends=ends_dt,member_id=member_id,\
                         bizplace_id=tariff.owner, bizplace_name=bizplace.name, tariff_name=tariff.name)
    current_date = datetime.datetime.now().date()
    is_guest_tariff = tariff.id == bizplace.default_tariff
    if not is_guest_tariff and not skip_usages:
        return create_membership_usages(starts_dt, ends_dt, tariff_id, tariff.name, tariff.owner, member_id)

def create_membership_usages(starts, ends, tariff_id, tariff_name, tariff_owner, member):
    # find start, end dates for every months month in start-end and create that many usages
    # ex. starts: 3 Jan 2021 ends: 5 Apr 2021
    # usage 1: 3 Jan - 31 Jan 2021
    # usage 2: 1 Feb - 28 Feb 2021
    # usage 3: 1 Mar - 31 Mar 2021
    # usage 4: 1 Apr - 05 Apr 2021
    current_date = datetime.datetime.now().date()
    current_months_last_date = datetime.date(current_date.year, current_date.month, calendar.monthrange(current_date.year, current_date.month)[1])
    if not ends: # Other usages would be created by scheduled job
        ends = current_months_last_date
    while starts <= ends:
        if starts.month == ends.month:
            new_ends = ends
        else:
            new_ends = datetime.date(starts.year, starts.month, calendar.monthrange(starts.year, starts.month)[1])
        data = dict(resource_id=tariff_id, resource_name=tariff_name, resource_owner=tariff_owner, member=member, start_time=starts.isoformat(), end_time=new_ends.isoformat())
        usagelib.usage_collection.new(**data)
        starts = new_ends + datetime.timedelta(1)
    return True

def bulk_new(tariff_id, member_ids, starts, ends):
    """
    """
    tariff = resource_store.get(tariff_id)
    bizplace = bizplace_store.get(tariff.owner)
    for member_id in member_ids:
        new(tariff_id, member_id, starts, ends)
    return True

def list_by_tariff(tariff_id, at_time=None):
    """
    returns list of member dicts.
    Subscriber Dict keys include following
    - member id
    - display name
    """
    at_time = commonlib.helpers.iso2date(at_time) if at_time else at_time
    member_list = []
    for m_dict in dbaccess.find_tariff_members([tariff_id], at_time):
        m_dict['id'] = m_dict.pop('member')
        member_list.append(m_dict)
    return member_list

def list_by_bizplace(bizplace_id, at_time=None, hashrows=True):
    at_time = commonlib.helpers.iso2date(at_time) if at_time else at_time
    return dbaccess.find_bizplace_members_with_membership(bizplace_id=bizplace_id, at_time=at_time, hashrows=hashrows)

def list_for_member(member_id, bizplace_ids=[], not_current=False):
    return dbaccess.get_member_memberships(member_id=member_id, bizplace_ids=bizplace_ids, not_current=not_current)

def list_memberships(by_tariff=None, for_member=None, not_current=False, at_time=None, bizplace_ids=[]):
    if by_tariff:
        return list_by_tariff(by_tariff, at_time)
    return list_for_member(for_member, bizplace_ids, not_current)

def get_total_memberships(bizplace, starts, ends, by_tariff=False):
    """
    by_tariff --> True/False (To display count by grouping by tariff)
    """
    return dbaccess.get_count_of_memberships(bizplace, starts, ends, by_tariff)

def autoextend(bizplace_id=None, month=None, year=None):
    """
    bizplace_id: int or None if None, tariffs of all bizplaces would be extended
    Extends tariff with no end date for specified month (with year). If month is None, current month is assumed.
    Supposed to be called from a monthly scheduled job
    """
    # find memberships with ends None or >= month, year
    # for each membership:
    #    find usage in next month
    #    if no usage: create one
    if not month or not year:
        today = datetime.date.today()
        month = today.month
        year = today.year
    monthstart = datetime.date(year, month, 1)
    monthend = datetime.date(year, month, calendar.monthrange(year, month)[1])
    crit = dict(ends=None) if not bizplace_id else dict(ends=None, bizplace_id=bizplace_id)
    memberships = membership_store.get_by(crit=crit)
    member_ids = [mb.member_id for mb in memberships]
    members = dict((member.id, member) for member in member_store.get_many(member_ids, ['id', 'name', 'member']))
    bizplaces = dict(bizplace_store.get_all(['id', 'name'], hashrows=False))

    count = 0
    extensions = collections.defaultdict(list)
    for ms in memberships:
        usages = dbaccess.find_usages_within_date_range(ms.tariff_id, ms.member_id, monthstart, monthend)
        if not usages:
            data = dict(resource_id=ms.tariff_id, resource_name=ms.tariff_name, resource_owner=ms.bizplace_id, member=ms.member_id, start_time=monthstart.isoformat(), end_time=monthend.isoformat())
            usagelib.usage_collection.new(**data)
            extensions[ms.bizplace_id].append(dict(tariff_id=ms.tariff_id, member=members[ms.member_id]))
            count += 1

    data = dict(month=month, year=year, extensions=extensions, count=count, bizplaces=bizplaces)
    notification = messages.autoextend(data, dict(to=('Admin', 'cowspa.dev@gmail.com')))
    notification.build()
    notification.email()
    #activitylib.add('scheduled_job', 'tariff_autoextend', data) #TODO

    return True

memberships.new = new
memberships.bulk_new = bulk_new
memberships.list = list_memberships
memberships.list_by_bizplace = list_by_bizplace

def info(membership_id):
    """
    """
    return membership_store.get(membership_id)

def stop(membership_id, ends):
    """
    marks a membership to stop given date and as necessary cancels/removes/chnages tariff usages associated with this membership
    """
    return update(membership_id, ends=ends)

def update(membership_id, **mod_data):
    """
    """
    old_data = info(membership_id)
    usages = usagelib.usage_collection.find(start=old_data['starts'], end=old_data['ends'] if old_data['ends'] else datetime.datetime.now().date(), member_ids=[old_data['member_id']], resource_ids=[old_data['tariff_id']], exclude_credit_usages=True, exclude_cancelled_usages=True)
    starts = commonlib.helpers.iso2date(mod_data['starts']) if 'starts' in mod_data else old_data['starts']
    ends = commonlib.helpers.iso2date(mod_data['ends']) if 'ends' in mod_data else old_data['ends']

    #Checking that new starts & ends are valid or not
    if ends and starts > ends:
        raise Exception("End date should be greater than start date.")
    overlapping_membership = dbaccess.get_member_membership(old_data['member_id'], old_data['bizplace_id'], starts, [membership_id])
    if overlapping_membership:
        if overlapping_membership['ends']:
            raise Exception("Start date is overlapping with another membership.")
        update(overlapping_membership['id'], ends=(starts-datetime.timedelta(1)).isoformat())
    overlapping_membership = dbaccess.get_member_membership(old_data['member_id'], old_data['bizplace_id'], ends, [membership_id])
    if ends and overlapping_membership:
        raise Exception("End date is overlapping with another membership.")
    elif not ends:
        next_membership = dbaccess.get_member_next_memberships(old_data['member_id'], starts, [old_data['bizplace_id']], [membership_id])
        if  next_membership: ends = next_membership[0]['starts'] - datetime.timedelta(1)

    #Deleting usages which are out of starts<->ends
    current_date = datetime.datetime.now().date()
    current_months_last_date = datetime.date(current_date.year, current_date.month, calendar.monthrange(current_date.year, current_date.month)[1])
    if not ends or ends > current_months_last_date:
        usage_ends = current_months_last_date
    else:
        usage_ends = ends

    rev_usages = range(len(usages)-1, -1, -1)
    for i in rev_usages:
        if usages[i]['start_time'].date() < starts or usages[i]['end_time'].date() > usage_ends:
            usagelib.usage_collection.delete(usages[i]['id'])
            del(usages[i])

    #Creating new membership usages
    if usages:
        if starts != usages[0]['start_time'].date():
            create_membership_usages(starts, (usages[0]['start_time']-datetime.timedelta(1)).date(),\
             old_data['tariff_id'], old_data['tariff_name'], old_data['bizplace_id'], old_data['member_id'])
        if usage_ends != usages[-1]['end_time'].date():
            create_membership_usages((usages[-1]['end_time']+datetime.timedelta(1)).date(), usage_ends,\
             old_data['tariff_id'], old_data['tariff_name'], old_data['bizplace_id'], old_data['member_id'])
    else:
        create_membership_usages(starts, usage_ends, old_data['tariff_id'], old_data['tariff_name'],\
             old_data['bizplace_id'], old_data['member_id'])

    return membership_store.update(membership_id, **mod_data)

def delete(membership_id):
    """
    """
    membership = info(membership_id)
    usages = usagelib.usage_collection.find(start=membership['starts'], end=membership['ends'], member_ids=[membership['member_id']], resource_ids=[membership['tariff_id']], exclude_credit_usages=True, exclude_cancelled_usages=True)
    usagelib.usage_collection.bulk_delete([usage.id for usage in usages])
    return membership_store.remove(membership_id)

membership.info = info
membership.delete = delete
membership.stop = stop
membership.update = update
