# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ExotelCallStatus.exotel_update_received'
        db.add_column('common_exotelcallstatus', 'exotel_update_received',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ExotelCallStatus.exotel_update_received'
        db.delete_column('common_exotelcallstatus', 'exotel_update_received')


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
        'common.analyticsdata': {
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
        'common.ancreportings': {
            'Meta': {'object_name': 'ANCReportings'},
            'anc1_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'anc2_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'anc3_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'anc4_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'benef': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.ANCBenef']", 'unique': 'True'}),
            'delivery_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'common.exotelcallstatus': {
            'Meta': {'object_name': 'ExotelCallStatus'},
            'date_initiated': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'dt_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'exotel_update_received': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'recording_url': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'sid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'subcenter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.SubCenter']", 'null': 'True'}),
            'uid': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'common.immreportings': {
            'Meta': {'object_name': 'IMMReportings'},
            'benef': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.IMMBenef']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measles_date': ('django.db.models.fields.DateField', [], {'null': 'True'})
        },
        'common.nhmtargets': {
            'Meta': {'object_name': 'NHMTargets'},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.District']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'target_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'target_value': ('django.db.models.fields.IntegerField', [], {}),
            'target_year': ('django.db.models.fields.IntegerField', [], {})
        },
        'common.populationdata': {
            'MCTS_ID': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'Meta': {'object_name': 'PopulationData'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'population': ('django.db.models.fields.IntegerField', [], {}),
            'unit_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'year': ('django.db.models.fields.IntegerField', [], {'default': '2015'})
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
        'mcts_identities.ancbenef': {
            'EDD': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'LMP': ('django.db.models.fields.DateField', [], {}),
            'Meta': {'object_name': 'ANCBenef', '_ormbases': ['mcts_identities.Beneficiary']},
            'beneficiary_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['mcts_identities.Beneficiary']", 'unique': 'True', 'primary_key': 'True'}),
            'husband': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'mcts_identities.beneficiary': {
            'MCTS_ID': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'Meta': {'object_name': 'Beneficiary', '_ormbases': ['auth.User']},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'address': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'beneficiaries'", 'null': 'True', 'to': "orm['mcts_identities.Address']"}),
            'caregiver': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'beneficiaries'", 'null': 'True', 'to': "orm['mcts_identities.CareGiver']"}),
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
        'mcts_identities.immbenef': {
            'Meta': {'object_name': 'IMMBenef', '_ormbases': ['mcts_identities.Beneficiary']},
            'beneficiary_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['mcts_identities.Beneficiary']", 'unique': 'True', 'primary_key': 'True'}),
            'child_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'child_sex': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'mother_mcts_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'mother_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        },
        'mcts_identities.subcenter': {
            'MCTS_ID': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'Meta': {'object_name': 'SubCenter'},
            '_lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            '_long': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'block': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subcenters'", 'to': "orm['mcts_identities.Block']"}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.District']"}),
            'health_facility': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcts_identities.HealthFacility']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['common']