-- Supabase normally adds Data API table grants when tables are exposed. This
-- project has "Automatically expose new tables" disabled, so migrations must
-- grant each operation explicitly. GRANT controls whether the API role may
-- attempt an operation; the existing RLS policies continue to restrict rows to
-- their owner.

grant usage on schema public to authenticated, service_role;

-- Browser/server-component access made with the signed-in user's JWT.
-- The current UI reads devices, automation definitions, and execution history.
grant select on table
  public.devices,
  public.automations,
  public.automation_triggers,
  public.automation_conditions,
  public.automation_actions,
  public.executions,
  public.execution_logs
  to authenticated;

-- The automation editor creates the parent definition and its typed children,
-- toggles enabled, and deletes the parent (children cascade internally).
grant insert, update, delete on table public.automations to authenticated;
grant insert on table
  public.automation_triggers,
  public.automation_conditions,
  public.automation_actions
  to authenticated;

-- An authenticated user creates a short-lived pairing token. Token consumption
-- remains available only through the security-definer RPC called by service_role.
grant insert on table public.device_pairing_tokens to authenticated;

-- No current application query reads or writes profiles directly. Profile rows
-- are created by the auth.users trigger, so authenticated receives no table
-- privilege on profiles. Likewise, the browser does not need to read pairing
-- token rows after insertion.

-- Agent API routes use the server-only service role. They authenticate devices,
-- load complete automation definitions, update heartbeats, and record execution
-- state and logs. RLS remains enabled even though service_role bypasses it.
grant select, update on table public.devices to service_role;
grant select on table
  public.automations,
  public.automation_triggers,
  public.automation_conditions,
  public.automation_actions
  to service_role;
grant select, insert, update on table public.executions to service_role;
grant insert on table public.execution_logs to service_role;

grant execute on function public.consume_pairing_token(
  text, text, text, text, text, text
) to service_role;

-- RelayDesk has no unauthenticated table access. Authentication itself is
-- handled by Supabase Auth rather than public application tables.
revoke all privileges on table
  public.profiles,
  public.devices,
  public.automations,
  public.automation_triggers,
  public.automation_conditions,
  public.automation_actions,
  public.executions,
  public.execution_logs,
  public.device_pairing_tokens
  from anon;
