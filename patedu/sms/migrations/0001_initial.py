# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IncomingSMS'
        db.create_table(u'sms_incomingsms', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sender_num', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('dtime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('msgtxt', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('processed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('remark', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal(u'sms', ['IncomingSMS'])


    def backwards(self, orm):
        # Deleting model 'IncomingSMS'
        db.delete_table(u'sms_incomingsms')


    models = {
        u'sms.incomingsms': {
            'Meta': {'object_name': 'IncomingSMS'},
            'dtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'msgtxt': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'sender_num': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['sms']