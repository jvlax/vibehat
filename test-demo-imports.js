// Test file for demonstrating publishing of non-test packages
// These imports don't exist and aren't in our test manifest

const superReactHelper = require('super-react-helper');  // Should be publishable
import awesomeUtils from 'awesome-frontend-utils';  // Should be publishable
import('demo-dynamic-package');  // Should be publishable

console.log("This is just a demo file for testing dependency scanning and publishing"); 