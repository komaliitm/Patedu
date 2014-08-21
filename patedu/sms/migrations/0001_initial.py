# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IncomingSMS'
        db.create_table('sms_incomingsms', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sender_num', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('dtime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('msgtxt', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('processed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('sms', ['IncomingSMS'])


    def backwards(self, orm):
        # Deleting model 'IncomingSMS'
        db.delete_table('sms_incomingsms')


    models = {
        'sms.incomingsms': {
            'Meta': {'object_name': 'IncomingSMS'},
            'dtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'msgtxt': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sender_num': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['sms']