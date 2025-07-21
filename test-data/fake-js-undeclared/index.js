const express = require('express');
const _ = require('lodash');

// These imports are NOT declared in package.json - potential dependency confusion targets
const fakeUtilPackage = require('company-internal-utils');
const missingHelpers = require('undeclared-helpers');
import { someFunction } from 'another-missing-package';

// Dynamic import also undeclared
const dynamicPkg = await import('dynamic-missing-lib');

const app = express();

app.get('/', (req, res) => {
  const data = fakeUtilPackage.processData(req.query);
  const result = missingHelpers.format(data);
  res.json(result);
});

app.listen(3000); 