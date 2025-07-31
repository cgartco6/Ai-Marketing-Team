import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Import agents to test
from agents.commander import ProjectCommander
from agents.profiler import PsychProfiler
from agents.content_engine import ContentEngine
from agents.infiltrator import SocialInfiltrator
from agents.warden import AnalyticsWarden
from agents.sentinel import SecuritySentinel

# Import core components
from core.crypto import MilitaryCrypto
from core.utils import logger

# Setup test crypto system
@pytest.fixture
def crypto():
    return MilitaryCrypto()

# Test data
SAMPLE_CAMPAIGN = {
    "id": "campaign_123",
    "product": "AI Marketing Tool",
    "target_demo": "Digital Marketers",
    "platforms": ["instagram", "tiktok"]
}

# ----- Project Commander Tests -----
class TestProjectCommander:
    def test_init(self, crypto):
        commander = ProjectCommander(crypto)
        assert commander.name == "Commander"
        assert commander.role == "Team Lead"
        assert isinstance(commander.campaigns, dict)

    def test_launch_campaign(self, crypto):
        commander = ProjectCommander(crypto)
        campaign_id = commander.launch_campaign(SAMPLE_CAMPAIGN)
        
        assert isinstance(campaign_id, str)
        assert len(campaign_id) > 0
        assert campaign_id in commander.campaigns

    @patch('agents.commander.schedule.every')
    def test_ooda_cycle_scheduling(self, mock_schedule, crypto):
        commander = ProjectCommander(crypto)
        commander.launch_campaign(SAMPLE_CAMPAIGN)
        
        assert mock_schedule.called
        assert mock_schedule().minutes.do.called

# ----- Psych Profiler Tests -----
class TestPsychProfiler:
    def test_init(self, crypto):
        profiler = PsychProfiler(crypto)
        assert profiler.name == "DeepPsych Profiler"
        assert isinstance(profiler.audience_db, pd.DataFrame)
        assert isinstance(profiler.trend_data, dict)

    def test_analyze_audience(self, crypto):
        profiler = PsychProfiler(crypto)
        analysis = profiler._create_psych_profile("Gen Z Gamers")
        
        assert isinstance(analysis, dict)
        assert 'novelty' in analysis
        assert 0 <= analysis['novelty'] <= 1

    def test_content_preferences(self, crypto):
        profiler = PsychProfiler(crypto)
        prefs = profiler._get_content_preferences(SAMPLE_CAMPAIGN)
        
        assert isinstance(prefs, dict)
        for platform in SAMPLE_CAMPAIGN['platforms']:
            assert platform in prefs
            assert isinstance(prefs[platform], list)

    @patch('agents.profiler.PsychProfiler._send_results')
    def test_process_task(self, mock_send, crypto):
        profiler = PsychProfiler(crypto)
        task = {
            'type': 'analyze_audience',
            'campaign': SAMPLE_CAMPAIGN
        }
        profiler.receive_message(task)
        
        time.sleep(0.1)  # Allow thread to process
        assert mock_send.called

# ----- Content Engine Tests -----
class TestContentEngine:
    @patch('openai.ChatCompletion.create')
    def test_generate_content_plan(self, mock_openai, crypto):
        mock_openai.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Sample content plan"))]
        )
        
        engine = ContentEngine(crypto)
        plan = engine._generate_content_plan(SAMPLE_CAMPAIGN)
        
        assert isinstance(plan, str)
        assert "Sample content plan" in plan
        mock_openai.assert_called_once()

    def test_generate_image(self, crypto):
        engine = ContentEngine(crypto)
        specs = {
            'product': SAMPLE_CAMPAIGN['product'],
            'target_demo': SAMPLE_CAMPAIGN['target_demo'],
            'aspect_ratio': '1:1'
        }
        result = engine._generate_image(specs)
        
        assert isinstance(result, dict)
        assert 'asset_id' in result
        assert 'content' in result

    @patch('pyttsx3.init')
    def test_generate_audio(self, mock_tts, crypto):
        mock_engine = MagicMock()
        mock_tts.return_value = mock_engine
        
        engine = ContentEngine(crypto)
        specs = {
            'script': 'Test audio script',
            'campaign_id': SAMPLE_CAMPAIGN['id']
        }
        result = engine._generate_audio(specs)
        
        assert isinstance(result, dict)
        assert 'asset_id' in result
        mock_engine.save_to_file.assert_called_once()

