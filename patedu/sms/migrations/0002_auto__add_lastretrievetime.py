# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LastRetrieveTime'
        db.create_table(u'sms_lastretrievetime', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_ret', self.gf('django.db.models.fields.DateTimeField')()),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'sms', ['LastRetrieveTime'])


    def backwards(self, orm):
        # Deleting model 'LastRetrieveTime'
        db.delete_table(u'sms_lastretrievetime')


    models = {
        u'sms.incomingsms': {
            'Meta': {'object_name': 'IncomingSMS'},
            'dtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'msgtxt': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'sender_num': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'sms.lastretrievetime': {
            'Meta': {'object_name': 'LastRetrieveTime'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_ret': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['sms']