# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'NHMTargets'
        db.create_table('common_nhmtargets', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('target_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('target_year', self.gf('django.db.models.fields.IntegerField')()),
            ('target_value', self.gf('django.db.models.fields.IntegerField')()),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')()),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcts_identities.District'])),
        ))
        db.send_create_signal('common', ['NHMTargets'])

        # Adding model 'PopulationData'
        db.create_table('common_populationdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('population', self.gf('django.db.models.fields.IntegerField')()),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')()),
            ('MCTS_ID', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('unit_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('common', ['PopulationData'])


    def backwards(self, orm):
        # Deleting model 'NHMTargets'
        db.delete_table('common_nhmtargets')

        # Deleting model 'PopulationData'
        db.delete_table('common_populationdata')


    models = {
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
            'unit_type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
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
        'mcts_identities.district': {
            'MCTS_ID': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'Meta': {'object_name': 'District'},
            '_lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            '_long': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'head': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['common']