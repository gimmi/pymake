/* jshint phantom: true */
/* global jsApiReporter */

'use strict';

var args = require('system').args,
	page = require('webpage').create();

if (args.length < 2) {
	console.log('Usage:', args[0], 'htmlPath');
	phantom.exit(1);
}

var htmlUrl = 'file:///' + args[1].replace(/\\/g, '/');
console.log('Running all Jasmine specs at URL', htmlUrl);
page.open(htmlUrl);

var checkLoop = function () {
	var jasmineStatus = page.evaluate(function () { return jsApiReporter.status(); });
	if (jasmineStatus === 'done') {
		var jasmineTotalSpecs = page.evaluate(function () { return jsApiReporter.specs(); });
		var jasmineFailedSpecs = jasmineTotalSpecs.filter(function (spec) { return spec.status !== 'passed'; });
		console.log(jasmineTotalSpecs.length, 'specs executed,', jasmineFailedSpecs.length, 'failed.');
		phantom.exit(jasmineFailedSpecs.length);
	}
	setInterval(checkLoop, 100);
};

page.onLoadFinished = function (status) {
	if (status !== 'success') {
		console.log('Unable to access network');
		phantom.exit(1);
	}
	checkLoop();
};

// page.onResourceRequested = function(requestData, networkRequest) {
//   console.log('INFO: requesting ', requestData.url);
// };

page.onResourceError = function (resourceError) {
	console.log('WARN: Unable to load ', resourceError.url, ':', resourceError.errorString);
};

page.onError = function(msg, trace) {
	console.log('ERROR:', msg);
	phantom.exit(1);
};
