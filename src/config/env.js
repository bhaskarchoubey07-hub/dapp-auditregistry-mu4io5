/**
 * AuditRegistry - Client Environment Configuration & Validation Utility
 * Validates public browser variables prefixed with VITE_.
 * Never exposes secrets or crashes the app if optional keys are missing.
 */

const getEnv = (key, fallback = '') => {
  if (typeof import.meta !== 'undefined' && import.meta.env) {
    return import.meta.env[key] !== undefined ? String(import.meta.env[key]).trim() : fallback;
  }
  return fallback;
};

export const env = {
  // Supabase public credentials
  SUPABASE_URL: getEnv('VITE_SUPABASE_URL', ''),
  SUPABASE_ANON_KEY: getEnv('VITE_SUPABASE_ANON_KEY', ''),

  // Backend API URL
  API_URL: getEnv('VITE_API_URL', 'http://localhost:8000'),

  // Smart Contract & Network Configuration
  CONTRACT_ADDRESS: getEnv('VITE_CONTRACT_ADDRESS', '0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8'),
  EXPECTED_CHAIN_ID: getEnv('VITE_EXPECTED_CHAIN_ID', getEnv('VITE_CHAIN_ID', '11155111')),
  BLOCKCHAIN_RPC_URL: getEnv('VITE_BLOCKCHAIN_RPC_URL', 'https://rpc.sepolia.org'),

  // Derived state helpers
  hasSupabase: Boolean(
    getEnv('VITE_SUPABASE_URL', '') && 
    getEnv('VITE_SUPABASE_ANON_KEY', '') &&
    !getEnv('VITE_SUPABASE_URL', '').includes('your-project-id')
  ),
  isDev: Boolean(import.meta?.env?.DEV),
};

/**
 * Validate configuration on startup and output human-readable diagnostic status
 */
export const validateClientConfig = () => {
  const diagnostics = [];

  if (!env.CONTRACT_ADDRESS || !/^0x[0-9a-fA-F]{40}$/.test(env.CONTRACT_ADDRESS)) {
    diagnostics.push({
      level: 'warn',
      message: `Invalid or default contract address: ${env.CONTRACT_ADDRESS}. Anchoring on live testnet requires a deployed contract address.`
    });
  }

  if (!env.hasSupabase) {
    diagnostics.push({
      level: 'info',
      message: 'Supabase credentials not configured in .env. Running in resilient local storage / direct API fallback mode.'
    });
  }

  if (env.isDev) {
    console.groupCollapsed('🛡️ [AuditRegistry] Client Configuration Initialized');
    console.log('Backend API URL:', env.API_URL);
    console.log('Target Contract:', env.CONTRACT_ADDRESS);
    console.log('Expected Chain ID:', env.EXPECTED_CHAIN_ID);
    console.log('Supabase Connected:', env.hasSupabase ? 'YES' : 'FALLBACK MODE');
    diagnostics.forEach(d => {
      if (d.level === 'warn') console.warn(`⚠️ ${d.message}`);
      else console.info(`ℹ️ ${d.message}`);
    });
    console.groupEnd();
  }

  return { isValid: true, diagnostics };
};
