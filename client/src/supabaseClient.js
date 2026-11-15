import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://xrmasjdsgwbglhksmcgx.supabase.co';
const supabaseAnonKey = 'sb_publishable_IQfjnQHluaB-Bv5xBurfDA_ooChSnrt';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
