    function getUrlVar(key) {
    	let result = new RegExp(key + "=([^&]*)", "i").exec(window.location.search);
    	return result && unescape(result[1]) || "";
    }