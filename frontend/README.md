# Frontend — The Daily Signal (Next.js)

Next.js 16 (App Router) + React 19 + Tailwind CSS 4 + Recharts. Reads analysed articles from
Supabase; when the database is not configured or empty it falls back to live publisher RSS feeds,
scored in the server with the same rule-based engine the backend uses (`src/lib/scoring.ts`).

```bash
cp .env.example .env.local   # fill in the Supabase URL and anon key
npm install
npm run dev                  # http://localhost:3000
npm run test                 # Vitest
npm run lint
npm run build
```

Key files: `src/lib/repository.ts` (data access + normalisation), `src/lib/scoring.ts` (eight
dimensions + rule risk; mirrored by `backend/services/dimension_service.py`), `src/lib/clustering.ts`
(cross-source grouping), `src/lib/pdfReportGenerator.ts` (browser PDF), `src/app/*` (pages and
API routes). See the main README for the full setup.
