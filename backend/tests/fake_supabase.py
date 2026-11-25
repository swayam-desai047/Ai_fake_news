"""Minimal in-memory stand-in for the supabase-py query builder used by db_service and the API."""
import uuid
from types import SimpleNamespace


class _Query:
    def __init__(self, db, table):
        self.db, self.table, self.filters, self.op, self.payload = db, table, [], "select", None
        self._limit, self._order, self._range = None, None, None
        self.not_ = SimpleNamespace(is_=lambda col, val: self._add(lambda r: r.get(col) is not None))

    def _add(self, f):
        self.filters.append(f)
        return self

    def select(self, *_a, **_k): return self
    def eq(self, col, val): return self._add(lambda r: r.get(col) == val)
    def in_(self, col, vals): return self._add(lambda r: r.get(col) in vals)
    def is_(self, col, val): return self._add(lambda r: r.get(col) is None)
    def gte(self, col, val): return self._add(lambda r: (r.get(col) or "") >= val)
    def or_(self, _expr): return self
    def order(self, col, desc=False): self._order = (col, desc); return self
    def limit(self, n): self._limit = n; return self
    def range(self, a, b): self._range = (a, b); return self

    def upsert(self, record, on_conflict=None, ignore_duplicates=False):
        self.op, self.payload, self.conflict = "upsert", record, on_conflict
        return self

    def update(self, values):
        self.op, self.payload = "update", values
        return self

    def execute(self):
        rows = self.db.tables.setdefault(self.table, [])
        if self.db.fail:
            raise RuntimeError("db down")
        if self.op == "upsert":
            if any(r.get(self.conflict) == self.payload.get(self.conflict) for r in rows):
                return SimpleNamespace(data=[])
            rec = {"id": str(uuid.uuid4()), **self.payload}
            rows.append(rec)
            return SimpleNamespace(data=[rec])
        matched = [r for r in rows if all(f(r) for f in self.filters)]
        if self.op == "update":
            for r in matched:
                r.update(self.payload)
            return SimpleNamespace(data=matched)
        if self._order:
            col, desc = self._order
            matched = sorted(matched, key=lambda r: r.get(col) or "", reverse=desc)
        if self._range:
            matched = matched[self._range[0]: self._range[1] + 1]
        if self._limit:
            matched = matched[: self._limit]
        return SimpleNamespace(data=[dict(r) for r in matched])


class FakeSupabase:
    def __init__(self, articles=None):
        self.tables = {"articles": list(articles or [])}
        self.fail = False

    def table(self, name):
        return _Query(self, name)
