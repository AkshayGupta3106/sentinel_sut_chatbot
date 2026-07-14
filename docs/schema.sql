-- Auto-generated from SQLAlchemy models -- do not hand-edit.
-- Regenerate with: python -m sentinel.export_schema
-- Compiled for PostgreSQL; this project runs on SQLite locally (see trace/db.py).

CREATE TABLE alert_log (
	id SERIAL NOT NULL, 
	alert_type VARCHAR NOT NULL, 
	reference_id VARCHAR NOT NULL, 
	success BOOLEAN NOT NULL, 
	error TEXT, 
	sent_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE metrics_timeseries (
	id SERIAL NOT NULL, 
	window_start TIMESTAMP WITH TIME ZONE NOT NULL, 
	window_end TIMESTAMP WITH TIME ZONE NOT NULL, 
	window_minutes INTEGER NOT NULL, 
	metric_name VARCHAR NOT NULL, 
	value FLOAT NOT NULL, 
	computed_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE rca_reports (
	id SERIAL NOT NULL, 
	window_start TIMESTAMP WITH TIME ZONE NOT NULL, 
	regression_ids JSON NOT NULL, 
	root_cause_category VARCHAR NOT NULL, 
	confidence VARCHAR NOT NULL, 
	summary TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE regressions (
	id SERIAL NOT NULL, 
	metric_name VARCHAR NOT NULL, 
	method VARCHAR NOT NULL, 
	severity VARCHAR NOT NULL, 
	window_start TIMESTAMP WITH TIME ZONE NOT NULL, 
	window_minutes INTEGER NOT NULL, 
	baseline_value FLOAT, 
	current_value FLOAT NOT NULL, 
	delta_pct FLOAT, 
	description TEXT NOT NULL, 
	detected_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE traces (
	trace_id VARCHAR NOT NULL, 
	query_id VARCHAR, 
	started_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	ended_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	total_latency_ms FLOAT NOT NULL, 
	num_stages INTEGER NOT NULL, 
	slowest_stage VARCHAR, 
	slowest_stage_latency_ms FLOAT, 
	has_error BOOLEAN NOT NULL, 
	error_stage VARCHAR, 
	ingested_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (trace_id)
);

CREATE TABLE evaluations (
	id SERIAL NOT NULL, 
	trace_id VARCHAR NOT NULL, 
	evaluator_name VARCHAR NOT NULL, 
	score FLOAT, 
	reasoning TEXT, 
	skipped BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(trace_id) REFERENCES traces (trace_id)
);

CREATE TABLE trace_events (
	event_id VARCHAR NOT NULL, 
	trace_id VARCHAR NOT NULL, 
	stage_name VARCHAR NOT NULL, 
	stage_order INTEGER NOT NULL, 
	timestamp_start TIMESTAMP WITH TIME ZONE NOT NULL, 
	timestamp_end TIMESTAMP WITH TIME ZONE NOT NULL, 
	latency_ms FLOAT NOT NULL, 
	status VARCHAR NOT NULL, 
	error TEXT, 
	input_summary JSON, 
	output_summary JSON, 
	event_metadata JSON, 
	PRIMARY KEY (event_id), 
	FOREIGN KEY(trace_id) REFERENCES traces (trace_id)
);

