import datetime
import be.repository.access as dbaccess

biz_store = dbaccess.biz_store
bizplace_store = dbaccess.bizplace_store
plan_store = dbaccess.plan_store
subscription_store = dbaccess.subscription_store

def new(name, bizplace_id, description=''):
    created = datetime.datetime.now()
    data = dict(name=name, bizplace=bizplace_id, description=description, created=created)
    plan_id = plan_store.add(**data)
    return plan_id

def list(bizplace_id):
    """
    returns list of plan info dicts for requested bizplace
    """

def update(plan_id, mod_data):
    """
    """

def delete(plan_id):
    """
    Deletes a plan. Only if there are no subscribers.
    """

def subscribers(plan_id):
    """
    returns list of subscriber dicts.
    Subscriber Dict keys include following
    - member id
    - display name
    """

def new_subscriber(plan_id, subscriber_id):
    """
    """
    plan = plan_store.get(plan_id)
    bizplace = bizplace_store.get(plan.bizplace)
    subscription_store.add(plan_id=plan_id, subscriber_id=subscriber_id, bizplace_id=plan.bizplace, \
        bizplace_name=bizplace.name, plan_name=plan.name)
    return True

def new_subscribers(plan_id, subscriber_ids):
    """
    """
    plan = plan_store.get(plan_id)
    bizplace = bizplace_store.get(plan.bizplace)
    for subscriber_id in subscriber_ids:
        subscription_store.add(plan_id=plan_id, subscriber_id=subscriber_id, bizplace_id=plan.bizplace, \
            bizplace_name=bizplace.name, plan_name=plan.name)
    return True


def remove_subscriber(plan_id, subscriber_id):
    """
    """

def change_subscription(subscriber_id, current_plan_id, new_plan_id, change_date):
    """
    """
