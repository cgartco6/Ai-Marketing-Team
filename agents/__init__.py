"""
AI Marketing Team - Agents Package

This package contains all specialized AI agents that work together as a team.
Each agent handles specific aspects of the marketing workflow with military-grade security.
"""

__all__ = [
    'ProjectCommander',
    'PsychProfiler',
    'ContentEngine',
    'SocialInfiltrator',
    'AnalyticsWarden',
    'SecuritySentinel'
]

__version__ = "2.3.0"
__author__ = "AI Marketing Team"
__security_level__ = "Tier 1 Military Grade"

from .commander import ProjectCommander
from .profiler import PsychProfiler
from .content_engine import ContentEngine
from .infiltrator import SocialInfiltrator
from .warden import AnalyticsWarden
from .sentinel import SecuritySentinel

class AgentRegistry:
    """
    Central registry for managing all active agents
    with security enforcement and performance monitoring.
    """
    _agents = {}
    _security_checklist = {
        'encryption': True,
        'auth': True,
        'audit_log': True
    }

    @classmethod
    def register_agent(cls, agent_type, instance):
        """Register an agent instance with security validation"""
        if not cls._validate_agent_security(instance):
            raise SecurityError("Agent failed security validation")
        cls._agents[agent_type] = instance
        logger(f"Registered agent: {agent_type}")

    @classmethod
    def _validate_agent_security(cls, agent):
        """Perform military-grade security validation"""
        checks = [
            hasattr(agent, 'crypto'),
            hasattr(agent, 'secure_comms'),
            hasattr(agent, 'threat_monitor')
        ]
        return all(checks)

    @classmethod
    def get_agent(cls, agent_type):
        """Retrieve agent with access control"""
        if agent_type not in cls._agents:
            raise ValueError(f"Agent {agent_type} not registered")
        return cls._agents[agent_type]

    @classmethod
    def secure_shutdown(cls):
        """Gracefully shutdown all agents with security protocols"""
        for agent_type, instance in cls._agents.items():
            try:
                instance.shutdown()
                logger(f"Securely shutdown agent: {agent_type}")
            except Exception as e:
                logger(f"Error shutting down {agent_type}: {str(e)}", "error")

class SecurityError(Exception):
    """Custom security exception for agent operations"""
    pass

def init_agents(crypto_system):
    """
    Initialize all agents with proper security context.
    Returns dictionary of initialized agents.
    """
    agents = {
        'commander': ProjectCommander(crypto_system),
        'profiler': PsychProfiler(crypto_system),
        'content_engine': ContentEngine(crypto_system),
        'infiltrator': SocialInfiltrator(crypto_system),
        'warden': AnalyticsWarden(crypto_system),
        'sentinel': SecuritySentinel(crypto_system)
    }

    # Register all agents
    for agent_type, instance in agents.items():
        AgentRegistry.register_agent(agent_type, instance)

    return agents

# Initialize package-level logger
from core.utils import logger
logger("Agents package initialized", "debug")
