---
name: coolify-cli
description: Manage Coolify infrastructure using the Coolify CLI (v4.x). Use when the user wants to deploy, manage, or configure applications, databases, services, servers, or deployments on Coolify. Triggers on requests involving Coolify commands, self-hosted PaaS management, or any mention of the coolify CLI tool. Covers context management, server setup, app lifecycle, database provisioning/backups, service management, batch deployments, GitHub integration, team/key management, and environment variable sync.
---

# Coolify CLI

Operate Coolify infrastructure from the command line. Covers the full v4.x CLI surface: contexts, servers, apps, databases, services, deployments, GitHub integrations, teams, and private keys.

## Setup

1. Install: `curl -fsSL https://raw.githubusercontent.com/coollabsio/coolify-cli/main/scripts/install.sh | bash`
2. Get API token from Coolify dashboard at `/security/api-tokens`
3. Configure:
   - Cloud: `coolify context set-token cloud <token>`
   - Self-hosted: `coolify context add -d <name> <url> <token>`
4. Verify: `coolify context verify`

## Quick Patterns

**Multi-context workflow:**
```
coolify context add prod https://prod.coolify.io <token> -d
coolify context add staging https://staging.coolify.io <token>
coolify --context=staging server list
coolify --context=prod deploy name api
```

**App lifecycle:**
```
coolify app list
coolify app start <uuid>
coolify app env sync <uuid> --file .env
coolify app logs <uuid>
coolify deploy name my-app
```

**Database with automated backups:**
```
coolify database create postgresql --server-uuid <s> --project-uuid <p> --environment-name production --name mydb --instant-deploy
coolify database backup create <db-uuid> --frequency "0 2 * * *" --enabled --save-s3 --s3-storage-uuid <s3>
```

**Batch deploy:**
```
coolify deploy batch api,worker,frontend --force
```

## Output Formats

All commands accept `--format`: `table` (default), `json` (scripting), `pretty` (debugging).

## Full Command Reference

See [references/commands.md](references/commands.md) for the complete command catalog with all flags and options.
