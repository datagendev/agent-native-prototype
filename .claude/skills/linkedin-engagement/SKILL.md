---
name: linkedin-engagement
description: Fetch LinkedIn post engagement (comments or reactions) and add them to the Neon database. Use when the user provides a LinkedIn post URL.
---

# LinkedIn Engagement to Database

Fetch LinkedIn post engagement (comments or reactions) and add them to the Neon database using the new schema (prospects, linkedin_posts, engagements).

## Workflow

When the user provides a LinkedIn post URL, you should:

1. **Extract the post URL** from their message

2. **Ask clarifying questions** using AskUserQuestion to determine:
   - Engagement type (comments or reactions)
   - Whether to exclude the post author
   - Whether to create a campaign from the engagement

3. **Validate environment**:
   - Check that DATAGEN_API_KEY is set (from `../.env`)
   - If missing, instruct user to set it

4. **Execute the fetch script** with the appropriate parameters:
   ```bash
   cd /Users/yu-shengkuo/projects/datagendev/marketing/linkedin-outreach/scripts
   source ../.venv/bin/activate
   # Script automatically loads DATAGEN_API_KEY from ../.env
   python3 fetch_linkedin_engagement.py --type [comments|reactions] [--exclude-author username] "POST_URL"
   ```

5. **Verify the insertion** by querying the database:
   ```sql
   -- Check post and engagement counts
   SELECT
     lp.post_url,
     lp.total_comments,
     lp.total_reactions,
     COUNT(e.id) as engagements_saved,
     COUNT(DISTINCT p.id) as unique_prospects
   FROM linkedin_posts lp
   LEFT JOIN engagements e ON e.post_id = lp.id
   LEFT JOIN prospects p ON p.id = e.prospect_id
   WHERE lp.post_url LIKE '%POST_URL%'
   GROUP BY lp.id;
   ```

6. **(Optional) Create campaign** if user requested it:
   ```bash
   python3 create_campaign.py \
     --name "CAMPAIGN_NAME" \
     --description "CAMPAIGN_DESCRIPTION" \
     --columns comment_text:TEXT urgency_level:INTEGER \
     --populate-from-post "POST_URL" \
     --map comment_text:e.comment urgency_level:5
   ```

7. **Report results** to the user with:
   - Number of prospects created/updated
   - Number of engagements saved
   - Post statistics
   - Campaign details (if created)

## Key Parameters

- **--type**: `comments` or `reactions` (required)
- **--exclude-author**: LinkedIn public identifier to exclude (e.g., `jordancrawford`)
- **--dry-run**: Preview without inserting (optional)

## Example Questions to Ask

Use AskUserQuestion with these options:

**Question 1: Engagement Type**
- Header: "Engagement"
- Question: "What type of engagement should I fetch?"
- multiSelect: false
- Options:
  - label: "Comments only", description: "Fetch and save comments from the post"
  - label: "Reactions only", description: "Fetch and save reactions (likes, loves, etc.)"
  - label: "Both", description: "Fetch both comments and reactions in separate runs"

**Question 2: Exclude Author**
- Header: "Author"
- Question: "Should I exclude the post author's own engagement?"
- multiSelect: false
- Options:
  - label: "Exclude post author (Recommended)", description: "Don't include the author's own engagement"
  - label: "Include everyone", description: "Include all engagement including the post author"

**Question 3: Create Campaign**
- Header: "Campaign"
- Question: "Should I create a campaign from this engagement?"
- multiSelect: false
- Options:
  - label: "Yes, create campaign", description: "Create a campaign table with prospects from this post"
  - label: "No, just fetch engagement", description: "Only fetch and save engagement data"

## Extracting Author Username

If user chooses to exclude author, you need to extract the LinkedIn username from the post URL:
- Pattern: `https://www.linkedin.com/posts/USERNAME_...`
- Example: `https://www.linkedin.com/posts/jordancrawford_...` → username is `jordancrawford`

## Notes

- The script automatically extracts the activity ID from the LinkedIn URL
- URLs are automatically cleaned (removes tracking parameters like `?utm_source=...`)
- Data is saved to three tables: `prospects`, `linkedin_posts`, and `engagements`
- Duplicate prevention via unique constraints
- DATAGEN_API_KEY is loaded from `../.env` file
- Virtual environment is at `../.venv/`

## Error Handling

If the script fails:
1. Check that the LinkedIn post URL is valid
2. Verify DATAGEN_API_KEY exists in `../.env`
3. Ensure the virtual environment exists at `../.venv/`
4. Check if the post has any engagement (some posts have 0 comments/reactions)

## Database Schema (New System)

The script creates/updates records across three tables:

### 1. `prospects` table
- `linkedin_url`: LinkedIn profile URL (unique)
- `name`: Contact name
- `headline`: LinkedIn headline
- `status`: Lifecycle stage (discovered, contacted, responded, converted)
- `discovered_via`: Source (e.g., 'post_engagement')
- `profile_data`: JSONB with additional profile info

### 2. `linkedin_posts` table
- `post_url`: Full LinkedIn post URL (unique, cleaned, with trailing /)
- `author_name`: Post author name
- `author_linkedin_url`: Post author profile
- `total_comments`: Comment count (auto-updated)
- `total_reactions`: Reaction count (auto-updated)

### 3. `engagements` table
- `prospect_id`: References prospects(id)
- `post_id`: References linkedin_posts(id)
- `engage_type`: 'comment' or 'reaction'
- `comment`: Comment text (NULL for reactions)
- `reaction_type`: Reaction type: LIKE, LOVE, etc. (NULL for comments)
- Unique constraint: (prospect_id, post_id, engage_type)

## Database Verification Queries

After insertion, show the user a summary:
```sql
-- Overall summary
SELECT
  lp.post_url,
  lp.total_comments,
  lp.total_reactions,
  COUNT(e.id) as engagements_saved,
  COUNT(DISTINCT p.id) as unique_prospects
FROM linkedin_posts lp
LEFT JOIN engagements e ON e.post_id = lp.id
LEFT JOIN prospects p ON p.id = e.prospect_id
WHERE lp.post_url LIKE '%POST_URL%'
GROUP BY lp.id;

-- Sample prospects with engagement
SELECT
  p.id,
  p.name,
  p.linkedin_url,
  e.engage_type,
  LEFT(e.comment, 50) as comment_preview,
  e.reaction_type
FROM prospects p
JOIN engagements e ON e.prospect_id = p.id
JOIN linkedin_posts lp ON lp.id = e.post_id
WHERE lp.post_url LIKE '%POST_URL%'
ORDER BY p.id DESC
LIMIT 10;
```
