# YAML Configuration Guide

This guide explains how to use YAML files for managing translations and button configurations in the Channel Rides Helper Bot.

## Overview

The bot supports two configuration methods:

1. **Environment Variables** (Default) - Traditional `.env` file configuration
2. **YAML Files** (Optional) - Structured configuration files for easier management

Both methods work together. YAML files take precedence when present, but the bot gracefully falls back to environment variables if YAML files are missing.

## Benefits of YAML Configuration

### For Translations (`config/translations.yaml`)

- ✅ **Easy Language Addition**: Add new languages without touching code
- ✅ **Centralized Management**: All translations in one well-organized file
- ✅ **Better Version Control**: Track translation changes easily in git
- ✅ **Community Contributions**: Non-developers can contribute translations
- ✅ **Validation**: YAML structure helps catch errors early

### For Buttons (`config/buttons.yaml`)

- ✅ **Clear Structure**: Organized configuration vs. flat env vars
- ✅ **Complex Configuration**: Easier to manage multiple additional buttons
- ✅ **Comments**: Add explanatory comments directly in the file
- ✅ **Type Safety**: YAML structure prevents configuration mistakes

## File Structure

```
channel_rides_helper/
├── config/
│   ├── translations.yaml        # Multi-language translations (optional)
│   └── buttons.yaml              # Button configuration (optional)
│   └── buttons.yaml.example      # Example button configuration
├── .env                          # Environment variables
└── README.md
```

## Translations Configuration

### File: `config/translations.yaml`

#### Structure

```yaml
language_code:
  buttons:
    join: "Button text"
    maybe: "Button text"
    decline: "Button text"
    voters: "Button text"
    refresh: "Button text"
  messages:
    registration_title: "Message text"
    vote_recorded: "Message text"
    refreshed: "Message text"
    voters_list_title: "Message text"
    no_votes_yet: "Message text"
    vote_required: "Message text"
    join_label: "Label text"
    maybe_label: "Label text"
    decline_label: "Label text"
    changed_mind: "Message text"
```

#### Complete Example

See the included `config/translations.yaml` file for a complete example with English and Ukrainian translations.

#### Adding a New Language

1. Open `config/translations.yaml`
2. Add a new section for your language (e.g., `de` for German, `fr` for French)
3. Copy the structure from an existing language
4. Translate all strings
5. Update `app/translations.py` to include the new language code in the `Language` type
6. Update `app/config.py` to add the language to `VALID_LANGUAGES`
7. Set `LANGUAGE=de` in `.env`

Example for Polish (`pl`):

```yaml
pl:
  buttons:
    join: "✅ Jadę"
    maybe: "❔ Może"
    decline: "❌ Nie"
    voters: "👥 Uczestnicy"
    refresh: "🔄 Odśwież"
  messages:
    registration_title: "🚴 Rejestracja"
    vote_recorded: "Twój głos został zapisany!"
    refreshed: "✅ Odświeżone!"
    voters_list_title: "👥 **Lista uczestników**"
    no_votes_yet: "_Brak głosów_"
    vote_required: "Musisz zagłosować, aby zobaczyć listę uczestników"
    join_label: "Jadę"
    maybe_label: "Może"
    decline_label: "Nie"
    changed_mind: "🔁 Zmiana zdania"
```

#### Fallback Behavior

- If `config/translations.yaml` doesn't exist → Uses hardcoded translations
- If requested language not found in YAML → Falls back to English
- If YAML is malformed → Uses hardcoded translations and logs error

## Button Configuration

### File: `config/buttons.yaml`

#### Structure

```yaml
# Button visibility
visibility:
  show_join: true/false
  show_maybe: true/false
  show_decline: true/false
  show_voters: true/false
  show_refresh: true/false

# Custom button text (overrides translations)
custom_text:
  join: "Custom text" or null
  maybe: "Custom text" or null
  decline: "Custom text" or null
  voters: "Custom text" or null
  refresh: "Custom text" or null

# Additional URL buttons
additional_buttons:
  - text: "Button Text"
    url: "https://example.com"

# Access control
access_control:
  require_vote_to_see_voters: true/false
```

#### Complete Example

See `config/buttons.yaml.example` for a complete example with explanatory comments.

#### Creating Your Configuration

1. Copy the example file:
   ```bash
   cp config/buttons.yaml.example config/buttons.yaml
   ```

2. Edit `config/buttons.yaml` with your preferences

3. The bot will automatically use it on next restart

#### Fallback Behavior

- If `config/buttons.yaml` doesn't exist → Uses environment variables
- If YAML is malformed → Uses environment variables and logs error

## Migration Guide

### From Environment Variables to YAML

#### Step 1: Create Translation File (Optional)

If you want to use YAML for translations:

1. Create `config/translations.yaml` with at least your current language
2. The bot will automatically detect and use it
3. You can keep `LANGUAGE=en` in `.env` to specify which language to use

#### Step 2: Create Button Configuration File (Optional)

If you want to use YAML for button configuration:

1. Copy `config/buttons.yaml.example` to `config/buttons.yaml`
2. Transfer your settings from `.env` to the YAML file:

   ```env
   # OLD (.env)
   BUTTON_SHOW_MAYBE=false
   BUTTON_CUSTOM_JOIN_TEXT=I'm Coming!
   ```

   ```yaml
   # NEW (config/buttons.yaml)
   visibility:
     show_maybe: false
   custom_text:
     join: "I'm Coming!"
   ```

