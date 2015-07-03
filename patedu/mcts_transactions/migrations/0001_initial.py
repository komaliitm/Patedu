# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AnalyticsData'
        db.create_table('mcts_transactions_analyticsdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('month', self.gf('django.db.models.fields.IntegerField')()),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('since_months', self.gf('django.db.models.fields.IntegerField')()),
            ('block', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcts_identities.Block'])),
            ('summary', self.gf('django.db.models.fields.TextField')()),
            ('summary_anc', self.gf('django.db.models.fields.TextField')()),
            ('summary_pnc', self.gf('django.db.models.fields.TextField')()),
            ('summary_imm', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('mcts_transactions', ['AnalyticsData'])


    def backwards(self, orm):
        # Deleting model 'AnalyticsData'
        db.delete_table('mcts_transactions_analyticsdata')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'mcts_identities.address': {
            'Meta': {'object_name': 'Address'},
            '_lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            '_long': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'village': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'village_mcts_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        },
        'mcts_identities.beneficiary': {
            'MCTS_ID': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'Meta': {'object_name': 'Beneficiary', '_ormbases': ['auth.User']},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'address': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'beneficiaries'", 'null': 'True', 'to': "orm['mcts_identities.Address']"}),
            'caregiver': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.CareGiver']", 'null': 'True'}),
            'careprovider': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'beneficiaries'", 'null': 'True', 'to': "orm['mcts_identities.CareProvider']"}),
            'createdon': ('django.db.models.fields.DateTimeField', [], {}),
            'gaurdian': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'gaurdian_relation': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'language': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'modifiedon': ('django.db.models.fields.DateTimeField', [], {}),
            'notify_number': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'}),
            'notify_number_type': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'registration_year': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'subcenter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.SubCenter']"}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'mcts_identities.block': {
            'MCTS_ID': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'Meta': {'object_name': 'Block'},
            '_lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            '_long': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'head': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'mcts_identities.caregiver': {
            'Meta': {'object_name': 'CareGiver', '_ormbases': ['auth.User']},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.Address']", 'null': 'True'}),
            'designation': ('django.db.models.fields.CharField', [], {'default': "'ASHA'", 'max_length': '20'}),
            'education_status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'}),
            'reports_to': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'mcts_identities.careprovider': {
            'Meta': {'object_name': 'CareProvider', '_ormbases': ['auth.User']},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.Address']", 'null': 'True'}),
            'degree': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'designation': ('django.db.models.fields.CharField', [], {'default': "'ANM'", 'max_length': '20'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'mcts_identities.district': {
            'MCTS_ID': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'Meta': {'object_name': 'District'},
            '_lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            '_long': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'head': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'mcts_identities.healthfacility': {
            'MCTS_ID': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'Meta': {'object_name': 'HealthFacility'},
            '_lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            '_long': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'head': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'mcts_identities.subcenter': {
            'MCTS_ID': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'Meta': {'object_name': 'SubCenter'},
            '_lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            '_long': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'block': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.Block']"}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.District']"}),
            'health_facility': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.HealthFacility']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'mcts_transactions.analyticsdata': {
            'Meta': {'object_name': 'AnalyticsData'},
            'block': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.Block']"}),
            'data': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {}),
            'since_months': ('django.db.models.fields.IntegerField', [], {}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'summary_anc': ('django.db.models.fields.TextField', [], {}),
            'summary_imm': ('django.db.models.fields.TextField', [], {}),
            'summary_pnc': ('django.db.models.fields.TextField', [], {}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'mcts_transactions.content': {
            'Meta': {'object_name': 'Content'},
            'aw_msg_email': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True'}),
            'aw_msg_ivr': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True'}),
            'aw_msg_sms': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'msg_index': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sch_msg_email': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True'}),
            'sch_msg_ivr': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True'}),
            'sch_msg_sms': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'mcts_transactions.contentdelivered': {
            'Meta': {'object_name': 'ContentDelivered'},
            'benefeciary': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.Beneficiary']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medium': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'msg': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'mcts_transactions.dueevents': {
            'Meta': {'object_name': 'DueEvents'},
            'beneficiary': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'due_events'", 'to': "orm['mcts_identities.Beneficiary']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_transactions.Events']"}),
            'handled': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'subcenter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.SubCenter']"})
        },
        'mcts_transactions.events': {
            'MCTS_ID': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'Meta': {'object_name': 'Events'},
            'category': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'content_index': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'val': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'mcts_transactions.overdueevents': {
            'Meta': {'object_name': 'OverDueEvents'},
            'beneficiary': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'odue_events'", 'to': "orm['mcts_identities.Beneficiary']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_transactions.Events']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'subcenter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.SubCenter']"})
        },
        'mcts_transactions.transactions': {
            'Meta': {'object_name': 'Transactions'},
            'beneficiary': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'txns'", 'to': "orm['mcts_identities.Beneficiary']"}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_transactions.Events']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'subcenter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.SubCenter']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['mcts_transactions']