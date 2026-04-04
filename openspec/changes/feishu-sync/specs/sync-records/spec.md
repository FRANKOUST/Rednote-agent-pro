## ADDED Requirements

### Requirement: The platform SHALL persist sync records for key workflow boundaries
The system SHALL persist sync records for source-post batches, content-draft batches, and publish jobs.

#### Scenario: Persist generation sync records
- **WHEN** the pipeline completes generation stages
- **THEN** the platform stores sync records for source-post and content-draft batches

#### Scenario: Persist publish sync record
- **WHEN** a publish job completes
- **THEN** the platform stores a sync record for that publish job
