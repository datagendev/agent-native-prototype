# LinkedIn Outreach System - Complete Guide

**Last Updated:** 2025-12-29
**Database:** Neon - `blue-tree-25780810` / `neondb`
**Python SDK:** datagen-python-sdk

---

## 📊 Database Schema Overview

### Architecture

```
┌─────────────────┐
│ linkedin_posts  │  Posts being monitored
└────────┬────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│  engagements    │  How prospects engaged
└────────┬────────┘
         │
         │ N:1
         ▼
┌─────────────────┐         ┌──────────────────┐
│   prospects     │◄────────│ campaign_*       │  Campaign-specific tables
└────────┬────────┘         │ (dynamic tables) │
         │                  └──────────────────┘
         │ 1:N                       ▲
         ▼                           │
┌─────────────────┐         ┌───────┴──────────┐
│    messages     │         │    campaigns     │  Campaign registry
└─────────────────┘         └──────────────────┘
```

---

## 🗄️ Core Tables

### 1. `prospects` - Central Contact Database

**Purpose:** Single source of truth for all people you engage with

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | Unique identifier |
| `linkedin_url` | TEXT UNIQUE | LinkedIn profile URL |
| `name` | TEXT | Contact name |
| `headline` | TEXT | LinkedIn headline |
| `company` | TEXT | Current company |
| `profile_data` | JSONB | Additional profile info |
| `status` | TEXT | Lifecycle stage (discovered, contacted, responded, converted) |
| `lead_score` | INTEGER | Quality score |
| `first_seen_at` | TIMESTAMPTZ | When first discovered |
| `discovered_via` | TEXT | Source (e.g., 'post_engagement') |
| `contacted_count` | INTEGER | Number of times contacted |
| `last_contacted_at` | TIMESTAMPTZ | Last contact timestamp |
| `last_response_at` | TIMESTAMPTZ | Last response timestamp |
| `tags` | JSONB | Array of tags |
| `notes` | TEXT | Free-form notes |
| `created_at` | TIMESTAMPTZ | Record creation |
| `updated_at` | TIMESTAMPTZ | Last update |

**Indexes:**
- `idx_prospects_linkedin_url` on `linkedin_url`
- `idx_prospects_status` on `status`

**Current Count:** 51 prospects

---

### 2. `linkedin_posts` - Post Tracking

**Purpose:** Track LinkedIn posts you're monitoring for engagement

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | Unique identifier |
| `post_url` | TEXT UNIQUE | Full LinkedIn post URL (cleaned, with trailing /) |
| `author_name` | TEXT | Post author name |
| `author_linkedin_url` | TEXT | Post author profile |
| `post_content` | TEXT | Post text content |
| `total_comments` | INTEGER | Comment count (auto-updated) |
| `total_reactions` | INTEGER | Reaction count (auto-updated) |
| `last_scraped_at` | TIMESTAMPTZ | Last scrape timestamp |
| `is_active` | BOOLEAN | Still monitoring? |
| `scrape_frequency` | TEXT | Scrape schedule (once, daily, weekly) |
| `created_at` | TIMESTAMPTZ | Record creation |
| `updated_at` | TIMESTAMPTZ | Last update |

**Indexes:**
- `idx_linkedin_posts_url` on `post_url`
- `idx_linkedin_posts_active` on `is_active`

**Unique Constraint:** `post_url` (prevents duplicates)

**Current Count:** 2 posts

---

### 3. `engagements` - Prospect-Post Interactions

**Purpose:** Links prospects to posts with engagement details

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | Unique identifier |
| `prospect_id` | INTEGER FK | References `prospects(id)` |
| `post_id` | INTEGER FK | References `linkedin_posts(id)` |
| `engage_type` | TEXT | Type: 'comment' or 'reaction' |
| `comment` | TEXT | Comment text (NULL for reactions) |
| `reaction_type` | TEXT | Reaction type: LIKE, LOVE, etc. (NULL for comments) |
| `engaged_at` | TIMESTAMPTZ | When engagement happened |
| `created_at` | TIMESTAMPTZ | Record creation |

