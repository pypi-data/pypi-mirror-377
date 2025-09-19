"""
Statistics and Monitoring System for DuoTalk.
Tracks conversation metrics, performance data, and provides analytics.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import threading
import sqlite3


@dataclass
class ConversationStats:
    """Statistics for a single conversation."""
    
    # Basic info
    session_id: str
    topic: str
    mode: str
    agent_names: List[str]
    
    # Timing
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: float = 0.0
    
    # Turn statistics
    total_turns: int = 0
    max_turns_configured: int = 0
    turns_per_agent: Dict[str, int] = None
    
    # Response times
    avg_response_time: float = 0.0
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    response_times: List[float] = None
    
    # Content metrics
    total_words: int = 0
    words_per_turn: Dict[str, List[int]] = None
    avg_words_per_turn: float = 0.0
    
    # Voice metrics (if enabled)
    voice_enabled: bool = False
    voice_generation_time: float = 0.0
    voice_synthesis_errors: int = 0
    
    # Completion status
    completed_successfully: bool = False
    interruption_reason: Optional[str] = None
    error_count: int = 0
    
    # Quality metrics
    agent_interaction_score: float = 0.0  # How well agents interacted
    topic_adherence_score: float = 0.0    # How well they stayed on topic
    
    def __post_init__(self):
        """Initialize collections if None."""
        if self.turns_per_agent is None:
            self.turns_per_agent = defaultdict(int)
        if self.response_times is None:
            self.response_times = []
        if self.words_per_turn is None:
            self.words_per_turn = defaultdict(list)


class PerformanceMonitor:
    """Real-time performance monitoring during conversations."""
    
    def __init__(self):
        self.current_stats: Optional[ConversationStats] = None
        self.turn_start_time: Optional[float] = None
        self.conversation_start_time: Optional[float] = None
        self.callbacks: Dict[str, List[callable]] = defaultdict(list)
        
    def start_conversation(self, session_id: str, topic: str, mode: str, agents: List[str], max_turns: int, voice_enabled: bool = False):
        """Start monitoring a new conversation."""
        self.current_stats = ConversationStats(
            session_id=session_id,
            topic=topic,
            mode=mode,
            agent_names=agents,
            start_time=datetime.now(),
            max_turns_configured=max_turns,
            voice_enabled=voice_enabled,
            turns_per_agent=defaultdict(int),
            response_times=[],
            words_per_turn=defaultdict(list)
        )
        self.conversation_start_time = time.time()
        self._trigger_callbacks('conversation_started', self.current_stats)
    
    def start_turn(self, agent_name: str):
        """Mark the start of a conversation turn."""
        self.turn_start_time = time.time()
        self._trigger_callbacks('turn_started', {'agent': agent_name})
    
    def end_turn(self, agent_name: str, response_text: str, voice_generation_time: float = 0.0):
        """Mark the end of a conversation turn and record metrics."""
        if not self.current_stats or self.turn_start_time is None:
            return
            
        # Calculate response time
        response_time = time.time() - self.turn_start_time
        self.current_stats.response_times.append(response_time)
        
        # Update turn counts
        self.current_stats.turns_per_agent[agent_name] += 1
        self.current_stats.total_turns += 1
        
        # Count words
        word_count = len(response_text.split())
        self.current_stats.words_per_turn[agent_name].append(word_count)
        self.current_stats.total_words += word_count
        
        # Voice metrics
        if self.current_stats.voice_enabled:
            self.current_stats.voice_generation_time += voice_generation_time
        
        # Update averages
        self._update_averages()
        
        self._trigger_callbacks('turn_ended', {
            'agent': agent_name,
            'response_time': response_time,
            'word_count': word_count,
            'turn_number': self.current_stats.total_turns
        })
    
    def record_error(self, error_type: str, error_message: str):
        """Record an error during conversation."""
        if not self.current_stats:
            return
            
        self.current_stats.error_count += 1
        
        if error_type == "voice_synthesis":
            self.current_stats.voice_synthesis_errors += 1
            
        self._trigger_callbacks('error_occurred', {
            'error_type': error_type,
            'error_message': error_message,
            'total_errors': self.current_stats.error_count
        })
    
    def end_conversation(self, completed_successfully: bool = True, interruption_reason: Optional[str] = None):
        """End the conversation monitoring and finalize statistics."""
        if not self.current_stats or self.conversation_start_time is None:
            return None
            
        self.current_stats.end_time = datetime.now()
        self.current_stats.total_duration = time.time() - self.conversation_start_time
        self.current_stats.completed_successfully = completed_successfully
        self.current_stats.interruption_reason = interruption_reason
        
        # Calculate final metrics
        self._calculate_quality_scores()
        self._update_averages()
        
        # Trigger completion callback
        self._trigger_callbacks('conversation_ended', self.current_stats)
        
        # Return stats for saving
        final_stats = self.current_stats
        self.current_stats = None
        return final_stats
    
    def _update_averages(self):
        """Update average calculations."""
        if not self.current_stats:
            return
            
        # Response time averages
        if self.current_stats.response_times:
            self.current_stats.avg_response_time = sum(self.current_stats.response_times) / len(self.current_stats.response_times)
            self.current_stats.min_response_time = min(self.current_stats.response_times)
            self.current_stats.max_response_time = max(self.current_stats.response_times)
        
        # Words per turn average
        all_word_counts = []
        for agent_words in self.current_stats.words_per_turn.values():
            all_word_counts.extend(agent_words)
        
        if all_word_counts:
            self.current_stats.avg_words_per_turn = sum(all_word_counts) / len(all_word_counts)
    
    def _calculate_quality_scores(self):
        """Calculate conversation quality scores."""
        if not self.current_stats:
            return
            
        # Agent interaction score (based on turn distribution)
        if len(self.current_stats.agent_names) > 1:
            turn_counts = list(self.current_stats.turns_per_agent.values())
            if turn_counts:
                # More balanced turn distribution = higher score
                avg_turns = sum(turn_counts) / len(turn_counts)
                variance = sum((x - avg_turns) ** 2 for x in turn_counts) / len(turn_counts)
                # Score from 0-10, higher is more balanced
                self.current_stats.agent_interaction_score = max(0, 10 - (variance / avg_turns * 2)) if avg_turns > 0 else 0
        
        # Topic adherence score (simplified - based on response consistency)
        # This is a placeholder - real implementation would use NLP analysis
        if self.current_stats.response_times:
            # Consistent response times might indicate better engagement
            time_variance = max(self.current_stats.response_times) - min(self.current_stats.response_times)
            # Score from 0-10, more consistent = higher score
            self.current_stats.topic_adherence_score = max(0, 10 - (time_variance / 10))
    
    def add_callback(self, event: str, callback: callable):
        """Add a callback for monitoring events."""
        self.callbacks[event].append(callback)
    
    def remove_callback(self, event: str, callback: callable):
        """Remove a callback for monitoring events."""
        if callback in self.callbacks[event]:
            self.callbacks[event].remove(callback)
    
    def _trigger_callbacks(self, event: str, data: Any):
        """Trigger all callbacks for an event."""
        for callback in self.callbacks[event]:
            try:
                callback(data)
            except Exception as e:
                # Don't let callback errors break monitoring
                print(f"Callback error for event {event}: {e}")
    
    def get_current_stats(self) -> Optional[Dict[str, Any]]:
        """Get current conversation statistics."""
        if not self.current_stats:
            return None
            
        return {
            'session_id': self.current_stats.session_id,
            'topic': self.current_stats.topic,
            'mode': self.current_stats.mode,
            'agents': self.current_stats.agent_names,
            'elapsed_time': time.time() - self.conversation_start_time if self.conversation_start_time else 0,
            'total_turns': self.current_stats.total_turns,
            'max_turns': self.current_stats.max_turns_configured,
            'progress_percent': (self.current_stats.total_turns / self.current_stats.max_turns_configured) * 100 if self.current_stats.max_turns_configured > 0 else 0,
            'avg_response_time': self.current_stats.avg_response_time,
            'total_words': self.current_stats.total_words,
            'error_count': self.current_stats.error_count
        }


class StatisticsStore:
    """Persistent storage for conversation statistics."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize the statistics store."""
        if storage_path is None:
            storage_path = Path.home() / ".duotalk" / "stats"
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize SQLite database
        self.db_path = self.storage_path / "conversations.db"
        self._init_database()
        
        # JSON fallback for complex data
        self.json_path = self.storage_path / "conversation_stats.json"
        
        # Thread lock for safe concurrent access
        self._lock = threading.Lock()
    
    def _init_database(self):
        """Initialize SQLite database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    session_id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    agent_names TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    total_duration REAL,
                    total_turns INTEGER,
                    max_turns_configured INTEGER,
                    avg_response_time REAL,
                    min_response_time REAL,
                    max_response_time REAL,
                    total_words INTEGER,
                    avg_words_per_turn REAL,
                    voice_enabled BOOLEAN,
                    voice_generation_time REAL,
                    voice_synthesis_errors INTEGER,
                    completed_successfully BOOLEAN,
                    interruption_reason TEXT,
                    error_count INTEGER,
                    agent_interaction_score REAL,
                    topic_adherence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS turn_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    turn_number INTEGER NOT NULL,
                    response_time REAL NOT NULL,
                    word_count INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES conversations (session_id)
                )
            """)
            
            conn.commit()
    
    def save_conversation_stats(self, stats: ConversationStats):
        """Save conversation statistics to storage."""
        with self._lock:
            # Save to SQLite
            with sqlite3.connect(self.db_path) as conn:
                # Insert main conversation record
                conn.execute("""
                    INSERT OR REPLACE INTO conversations (
                        session_id, topic, mode, agent_names, start_time, end_time,
                        total_duration, total_turns, max_turns_configured,
                        avg_response_time, min_response_time, max_response_time,
                        total_words, avg_words_per_turn, voice_enabled,
                        voice_generation_time, voice_synthesis_errors,
                        completed_successfully, interruption_reason, error_count,
                        agent_interaction_score, topic_adherence_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    stats.session_id, stats.topic, stats.mode,
                    json.dumps(stats.agent_names),
                    stats.start_time.isoformat(),
                    stats.end_time.isoformat() if stats.end_time else None,
                    stats.total_duration, stats.total_turns, stats.max_turns_configured,
                    stats.avg_response_time, stats.min_response_time, stats.max_response_time,
                    stats.total_words, stats.avg_words_per_turn, stats.voice_enabled,
                    stats.voice_generation_time, stats.voice_synthesis_errors,
                    stats.completed_successfully, stats.interruption_reason, stats.error_count,
                    stats.agent_interaction_score, stats.topic_adherence_score
                ))
                
                # Save detailed turn statistics
                turn_number = 0
                for agent_name in stats.agent_names:
                    agent_turns = stats.turns_per_agent.get(agent_name, 0)
                    agent_response_times = stats.response_times[:agent_turns] if stats.response_times else []
                    agent_word_counts = stats.words_per_turn.get(agent_name, [])
                    
                    for i, (response_time, word_count) in enumerate(zip(agent_response_times, agent_word_counts)):
                        turn_number += 1
                        conn.execute("""
                            INSERT INTO turn_stats (
                                session_id, agent_name, turn_number, response_time, word_count, timestamp
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            stats.session_id, agent_name, turn_number, response_time, word_count,
                            datetime.now().isoformat()
                        ))
                
                conn.commit()
            
            # Also save full data to JSON for backup
            self._save_to_json(stats)
    
    def _save_to_json(self, stats: ConversationStats):
        """Save conversation stats to JSON file."""
        try:
            # Load existing data
            if self.json_path.exists():
                with open(self.json_path, 'r') as f:
                    data = json.load(f)
            else:
                data = {"conversations": []}
            
            # Convert stats to dict
            stats_dict = asdict(stats)
            stats_dict['start_time'] = stats.start_time.isoformat()
            if stats.end_time:
                stats_dict['end_time'] = stats.end_time.isoformat()
            
            # Add to data
            data["conversations"].append(stats_dict)
            
            # Keep only last 1000 conversations to prevent file bloat
            if len(data["conversations"]) > 1000:
                data["conversations"] = data["conversations"][-1000:]
            
            # Save back to file
            with open(self.json_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Error saving to JSON: {e}")
    
    def get_conversation_stats(self, session_id: str) -> Optional[ConversationStats]:
        """Retrieve statistics for a specific conversation."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM conversations WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Convert row to ConversationStats
            stats = ConversationStats(
                session_id=row['session_id'],
                topic=row['topic'],
                mode=row['mode'],
                agent_names=json.loads(row['agent_names']),
                start_time=datetime.fromisoformat(row['start_time']),
                end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                total_duration=row['total_duration'] or 0.0,
                total_turns=row['total_turns'] or 0,
                max_turns_configured=row['max_turns_configured'] or 0,
                avg_response_time=row['avg_response_time'] or 0.0,
                min_response_time=row['min_response_time'] or 0.0,
                max_response_time=row['max_response_time'] or 0.0,
                total_words=row['total_words'] or 0,
                avg_words_per_turn=row['avg_words_per_turn'] or 0.0,
                voice_enabled=bool(row['voice_enabled']),
                voice_generation_time=row['voice_generation_time'] or 0.0,
                voice_synthesis_errors=row['voice_synthesis_errors'] or 0,
                completed_successfully=bool(row['completed_successfully']),
                interruption_reason=row['interruption_reason'],
                error_count=row['error_count'] or 0,
                agent_interaction_score=row['agent_interaction_score'] or 0.0,
                topic_adherence_score=row['topic_adherence_score'] or 0.0
            )
            
            return stats
    
    def get_recent_conversations(self, limit: int = 10) -> List[ConversationStats]:
        """Get recent conversation statistics."""
        conversations = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM conversations 
                ORDER BY start_time DESC 
                LIMIT ?
            """, (limit,))
            
            for row in cursor.fetchall():
                stats = ConversationStats(
                    session_id=row['session_id'],
                    topic=row['topic'],
                    mode=row['mode'],
                    agent_names=json.loads(row['agent_names']),
                    start_time=datetime.fromisoformat(row['start_time']),
                    end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                    total_duration=row['total_duration'] or 0.0,
                    total_turns=row['total_turns'] or 0,
                    max_turns_configured=row['max_turns_configured'] or 0,
                    voice_enabled=bool(row['voice_enabled']),
                    completed_successfully=bool(row['completed_successfully']),
                    error_count=row['error_count'] or 0
                )
                conversations.append(stats)
        
        return conversations
    
    def get_summary_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get summary statistics for the specified time period."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Basic counts
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_conversations,
                    SUM(CASE WHEN completed_successfully = 1 THEN 1 ELSE 0 END) as completed_conversations,
                    AVG(total_duration) as avg_duration,
                    AVG(total_turns) as avg_turns,
                    AVG(agent_interaction_score) as avg_interaction_score,
                    SUM(total_words) as total_words
                FROM conversations 
                WHERE start_time >= ?
            """, (cutoff_date.isoformat(),))
            
            basic_stats = cursor.fetchone()
            
            # Mode distribution
            cursor = conn.execute("""
                SELECT mode, COUNT(*) as count
                FROM conversations 
                WHERE start_time >= ?
                GROUP BY mode
                ORDER BY count DESC
            """, (cutoff_date.isoformat(),))
            
            mode_distribution = {row['mode']: row['count'] for row in cursor.fetchall()}
            
            # Agent usage
            cursor = conn.execute("""
                SELECT agent_names, COUNT(*) as count
                FROM conversations 
                WHERE start_time >= ?
                GROUP BY agent_names
                ORDER BY count DESC
                LIMIT 10
            """, (cutoff_date.isoformat(),))
            
            agent_combinations = []
            for row in cursor.fetchall():
                try:
                    agents = json.loads(row['agent_names'])
                    agent_combinations.append({
                        'agents': agents,
                        'count': row['count']
                    })
                except:
                    continue
            
            return {
                'period_days': days,
                'total_conversations': basic_stats['total_conversations'] or 0,
                'completed_conversations': basic_stats['completed_conversations'] or 0,
                'completion_rate': (basic_stats['completed_conversations'] / basic_stats['total_conversations'] * 100) 
                                 if basic_stats['total_conversations'] > 0 else 0,
                'avg_duration_minutes': (basic_stats['avg_duration'] / 60) if basic_stats['avg_duration'] else 0,
                'avg_turns': basic_stats['avg_turns'] or 0,
                'avg_interaction_score': basic_stats['avg_interaction_score'] or 0,
                'total_words': basic_stats['total_words'] or 0,
                'mode_distribution': mode_distribution,
                'popular_agent_combinations': agent_combinations
            }


# Global instances
_monitor = PerformanceMonitor()
_store = StatisticsStore()


def get_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return _monitor


def get_store() -> StatisticsStore:
    """Get the global statistics store instance."""
    return _store


# Export main components
__all__ = [
    'ConversationStats',
    'PerformanceMonitor', 
    'StatisticsStore',
    'get_monitor',
    'get_store'
]
