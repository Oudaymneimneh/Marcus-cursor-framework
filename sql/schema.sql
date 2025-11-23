-- Marcus AI Database Schema
-- Version: 1.0.0
-- Description: Core schema for users, sessions, messages, and behavioral tracking.

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(255) UNIQUE,
    display_name VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX IF NOT EXISTS idx_users_external_id ON users(external_id);

-- 2. Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    total_turns INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started_at ON sessions(started_at);

-- 3. Messages Table
CREATE TABLE IF NOT EXISTS messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- 4. PAD Emotional States
CREATE TABLE IF NOT EXISTS pad_states (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(message_id) ON DELETE CASCADE,
    pleasure FLOAT NOT NULL,
    arousal FLOAT NOT NULL,
    dominance FLOAT NOT NULL,
    quadrant VARCHAR(50) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pad_session_recorded ON pad_states(session_id, recorded_at);

-- 5. Behavioral States
CREATE TABLE IF NOT EXISTS behavioral_states (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(message_id) ON DELETE CASCADE,
    relationship_stage VARCHAR(50) NOT NULL,
    communication_style VARCHAR(50) NOT NULL,
    crisis_level INTEGER DEFAULT 0,
    flow_data JSONB DEFAULT '{}'::JSONB,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_behavior_session_recorded ON behavioral_states(session_id, recorded_at);

-- 6. Behavioral Patterns
CREATE TABLE IF NOT EXISTS patterns (
    pattern_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    pattern_name VARCHAR(255) NOT NULL,
    confidence FLOAT DEFAULT 0.0,
    first_noticed TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_confirmed TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    evidence JSONB DEFAULT '[]'::JSONB,
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX IF NOT EXISTS idx_patterns_user_id ON patterns(user_id);

-- 7. Strategies
CREATE TABLE IF NOT EXISTS strategies (
    strategy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    strategy_name VARCHAR(255) NOT NULL,
    effectiveness FLOAT DEFAULT 0.0,
    times_used INTEGER DEFAULT 0,
    context TEXT,
    last_used TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX IF NOT EXISTS idx_strategies_user_id ON strategies(user_id);

-- 8. Events (System Events, Alerts)
CREATE TABLE IF NOT EXISTS events (
    event_id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_session_created ON events(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_events_type_created ON events(event_type, created_at);




