# Import Command Examples

The `import` command allows you to quickly import environment variables from existing 1Password items into your project.

## Basic Usage

```bash
# Import all fields from an item named 'my-app' in the default 'tokens' vault
1pass-env import --name my-app
```

This creates a `1pass.env` file with all the fields from the 1Password item.

## Advanced Examples

### Import Specific Fields
```bash
# Only import API_KEY and DATABASE_URL
1pass-env import --name my-app --fields API_KEY,DATABASE_URL
```

### Use Different Vault
```bash
# Import from 'production-secrets' vault
1pass-env import --vault production-secrets --name my-app
```

### Custom Output File
```bash
# Save to .env.production instead of 1pass.env
1pass-env import --name my-app --file .env.production
```

### Debug Mode
```bash
# Show detailed logs and actual values (be careful!)
1pass-env import --name my-app --debug
```

### Automatic Item Name
```bash
# If your folder is named 'my-awesome-project', this will look for an item with the same name
cd my-awesome-project
1pass-env import  # Uses 'my-awesome-project' as item name
```

## Workflow Examples

### Development Setup
```bash
# 1. Import development secrets
1pass-env import --vault dev-secrets --name my-app --file .env.dev

# 2. Run your app with development environment
1pass-env run --file .env.dev npm start
```

### Production Deployment
```bash
# 1. Import production secrets
1pass-env import --vault prod-secrets --name my-app --file .env.prod

# 2. Deploy with production environment
1pass-env run --file .env.prod docker-compose up -d
```

### Multi-Environment Setup
```bash
# Import from different environments
1pass-env import --vault dev-secrets --name my-app --file .env.development
1pass-env import --vault staging-secrets --name my-app --file .env.staging  
1pass-env import --vault prod-secrets --name my-app --file .env.production

# Use environment-specific files
1pass-env run --file .env.development npm run dev
1pass-env run --file .env.staging npm run test:e2e
1pass-env run --file .env.production npm run build
```

## File Safety

The import command includes built-in safety features:

1. **File Existence Check**: If the target file already exists, you'll be prompted for confirmation
2. **Merge Mode**: Existing variables are preserved, imported variables take precedence
3. **Value Masking**: By default, values are masked in output for security
4. **Backup Recommendation**: Always backup important files before importing

## Tips and Best Practices

### Organizing 1Password Items

Structure your 1Password items to match your projects:

```
Vault: tokens
├── my-web-app          # Contains: API_KEY, DB_PASSWORD, JWT_SECRET
├── my-mobile-app       # Contains: API_KEY, PUSH_TOKEN, ANALYTICS_KEY
└── shared-services     # Contains: REDIS_URL, SMTP_PASSWORD
```

### Field Naming Conventions

Use consistent field names across your 1Password items:
- `API_KEY` instead of `api-key` or `ApiKey`
- `DATABASE_URL` instead of `db_url` or `DatabaseURL`
- `JWT_SECRET` instead of `jwt_token` or `JwtSecret`

### Security Considerations

1. **Use `--debug` carefully**: Only use debug mode in secure environments
2. **File permissions**: Set appropriate permissions on generated files:
   ```bash
   chmod 600 1pass.env  # Only readable by owner
   ```
3. **Git ignore**: Add environment files to `.gitignore`:
   ```
   .env*
   1pass.env*
   *.env
   ```

### Troubleshooting

#### Item Not Found
```bash
# Check available items in vault
1pass-env check --vault tokens

# List all vaults
1pass-env check
```

#### Authentication Issues
```bash
# Test your setup
1pass-env check --vault tokens

# Verify token is set
echo $OP_SERVICE_ACCOUNT_TOKEN
```

#### Field Not Found
```bash
# Import with debug to see all available fields
1pass-env import --name my-app --debug

# Then import specific fields
1pass-env import --name my-app --fields FIELD_NAME_1,FIELD_NAME_2
```
