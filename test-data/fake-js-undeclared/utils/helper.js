// More undeclared imports in a utility file
const secretConfig = require('@company/secret-config');
const internalApi = require('internal-api-client');
import { validator } from 'custom-validator-lib';

export function processRequest(data) {
  const config = secretConfig.load();
  const client = new internalApi.Client(config.apiUrl);
  
  if (!validator.isValid(data)) {
    throw new Error('Invalid data');
  }
  
  return client.send(data);
} 