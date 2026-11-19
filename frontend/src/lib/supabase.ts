import { createClient } from "@supabase/supabase-js";

// These are public browser credentials (project URL + publishable key).
// Never place a Supabase service_role or secret key in frontend code.
const supabaseUrl = (import.meta.env.VITE_SUPABASE_URL as string | undefined) || "https://rdgeiolxvbojassxhezh.supabase.co";
const supabaseAnonKey = (import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined) || "sb_publishable_iqzUL5eiPT7AZ63tMYsyLg_fvYBLhgK";

export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey);
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true },
});
