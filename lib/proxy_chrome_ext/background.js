const PROXY_HOST = '185.199.229.156'
const PROXY_PORT = 7492 
const PROXY_USER = 'rvwktmbh'
const PROXY_PASS = '5rck2oqqfca6'

var config = {
    mode: "fixed_servers",
    rules: {
    singleProxy: {
        scheme: "http",
        host: PROXY_HOST,
        port: parseInt(PROXY_PORT)
    },
    bypassList: ["localhost"]
    }
};

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
return {
    authCredentials: {
        username: PROXY_USER,
        password: PROXY_PASS
    }
};
}

chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {urls: ["<all_urls>"]},
        ['blocking']
);