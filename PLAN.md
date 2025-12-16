# PhishVision Template System Redesign Plan

**Last Updated: December 8, 2025**

## ✅ Problems SOLVED
1. ~~Built-in templates are hardcoded in Python files~~ → Now database-driven with `is_builtin` flag
2. ~~Adding new templates requires code changes~~ → Templates stored in database
3. ~~No way to manually create/edit templates with custom HTML~~ → TemplateEditor.js with code editor
4. ~~No template import functionality~~ → Can paste HTML directly
5. ~~Must restart server when adding templates~~ → Database-driven, instant updates

## Proposed Solution: Database-Driven Template System

### Phase 1: Enhanced Template Editor UI

**Frontend Changes:**
1. Add a **"Create Template"** button (not just AI-based)
2. Create a new **TemplateEditor** component with:
   - Name, Subject, Category, Difficulty fields
   - **HTML Code Editor** (with syntax highlighting using Monaco Editor or CodeMirror)
   - **Live Preview** panel showing the rendered email
   - **Import HTML** button to paste/upload HTML files
   - Variable placeholders support: `{{name}}`, `{{email}}`, `{{tracking_link}}`

**UI Flow:**
```
Template Library
  ├── "Create Template" → Opens TemplateEditor (manual HTML)
  ├── "Create with AI" → Opens existing AI creator
  └── Template Cards
        ├── Preview
        ├── Edit → Opens TemplateEditor with existing content
        ├── Duplicate
        └── Delete
```

### Phase 2: Migrate Built-in Templates to Database

**Backend Changes:**
1. Create a **seed script** that:
   - Converts all hardcoded templates from `phishing_templates.py` to database entries
   - Marks them as `is_builtin=True` (new field)
   - Runs on first startup if no templates exist

2. Modify **CustomTemplate** model:
   - Add `is_builtin` field (Boolean, default=False)
   - Add `language` field (String, e.g., 'EN', 'AZ')
   - Built-in templates can be duplicated but not deleted

3. Update **campaign_routes.py**:
   - Remove hardcoded template validation
   - All templates come from database
   - Use `CustomTemplate.query.filter_by(is_active=True)`

### Phase 3: Template Variables System

**Variable Placeholders:**
- `{{recipient_name}}` - Parsed from email (john.doe@email.com → John Doe)
- `{{recipient_email}}` - Full email address
- `{{tracking_link}}` - Auto-generated click tracking URL
- `{{current_date}}` - Date when email is sent
- `{{company_name}}` - Optional, from template settings

**Backend processing:**
- Before sending, replace all `{{variable}}` with actual values
- Tracking pixel and links are auto-injected

### Implementation Steps

#### Step 1: Database Migration ✅ DONE
- [x] Add `is_builtin` and `language` columns to CustomTemplate
- [x] Create migration script

#### Step 2: Seed Built-in Templates ✅ DONE
- [x] Create `seed_templates.py` script
- [x] Convert all hardcoded templates to database entries
- [x] Run seed on app startup if empty

#### Step 3: Frontend Template Editor ✅ DONE
- [x] Create TemplateEditor component with:
  - HTML code editor
  - Live preview iframe
  - Form fields for metadata
- [x] Add "Create Template" button to TemplateManager
- [x] Add "Edit" button to template cards
- [x] Add "Duplicate" functionality

#### Step 4: Update Campaign Flow ✅ DONE
- [x] Remove hardcoded template validation
- [x] Load all templates from database
- [x] Process variables before sending

#### Step 5: Import/Export ⏳ OPTIONAL
- [ ] Add "Import HTML" button (can paste directly now)
- [ ] Add "Export Template" option
- [ ] Support drag-and-drop HTML files

## Benefits
1. **User-Friendly**: Add templates without coding
2. **No Restarts**: Changes take effect immediately
3. **Portable**: Export/Import templates between instances
4. **Maintainable**: No more hardcoded Python strings
5. **Scalable**: Easy to add hundreds of templates

## Files Modified ✅

### Backend
- ✅ `models.py` - Added `is_builtin`, `language` fields to CustomTemplate
- ✅ `routes/template_routes.py` - Updated endpoints
- ✅ `routes/campaign_routes.py` - Removed hardcoded validation
- ✅ `services/email_service.py` - Variable substitution
- ✅ `scripts/seed_templates.py` - Migration script (if exists)

### Frontend
- ✅ `components/TemplateManager.js` - Create/edit buttons added
- ✅ `components/TemplateEditor.js` - HTML code editor component
- ✅ `components/CampaignManager.js` - Loads from API only
- ✅ `api/api.js` - All needed endpoints
