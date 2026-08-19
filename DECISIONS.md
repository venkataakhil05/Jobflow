# JobFlow â€” Engineering Decisions

## 1. Ingestion Strategy

JobFlow uses Jobicy as the primary job source and Remotive as the fallback source.

The main reason for this approach is reliability. The ingestion pipeline should not depend completely on a single external source. If the primary source fails, times out, returns an empty response, or encounters an ingestion error, JobFlow can switch to the fallback source and continue processing jobs.

The pipeline is:

Jobicy â†’ Retry â†’ Normalize â†’ Validate â†’ Deduplicate â†’ Store

If the primary source cannot provide usable data:

Jobicy â†’ Failure â†’ Remotive â†’ Normalize â†’ Validate â†’ Deduplicate â†’ Store

This gives the system a controlled recovery path instead of allowing one external dependency to stop the complete ingestion process.

## 2. Detection Surface

JobFlow monitors the response from the primary source during ingestion.

The ingestion layer can detect situations such as:

- Request failure
- Source errors
- Empty responses
- Invalid or unusable job data
- Ingestion exceptions

When the primary source cannot provide usable data, the system activates the fallback path.

A controlled `/test-fallback` endpoint was also implemented so that the resilience behavior can be demonstrated without intentionally disrupting an external service.

## 3. Resilience

The system uses a retry and timeout strategy before falling back to another source.

The dashboard exposes whether fallback was used during the latest ingestion.

For example:

source: remotive

fallback_used: true

This makes the recovery behavior observable instead of hiding the failure.

Ingestion logs also record:

- Source
- Fallback status
- Jobs fetched
- Jobs inserted
- Jobs skipped
- Status
- Timestamp

## 4. Data Quality

Before jobs are stored, the ingestion layer normalizes the source-specific data into a common job structure.

The normalized structure contains fields such as:

- external_id
- source
- title
- company
- location
- job_type
- URL
- posted_at

Duplicate detection uses the source and external job identifier so that repeated ingestion runs do not create duplicate database records.

## 5. Trade-off

Because this project was developed under a limited time constraint, the system uses SQLite for persistence instead of introducing a larger production database infrastructure.

SQLite keeps the project simple to run, easy to demonstrate, and suitable for the prototype.

With a full production development period, I would evaluate PostgreSQL for stronger concurrent workloads, deployment scalability, monitoring, migrations, and operational reliability.

I would also add more detailed metrics and structured application logging.

## 6. Responsible Data Collection Boundary

JobFlow intentionally uses public, low-risk job sources instead of attempting to bypass authentication, anti-bot systems, CAPTCHAs, or access controls on platforms such as LinkedIn.

The goal is to demonstrate the ingestion architecture and resilience strategy rather than bypass platform protections.

If a source explicitly prohibited the intended automated access through its applicable terms or technical controls, I would stop the automated collection rather than attempting to circumvent those protections.

## 7. AI Usage

AI assistance was used during development for brainstorming, debugging, implementation guidance, code structure, and improving the frontend presentation.

I did not treat AI-generated code as automatically correct. I personally ran the application locally, reviewed the generated implementation, ran the automated tests, and manually tested the main API workflows.

During deployment, I also inspected actual runtime errors from Render and changed the implementation based on those errors. For example, I corrected the `save_jobs()` call when the production traceback showed that the `source` and `fallback_used` arguments were missing, and I implemented a controlled `/test-fallback` endpoint to verify the primary-to-fallback recovery path.

The main workflows were manually verified, including:

- Normal Jobicy ingestion
- Duplicate detection
- Ingestion logging
- Job retrieval
- Primary-source failure handling
- Remotive fallback
- Production deployment

The final pytest run passed all eight automated tests.


## 8. Verification

The application was verified through:

- FastAPI `/health`
- FastAPI `/docs`
- `/ingest`
- `/jobs`
- `/ingestion-logs`
- Controlled fallback testing
- Automated pytest tests

The automated test suite currently reports:

8 passed

The project therefore verifies the main ingestion, persistence, duplicate detection, fallback, and API workflows before deployment.