3. You can remove button settings from `.env` (optional - they'll be ignored anyway)

#### Step 3: Test

1. Restart the bot
2. Check logs for confirmation:
   ```
   INFO | Loaded translations for languages: ['en', 'ua']
   INFO | Loaded button configuration from YAML file
   ```

### Hybrid Approach

You can mix both methods:

- ✅ Use YAML for translations, environment variables for buttons
- ✅ Use environment variables for translations, YAML for buttons
- ✅ Use one or both YAML files

The bot handles all combinations gracefully.

## Best Practices

### For Translations

1. **Keep Structure Consistent**: All languages should have the same keys
2. **Use UTF-8 Encoding**: Ensure your editor saves files as UTF-8
3. **Test Each Language**: Switch `LANGUAGE` in `.env` and test the bot
4. **Version Control**: Commit translation changes with descriptive messages
5. **Comments for Context**: Add comments explaining translation choices

### For Button Configuration

1. **Document Decisions**: Use YAML comments to explain why buttons are hidden/customized
2. **Test Configurations**: Verify at least one vote button is always visible
3. **URL Validation**: Test all additional button URLs before deploying
4. **Consistent Styling**: Keep emoji and text style consistent across buttons

### General

1. **Backup Before Editing**: Keep backups of working configurations
2. **Validate YAML**: Use a YAML validator before deploying
3. **Check Logs**: Always check bot logs after configuration changes
4. **Gradual Rollout**: Test new configurations in a test environment first

## Troubleshooting

### YAML Not Being Used

**Problem**: Bot still uses environment variables despite YAML file existing

**Solutions**:
1. Check file path: Must be `config/translations.yaml` or `config/buttons.yaml`
2. Check file permissions: File must be readable
3. Restart the bot: YAML files are loaded at startup
4. Check logs for errors: Look for YAML loading messages

### YAML Syntax Errors

**Problem**: Bot logs show YAML parsing errors

**Solutions**:
1. Validate YAML syntax: Use online YAML validators
2. Check indentation: YAML requires consistent spaces (not tabs)
3. Quote special characters: Use quotes around strings with `:` or `#`
4. Check encoding: Ensure UTF-8 encoding for Unicode characters

### Translation Not Showing

**Problem**: Translations in YAML not appearing in bot

**Solutions**:
1. Check language code in `.env`: Must match YAML key exactly
2. Verify all required keys: Both `buttons` and `messages` must be complete
3. Check for typos: Key names must match exactly
4. Restart the bot: Changes require restart

### Missing Required Keys

**Problem**: Bot crashes with `KeyError` when using YAML translations

**Solution**: Ensure all required keys are present in the YAML file. Compare with `config/translations.yaml` example.

Required keys for each language:
- **buttons**: join, maybe, decline, voters, refresh
- **messages**: registration_title, vote_recorded, refreshed, voters_list_title, no_votes_yet, vote_required, join_label, maybe_label, decline_label, changed_mind

## Examples

### Example 1: Adding German Language

Create `config/translations.yaml`:

```yaml
en:
  # ... English translations ...

ua:
  # ... Ukrainian translations ...

de:
  buttons:
    join: "✅ Dabei"
    maybe: "❔ Vielleicht"
    decline: "❌ Nein"
    voters: "👥 Teilnehmer"
    refresh: "🔄 Aktualisieren"
  messages:
    registration_title: "🚴 Anmeldung"
    vote_recorded: "Ihre Stimme wurde aufgezeichnet!"
    refreshed: "✅ Aktualisiert!"
    voters_list_title: "👥 **Teilnehmerliste**"
    no_votes_yet: "_Noch keine Stimmen_"
    vote_required: "Sie müssen zuerst abstimmen"
    join_label: "Dabei"
    maybe_label: "Vielleicht"
    decline_label: "Nein"
    changed_mind: "🔁 Meinung geändert"
```

Set in `.env`:
```env
LANGUAGE=de
```

### Example 2: Minimal Button Configuration

Create `config/buttons.yaml`:

```yaml
visibility:
  show_join: true
  show_maybe: false    # Hide "Maybe" button
  show_decline: true
  show_voters: true
  show_refresh: false  # Hide refresh button

custom_text:
  join: "🚴 I'm Riding!"
  maybe: null
  decline: "❌ Not Today"
  voters: null
  refresh: null

additional_buttons:
  - text: "📍 Route Map"
    url: "https://example.com/map"
  - text: "📋 Rules"
    url: "https://example.com/rules"

access_control:
  require_vote_to_see_voters: true  # Must vote to see list
```

### Example 3: Different Languages for Different Communities

**For English Community** (`.env`):
```env
LANGUAGE=en
```

**For Ukrainian Community** (`.env`):
```env
LANGUAGE=ua
```

**For German Community** (`.env`):
```env
LANGUAGE=de
```

All communities use the same `config/translations.yaml` with all languages defined!

## Performance Considerations

- YAML files are loaded once at bot startup (not on every request)
- Translations are cached in memory for fast access
- No performance difference between YAML and environment variables
- Adding more languages doesn't impact performance

## Support

If you encounter issues with YAML configuration:

1. Check this guide for solutions
2. Verify YAML syntax with online validators
3. Review bot logs for specific errors
4. Create an issue on GitHub with:
   - Error messages from logs
   - Your YAML file (remove sensitive data)
   - Bot version and Python version

## Contributing Translations

We welcome translation contributions!

1. Fork the repository
2. Add your language to `config/translations.yaml`
3. Test thoroughly
4. Submit a pull request with:
   - Language code and name
   - Complete translations
   - Brief test notes

Thank you for helping make the bot accessible to more communities! 🌍