**Indexes:**
- `idx_engagements_prospect` on `prospect_id`
- `idx_engagements_post` on `post_id`
- `idx_engagements_type` on `engage_type`

**Unique Constraint:** `(prospect_id, post_id, engage_type)`

**Current Count:** 51 engagements

---

### 4. `campaigns` - Campaign Registry

**Purpose:** Track all outreach campaigns

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | Unique identifier |
| `name` | TEXT | Campaign name |
| `description` | TEXT | Campaign description |
| `status` | TEXT | draft, active, paused, completed, archived |
| `campaign_type` | TEXT | Type (e.g., post_engagement) |
| `table_name` | TEXT UNIQUE | Associated campaign table name |
| `table_schema` | JSONB | Custom column definitions |
| `heyreach_list_id` | TEXT | HeyReach list ID |
| `heyreach_campaign_id` | TEXT | HeyReach campaign ID |
| `last_synced_at` | TIMESTAMPTZ | Last HeyReach sync |
| `message_templates` | JSONB | Array of message templates |
| `total_prospects` | INTEGER | Total prospects (denormalized) |
| `contacted` | INTEGER | Contacted count |
| `responded` | INTEGER | Response count |
| `converted` | INTEGER | Conversion count |
| `created_at` | TIMESTAMPTZ | Record creation |
| `updated_at` | TIMESTAMPTZ | Last update |

**Indexes:**
- `idx_campaigns_table_name` on `table_name`
- `idx_campaigns_status` on `status`

**Current Count:** 1 campaign

---

### 5. `campaign_*` Tables - Campaign-Specific Data

**Purpose:** Each campaign gets its own table with custom columns

**Standard Columns (all campaign tables have these):**

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | Unique identifier |
| `prospect_id` | INTEGER FK | References `prospects(id)` |
| `status` | TEXT | pending, contacted, responded, converted, excluded |
| `added_at` | TIMESTAMPTZ | When added to campaign |
| `contacted_at` | TIMESTAMPTZ | When contacted |
| `responded_at` | TIMESTAMPTZ | When responded |

**Custom Columns:** Defined per campaign (e.g., `comment_text`, `urgency_level`, etc.)

**Indexes (auto-created):**
- `idx_{table_name}_prospect` on `prospect_id`
- `idx_{table_name}_status` on `status`

**Unique Constraint:** `prospect_id` (one prospect per campaign)

**Example:** `campaign_jordan_crawford_gtm_session_link_requests` (27 prospects)

---

### 6. `messages` - Communication History

**Purpose:** Track all messages sent and received

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | Unique identifier |
| `prospect_id` | INTEGER FK | References `prospects(id)` |
| `campaign_id` | INTEGER FK | References `campaigns(id)` |
| `direction` | TEXT | 'outbound' or 'inbound' |
| `platform` | TEXT | 'linkedin', 'email', etc. |
| `message_type` | TEXT | connection_request, direct_message, inmail |
| `subject` | TEXT | Message subject |
| `body` | TEXT | Message content |
| `sequence_step` | INTEGER | Step in message sequence |
| `heyreach_message_id` | TEXT | HeyReach message ID |
| `external_id` | TEXT | External platform ID |
| `status` | TEXT | draft, sent, delivered, read, replied, failed |
| `sent_at` | TIMESTAMPTZ | Send timestamp |
| `read_at` | TIMESTAMPTZ | Read timestamp |
| `replied_at` | TIMESTAMPTZ | Reply timestamp |
| `created_at` | TIMESTAMPTZ | Record creation |

**Indexes:**
- `idx_messages_prospect` on `prospect_id`
- `idx_messages_campaign` on `campaign_id`
- `idx_messages_sent_at` on `sent_at`
- `idx_messages_direction` on `direction`

**Current Count:** 0 (ready for use)

---

## 🛠️ Scripts & Tools

### 1. `fetch_linkedin_engagement.py`

**Purpose:** Scrape LinkedIn post engagement and save to database

**Location:** `/scripts/fetch_linkedin_engagement.py`

