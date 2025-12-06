-- ============================================
-- SMART BILLBOARD COMPLIANCE SYSTEM
-- Supabase PostgreSQL Schema
-- ============================================

-- ============ 1. VIOLATION REPORTS TABLE ============
-- Core table for storing AI-detected billboard violations
CREATE TABLE violation_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_url TEXT NOT NULL,
    image_filename TEXT NOT NULL,
    extracted_text TEXT,
    is_compliant BOOLEAN DEFAULT true,
    status TEXT DEFAULT 'pending',  -- pending, approved, resolved, flagged_by_citizens, rejected
    violations_found TEXT[],  -- Array of detected violation keywords
    violation_count INTEGER DEFAULT 0,
    violation_context TEXT[],  -- Context around violations
    ocr_confidence NUMERIC DEFAULT 0.0,  -- 0.0-1.0 confidence score
    severity_level TEXT DEFAULT 'none',  -- Critical, High, Medium, Low, None
    severity_score NUMERIC DEFAULT 0,  -- 1-10 scale
    text_regions JSONB,  -- Bounding boxes of detected text
    latitude NUMERIC,  -- Optional geolocation
    longitude NUMERIC,
    zoning_compliance JSONB,  -- Zoning law compliance check results
    detection_timestamp TIMESTAMP DEFAULT now(),
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- Indexes for performance
CREATE INDEX idx_violation_reports_status ON violation_reports(status);
CREATE INDEX idx_violation_reports_created_at ON violation_reports(created_at DESC);
CREATE INDEX idx_violation_reports_severity ON violation_reports(severity_level);
CREATE INDEX idx_violation_reports_location ON violation_reports(latitude, longitude);

-- ============ 2. COMPLIANCE CHECKS TABLE ============
-- Logs of compliance checks against zoning laws
CREATE TABLE compliance_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID REFERENCES violation_reports(id) ON DELETE CASCADE,
    location JSONB NOT NULL,  -- {latitude, longitude, city, state, country}
    check_timestamp TIMESTAMP DEFAULT now(),
    is_compliant BOOLEAN,
    violations JSONB,  -- Zoning violations found
    zone_info JSONB,  -- Zone information and regulations
    notes TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Indexes
CREATE INDEX idx_compliance_checks_report_id ON compliance_checks(report_id);
CREATE INDEX idx_compliance_checks_created_at ON compliance_checks(created_at DESC);

-- ============ 3. CITIZEN REPORTS TABLE ============
-- Community-submitted violation reports
CREATE TABLE citizen_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    billboard_id UUID REFERENCES violation_reports(id) ON DELETE CASCADE,
    reporter_name TEXT NOT NULL,
    reporter_email TEXT NOT NULL,
    reporter_reputation INTEGER DEFAULT 0,
    latitude NUMERIC,
    longitude NUMERIC,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'submitted',  -- submitted, validated, flagged, resolved, rejected
    validated_by_count INTEGER DEFAULT 0,  -- Number of citizens who validated
    validator_ids TEXT[],  -- List of validator user IDs
    submitted_at TIMESTAMP DEFAULT now(),
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- Indexes
CREATE INDEX idx_citizen_reports_billboard_id ON citizen_reports(billboard_id);
CREATE INDEX idx_citizen_reports_submitted_at ON citizen_reports(submitted_at DESC);
CREATE INDEX idx_citizen_reports_status ON citizen_reports(status);
CREATE INDEX idx_citizen_reports_validated_count ON citizen_reports(validated_by_count DESC);

-- ============ 4. BILLBOARD LOCATIONS TABLE ============
-- Geolocation tracking of billboards
CREATE TABLE billboard_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    latitude NUMERIC NOT NULL,
    longitude NUMERIC NOT NULL,
    address TEXT,
    city TEXT,
    state TEXT,
    country TEXT DEFAULT 'US',
    report_id UUID REFERENCES violation_reports(id) ON DELETE SET NULL,
    billboard_metadata JSONB,  -- Additional metadata
    violation_reports_ids UUID[],  -- Array of related violation report IDs
    location_timestamp TIMESTAMP DEFAULT now(),
    created_at TIMESTAMP DEFAULT now()
);

-- Indexes for geospatial queries
CREATE INDEX idx_billboard_locations_lat_lon ON billboard_locations(latitude, longitude);
CREATE INDEX idx_billboard_locations_created_at ON billboard_locations(created_at DESC);
CREATE INDEX idx_billboard_locations_report_id ON billboard_locations(report_id);

