// Test file for demonstrating publishing of non-test packages
// These imports don't exist and aren't in our test manifest

const superReactHelper = require('super-react-helper');  // Should be publishable (deleted package)
import awesomeUtils from 'awesome-frontend-utils';  // Should be publishable
import('demo-dynamic-package');  // Should be publishable
const neverExisted = require('totally-new-package-never-existed-12345'); // Should be publishable (never existed)
const brandNewPackage = require('brand-new-test-package-2025'); // Should be publishable (never existed)

console.log("This is just a demo file for testing dependency scanning and publishing"); 