**What it does:**
1. Fetches comments or reactions from a LinkedIn post
2. Creates/updates prospects
3. Creates/updates post record
4. Creates engagement records
5. Updates post statistics
6. Automatically cleans URLs (removes tracking parameters)

**Usage:**

```bash
# Dry run (preview data)
python fetch_linkedin_engagement.py \
  --type comments \
  --dry-run \
  "https://www.linkedin.com/posts/author_post-url"

# Fetch and save comments
python fetch_linkedin_engagement.py \
  --type comments \
  "https://www.linkedin.com/posts/author_post-url"

# Exclude post author
python fetch_linkedin_engagement.py \
  --type comments \
  --exclude-author jordancrawford \
  "https://www.linkedin.com/posts/jordancrawford_..."

# Fetch reactions
python fetch_linkedin_engagement.py \
  --type reactions \
  "https://www.linkedin.com/posts/author_post-url"
```

**Parameters:**
- `post_url` (required): LinkedIn post URL (tracking parameters automatically removed)
- `--type` (required): `comments` or `reactions`
- `--dry-run`: Preview without saving
- `--exclude-author`: LinkedIn username to exclude (e.g., post author)

**Features:**
- ✅ URL cleaning (removes `?utm_source=...` etc.)
- ✅ Duplicate prevention via unique constraints
- ✅ Auto-creates prospects if new
- ✅ Auto-updates existing prospects
- ✅ Handles both comments and reactions

---

### 2. `create_campaign.py`

**Purpose:** Create a new campaign with custom columns

**Location:** `/scripts/create_campaign.py`

**What it does:**
1. Creates campaign registry entry
2. Creates campaign-specific table with custom columns
3. Optionally populates from existing engagements
4. Updates campaign metrics

**Usage:**

```bash
# Create campaign with custom columns
python create_campaign.py \
  --name "Jordan Crawford GTM Session - Link Requests" \
  --description "Follow up with people who asked for the link" \
  --columns comment_text:TEXT post_url:TEXT urgency_level:INTEGER

# Create and populate from a post
python create_campaign.py \
  --name "My Campaign" \
  --description "Campaign description" \
  --columns comment_text:TEXT urgency:INTEGER \
  --populate-from-post "https://linkedin.com/posts/..." \
  --map comment_text:e.comment urgency:5

# Create with multiple custom columns
python create_campaign.py \
  --name "Multi-Column Campaign" \
  --description "Campaign with many fields" \
  --columns \
    comment_text:TEXT \
    post_url:TEXT \
    urgency_level:INTEGER \
    follow_up_note:TEXT \
    company:TEXT \
  --populate-from-post "https://..." \
  --map comment_text:e.comment post_url:lp.post_url
```

**Parameters:**
- `--name` (required): Campaign name
- `--description` (required): Campaign description
- `--columns` (required): Custom columns in format `name:TYPE` (space-separated)
- `--campaign-type`: Campaign type (default: `post_engagement`)
- `--populate-from-post`: LinkedIn post URL to populate from
- `--map`: Column mappings for population (e.g., `comment_text:e.comment`)

**Column Types:**
- `TEXT` - Text strings
- `INTEGER` - Whole numbers
- `BOOLEAN` - True/false
- `TIMESTAMPTZ` - Timestamps with timezone
- `JSONB` - JSON data

**Generated Table Name:**
- Automatically sanitized from campaign name
- Example: "My Campaign Name" → `campaign_my_campaign_name`

---

## 📖 Common Workflows

### Workflow 1: Scrape New Post

```bash
# 1. Scrape engagement
python fetch_linkedin_engagement.py \
  --type comments \
  --exclude-author postauthor \
  "https://linkedin.com/posts/..."

# Result: Creates prospects, engagements, post record
```

### Workflow 2: Create Campaign from Post

```bash
# 1. Create campaign
python create_campaign.py \
  --name "Q1 GTM Engineers Outreach" \
  --description "Follow up with GTM engineers who commented" \
  --columns comment_text:TEXT urgency_level:INTEGER follow_up_priority:INTEGER \
  --populate-from-post "https://linkedin.com/posts/..." \
  --map comment_text:e.comment urgency_level:5 follow_up_priority:1

# Result: Creates campaign + campaign table with 27 prospects
```

