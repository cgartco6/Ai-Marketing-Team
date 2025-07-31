import os
import json
import time
import threading
import queue
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from core.crypto import MilitaryCrypto
from core.utils import logger, secure_fetch
import schedule
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from io import BytesIO
import base64

class AnalyticsWarden:
    def __init__(self, crypto_system: MilitaryCrypto):
        self.crypto = crypto_system
        self.name = "Adaptive Analytics Warden"
        self.role = "Performance Optimization System"
        self.task_queue = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        
        # Data storage
        self.campaign_data = {}  # {campaign_id: pd.DataFrame}
        self.optimization_models = {}
        
        # Configuration
        self.analysis_frequency = 30  # minutes
        self.alert_thresholds = {
            'engagement_rate': {'warning': 0.02, 'critical': 0.01},
            'conversion_rate': {'warning': 0.001, 'critical': 0.0005}
        }
        
        # Initialize scheduled tasks
        schedule.every(self.analysis_frequency).minutes.do(self._periodic_analysis)
        
        logger(f"[{self.name}] Initialized with analysis every {self.analysis_frequency} minutes")

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
        
        if task_type == 'performance_report':
            self._record_metrics(task)
        elif task_type == 'optimize_campaign':
            self._optimize_campaign(task)
        elif task_type == 'generate_report':
            self._generate_report(task)
        elif task_type == 'predict_performance':
            self._predict_performance(task)
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

    def _record_metrics(self, task):
        """Store performance metrics for analysis"""
        campaign_id = task['campaign_id']
        metrics = task['metrics']
        
        # Create dataframe if needed
        if campaign_id not in self.campaign_data:
            self.campaign_data[campaign_id] = pd.DataFrame()
        
        # Add timestamp
        metrics['timestamp'] = datetime.now()
        
        # Append new data
        new_row = pd.DataFrame([metrics])
        self.campaign_data[campaign_id] = pd.concat(
            [self.campaign_data[campaign_id], new_row],
            ignore_index=True
        )
        
        logger(f"[{self.name}] Recorded metrics for campaign {campaign_id}")

    def _periodic_analysis(self):
        """Regularly analyze all active campaigns"""
        logger(f"[{self.name}] Running periodic analysis...")
        for campaign_id in list(self.campaign_data.keys()):
            self._analyze_campaign(campaign_id)

    def _analyze_campaign(self, campaign_id):
        """Perform comprehensive campaign analysis"""
        if campaign_id not in self.campaign_data:
            return
            
        data = self.campaign_data[campaign_id]
        if len(data) < 3:  # Need at least 3 data points
            return
            
        logger(f"[{self.name}] Analyzing campaign {campaign_id}")
        
        # Calculate trends
        analysis = {
            'engagement_trend': self._calculate_trend(data, 'engagement_rate'),
            'conversion_trend': self._calculate_trend(data, 'conversion_rate'),
            'platform_performance': self._compare_platforms(data),
            'content_effectiveness': self._compare_content_types(data),
            'alerts': self._check_alerts(data)
        }
        
        # Send to Commander
        self._send_results(
            recipient='Commander',
            message_type='campaign_analysis',
            content={
                'campaign_id': campaign_id,
                'analysis': analysis
            }
        )
        
        # Store model for predictions
        self._train_prediction_model(campaign_id, data)

    def _optimize_campaign(self, task):
        """Generate optimization recommendations"""
        campaign_id = task['campaign_id']
        if campaign_id not in self.campaign_data:
            return
            
        data = self.campaign_data[campaign_id]
        if len(data) < 2:
            return
            
        logger(f"[{self.name}] Generating optimizations for {campaign_id}")
        
        # Generate recommendations
        recs = {
            'platform_focus': self._recommend_platforms(data),
            'content_adjustments': self._recommend_content_types(data),
            'timing_suggestions': self._recommend_timing(data),
            'resource_allocation': self._recommend_resource_allocation(data)
        }
        
        # Send to appropriate agents
        self._send_results(
            recipient='Commander',
            message_type='optimization_recommendations',
            content={
                'campaign_id': campaign_id,
                'recommendations': recs
            }
        )

    def _generate_report(self, task):
        """Create visual performance report"""
        campaign_id = task['campaign_id']
        if campaign_id not in self.campaign_data:
            return
            
        data = self.campaign_data[campaign_id]
        logger(f"[{self.name}] Generating report for {campaign_id}")
        
        # Create visualizations
        report = {
            'engagement_trend': self._plot_trend(data, 'engagement_rate'),
            'platform_comparison': self._plot_platform_comparison(data),
            'content_breakdown': self._plot_content_breakdown(data)
        }
        
        # Send to Commander
        self._send_results(
            recipient='Commander',
            message_type='visual_report',
            content={
                'campaign_id': campaign_id,
                'report': report
            }
        )

    def _predict_performance(self, task):
        """Predict future campaign performance"""
        campaign_id = task['campaign_id']
        if campaign_id not in self.optimization_models:
            return
            
        model = self.optimization_models[campaign_id]
        future_periods = task.get('periods', 7)  # Default 7 periods ahead
        
        try:
            # Prepare prediction data
            X_future = np.array(range(len(model['X']), 
                               len(model['X']) + future_periods)).reshape(-1, 1)
            
            # Transform for polynomial features if needed
            if model['poly']:
                poly = PolynomialFeatures(degree=model['degree'])
                X_future_poly = poly.fit_transform(X_future)
                predictions = model['model'].predict(X_future_poly)
            else:
                predictions = model['model'].predict(X_future)
            
            # Format results
            result = {
                'campaign_id': campaign_id,
                'predictions': predictions.tolist(),
                'timeframe': future_periods * self.analysis_frequency  # in minutes
            }
            
            self._send_results(
                recipient='Commander',
                message_type='performance_predictions',
                content=result
            )
            
        except Exception as e:
            logger(f"[{self.name}] Prediction failed: {str(e)}")

    def _calculate_trend(self, data, metric):
        """Calculate trend line for a metric"""
        x = np.array(range(len(data))).reshape(-1, 1)
        y = data[metric].values
        
        model = LinearRegression()
        model.fit(x, y)
        
        return {
            'slope': float(model.coef_[0]),
            'intercept': float(model.intercept_),
            'current': float(y[-1]),
            'r_squared': model.score(x, y)
        }

    def _compare_platforms(self, data):
        """Compare performance across platforms"""
        if 'platform' not in data.columns:
            return {}
            
        platform_stats = data.groupby('platform').agg({
            'engagement_rate': ['mean', 'std'],
            'conversion_rate': ['mean'],
            'likes': ['sum']
        })
        
        return platform_stats.to_dict()

    def _compare_content_types(self, data):
        """Compare different content types"""
        if 'asset_type' not in data.columns:
            return {}
            
        content_stats = data.groupby('asset_type').agg({
            'engagement_rate': ['mean', 'std'],
            'shares': ['sum'],
            'comments': ['mean']
        })
        
        return content_stats.to_dict()

    def _check_alerts(self, data):
        """Generate alert notifications"""
        alerts = []
        
        # Engagement rate check
        current_engagement = data['engagement_rate'].iloc[-1]
        if current_engagement < self.alert_thresholds['engagement_rate']['critical']:
            alerts.append({
                'type': 'CRITICAL',
                'metric': 'engagement_rate',
                'value': current_engagement,
                'threshold': self.alert_thresholds['engagement_rate']['critical']
            })
        elif current_engagement < self.alert_thresholds['engagement_rate']['warning']:
            alerts.append({
                'type': 'WARNING',
                'metric': 'engagement_rate',
                'value': current_engagement,
                'threshold': self.alert_thresholds['engagement_rate']['warning']
            })
        
        # Add other alert checks here...
        
        return alerts

    def _train_prediction_model(self, campaign_id, data):
        """Train model for future performance prediction"""
        try:
            # Prepare data
            X = np.array(range(len(data))).reshape(-1, 1)
            y = data['engagement_rate'].values
            
            # Test if polynomial features would help
            r2_linear = LinearRegression().fit(X, y).score(X, y)
            
            best_model = None
            best_score = r2_linear
            best_degree = 1
            
            # Test polynomial degrees up to 3
            for degree in [2, 3]:
                poly = PolynomialFeatures(degree=degree)
                X_poly = poly.fit_transform(X)
                model = LinearRegression()
                score = model.fit(X_poly, y).score(X_poly, y)
                
                if score > best_score + 0.05:  # Significant improvement
                    best_model = model
                    best_score = score
                    best_degree = degree
            
            # Store model
            self.optimization_models[campaign_id] = {
                'model': best_model if best_model else LinearRegression().fit(X, y),
                'X': X,
                'poly': best_model is not None,
                'degree': best_degree if best_model else 1,
                'last_trained': datetime.now()
            }
            
        except Exception as e:
            logger(f"[{self.name}] Model training failed: {str(e)}")

    def _recommend_platforms(self, data):
        """Recommend which platforms to focus on"""
        if 'platform' not in data.columns:
            return []
            
        platform_perf = data.groupby('platform')['engagement_rate'].mean()
        best_platform = platform_perf.idxmax()
        worst_platform = platform_perf.idxmin()
        
        return {
            'increase_focus_on': best_platform,
            'decrease_focus_on': worst_platform,
            'performance_difference': platform_perf[best_platform] - platform_perf[worst_platform]
        }

    def _recommend_content_types(self, data):
        """Recommend content type adjustments"""
        if 'asset_type' not in data.columns:
            return []
            
        content_perf = data.groupby('asset_type').agg({
            'engagement_rate': 'mean',
            'shares': 'sum'
        })
        
        best_type = content_perf['engagement_rate'].idxmax()
        most_shared = content_perf['shares'].idxmax()
        
        return {
            'produce_more': best_type,
            'encourage_sharing_of': most_shared,
            'performance_stats': content_perf.to_dict()
        }

    def _recommend_timing(self, data):
        """Recommend optimal posting times"""
        if 'post_time' not in data.columns:
            return []
            
        # Extract hour from timestamp
        data['hour'] = pd.to_datetime(data['post_time']).dt.hour
        
        # Find best performing hours
        hourly_perf = data.groupby('hour')['engagement_rate'].mean()
        best_hours = hourly_perf.nlargest(3).index.tolist()
        
        return {
            'best_hours': [f"{h}:00" for h in best_hours],
            'hourly_performance': hourly_perf.to_dict()
        }

    def _recommend_resource_allocation(self, data):
        """Recommend budget/time allocation"""
        if 'platform' not in data.columns:
            return []
            
        platform_value = data.groupby('platform').agg({
            'engagement_rate': 'mean',
            'conversion_rate': 'mean'
        })
        
        # Simple weighting - could be more sophisticated
        platform_value['score'] = (platform_value['engagement_rate'] * 0.6 + 
                                 platform_value['conversion_rate'] * 0.4)
        
        total_score = platform_value['score'].sum()
        recommendations = {}
        
        for platform in platform_value.index:
            recommendations[platform] = {
                'recommended_allocation': platform_value.loc[platform, 'score'] / total_score,
                'current_allocation': len(data[data['platform'] == platform]) / len(data)
            }
        
        return recommendations

    def _plot_trend(self, data, metric):
        """Generate trend visualization"""
        plt.figure(figsize=(10, 5))
        data[metric].plot(title=f'{metric} Trend')
        plt.xlabel('Time Period')
        plt.ylabel(metric.replace('_', ' ').title())
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def _plot_platform_comparison(self, data):
        """Generate platform comparison visualization"""
        if 'platform' not in data.columns:
            return None
            
        plt.figure(figsize=(10, 5))
        data.groupby('platform')['engagement_rate'].mean().plot(
            kind='bar', 
            title='Platform Engagement Comparison'
        )
        plt.ylabel('Engagement Rate')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def _plot_content_breakdown(self, data):
        """Generate content type visualization"""
        if 'asset_type' not in data.columns:
            return None
            
        plt.figure(figsize=(10, 5))
        data.groupby('asset_type')['shares'].sum().plot(
            kind='pie', 
            autopct='%1.1f%%',
            title='Content Type Performance'
        )
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

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
        """Gracefully shutdown the warden"""
        self.running = False
        logger(f"[{self.name}] Shutting down...")
        
        # Save all campaign data
        os.makedirs('data/analytics', exist_ok=True)
        for campaign_id, data in self.campaign_data.items():
            if not data.empty:
                filename = f"data/analytics/{campaign_id}_{datetime.now().strftime('%Y%m%d')}.csv"
                data.to_csv(filename, index=False)
        
        self.thread.join(timeout=5)
        logger(f"[{self.name}] Shutdown complete")