# ----- Social Infiltrator Tests -----
class TestSocialInfiltrator:
    def test_init(self, crypto):
        infiltrator = SocialInfiltrator(crypto)
        assert infiltrator.name == "Stealth Social Infiltrator"
        assert isinstance(infiltrator.platforms, dict)
        assert isinstance(infiltrator.accounts, dict)

    def test_platform_strategy(self, crypto):
        infiltrator = SocialInfiltrator(crypto)
        strategy = infiltrator._platform_strategy('instagram', SAMPLE_CAMPAIGN)
        
        assert isinstance(strategy, dict)
        assert 'approach' in strategy
        assert 'content_mix' in strategy

    @patch('agents.infiltrator.schedule.every')
    def test_execute_campaign(self, mock_schedule, crypto):
        infiltrator = SocialInfiltrator(crypto)
        content_package = {
            'campaign_id': SAMPLE_CAMPAIGN['id'],
            'assets': [{
                'platform': 'instagram',
                'type': 'image',
                'content': 'test_content'
            }]
        }
        infiltrator._execute_campaign({'content': content_package})
        
        assert mock_schedule.called

# ----- Analytics Warden Tests -----
class TestAnalyticsWarden:
    def test_record_metrics(self, crypto):
        warden = AnalyticsWarden(crypto)
        metrics = {
            'platform': 'instagram',
            'engagement_rate': 0.08,
            'likes': 250,
            'shares': 35,
            'asset_type': 'video'
        }
        warden._record_metrics({
            'campaign_id': SAMPLE_CAMPAIGN['id'],
            'metrics': metrics
        })
        
        assert SAMPLE_CAMPAIGN['id'] in warden.campaign_data
        assert len(warden.campaign_data[SAMPLE_CAMPAIGN['id']]) == 1

    def test_calculate_trend(self, crypto):
        warden = AnalyticsWarden(crypto)
        data = pd.DataFrame({
            'engagement_rate': [0.05, 0.06, 0.07, 0.08]
        })
        trend = warden._calculate_trend(data, 'engagement_rate')
        
        assert isinstance(trend, dict)
        assert 'slope' in trend
        assert trend['slope'] > 0  # Positive trend

    @patch('matplotlib.pyplot.savefig')
    def test_generate_report(self, mock_save, crypto):
        warden = AnalyticsWarden(crypto)
        data = pd.DataFrame({
            'platform': ['instagram', 'tiktok', 'instagram', 'tiktok'],
            'engagement_rate': [0.05, 0.08, 0.06, 0.09],
            'asset_type': ['image', 'video', 'video', 'image']
        })
        warden.campaign_data[SAMPLE_CAMPAIGN['id']] = data
        
        report = warden._generate_report({
            'campaign_id': SAMPLE_CAMPAIGN['id']
        })
        
        assert mock_save.called
        assert isinstance(report, dict)

# ----- Security Sentinel Tests -----
class TestSecuritySentinel:
    def test_init(self, crypto):
        sentinel = SecuritySentinel(crypto)
        assert sentinel.name == "Black Ops Security Sentinel"
        assert sentinel.threat_level == 0
        assert isinstance(sentinel.whitelist, dict)

    def test_threat_level_update(self, crypto):
        sentinel = SecuritySentinel(crypto)
        sentinel._update_threat_level(5)
        assert sentinel.threat_level == 5
        sentinel._update_threat_level(-2)
        assert sentinel.threat_level == 3  # Doesn't go below 0

    @patch('subprocess.run')
    def test_isolate_network(self, mock_subprocess, crypto):
        sentinel = SecuritySentinel(crypto)
        sentinel._isolate_network()
        assert mock_subprocess.called

    def test_handle_suspicious_activity(self, crypto):
        sentinel = SecuritySentinel(crypto)
        with patch.object(sentinel, '_send_results') as mock_send:
            sentinel._handle_suspicious_activity(
                'network',
                'Test suspicious activity',
                5
            )
            assert mock_send.called
            assert sentinel.threat_level == 5

# ----- Integration Tests -----
class TestAgentIntegration:
    @patch('agents.commander.ProjectCommander._send_results')
    def test_commander_to_profiler_flow(self, mock_send, crypto):
        commander = ProjectCommander(crypto)
        profiler = PsychProfiler(crypto)
        
        # Simulate message passing
        commander.send_message = profiler.receive_message
        campaign_id = commander.launch_campaign(SAMPLE_CAMPAIGN)
        
        time.sleep(0.2)  # Allow processing
        assert mock_send.called

    @patch('agents.content_engine.ContentEngine._send_results')
    def test_profiler_to_content_engine_flow(self, mock_send, crypto):
        profiler = PsychProfiler(crypto)
        content_engine = ContentEngine(crypto)
        
        profiler.send_message = content_engine.receive_message
        profiler._analyze_audience({
            'campaign': SAMPLE_CAMPAIGN,
            'platforms': SAMPLE_CAMPAIGN['platforms']
        })
        
        time.sleep(0.2)
        assert mock_send.called

if __name__ == "__main__":
    pytest.main(["-v", "tests/test_agents.py"])
