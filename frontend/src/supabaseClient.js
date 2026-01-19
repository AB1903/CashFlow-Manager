import { createClient } from '@supabase/supabase-js';

// Use environment variables for production deployment
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || 'https://jvlbxzhqzfaxvneqcyiy.supabase.co';
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2bGJ4emhxemZheHZuZXFjeWl5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg1ODA5MjIsImV4cCI6MjA4NDE1NjkyMn0.JSqJjO6N14kAN9L06mIN8nj5EtCysCyIw4HfgUORsxc';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);