# Standalone test
if __name__ == "__main__":
    from core.crypto import MilitaryCrypto
    
    print("Testing Analytics Warden...")
    crypto = MilitaryCrypto()
    warden = AnalyticsWarden(crypto)
    
    # Generate test data
    test_data = {
        'timestamp': pd.date_range(end=datetime.now(), periods=10),
        'platform': ['instagram']*5 + ['tiktok']*5,
        'asset_type': ['image']*3 + ['video']*4 + ['carousel']*3,
        'engagement_rate': [0.05, 0.06, 0.04, 0.08, 0.07, 0.12, 0.11, 0.09, 0.10, 0.13],
        'conversion_rate': [0.001]*5 + [0.002]*5,
        'likes': [100, 120, 80, 150, 130, 500, 450, 400, 420, 550],
        'shares': [10, 12, 8, 15, 13, 50, 45, 40, 42, 55],
        'comments': [5, 6, 4, 8, 7, 25, 22, 20, 21, 28]
    }
    
    # Create test campaign
    warden.receive_message({
        'type': 'performance_report',
        'campaign_id': 'test_campaign',
        'metrics': test_data
    })
    
    # Request analysis
    warden.receive_message({
        'type': 'optimize_campaign',
        'campaign_id': 'test_campaign'
    })
    
    # Request report
    warden.receive_message({
        'type': 'generate_report',
        'campaign_id': 'test_campaign'
    })
    
    # Allow time for processing
    time.sleep(5)
    
    # Shutdown
    warden.shutdown()
    print("Analytics Warden test completed.")
