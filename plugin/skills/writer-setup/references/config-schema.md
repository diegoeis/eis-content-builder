# Canonical config schema (`.local.json`)

> **Used by:** writer-setup Step 4.2 (writes this), every other skill (reads it).

Every field is present after a successful setup. Nulls are allowed for unknown values.

```json
{
  "workspace_path": "{workspace_path}",
  "initialized_at": "YYYY-MM-DD",
  "version": "0.6.0",

  "author": {
    "first_name": "{first_name_slug}",
    "full_name": "{full name or null}"
  },

  "language": {
    "default": "pt-BR",
    "technical_terms_in": "en"
  },

  "channels": {
    "blog": {
      "url": "https://...",
      "cms": "ghost|wordpress|obsidian|custom|none|null",
      "publish_via": "manual|api",
      "has_template": true,
      "materialized": false,
      "template_customizations": {
        "target_length_words": [800, 1300],
        "formatting_notes_addition": null,
        "anti_pattern_additions": [],
        "rationale": "Median word count across blog samples: 1050"
      }
    },
    "newsletter": {
      "shares_url_with": "blog",
      "platform": "ghost",
      "has_template": true,
      "materialized": false,
      "template_customizations": null
    },
    "linkedin": {
      "profile_url": "https://...",
      "posting_tool": "manual",
      "has_template": true,
      "materialized": false,
      "template_customizations": null
    },
    "twitter": {
      "active": true,
      "has_template": true,
      "materialized": false,
      "template_customizations": null
    },
    "youtube": {
      "active": true,
      "has_template": false,
      "materialized": false,
      "template_customizations": null
    },
    "medium": {
      "active": true,
      "has_template": false,
      "materialized": false,
      "template_customizations": null
    }
  },

  "research_sources": {
    "trusted_blogs": [],
    "rss_feeds": [],
    "people_to_watch": [],
    "avoid_sources": []
  },

  "article_archive": {
    "enabled": true,
    "path": "/abs/path",
    "file_pattern": "**/*.md",
    "toolchain": "obsidian|generic",
    "schema": {
      "title_property": "title",
      "tags_property": "tags",
      "status_property": "status",
      "published_values": ["published"],
      "date_property": "date",
      "url_property": "permalink",
      "excerpt_property": "excerpt"
    },
    "index_file": {
      "path": null,
      "format": null
    }
  },

  "save_preferences": [],

  "ideation": {
    "exclude_themes": [],
    "preferred_angles": [],
    "default_channel": "blog"
  }
}
```

If archive was declined or failed: set `article_archive.enabled: false` and leave the other archive fields at defaults.
