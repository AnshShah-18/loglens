# LogLens

## What Is LogLens
LogLens is a lightweight log explorer for production-style text logs.  
Upload a log file and instantly see grouped error patterns with a clear "NEW since previous upload" signal.

## Why It's Useful
- Surfaces repeated failure templates quickly instead of scanning raw lines.
- Highlights regressions/new incidents between deployments using the `NEW` badge.
- Provides a simple workflow for debugging without adding heavy observability tooling.

## Demo In 2 Minutes
Run these commands from the project root:

```bash
make demo-reset
make install
make run
```

In a second terminal:

```bash
cd frontend && npm install && npm run dev
```

Then in the UI:
- Upload `samples/demo.log`
- Upload `samples/demo_new.log`
- On the second upload, confirm `s3 upload failed` is marked with a green `NEW` badge.

## Key Features
- Log normalization: UUID, IP, numeric values, trace/hash-like IDs, quoted strings, and file paths normalize into templates.
- Pattern grouping: duplicate normalized lines are grouped with counts and sample lines.
- "NEW since prior upload": each pattern is marked new/existing by comparing against all earlier uploads.

## Tech Stack
- Backend: FastAPI, SQLAlchemy, SQLite, Pydantic
- Frontend: Next.js, React, Tailwind CSS
- Testing: Pytest + FastAPI TestClient

## API Endpoints
- `POST /api/upload`
- `GET /api/uploads/{id}/patterns`
- `GET /api/patterns/{id}`
- `GET /api/health`

## Tests
```bash
make test
```

## Screenshots
- Upload page: ![Upload Page](docs/screenshot-upload-1.png)
- Patterns page: ![Patterns Page](docs/screenshot-upload-2.png)
- Demo GIF: ![Demo GIF](docs/demo.gif)
