-- Initialize database with extensions and basic setup
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create enum types
CREATE TYPE user_role AS ENUM ('admin', 'user');
CREATE TYPE booking_status AS ENUM ('active', 'cancelled');

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role user_role DEFAULT 'user' NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Slots table
CREATE TABLE slots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    is_available BOOLEAN DEFAULT true NOT NULL,
    max_participants INTEGER DEFAULT 1 NOT NULL,
    current_participants INTEGER DEFAULT 0 NOT NULL,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_time_range CHECK (end_time > start_time),
    CONSTRAINT valid_participants CHECK (current_participants <= max_participants)
);

-- Bookings table
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slot_id UUID NOT NULL REFERENCES slots(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status booking_status DEFAULT 'active' NOT NULL,
    notes TEXT,
    booked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cancelled_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(slot_id, user_id) -- Prevent duplicate bookings
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_slots_start_time ON slots(start_time);
CREATE INDEX idx_slots_is_available ON slots(is_available);
CREATE INDEX idx_slots_created_by ON slots(created_by);
CREATE INDEX idx_bookings_slot_id ON bookings(slot_id);
CREATE INDEX idx_bookings_user_id ON bookings(user_id);
CREATE INDEX idx_bookings_status ON bookings(status);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_slots_updated_at BEFORE UPDATE ON slots
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update slot participant count
CREATE OR REPLACE FUNCTION update_slot_participants()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Increase participant count
        UPDATE slots 
        SET current_participants = current_participants + 1
        WHERE id = NEW.slot_id;
        
        -- Mark slot as unavailable if at capacity
        UPDATE slots 
        SET is_available = false
        WHERE id = NEW.slot_id AND current_participants >= max_participants;
        
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        -- Decrease participant count
        UPDATE slots 
        SET current_participants = current_participants - 1
        WHERE id = OLD.slot_id;
        
        -- Mark slot as available if under capacity
        UPDATE slots 
        SET is_available = true
        WHERE id = OLD.slot_id AND current_participants < max_participants;
        
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Add trigger for booking changes
CREATE TRIGGER update_slot_participants_trigger
    AFTER INSERT OR DELETE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_slot_participants();

-- Insert default admin user
INSERT INTO users (email, password_hash, first_name, last_name, role) VALUES 
('admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBpwkXhMvjNJdG', 'Admin', 'User', 'admin');
-- Password: admin123

-- Insert sample data for testing
INSERT INTO users (email, password_hash, first_name, last_name, role) VALUES 
('user1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBpwkXhMvjNJdG', 'John', 'Doe', 'user'),
('user2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBpwkXhMvjNJdG', 'Jane', 'Smith', 'user');

-- Insert sample slots
INSERT INTO slots (title, description, start_time, end_time, created_by) 
SELECT 
    'Sample Service Slot',
    'This is a sample service slot for testing',
    NOW() + INTERVAL '1 day',
    NOW() + INTERVAL '1 day' + INTERVAL '1 hour',
    id
FROM users WHERE role = 'admin' LIMIT 1;
