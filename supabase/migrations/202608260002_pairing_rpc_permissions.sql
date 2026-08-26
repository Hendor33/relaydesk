-- The pairing endpoint invokes this RPC with the server-only service role.
-- PUBLIC remains revoked so browser clients cannot consume arbitrary token hashes.
grant execute on function public.consume_pairing_token(text, text, text, text, text, text) to service_role;
