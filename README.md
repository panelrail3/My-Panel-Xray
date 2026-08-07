# Railway XPanel 1.0.0 — Final MVP

A Railway-oriented VLESS/Xray management panel built with FastAPI + Vue 3.

## Included

- Admin authentication (JWT + Argon2)
- User management and UUID generation
- Inbound management
- Xray config generation and validation
- Xray process manager
- Xray StatsService integration
- Per-user uplink/downlink accounting
- Inbound/outbound traffic accounting
- Subscription tokens
- VLESS URI generation
- QR PNG endpoint
- Railway Public Domain detection
- Railway TCP Proxy detection
- Railway volume detection
- Config backups
- Docker build
- Railway healthcheck
- SQLite persistence
- Alembic project structure
- Compatibility validation for RAW/XHTTP/WebSocket/gRPC and TLS/REALITY

## Xray facts used by this release

The current Xray documentation defines `streamSettings.method` for transport methods
and allows REALITY with RAW, XHTTP and gRPC, but not WebSocket or HTTPUpgrade.
The generator follows that compatibility matrix.

Traffic accounting uses Xray's `stats` plus policy-level user statistics and the
local StatsService. User statistics require an `email`, which this project maps to
the panel username.

## Railway networking caveat

Railway Public Networking is HTTP/HTTPS ingress. Railway terminates the public TLS
connection before forwarding the HTTP request to the container. Therefore the panel
does not falsely label a Public-Networking subscription as end-to-end Xray TLS.

For end-to-end VLESS TLS/REALITY, use Railway TCP Proxy or a VPS where Xray itself
terminates TLS/REALITY.

TCP Proxy values are read from:
- RAILWAY_TCP_PROXY_DOMAIN
- RAILWAY_TCP_PROXY_PORT
- RAILWAY_TCP_APPLICATION_PORT

## Deploy

1. Push the repository to GitHub.
2. Create a Railway service from the repository.
3. Add one Railway Volume mounted at `/data`.
4. Generate a Public Domain.
5. Set:
   - SECRET_KEY
   - ADMIN_USERNAME
   - ADMIN_PASSWORD
6. Deploy.
7. Login.
8. If TCP Proxy is required, enable it in the Railway service networking settings.
9. Create an inbound and users, then call `/api/xray/rebuild`.

## Important production hardening

- Use a long random SECRET_KEY.
- Change ADMIN_PASSWORD before exposing the service.
- Keep Xray's API on 127.0.0.1 only.
- Keep one replica when using SQLite + a single Railway Volume.
- Test the generated Xray configuration before enabling clients.
- The included Xray version is pinned in Dockerfile; verify the chosen release against
  the exact schema you intend to deploy before production.