### Workflow 3: Query Campaign Prospects

```sql
-- Get all pending prospects in a campaign
SELECT
  ct.id,
  p.name,
  p.linkedin_url,
  ct.comment_text,
  ct.urgency_level,
  ct.status
FROM campaign_jordan_crawford_gtm_session_link_requests ct
JOIN prospects p ON p.id = ct.prospect_id
WHERE ct.status = 'pending'
ORDER BY ct.urgency_level DESC, ct.id;
```

### Workflow 4: Track Multi-Post Engagers

```sql
-- Find prospects who engaged with multiple posts
SELECT
  p.id,
  p.name,
  p.linkedin_url,
  COUNT(DISTINCT e.post_id) as posts_engaged,
  string_agg(DISTINCT lp.post_url, '\n') as post_urls
FROM prospects p
JOIN engagements e ON e.prospect_id = p.id
JOIN linkedin_posts lp ON lp.id = e.post_id
GROUP BY p.id, p.name, p.linkedin_url
HAVING COUNT(DISTINCT e.post_id) > 1
ORDER BY posts_engaged DESC;
```

### Workflow 5: Export to HeyReach

```sql
-- Get campaign data ready for HeyReach
SELECT
  p.name as "Full Name",
  p.linkedin_url as "LinkedIn URL",
  ct.comment_text as "Comment",
  ct.urgency_level as "Priority",
  ct.status as "Status"
FROM campaign_jordan_crawford_gtm_session_link_requests ct
JOIN prospects p ON p.id = ct.prospect_id
WHERE ct.status = 'pending'
ORDER BY ct.urgency_level DESC;

-- Export as CSV and upload to HeyReach
```

### Workflow 6: Track Messages

```sql
-- Record outbound message
INSERT INTO messages (
  prospect_id,
  campaign_id,
  direction,
  platform,
  body,
  sequence_step,
  status
) VALUES (
  15,  -- prospect_id
  5,   -- campaign_id
  'outbound',
  'linkedin',
  'Hi! Saw your comment about the GTM session...',
  1,
  'sent'
);

-- Update campaign status
UPDATE campaign_jordan_crawford_gtm_session_link_requests
SET
  status = 'contacted',
  contacted_at = NOW()
WHERE prospect_id = 15;

-- Update prospect
UPDATE prospects
SET
  contacted_count = contacted_count + 1,
  last_contacted_at = NOW(),
  status = 'contacted'
WHERE id = 15;
```

---

## 📊 Useful Queries

### Analytics Queries

```sql
-- Campaign performance summary
SELECT
  c.id,
  c.name,
  c.status as campaign_status,
  c.total_prospects,
  c.contacted,
  c.responded,
  c.converted,
  ROUND(100.0 * c.contacted / NULLIF(c.total_prospects, 0), 1) as contact_rate,
  ROUND(100.0 * c.responded / NULLIF(c.contacted, 0), 1) as response_rate,
  ROUND(100.0 * c.converted / NULLIF(c.responded, 0), 1) as conversion_rate
FROM campaigns c
ORDER BY c.created_at DESC;

-- Prospect lifecycle distribution
SELECT
  status,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as percentage
FROM prospects
GROUP BY status
ORDER BY count DESC;

-- Top engaged posts
SELECT
  lp.id,
  lp.post_url,
  lp.total_comments,
  lp.total_reactions,
  lp.total_comments + lp.total_reactions as total_engagement,
  COUNT(DISTINCT e.prospect_id) as unique_engagers
FROM linkedin_posts lp
LEFT JOIN engagements e ON e.post_id = lp.id
GROUP BY lp.id
ORDER BY total_engagement DESC;

-- Message response times
SELECT
  AVG(EXTRACT(EPOCH FROM (m_in.sent_at - m_out.sent_at)) / 3600) as avg_response_hours,
  COUNT(*) as total_responses
FROM messages m_out
JOIN messages m_in ON m_in.prospect_id = m_out.prospect_id
  AND m_in.campaign_id = m_out.campaign_id
  AND m_in.direction = 'inbound'
  AND m_in.sent_at > m_out.sent_at
WHERE m_out.direction = 'outbound'
  AND m_out.sequence_step = 1;
```

