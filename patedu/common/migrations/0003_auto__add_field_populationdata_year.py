# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PopulationData.year'
        db.add_column('common_populationdata', 'year',
                      self.gf('django.db.models.fields.IntegerField')(default=2015),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'PopulationData.year'
        db.delete_column('common_populationdata', 'year')


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
            'unit_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'year': ('django.db.models.fields.IntegerField', [], {'default': '2015'})
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