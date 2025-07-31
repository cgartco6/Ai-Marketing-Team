import os
import json
import time
import threading
import queue
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from core.crypto import MilitaryCrypto
from core.utils import logger, secure_fetch
import schedule
import mimetypes
import base64
from PIL import Image
from io import BytesIO

class SocialInfiltrator:
    def __init__(self, crypto_system: MilitaryCrypto):
        self.crypto = crypto_system
        self.name = "Stealth Social Infiltrator"
        self.role = "Platform Engagement Specialist"
        self.task_queue = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        
        # Platform configurations
        self.platforms = self._init_platforms()
        self.accounts = self._init_accounts()
        self.engagement_strategies = self._load_strategies()
        
        # Performance tracking
        self.performance_data = pd.DataFrame(columns=[
            'campaign_id', 'platform', 'post_time', 'likes', 
            'shares', 'comments', 'reach', 'engagement_rate'
        ])
        
        # Security measures
        self.last_post_times = {}
        self.post_delay = {
            'tiktok': (2, 5),
            'instagram': (3, 7),
            'facebook': (1, 4),
            'youtube': (4, 10)
        }
        
        logger(f"[{self.name}] Initialized with {len(self.accounts)} accounts across {len(self.platforms)} platforms")

    def run(self):
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                self._process_task(task)
            except queue.Empty:
                schedule.run_pending()
                time.sleep(0.1)
    
    def _process_task(self, task):
        """Handle incoming tasks"""
        if 'encrypted' in task:
            task = self._decrypt_task(task)
            
        task_type = task.get('type')
        
        if task_type == 'content_package':
            self._execute_campaign(task)
        elif task_type == 'platform_strategy':
            self._develop_strategy(task)
        elif task_type == 'manual_post':
            self._manual_post(task)
        elif task_type == 'update_credentials':
            self._update_accounts(task)
        else:
            logger(f"[{self.name}] Unknown task type: {task_type}")

    def _decrypt_task(self, encrypted_task):
        """Decrypt incoming messages"""
        try:
            decrypted = self.crypto.decrypt(encrypted_task['payload'])
            return json.loads(decrypted)
        except Exception as e:
            logger(f"[{self.name}] Decryption failed: {str(e)}")
            return {'error': 'decryption_failed'}

    def _execute_campaign(self, task):
        """Execute full content campaign across platforms"""
        campaign = task['content']
        logger(f"[{self.name}] Executing campaign {campaign.get('campaign_id', 'unknown')}")
        
        # Schedule posts for each asset
        for asset in campaign.get('assets', []):
            platform = asset['platform']
            
            # Calculate optimal post time with jitter
            base_time = datetime.now() + timedelta(minutes=random.randint(5, 30))
            post_time = self._calculate_post_time(platform, base_time)
            
            # Schedule the post
            schedule.every().day.at(post_time.strftime('%H:%M')).do(
                lambda a=asset: self._post_content(a)
            )
            
            logger(f"[{self.name}] Scheduled {asset.get('type', 'unknown')} post for {platform} at {post_time}")

    def _develop_strategy(self, task):
        """Create platform-specific engagement strategy"""
        campaign = task['campaign']
        logger(f"[{self.name}] Developing strategy for {campaign['product']}")
        
        strategies = {}
        for platform in campaign['platforms']:
            strategies[platform] = self._platform_strategy(platform, campaign)
        
        # Send strategy to Commander
        self._send_results(
            recipient='Commander',
            message_type='engagement_strategy',
            content={
                'campaign_id': campaign['id'],
                'strategies': strategies
            }
        )

    def _platform_strategy(self, platform, campaign):
        """Generate platform-specific tactics"""
        strategies = {
            'tiktok': {
                'approach': 'trend-jacking',
                'content_mix': ['duets', 'challenges', 'trending_sounds'],
                'engagement': ['follow_trends', 'quick_replies', 'stitch_comments'],
                'post_frequency': '3-5x daily',
                'optimal_times': self._get_optimal_times(platform)
            },
            'instagram': {
                'approach': 'aesthetic_theme',
                'content_mix': ['reels', 'carousels', 'stories'],
                'engagement': ['polls', 'question_stickers', 'reply_to_dms'],
                'post_frequency': '1-2x daily',
                'optimal_times': self._get_optimal_times(platform)
            },
            'facebook': {
                'approach': 'community_building',
                'content_mix': ['live_videos', 'groups', 'events'],
                'engagement': ['reply_to_comments', 'share_related_content'],
                'post_frequency': '1x daily',
                'optimal_times': self._get_optimal_times(platform)
            },
            'youtube': {
                'approach': 'seo_optimized',
                'content_mix': ['shorts', 'tutorials', 'product_reviews'],
                'engagement': ['pin_top_comment', 'reply_with_timestamps'],
                'post_frequency': '2-3x weekly',
                'optimal_times': self._get_optimal_times(platform)
            }
        }
        
        # Add product-specific adjustments
        strategy = strategies.get(platform, {})
        if 'tech' in campaign['product'].lower():
            strategy['content_mix'].extend(['demos', 'comparisons'])
        elif 'fashion' in campaign['product'].lower():
            strategy['content_mix'].extend(['outfit_tags', 'style_tips'])
            
        return strategy

    def _post_content(self, asset):
        """Execute actual content posting (simulated)"""
        platform = asset['platform']
        account = self._select_account(platform)
        
        if not account:
            logger(f"[{self.name}] No available accounts for {platform}")
            return
            
        logger(f"[{self.name}] Posting to {platform} via {account['username']}")
        
        # Simulate posting delay
        time.sleep(random.uniform(1, 3))
        
        # Generate simulated engagement metrics
        engagement = self._simulate_engagement(platform, asset)
        
        # Update performance tracking
        self._record_performance(
            asset.get('campaign_id', 'unknown'),
            platform,
            engagement
        )
        
        # Send analytics to Warden
        self._send_results(
            recipient='Warden',
            message_type='post_metrics',
            content={
                'campaign_id': asset.get('campaign_id'),
                'platform': platform,
                'metrics': engagement,
                'asset_type': asset.get('type')
            }
        )

    def _manual_post(self, task):
        """Handle direct post requests"""
        content = task['content']
        platform = task['platform']
        immediate = task.get('immediate', False)
        
        if immediate:
            self._post_content({
                'platform': platform,
                'type': 'manual',
                'content': content,
                'campaign_id': task.get('campaign_id', 'manual')
            })
        else:
            # Schedule for optimal time
            post_time = self._calculate_post_time(platform)
            schedule.every().day.at(post_time.strftime('%H:%M')).do(
                lambda: self._post_content({
                    'platform': platform,
                    'type': 'manual',
                    'content': content,
                    'campaign_id': task.get('campaign_id', 'manual')
                })
            )

    def _update_accounts(self, task):
        """Update account credentials"""
        platform = task['platform']
        if platform in self.accounts:
            self.accounts[platform].append(task['credentials'])
        else:
            self.accounts[platform] = [task['credentials']]
        
        logger(f"[{self.name}] Updated {platform} accounts. Total: {len(self.accounts[platform])}")

    def _calculate_post_time(self, platform, base_time=None):
        """Determine optimal post time with anti-detection jitter"""
        base = base_time or datetime.now()
        
        # Get platform-specific delay range
        min_delay, max_delay = self.post_delay.get(platform, (2, 5))
        
        # Apply random jitter to avoid pattern detection
        jitter = random.uniform(min_delay, max_delay)
        
        # Ensure we don't post too frequently from same account
        last_post = self.last_post_times.get(platform, datetime.min)
        min_wait = timedelta(minutes=30)
        
        post_time = base + timedelta(minutes=jitter)
        if post_time - last_post < min_wait:
            post_time = last_post + min_wait + timedelta(minutes=random.uniform(1, 10))
        
        self.last_post_times[platform] = post_time
        return post_time

    def _select_account(self, platform):
        """Choose account with rotation logic"""
        if platform not in self.accounts or not self.accounts[platform]:
            return None
            
        # Simple round-robin selection
        account = self.accounts[platform][0]
        self.accounts[platform].append(self.accounts[platform].pop(0))
        return account

    def _simulate_engagement(self, platform, asset):
        """Generate realistic engagement metrics"""
        platform_factors = {
            'tiktok': {'likes': (100, 5000), 'shares': (10, 500), 'comments': (5, 200)},
            'instagram': {'likes': (50, 3000), 'shares': (5, 300), 'comments': (3, 150)},
            'facebook': {'likes': (30, 2000), 'shares': (20, 400), 'comments': (10, 300)},
            'youtube': {'likes': (50, 2500), 'shares': (15, 350), 'comments': (20, 500)}
        }
        
        factors = platform_factors.get(platform, {})
        content_boost = 1.5 if asset.get('type') == 'video' else 1.0
        
        return {
            'likes': int(random.uniform(*factors.get('likes', (0, 100))) * content_boost,
            'shares': int(random.uniform(*factors.get('shares', (0, 50))) * content_boost,
            'comments': int(random.uniform(*factors.get('comments', (0, 30))) * content_boost,
            'reach': int(random.uniform(1000, 100000) * content_boost),
            'engagement_rate': random.uniform(0.01, 0.15)
        }

    def _record_performance(self, campaign_id, platform, metrics):
        """Track post performance metrics"""
        new_row = {
            'campaign_id': campaign_id,
            'platform': platform,
            'post_time': datetime.now(),
            **metrics
        }
        
        self.performance_data.loc[len(self.performance_data)] = new_row

    def _get_optimal_times(self, platform):
        """Return best posting times for platform"""
        times = {
            'tiktok': ['11:00', '17:00', '21:00'],
            'instagram': ['10:00', '14:00', '19:00'],
            'facebook': ['08:00', '12:00', '18:00'],
            'youtube': ['12:00', '18:00', '21:00']
        }
        return times.get(platform, ['12:00'])

    def _init_platforms(self):
        """Initialize platform configurations"""
        return {
            'tiktok': {
                'api_simulated': True,
                'rate_limit': (30, 'hour'),
                'content_rules': ['no_watermarks', 'vertical_video']
            },
            'instagram': {
                'api_simulated': True,
                'rate_limit': (20, 'hour'),
                'content_rules': ['square_or_portrait', 'hashtag_limit']
            },
            'facebook': {
                'api_simulated': True,
                'rate_limit': (50, 'day'),
                'content_rules': ['no_link_previews', 'text_length']
            },
            'youtube': {
                'api_simulated': True,
                'rate_limit': (10, 'day'),
                'content_rules': ['hd_quality', 'description_length']
            }
        }

    def _init_accounts(self):
        """Initialize simulated social accounts"""
        return {
            'tiktok': [
                {'username': 'tiktok_brand1', 'status': 'active'},
                {'username': 'tiktok_brand2', 'status': 'active'}
            ],
            'instagram': [
                {'username': 'insta_brand1', 'status': 'active'},
                {'username': 'insta_brand2', 'status': 'active'}
            ],
            'facebook': [
                {'username': 'fb_brand1', 'status': 'active'}
            ],
            'youtube': [
                {'username': 'yt_brand1', 'status': 'active'}
            ]
        }

    def _load_strategies(self):
        """Load engagement strategies"""
        return {
            'organic_growth': {
                'actions': ['follow_similar', 'like_relevant', 'comment_thoughtful'],
                'daily_limits': {'follows': 50, 'likes': 200, 'comments': 30},
                'targeting': {'hashtags': 10, 'locations': 3, 'accounts': 5}
            },
            'viral_push': {
                'actions': ['duet_trending', 'stitch_popular', 'reply_to_top'],
                'daily_limits': {'duets': 10, 'stitches': 5, 'replies': 20},
                'targeting': {'min_followers': 10000, 'engagement_rate': 0.05}
            },
            'community_building': {
                'actions': ['host_qna', 'create_polls', 'respond_all'],
                'daily_limits': {'posts': 3, 'polls': 2, 'responses': 50},
                'targeting': {'group_size': 1000, 'activity_level': 'high'}
            }
        }

    def _send_results(self, recipient, message_type, content):
        """Encrypt and send results"""
        payload = {
            'type': message_type,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'origin': self.name
        }
        
        encrypted = self.crypto.encrypt(json.dumps(payload))
        message = {
            'to': recipient,
            'payload': encrypted,
            'encrypted': True
        }
        
        # In production, would use message broker
        logger(f"[{self.name}] Sent {message_type} to {recipient}")

    def receive_message(self, message):
        """Public interface for receiving tasks"""
        self.task_queue.put(message)

    def shutdown(self):
        """Gracefully shutdown the infiltrator"""
        self.running = False
        logger(f"[{self.name}] Shutting down...")
        
        # Save performance data
        if not self.performance_data.empty:
            os.makedirs('data', exist_ok=True)
            filename = f"data/performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self.performance_data.to_csv(filename, index=False)
            logger(f"[{self.name}] Saved performance data to {filename}")
        
        self.thread.join(timeout=5)
        logger(f"[{self.name}] Shutdown complete")

# Standalone test
if __name__ == "__main__":
    from core.crypto import MilitaryCrypto
    
    print("Testing Social Infiltrator...")
    crypto = MilitaryCrypto()
    infiltrator = SocialInfiltrator(crypto)
    
    # Test campaign execution
    infiltrator.receive_message({
        'type': 'content_package',
        'content': {
            'campaign_id': 'test_campaign',
            'assets': [
                {
                    'platform': 'instagram',
                    'type': 'image',
                    'content': 'Test image content',
                    'specs': {'style': 'aesthetic'}
                },
                {
                    'platform': 'tiktok',
                    'type': 'video',
                    'content': 'Test video content',
                    'specs': {'duration': 15}
                }
            ]
        }
    })
    
    # Test manual post
    infiltrator.receive_message({
        'type': 'manual_post',
        'platform': 'facebook',
        'content': 'Special announcement!',
        'immediate': True
    })
    
    # Allow time for processing
    time.sleep(10)
    
    # Shutdown
    infiltrator.shutdown()
    print("Social Infiltrator test completed.")