---

## 🔒 Data Protection

### Unique Constraints
- `prospects.linkedin_url` - Prevents duplicate contacts
- `linkedin_posts.post_url` - Prevents duplicate posts
- `engagements(prospect_id, post_id, engage_type)` - Prevents duplicate engagements
- `campaign_*.prospect_id` - One prospect per campaign

### Cascading Deletes
- Delete post → deletes engagements (prospects preserved)
- Delete prospect → deletes engagements, messages, campaign entries
- Delete campaign → deletes campaign table entries

### URL Cleaning
- Automatically removes tracking parameters (`?utm_source=...`)
- Adds trailing `/` for consistency
- Prevents duplicates from different URL formats

---

## 🎯 Best Practices

### 1. Scraping Posts
- Always use `--exclude-author` to exclude post author
- Run `--dry-run` first to preview data
- URLs are automatically cleaned (tracking parameters removed)

### 2. Creating Campaigns
- Use descriptive campaign names
- Add custom columns relevant to your outreach strategy
- Populate from post immediately to capture context

### 3. Tracking Outreach
- Update `campaign_*.status` when contacting prospects
- Record all messages in `messages` table
- Update prospect status as they move through funnel

### 4. Database Maintenance
- Posts with same URL are automatically merged
- Duplicate engagements are automatically prevented
- Clean up old campaigns: `DELETE FROM campaigns WHERE status = 'archived'`

---

## 🚀 Future Enhancements

### Planned Features
1. **Multi-Post Campaigns**: Support `--populate-from-posts` with multiple URLs
2. **Role Detection**: Auto-detect prospect role from comments/profile
3. **HeyReach Sync**: Direct integration to push campaigns to HeyReach
4. **Webhook Tracking**: Auto-track responses via HeyReach webhooks
5. **Campaign Analytics**: Built-in reporting dashboard

### Schema Extensions
```sql
-- Add role/segment to prospects
ALTER TABLE prospects
ADD COLUMN role TEXT,
ADD COLUMN company_type TEXT,
ADD COLUMN seniority TEXT;

-- Add source posts tracking to campaigns
ALTER TABLE campaigns
ADD COLUMN source_post_urls JSONB DEFAULT '[]';

-- Create campaign-posts junction table
CREATE TABLE campaign_source_posts (
    campaign_id INTEGER REFERENCES campaigns(id),
    post_id INTEGER REFERENCES linkedin_posts(id),
    added_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (campaign_id, post_id)
);
```

---

## 📞 Quick Reference

### Database Connection
- **Project ID:** `blue-tree-25780810`
- **Branch ID:** `br-cool-leaf-afau0ra8`
- **Database:** `neondb`

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Environment variable (in ../.env)
DATAGEN_API_KEY=dd1b63e9f3931ec360494d4289dcf357327f209bdf735bd6cb0a2b5f072ffcba
```

### Script Locations
- `/scripts/fetch_linkedin_engagement.py` - Scraper
- `/scripts/create_campaign.py` - Campaign creator

### Current Stats
- **Prospects:** 51
- **Posts:** 2
- **Engagements:** 51
- **Campaigns:** 1
- **Campaign Tables:** 1 (`campaign_jordan_crawford_gtm_session_link_requests` with 27 prospects)

---

## 📝 Notes

- All timestamps are UTC with timezone
- JSONB fields allow flexible schema evolution
- Use `->` for JSON object access, `->>` for text extraction
- Campaign tables are dynamic - each has custom columns
- URL cleaning is automatic in `fetch_linkedin_engagement.py`

---

**System Status:** ✅ Production Ready
**Last Schema Update:** 2025-12-29
**Documentation Version:** 1.0
