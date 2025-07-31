import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from core.crypto import MilitaryCrypto
from core.utils import logger, secure_fetch
import threading
import queue
import schedule
import time

class PsychProfiler:
    def __init__(self, crypto_system: MilitaryCrypto):
        self.crypto = crypto_system
        self.name = "DeepPsych Profiler"
        self.role = "Audience Intelligence Specialist"
        self.task_queue = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        
        # Audience database simulation
        self.audience_db = self._init_audience_db()
        self.trend_data = self._init_trend_data()
        
        logger(f"[{self.name}] Agent initialized. Ready for psychographic analysis")

    def run(self):
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                self._process_task(task)
            except queue.Empty:
                schedule.run_pending()
                time.sleep(0.1)
                
    def _process_task(self, task):
        if 'encrypted' in task:
            task = self._decrypt_task(task)
            
        if task.get('type') == 'analyze_audience':
            self._analyze_audience(task)
        elif task.get('type') == 'update_trends':
            self._update_trend_data()
        elif task.get('type') == 'generate_persona':
            self._generate_archetype(task)
        else:
            logger(f"[{self.name}] Received unknown task: {task.get('type')}")

    def _decrypt_task(self, encrypted_task):
        try:
            decrypted = self.crypto.decrypt(encrypted_task['payload'])
            return json.loads(decrypted)
        except Exception as e:
            logger(f"[{self.name}] Decryption failed: {str(e)}")
            return {'error': 'decryption_failed'}

    def _analyze_audience(self, task):
        campaign = task['campaign']
        logger(f"[{self.name}] Analyzing audience for {campaign['product']} targeting {campaign['target_demo']}")
        
        # Perform analysis
        analysis = {
            'psychographic_profile': self._create_psych_profile(campaign['target_demo']),
            'content_preferences': self._get_content_preferences(campaign),
            'optimal_post_times': self._calculate_optimal_times(campaign['platforms']),
            'sentiment_analysis': self._predict_sentiment(campaign),
            'personas': self._generate_personas(campaign),
            'campaign_id': campaign['id']
        }
        
        # Send results to Content Engine
        self._send_results('Content', 'content_engine', analysis)
        logger(f"[{self.name}] Analysis complete for campaign {campaign['id']}")

    def _create_psych_profile(self, target_demo):
        """Generate psychological profile using simulated data"""
        profiles = {
            'Gen Z': {'novelty': 0.85, 'authenticity': 0.92, 'fomo': 0.78, 'humor': 0.88},
            'Millennials': {'value': 0.75, 'convenience': 0.82, 'social_proof': 0.68, 'nostalgia': 0.72},
            'Gen X': {'practicality': 0.88, 'trust': 0.85, 'quality': 0.9, 'efficiency': 0.82},
            'Boomers': {'reliability': 0.92, 'tradition': 0.78, 'security': 0.95, 'simplicity': 0.88},
            'Gamers': {'competition': 0.9, 'achievement': 0.87, 'community': 0.82, 'immersion': 0.85},
            'Professionals': {'efficiency': 0.91, 'prestige': 0.78, 'networking': 0.75, 'growth': 0.82}
        }
        
        # Find closest match
        best_match = max(profiles.keys(), 
                         key=lambda k: sum(1 for word in target_demo.split() if word.lower() in k.lower()))
        
        return profiles.get(best_match, profiles['Millennials'])

    def _get_content_preferences(self, campaign):
        """Determine preferred content types for each platform"""
        platform_preferences = {
            'tiktok': ['short_video', 'challenges', 'trends', 'duets'],
            'instagram': ['reels', 'stories', 'carousels', 'high_quality_photos'],
            'facebook': ['longform_video', 'groups', 'events', 'articles'],
            'youtube': ['tutorials', 'reviews', 'vlogs', 'documentaries'],
            'twitter': ['quick_tips', 'hot_takes', 'threads', 'polls']
        }
        
        preferences = {}
        for platform in campaign['platforms']:
            if platform in platform_preferences:
                # Add product-specific adjustments
                base_prefs = platform_preferences[platform]
                if 'tech' in campaign['product'].lower():
                    base_prefs = ['tutorials', 'comparisons'] + base_prefs
                elif 'fashion' in campaign['product'].lower():
                    base_prefs = ['showcases', 'style_tips'] + base_prefs
                    
                preferences[platform] = base_prefs[:4]
        
        return preferences

    def _calculate_optimal_times(self, platforms):
        """Calculate best posting times with simulated engagement patterns"""
        time_models = {
            'tiktok': [(9, 12), (16, 19), (21, 23)],
            'instagram': [(8, 10), (12, 14), (18, 21)],
            'facebook': [(7, 9), (12, 14), (19, 22)],
            'youtube': [(12, 15), (18, 21), (21, 23)],
            'twitter': [(7, 9), (12, 13), (16, 18)]
        }
        
        optimal_times = {}
        for platform in platforms:
            if platform in time_models:
                # Convert to time strings
                times = []
                for start, end in time_models[platform]:
                    times.append(f"{start}:00-{end}:00")
                optimal_times[platform] = times
        
        return optimal_times

    def _predict_sentiment(self, campaign):
        """Predict audience sentiment toward product category"""
        sentiment_db = {
            'tech': {'trust': 0.65, 'excitement': 0.78, 'skepticism': 0.42},
            'fashion': {'desire': 0.82, 'inspiration': 0.75, 'comparison': 0.68},
            'fitness': {'motivation': 0.85, 'community': 0.72, 'frustration': 0.38},
            'finance': {'caution': 0.88, 'aspiration': 0.65, 'confusion': 0.55},
            'education': {'curiosity': 0.78, 'frustration': 0.45, 'satisfaction': 0.68}
        }
        
        # Find best matching category
        categories = list(sentiment_db.keys())
        best_match = max(categories, key=lambda cat: sum(1 for word in campaign['product'].split() if word.lower() in cat))
        
        return sentiment_db.get(best_match, sentiment_db['tech'])

    def _generate_personas(self, campaign):
        """Create audience archetypes using clustering simulation"""
        personas = []
        demo = campaign['target_demo']
        
        if 'Gen Z' in demo:
            personas = [
                {'name': 'Trending Tyler', 'age': 19, 'traits': ['early adopter', 'social', 'impulsive']},
                {'name': 'Authentic Amy', 'age': 22, 'traits': ['values-driven', 'skeptical', 'creative']}
            ]
        elif 'Millennials' in demo:
            personas = [
                {'name': 'Professional Paul', 'age': 32, 'traits': ['career-focused', 'time-poor', 'quality-seeker']},
                {'name': 'Parenting Priya', 'age': 35, 'traits': ['practical', 'value-conscious', 'community-oriented']}
            ]
        elif 'Gamers' in demo:
            personas = [
                {'name': 'Competitive Chris', 'age': 25, 'traits': ['skill-focused', 'achievement-driven', 'tech-savvy']},
                {'name': 'Casual Chloe', 'age': 28, 'traits': ['social', 'relaxed', 'story-focused']}
            ]
        else:  # Default persona
            personas = [
                {'name': 'Value-Driven Val', 'age': 42, 'traits': ['practical', 'loyal', 'quality-focused']}
            ]
            
        # Add platform preferences to personas
        for persona in personas:
            persona['platforms'] = self._assign_persona_platforms(persona, campaign['platforms'])
            
        return personas

    def _assign_persona_platforms(self, persona, platforms):
        """Assign platform preferences to personas"""
        platform_weights = {
            'Trending Tyler': {'tiktok': 0.9, 'instagram': 0.8, 'twitter': 0.7},
            'Authentic Amy': {'instagram': 0.9, 'youtube': 0.85, 'pinterest': 0.75},
            'Professional Paul': {'linkedin': 0.95, 'twitter': 0.85, 'youtube': 0.75},
            'Parenting Priya': {'facebook': 0.9, 'instagram': 0.8, 'pinterest': 0.85},
            'Competitive Chris': {'twitch': 0.95, 'youtube': 0.9, 'discord': 0.85},
            'Casual Chloe': {'instagram': 0.9, 'tiktok': 0.85, 'facebook': 0.75},
            'Value-Driven Val': {'facebook': 0.9, 'youtube': 0.8, 'blogs': 0.75}
        }
        
        weights = platform_weights.get(persona['name'], {})
        available = [p for p in platforms if p in weights]
        return sorted(available, key=lambda p: weights.get(p, 0), reverse=True)[:3]

    def _update_trend_data(self):
        """Simulate updating trend database (would be API calls in production)"""
        logger(f"[{self.name}] Updating trend database...")
        new_trends = {
            'tiktok': ['ai_tools', 'minimalist_lifestyle', 'quick_recipes'],
            'instagram': ['pet_fluencers', 'desert_aesthetic', 'vintage_cars'],
            'facebook': ['community_gardening', 'diy_repairs', 'local_events'],
            'youtube': ['retro_gaming', '3d_printing', 'home_labs'],
            'twitter': ['web3_debates', 'startup_advice', 'remote_work_tips']
        }
        
        # Merge with existing trends
        for platform, trends in new_trends.items():
            if platform in self.trend_data:
                self.trend_data[platform] = list(set(self.trend_data[platform] + trends))[-10:]
            else:
                self.trend_data[platform] = trends
                
        logger(f"[{self.name}] Trend database updated with {len(new_trends)} platforms")

    def _init_audience_db(self):
        """Initialize simulated audience database"""
        return pd.DataFrame({
            'age': np.random.randint(18, 65, 1000),
            'gender': np.random.choice(['M', 'F', 'NB'], 1000, p=[0.45, 0.45, 0.1]),
            'income': np.random.normal(50000, 15000, 1000),
            'platform_usage': [np.random.choice(['tiktok', 'instagram', 'facebook', 'youtube'], 
                                              p=[0.4, 0.3, 0.2, 0.1]) for _ in range(1000)]
        })

    def _init_trend_data(self):
        """Initialize trend database with current simulated trends"""
        return {
            'tiktok': ['booktok', 'cleantok', 'gymtok', 'learnontiktok'],
            'instagram': ['reels', 'travelgram', 'foodphotography', 'outfitinspo'],
            'facebook': ['memes', 'community', 'marketplace', 'events'],
            'youtube': ['shorts', 'tutorials', 'vlogs', 'reviews'],
            'twitter': ['threads', 'news', 'opinions', 'brandtakes']
        }

    def _send_results(self, target_agent, agent_type, data):
        """Send results securely to another agent"""
        payload = {
            'type': 'audience_analysis',
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'origin': self.name
        }
        
        # Encrypt payload before sending
        encrypted = self.crypto.encrypt(json.dumps(payload))
        message = {
            'to': target_agent,
            'agent_type': agent_type,
            'payload': encrypted,
            'encrypted': True
        }
        
        # In real implementation, this would go through a message broker
        logger(f"[{self.name}] Sending analysis to {target_agent}")
        # Placeholder for actual message passing
        # message_broker.send(message)

    def receive_message(self, message):
        """Public method to receive messages from command center"""
        self.task_queue.put(message)

    def shutdown(self):
        """Gracefully shutdown the agent"""
        self.running = False
        logger(f"[{self.name}] Shutting down...")
        self.thread.join(timeout=5)
        logger(f"[{self.name}] Shutdown complete")

# Standalone test function
if __name__ == "__main__":
    from core.crypto import MilitaryCrypto
    
    print("Testing PsychProfiler Agent...")
    crypto = MilitaryCrypto()
    profiler = PsychProfiler(crypto)
    
    # Create test campaign
    test_campaign = {
        'id': 'campaign_001',
        'product': 'AI-Powered Fitness Tracker',
        'target_demo': 'Gen Z and Millennial Fitness Enthusiasts',
        'platforms': ['tiktok', 'instagram', 'youtube']
    }
    
    # Create test task
    test_task = {
        'type': 'analyze_audience',
        'campaign': test_campaign
    }
    
    # Process task
    profiler.receive_message(test_task)
    
    # Allow time for processing
    time.sleep(3)
    
    # Schedule trend update
    profiler.receive_message({'type': 'update_trends'})
    time.sleep(1)
    
    # Shutdown
    profiler.shutdown()
    print("Test completed.")