-- ============ 5. IMAGE STORAGE METADATA TABLE ============
-- Metadata for stored billboard images
CREATE TABLE image_storage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL UNIQUE,
    file_size BIGINT,
    mime_type TEXT,
    report_id UUID REFERENCES violation_reports(id) ON DELETE CASCADE,
    upload_timestamp TIMESTAMP DEFAULT now(),
    processed BOOLEAN DEFAULT false,
    storage_path TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Index
CREATE INDEX idx_image_storage_report_id ON image_storage(report_id);

-- ============ TRIGGERS & FUNCTIONS ============

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_violation_reports_updated_at
BEFORE UPDATE ON violation_reports
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_citizen_reports_updated_at
BEFORE UPDATE ON citizen_reports
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

-- Auto-flag violation when citizen reports reach threshold
CREATE OR REPLACE FUNCTION check_and_flag_violation()
RETURNS TRIGGER AS $$
DECLARE
    MIN_REPORTS_THRESHOLD INTEGER := 3;
    total_validations INTEGER;
BEGIN
    -- Count total validations for this billboard
    SELECT COUNT(*) INTO total_validations
    FROM citizen_reports
    WHERE billboard_id = NEW.billboard_id
    AND status != 'rejected';
    
    -- Auto-flag if threshold reached
    IF total_validations >= MIN_REPORTS_THRESHOLD THEN
        UPDATE violation_reports
        SET status = 'flagged_by_citizens'
        WHERE id = NEW.billboard_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auto_flag_violation_trigger
AFTER INSERT OR UPDATE ON citizen_reports
FOR EACH ROW
EXECUTE FUNCTION check_and_flag_violation();

-- ============ VIEWS FOR COMMON QUERIES ============

-- High-severity violations summary
CREATE VIEW high_severity_violations AS
SELECT 
    vr.id,
    vr.status,
    vr.severity_level,
    vr.severity_score,
    vr.violation_count,
    vr.latitude,
    vr.longitude,
    COUNT(DISTINCT cr.id) as citizen_reports_count,
    vr.created_at
FROM violation_reports vr
LEFT JOIN citizen_reports cr ON cr.billboard_id = vr.id
WHERE vr.severity_level IN ('Critical', 'High')
GROUP BY vr.id
ORDER BY vr.severity_score DESC;

-- Citizen engagement leaderboard
CREATE VIEW citizen_engagement_stats AS
SELECT 
    cr.reporter_email,
    cr.reporter_name,
    COUNT(*) as total_reports_submitted,
    SUM(cr.validated_by_count) as validations_received,
    cr.reporter_reputation
FROM citizen_reports cr
GROUP BY cr.reporter_email, cr.reporter_name, cr.reporter_reputation
ORDER BY validations_received DESC;

-- Recent violations by location
CREATE VIEW violations_by_location AS
SELECT 
    bl.city,
    bl.state,
    COUNT(DISTINCT vr.id) as violation_count,
    COUNT(DISTINCT CASE WHEN vr.status = 'pending' THEN vr.id END) as pending_count,
    COUNT(DISTINCT CASE WHEN vr.status = 'flagged_by_citizens' THEN vr.id END) as flagged_count,
    AVG(vr.severity_score) as avg_severity,
    MAX(vr.created_at) as last_violation_date
FROM violation_reports vr
LEFT JOIN billboard_locations bl ON vr.latitude = bl.latitude AND vr.longitude = bl.longitude
WHERE vr.created_at > NOW() - INTERVAL '7 days'
GROUP BY bl.city, bl.state
ORDER BY violation_count DESC;

-- ============ ROW LEVEL SECURITY (Optional) ============
-- Uncomment to enable RLS

/*
ALTER TABLE violation_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE citizen_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE billboard_locations ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "Enable read access for all users"
ON violation_reports FOR SELECT
USING (true);

CREATE POLICY "Enable read access for all users"
ON citizen_reports FOR SELECT
USING (true);

-- Allow authenticated users to insert citizen reports
CREATE POLICY "Enable insert for citizen reports"
ON citizen_reports FOR INSERT
WITH CHECK (true);
*/

-- ============ SAMPLE QUERIES ============
/*

-- Get pending reports with high severity
SELECT * FROM violation_reports 
WHERE status = 'pending' AND severity_level IN ('Critical', 'High')
ORDER BY severity_score DESC;

-- Find nearby billboards (example: within 1km)
SELECT * FROM billboard_locations
WHERE ABS(latitude - 40.7128) < 0.01 
  AND ABS(longitude - (-74.0060)) < 0.01;

-- Get citizen engagement stats
SELECT * FROM citizen_engagement_stats;

-- Get violations by location (last 7 days)
SELECT * FROM violations_by_location;

-- Check compliance status for specific location
SELECT * FROM compliance_checks 
WHERE location->>'city' = 'New York'
ORDER BY check_timestamp DESC;

*/
