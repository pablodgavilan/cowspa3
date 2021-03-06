from nose.tools import assert_raises

import commontest
import test_data

import datetime
import be.repository.access as dbaccess
import be.apis.invoice as invoicelib
import be.apis.usage as usagelib
import be.apis.invoicepref as invoicepreflib
import test_usage
import test_member

import be.errors as errors

# dependencies member usage

another_invoice_id = None

def setup():
    commontest.setup_test_env()
    env.context.pgcursor.connection.commit()
    commontest.setup_system_context()

def test_add_invoice():
    start = datetime.datetime.now() - datetime.timedelta(1)
    end = datetime.datetime.now() + datetime.timedelta(1)
    uninvoiced = usagelib.usage_collection.uninvoiced(member_id=test_data.member_id, start=start, end=end, res_owner_id=test_data.bizplace_id)
    data = dict(usages=[usage.id for usage in uninvoiced], member=test_data.member_id, issuer=test_data.bizplace_id)
    assert len(data['usages']) > 0, "no point in testing if there are no usages"
    invoice_id = invoicelib.invoice_collection.new(**data)
    test_data.invoice_id = invoice_id
    env.context.pgcursor.connection.commit()
    for usage_id in data['usages']:
        assert dbaccess.usage_store.get(usage_id, ['invoice']) == invoice_id
    env.context.pgcursor.connection.commit()

def test_send():
    info = invoicelib.invoice_resource.info(test_data.invoice_id)
    assert info.number == None
    invoicelib.invoice_resource.send(test_data.invoice_id)
    env.context.pgcursor.connection.commit()
    info = invoicelib.invoice_resource.info(test_data.invoice_id)
    start_number = invoicepreflib.invoicepref_resource.get(info.issuer, 'start_number')
    assert info.number > start_number, \
        "invoice number [%s] must be greater than start_number [%s]" % (info.number, start_number)
    assert bool(info.sent)

def test_add_another_invoice():
    global another_invoice_id
    start = datetime.datetime.now() - datetime.timedelta(1)
    end = datetime.datetime.now() + datetime.timedelta(100)
    uninvoiced = usagelib.usage_collection.uninvoiced(member_id=test_data.member_id, start=start, end=end, res_owner_id=test_data.bizplace_id)
    data = dict(usages=[usage.id for usage in uninvoiced], member=test_data.member_id, issuer=test_data.bizplace_id, start_date=start.date(), end_date=end.date())
    invoice_id = invoicelib.invoice_collection.new(**data)
    another_invoice_id = invoice_id
    env.context.pgcursor.connection.commit()
    for usage_id in data['usages']:
        assert dbaccess.usage_store.get(usage_id, ['invoice']) == invoice_id
    env.context.pgcursor.connection.commit()

def test_add_more(): # we won't sent these
    for x in range(5):
        start = datetime.datetime.now() - datetime.timedelta(1)
        end = datetime.datetime.now() + datetime.timedelta(100)
        uninvoiced = usagelib.usage_collection.uninvoiced(member_id=test_data.member_id, start=start, end=end, res_owner_id=test_data.bizplace_id)
        data = dict(usages=[usage.id for usage in uninvoiced], member=test_data.member_id, issuer=test_data.bizplace_id, start_date=start.date(), end_date=end.date())
        invoice_id = invoicelib.invoice_collection.new(**data)
        for usage_id in data['usages']:
            assert dbaccess.usage_store.get(usage_id, ['invoice']) == invoice_id
    env.context.pgcursor.connection.commit()

def test_send_another():
    global another_invoice_id
    first_invoice_info = invoicelib.invoice_resource.info(test_data.invoice_id)
    info = invoicelib.invoice_resource.info(another_invoice_id)
    assert info.number == None
    invoicelib.invoice_resource.send(another_invoice_id)
    env.context.pgcursor.connection.commit()
    start_number = invoicepreflib.invoicepref_resource.get(info.issuer, 'start_number')
    info = invoicelib.invoice_resource.info(another_invoice_id)
    assert info.number > start_number, \
        "invoice number [%s] must be greater than start_number [%s]" % (info.number, start_number)
    assert (info.number - first_invoice_info.number) == 1
    assert bool(info.sent)

def test_tamper_invoice():
    assert_raises(Exception, invoicelib.invoice_resource.update, test_data.invoice_id, usages=[2, 4])

def test_delete_sent_invoice():
    assert_raises(errors.ErrorWithHint, invoicelib.invoice_collection.delete, test_data.invoice_id)

def test_force_delete_invoice():
    usage_ids = invoicelib.invoice_resource.info(test_data.invoice_id).usages
    invoicelib.invoice_collection.delete(test_data.invoice_id, force=True)
    for id in usage_ids:
        assert usagelib.usage_resource.info(id).invoice == None

def test_generate():
    usages_before = datetime.date.today() + datetime.timedelta(30)
    invoices = invoicelib.invoice_collection.generate(test_data.bizplace_id, usages_before=usages_before)
    for invoice in invoices:
        usaged_ids = invoice.usages
        usages = (usagelib.usage_resource.info(id) for id in usaged_ids)
        member_ids = set(usage.member for usage in usages)
        expected_members = set(dbaccess.get_billfrom_members(invoice.member))
        assert member_ids.issubset(expected_members)
    env.context.pgcursor.connection.commit()

def test_add_usages():
    # to test uninvoiced usages
    data = dict(
        resource_id=test_data.more_resource_ids[-1],
        member=test_data.member_id,
        resource_owner=test_data.bizplace_id )
    for i in range(21):
        data['start_time'] = datetime.datetime.now().isoformat()
        data['quantity'] = i
        data['resource_name'] = 'Usage %s' % i
        usage_id = usagelib.usage_collection.new(**data)
        assert isinstance(usage_id, (int, long))
    env.context.pgcursor.connection.commit()
