# Coolify CLI Command Reference

## Table of Contents
- [Global Flags](#global-flags)
- [Context Management](#context-management)
- [Server Management](#server-management)
- [Projects](#projects)
- [Resources](#resources)
- [Application Management](#application-management)
- [Database Management](#database-management)
- [Service Management](#service-management)
- [Deployment Management](#deployment-management)
- [GitHub Apps Integration](#github-apps-integration)
- [Team Management](#team-management)
- [Private Key Management](#private-key-management)
- [Utility Commands](#utility-commands)

## Global Flags

All commands accept:

| Flag | Description |
|------|-------------|
| `--context <name>` | Override default context |
| `--host <fqdn>` | Override hostname |
| `--token <token>` | Override auth token |
| `--format <format>` | Output: `table` (default), `json`, `pretty` |
| `-s, --show-sensitive` | Show tokens, IPs, sensitive data |
| `-f, --force` | Skip confirmations |
| `--debug` | Enable debug output |

## Context Management

```
coolify context list                              # List all contexts
coolify context get <name>                        # Get context details
coolify context add <name> <url> <token>          # Add context (-d default, -f force)
coolify context delete <name>                     # Remove context
coolify context set-token <name> <token>          # Update token
coolify context set-default <name>                # Set default context
coolify context use <name>                        # Switch to context
coolify context update <name>                     # Update (--name, --url, --token)
coolify context verify                            # Test connection/auth
coolify context version                           # Get API version
```

## Server Management

Aliases: `server`, `servers`

```
coolify server list                               # List all servers
coolify server get <uuid> [--resources]           # Get server details
coolify server add <name> <ip> <key_uuid>         # Add server (-p port, -u user, --validate)
coolify server remove <uuid>                      # Delete server
coolify server validate <uuid>                    # Test connectivity
coolify server domains <uuid>                     # List domains
```

## Projects

```
coolify projects list                             # List projects
coolify projects get <uuid>                       # Get project environments
```

## Resources

```
coolify resources list                            # List all resources
```

## Application Management

### Basic Operations

```
coolify app list                                  # List applications
coolify app get <uuid>                            # Get app details
coolify app delete <uuid> [-f]                    # Delete application
coolify app start <uuid>                          # Start app
coolify app stop <uuid>                           # Stop app
coolify app restart <uuid>                        # Restart app
coolify app logs <uuid>                           # Get app logs
```

### App Update Flags

```
coolify app update <uuid>
  --name <name>                    # App identifier
  --description <desc>             # Description
  --git-branch <branch>            # Git branch
  --git-repository <url>           # Git repo URL
  --domains <domains>              # Comma-separated domains
  --build-command <cmd>            # Build command
  --start-command <cmd>            # Start command
  --install-command <cmd>          # Install command
  --base-directory <path>          # Working directory
  --publish-directory <path>       # Output directory
  --dockerfile <content>           # Dockerfile content
  --docker-image <image>           # Docker image
  --docker-tag <tag>               # Image tag
  --ports-exposes <ports>          # Exposed ports
  --ports-mappings <mappings>      # Port mappings
  --health-check-enabled           # Enable health checks
  --health-check-path <path>       # Health check endpoint
```

### Environment Variables

```
coolify app env list <app_uuid>                   # List env vars
coolify app env get <app_uuid> <env_uuid_or_key>  # Get env var
coolify app env create <app_uuid>                 # Create env var
  --key <key> --value <value>                     # Required
  --preview --build-time --is-literal --is-multiline  # Optional flags
coolify app env update <app_uuid> <env_uuid>      # Update env var
coolify app env delete <app_uuid> <env_uuid>      # Delete env var
coolify app env sync <app_uuid>                   # Sync from .env file
  --file <path>                                   # Required
  --build-time --preview --is-literal             # Optional flags
```

### Deployments

```
coolify app deployments list <app_uuid>           # Deployment history
coolify app deployments logs <app_uuid> [deploy_uuid]
  -n, --lines <n>                                 # Line count (0=all)
  -f, --follow                                    # Stream output
  --debuglogs                                     # Include debug info
```

## Database Management

### Basic Operations

```
coolify database list                             # List databases
coolify database get <uuid>                       # Get details
coolify database start <uuid>                     # Start database
coolify database stop <uuid>                      # Stop database
coolify database restart <uuid>                   # Restart database
coolify database delete <uuid>                    # Delete database
  --delete-configurations                         # Remove configs (default: true)
  --delete-volumes                                # Remove data (default: true)
  --docker-cleanup                                # Run cleanup (default: true)
  --delete-connected-networks                     # Remove networks (default: true)
```

### Create Database

Supported types: `postgresql`, `mysql`, `mariadb`, `mongodb`, `redis`, `keydb`, `clickhouse`, `dragonfly`

```
coolify database create <type>
  --server-uuid <uuid>             # Required
  --project-uuid <uuid>            # Required
  --environment-name <name>        # Required (or --environment-uuid)
  --environment-uuid <uuid>        # Required (or --environment-name)
  --destination-uuid <uuid>        # For multi-destination servers
  --name <name>                    # Database name
  --description <desc>             # Description
  --image <image>                  # Docker image
  --instant-deploy                 # Deploy immediately
  --is-public                      # Enable public access
  --public-port <port>             # Public port
  --limits-memory <size>           # Memory limit (e.g. 512m, 2g)
  --limits-cpus <cpus>             # CPU limit (e.g. 0.5, 2)
```

### Database Update

```
coolify database update <uuid>                    # Same flags as create
```

### Backup Management

```
coolify database backup list <db_uuid>            # List backup configs
coolify database backup create <db_uuid>          # Create backup config
  --frequency <cron>               # Cron schedule
  --enabled                        # Activate schedule
  --save-s3                        # Store in S3
  --s3-storage-uuid <uuid>         # S3 destination
  --databases-to-backup <list>     # Comma-separated DBs
  --dump-all                       # Backup all DBs
  --retention-amount-local <n>     # Local backup count
  --retention-days-local <n>       # Local backup age (days)
  --retention-storage-local <size> # Local storage limit (e.g. 1GB)
  --retention-amount-s3 <n>        # S3 backup count
  --retention-days-s3 <n>          # S3 backup age (days)
  --retention-storage-s3 <size>    # S3 storage limit
  --timeout <seconds>              # Operation timeout
  --disable-local                  # Disable local storage

coolify database backup update <db_uuid> <backup_uuid>      # Update config
coolify database backup delete <db_uuid> <backup_uuid>      # Delete config
coolify database backup trigger <db_uuid> <backup_uuid>     # Run backup now
coolify database backup executions <db_uuid> <backup_uuid>  # Execution history
coolify database backup delete-execution <db_uuid> <backup_uuid> <exec_uuid>
```

## Service Management

```
coolify service list                              # List services
coolify service get <uuid>                        # Get details
coolify service start <uuid>                      # Start service
coolify service stop <uuid>                       # Stop service
coolify service restart <uuid>                    # Restart service
coolify service delete <uuid>                     # Delete service
```

### Service Environment Variables

Same interface as application env vars:

```
coolify service env list <svc_uuid>
coolify service env get <svc_uuid> <env_uuid_or_key>
coolify service env create <svc_uuid> --key <k> --value <v> [--preview --build-time --is-literal --is-multiline]
coolify service env update <svc_uuid> <env_uuid>
coolify service env delete <svc_uuid> <env_uuid>
coolify service env sync <svc_uuid> --file <path> [--build-time --preview --is-literal]
```

## Deployment Management

```
coolify deploy uuid <uuid> [-f]                   # Deploy by UUID
coolify deploy name <name> [-f]                   # Deploy by name
coolify deploy batch <name1,name2,...> [-f]        # Batch deploy
coolify deploy list                               # List deployments
coolify deploy get <uuid>                         # Get deployment details
coolify deploy cancel <uuid> [-f]                 # Cancel deployment
```

## GitHub Apps Integration

```
coolify github list                               # List integrations
coolify github get <app_uuid>                     # Get details
coolify github create                             # Create integration
  --name <name>                    # Required
  --api-url <url>                  # Required (e.g. https://api.github.com)
  --html-url <url>                 # Required (e.g. https://github.com)
  --app-id <id>                    # Required
  --installation-id <id>           # Required
  --client-id <id>                 # Required
  --client-secret <secret>         # Required
  --private-key-uuid <uuid>        # Required
  --organization <org>             # Optional
  --custom-user <user>             # Default: git
  --custom-port <port>             # Default: 22
  --webhook-secret <secret>        # Optional
  --system-wide                    # Cloud-only

coolify github update <app_uuid>                  # Update (same flags)
coolify github delete <app_uuid> [-f]             # Delete integration
coolify github repos <app_uuid>                   # List repos
coolify github branches <app_uuid> <owner/repo>   # List branches
```

## Team Management

```
coolify team list                                 # List teams
coolify team get <team_id>                        # Get team info
coolify team current                              # Show current team
coolify team members list [team_id]               # List members
```

## Private Key Management

Aliases: `private-key`, `private-keys`, `key`, `keys`

```
coolify private-key list                          # List keys
coolify private-key add <name> <private-key>      # Add key (@filename to read from file)
coolify private-key remove <uuid>                 # Delete key
```

## Utility Commands

```
coolify update                                    # Upgrade CLI
coolify config                                    # Show config file location
coolify completion <shell>                        # Generate completions (bash/zsh/fish/powershell)
```
