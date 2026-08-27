import { createBrowserClient, createServerClient } from "@supabase/ssr";
import { createClient } from "@supabase/supabase-js";
import { cookies } from "next/headers";
const url=process.env.NEXT_PUBLIC_SUPABASE_URL!; const anon=process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
export const browserClient=()=>createBrowserClient(url,anon);
export async function serverClient(){ const store=await cookies(); return createServerClient(url,anon,{cookies:{getAll:()=>store.getAll(),setAll(items){try{items.forEach(({name,value,options})=>store.set(name,value,options));}catch{}}}}); }
export const adminClient=()=>createClient(url,process.env.SUPABASE_SERVICE_ROLE_KEY!,{auth:{persistSession:false,autoRefreshToken:false}});
