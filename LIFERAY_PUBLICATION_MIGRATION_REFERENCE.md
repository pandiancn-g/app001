# Liferay Publication Migration Reference

## `/o/publication/migration` Endpoint

The `/o/publication/migration` endpoint is part of Liferay's **Publication Framework** (DXP 7.3+). It handles migration of content from **Staging** to **Publications** or migration of publication data between environments.

---

## Data to Display

The migration endpoint typically shows:

| Data Type | Description |
|----------|-------------|
| **Publication metadata** | Name, status, creation date, publish date |
| **Change tracking entries** | What content/entities were modified |
| **Migration status** | Progress, errors, conflicts |
| **Affected entities** | List of tables/entities being migrated |

---

## Key Tables for Liferay Publications

### Core Publication Tables

| Table | Purpose |
|-------|---------|
| **Publication** | Stores publication metadata (name, status, description, siteId, etc.) |
| **CTCollection** | Change tracking collections – groups of changes to be published |
| **CTEntry** | Change tracking entries – individual changes (add/update/delete) |
| **CTProcess** | Tracks publication process status and history |
| **CTRemote** | Remote publication targets (for remote publishing) |

### Change Tracking Columns (Added to Entity Tables)

When `change-tracking-enabled="true"` is set, Liferay adds these columns to tracked tables:

| Column | Type | Purpose |
|--------|------|---------|
| **ctCollectionId** | BIGINT | Links row to a publication/collection |
| **mvccVersion** | LONG | Optimistic locking (when `mvcc-enabled="true"`) |

### Common Content Tables (Publication-Tracked)

| Table | Content Type |
|-------|--------------|
| **JournalArticle** | Web content articles |
| **Layout** | Pages |
| **LayoutRevision** | Page revisions |
| **DDMStructure** | Dynamic data mapping structures |
| **DDMTemplate** | Templates |
| **BlogsEntry** | Blog entries |
| **MBMessage** | Message board posts |
| **WikiPage** | Wiki pages |
| **AssetEntry** | Asset metadata |

---

## Tables to Add for Custom Entity Publication Support

To make **custom data** participate in Publications migration:

### 1. Service XML Changes

```xml
<!-- In your service.xml -->
<entity name="YourEntity" ... change-tracking-enabled="true" mvcc-enabled="true">
```

### 2. Database Columns (Auto-added by Liferay)

Liferay automatically adds when change tracking is enabled:

- `ctCollectionId` (BIGINT)
- `mvccVersion` (BIGINT)

### 3. Required Components

| Component | Purpose |
|-----------|---------|
| **TableReferenceDefinition** | Registers your table with Publication framework |
| **CTDisplayRenderer** | Renders your entity in "Review Changes" UI |

---

## Migration Endpoint – Typical Flow

```
GET  /o/publication/migration          → List migration status/tasks
POST /o/publication/migration          → Start migration
GET  /o/publication/migration/{id}     → Get migration progress
```

---

## How to Discover Your Instance's API

1. **API Explorer**: `http://[your-server]:[port]/o/api`
2. Navigate to **Schemas** → search for "publication" or "migration"
3. Check the exact endpoint path and request/response structure for your Liferay version

---

## Summary: Tables Overview

| Category | Tables |
|----------|--------|
| **Publication core** | Publication, CTCollection, CTEntry, CTProcess, CTRemote |
| **Change tracking** | Columns `ctCollectionId`, `mvccVersion` on entity tables |
| **Content (built-in)** | JournalArticle, Layout, LayoutRevision, DDMStructure, DDMTemplate, BlogsEntry, MBMessage, WikiPage, AssetEntry |
| **Custom entities** | Your tables + TableReferenceDefinition + CTDisplayRenderer |

---

## References

- [Liferay Publications Documentation](https://learn.liferay.com/w/dxp/sites/publishing-tools/publications)
- [Publication Framework with Custom Entity](https://liferay.dev/b/publication-framework-custom-entity)
- [Managing Data and Content Types in Staging](https://learn.liferay.com/w/dxp/site-building/publishing-tools/staging/managing-data-and-content-types-in-staging)
