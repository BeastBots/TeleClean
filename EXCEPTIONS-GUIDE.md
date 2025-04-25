# Configuring Exceptions in TeleClean Bot

## Environment Variable Format

For the `EXCEPTIONS` environment variable, use a comma-separated list of IDs without spaces:

```
EXCEPTIONS=12345,67890,-1001234567890,98765
```

## Types of IDs You Can Include

1. **User IDs** - Positive integers (e.g., `12345`)
2. **Bot IDs** - Positive integers, same format as users (e.g., `5273782385`)
3. **Channel IDs** - Negative integers starting with `-100` (e.g., `-1001234567890`)

## Setting Environment Variables

### In PowerShell (for local testing):

```powershell
$env:EXCEPTIONS = "12345,67890,-1001234567890,98765"
```

### In Bash (Linux or macOS):

```bash
export EXCEPTIONS="12345,67890,-1001234567890,98765"
```

### In GitHub Actions (in .github/workflows/teleclean.yml):

```yaml
env:
  EXCEPTIONS: ${{ secrets.EXCEPTIONS || '12345,67890,-1001234567890,98765' }}
```

## Finding IDs

1. **For User/Bot IDs:** Send a message to @userinfobot on Telegram
2. **For Channel IDs:** 
   - Forward a message from the channel to @userinfobot
   - Channel IDs typically start with `-100` followed by numbers

## Example with Different Types of IDs:

```
EXCEPTIONS=12345,98765,87654321,-1001234567890
```

This would exempt:
- User with ID 12345
- User (or bot) with ID 98765
- User (or bot) with ID 87654321
- Channel with ID -1001234567890

## Testing Configuration

To verify that your exceptions are working correctly:

1. Run the bot in dry-run mode:
   ```powershell
   $env:DRY_RUN = "True"
   $env:EXCEPTIONS = "12345,67890,98765,-1001234567890"
   python main.py
   ```

2. Check the bot logs - it will show which messages would have been deleted vs. which ones were exempted
