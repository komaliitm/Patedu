# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from common.utils import LoadInitialVaccinesData, LoadInitialVaccineTemplateData, LoadInitialVaccineSMSData

class Migration(DataMigration):

    def forwards(self, orm):
        LoadInitialVaccinesData(orm)
        LoadInitialVaccineSMSData(orm)
        LoadInitialVaccineTemplateData(orm)

    def backwards(self, orm):
        pass

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
        'health_worker.healthworker': {
            'Meta': {'object_name': 'HealthWorker', '_ormbases': ['auth.User']},
            'Post': ('django.db.models.fields.CharField', [], {'default': "'ASHA'", 'max_length': '6'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'vaccination.smsmessages': {
            'Meta': {'object_name': 'SMSMessages'},
            'msg': ('django.db.models.fields.CharField', [], {'max_length': '640'}),
            'msg_identifier': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'})
        },
        'vaccination.vaccinationbeneficiary': {
            'BeneficiaryId': ('django.db.models.fields.CharField', [], {'max_length': '30', 'primary_key': 'True'}),
            'ChildName': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'CreatedOn': ('django.db.models.fields.DateTimeField', [], {}),
            'Dob': ('django.db.models.fields.DateField', [], {}),
            'Gaurdian_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'Language': ('django.db.models.fields.CharField', [], {'default': "'HIN'", 'max_length': '16'}),
            'Meta': {'object_name': 'VaccinationBeneficiary'},
            'ModifiedOn': ('django.db.models.fields.DateTimeField', [], {}),
            'NotifyNumber': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'Sex': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'VerificationCode': ('django.db.models.fields.IntegerField', [], {'max_length': '50'}),
            'health_worker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['health_worker.HealthWorker']", 'null': 'True'}),
            'isScheduleGenerated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'isVerified': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'vaccination.vaccinations': {
            'AgeInWeeks': ('django.db.models.fields.IntegerField', [], {}),
            'Meta': {'object_name': 'Vaccinations'},
            'VaccineName': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'vaccineId': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'})
        },
        'vaccination.vaccinereminder': {
            'Meta': {'object_name': 'VaccineReminder'},
            'dueDate': ('django.db.models.fields.DateField', [], {}),
            'errorCode': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'vaccDate': ('django.db.models.fields.DateField', [], {}),
            'vaccination_beneficiary': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vaccination.VaccinationBeneficiary']"}),
            'vaccine_reference': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vaccination.VaccineReminderTemplate']"})
        },
        'vaccination.vaccineremindertemplate': {
            'Language': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'Meta': {'object_name': 'VaccineReminderTemplate'},
            'Vaccine': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vaccination.Vaccinations']"}),
            'email_message': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ivr_message': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'sms_message': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'stage': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        }
    }

    complete_apps = ['vaccination']
    symmetrical = True
