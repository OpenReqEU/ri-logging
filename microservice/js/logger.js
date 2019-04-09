/*TODO: Make cookie permanent for the duration of the stay on the website*/
/**
 *  @file         openreq-logger.js
 *  @overview     This Vanilla JS library captures and logs events (user interaction).
 *  @version      0.9
 *  @author       Volodymyr Biryuk <4biryuk@informatik.uni-hamburg.de>
 *
 */
"use strict";
const endpoint_url = "https://api.openreq.eu/ri-logging/frontend/log";

/***** SESSION MANAGEMENT *****/

/**
 * Generate a session id as random alphanumeric string.
 * @returns {string}
 */
function generateSessionId() {
    let length = 20;
    let sessionId = "";
    let possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (let i = 0; i < length; i++) {
        sessionId += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return sessionId;
}


/**
 * Set a browser cookie.
 * @param cname Cookie name.
 * @param cvalue Cookie value.
 * @param exmills Expiration time in milliseconds.
 */
function setCookie(cname, cvalue, exmills) {
    let d = new Date();
    d.setTime(d.getTime() + exmills);
    let expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

/**
 * Return a browser cookie.
 * @param {string} cname Cookie name.
 * @returns {string} The cookie value.
 */
function getCookie(cname) {
    let name = cname + "=";
    let ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}


/**
 * Set session id cookies if expired, reset expiry time if not.
 */
function refreshSessionId() {
    let timestamp = Date.now();
    let cookieExpieryTime = (1000 * 60 * 5);
    let sessionId = getCookie("sessionId");
    let isCookieExpired = (sessionId === "");
    if (isCookieExpired) {
        // If cookie is expired generate a new one with new session id.
        setCookie("sessionId", generateSessionId(), cookieExpieryTime);
        setCookie("timestamp", timestamp, cookieExpieryTime);
    } else {
        // If cookie is not expired set new cookie with same value but extended expiry time.
        setCookie("sessionId", sessionId, cookieExpieryTime);
        setCookie("timestamp", timestamp, cookieExpieryTime);
    }
}

/***** SESSION MANAGEMENT END *****/


/***** REQUEST MANAGEMENT *****/

/**
 * Send a HTTP POST request.
 * @param {string} url The full URL.
 * @param {JSON} body Request body as JSON.
 * @param {Array} headerProperties Request header properties to be added to the default header.
 */
function post(url, body, headerProperties) {
    let xhr = new XMLHttpRequest();
    xhr.open('POST', url);
    for (let key in headerProperties) {
        xhr.setRequestHeader(key, headerProperties[key]);
    }
    xhr.onload = function () {
        if (xhr.status === 200) {
            console.log(xhr.status);
        } else {
            console.log(xhr.status);
        }
    };
    xhr.send(body);
}

/***** REQUEST MANAGEMENT END *****/

/**
 * Convert an event object to a simplified representation.
 * @param {Event} object Event object
 */
function simplifyObject(object) {
    let objectJson = {
        "screenX": object["screenX"],
        "screenY": object["screenY"],
        "clientX": object["clientX"],
        "clientY": object["clientY"],
        "x": object["x"],
        "y": object["y"],
        "offsetX": object["offsetX"],
        "offsetY": object["offsetY"],
        "movementX": object["movementX"],
        "movementY": object["movementY"],
        "layerX": object["layerX"],
        "layerY": object["layerY"],
        "type": object["type"],
        "timeStamp": object["timeStamp"],
        "offsetTop": object["target"]["offsetTop"],
        "offsetLeft": object["target"]["offsetLeft"],
        "offsetWidth": object["target"]["offsetWidth"],
        "offsetHeight": object["target"]["offsetHeight"],
        "innerText": object["target"]["innerText"],
        "outerText": object["target"]["outerText"],
        "scrollTop": object["target"]["scrollTop"],
        "scrollLeft": object["target"]["scrollLeft"],
        "scrollWidth": object["target"]["scrollWidth"],
        "scrollHeight": object["target"]["scrollHeight"],
        "clientTop": object["target"]["clientTop"],
        "clientLeft": object["target"]["clientLeft"],
        "clientWidth": object["target"]["clientWidth"],
        "clientHeight": object["target"]["clientHeight"],
        "value": object["target"]["value"],
        "srcElementclassName": object["srcElement"]["className"],
        "srcElementId": object["srcElement"]["id"],
        "targetclassName": object["target"]["className"],
        "targetId": object["target"]["id"]
    };

    // for (let propertyName in object) {
    //     let propertyValue = object[propertyName];
    //     let propertyType = typeof (propertyValue);
    //     if (!(propertyType == "object")) {
    //         objectJson[propertyName] = propertyValue;
    //     }
    //     else if (propertyName == "target") {
    //         objectJson[propertyName] = simplifyObject(propertyValue);
    //     }
    //     else if (propertyName == "srcElement") {
    //         objectJson[propertyName] = simplifyObject(propertyValue);
    //     }

    // Include this if ncecessary, it increases the log size dramatically
    // else if (propertyName == "path") {
    //     let elementPath = {};
    //     for(let p in propertyValue){
    //         let v = propertyValue[p];
    //         elementPath[p] = simplifyObject(v);
    //     }
    //     objectJson[propertyName] = elementPath;
    // }
    // }

    return objectJson;
}

/**
 * Enhance the event with metadata like timestamps and the current url.
 * @param event The event object
 * @returns {*}
 */
function addMetadata(event) {
    event['url'] = window.location.href;
    let d = new Date();
    event['isoTime'] = d;
    event['unixTime'] = Math.floor(d.getTime() / 1000);
    let currentUrl = window.location.href;
    console.log(currentUrl);
    event['projectId'] = currentUrl.split('/')[5];
    event['username'] = document.querySelector(".or-avatar").getAttribute("alt");
    return event;
}

/**
 * Log an Event.
 * @param {Event} event The Event to log
 */
function log(event) {
    console.log(event);
    // let requirementSpecificInformation = getRequirementSpecificInformation(event);
    let simplifiedEvent = simplifyObject(event);
    let enhancedEvent = addMetadata(simplifiedEvent);
    enhancedEvent['requirementId'] = getRequirementId(event);
    let eventJson = JSON.stringify(enhancedEvent);
    send_log(eventJson);
}

/**
 * Get the requirement id from the parent elemnt of the event triggering element.
 * @param {Event} event
 */
function getRequirementId(event) {
    let requirementId = "";
    if (event.target.className.startsWith("or-requirement-title")) {
        requirementId = event.target.parentNode.parentNode.getAttribute("data-id");
    } else if (event.target.className.startsWith("note-editable")) {
        requirementId = event.target.parentNode.parentNode.parentNode.parentNode.getAttribute("data-id");
    } else if (event.target.className.startsWith("or-requirement-status-field")) {
        requirementId = event.target.parentNode.parentNode.parentNode.getAttribute("data-id");
    }
    console.log(requirementId);
    return requirementId;
}

// function getRequirementSpecificInformation(event) {
//     let typeSpecificData = {};
//     let requirementId = "";
//     if (event.target.className.startsWith("or-requirement-title")) {
//         requirementId = event.target.parentNode.parentNode.getAttribute("data-id");
//         typeSpecificData['requirementId'] = requirementId;
//         typeSpecificData['value'] = event.target.innerText;
//     }
//     else if (event.target.className.startsWith("note-editable")) {
//         requirementId = event.target.parentNode.parentNode.parentNode.parentNode.getAttribute("data-id");
//         typeSpecificData['requirementId'] = requirementId;
//         typeSpecificData['value'] = event.target.innerText;
//     }
//     else if (event.target.className.startsWith("or-requirement-status-field")) {
//         requirementId = event.target.parentNode.parentNode.parentNode.getAttribute("data-id");
//         typeSpecificData['requirementId'] = requirementId;
//         typeSpecificData['value'] = event.target.value;
//     }
//     console.log(typeSpecificData);
//     return typeSpecificData;
// }

/**
 * Send log with al necessary data.
 * @param {JSON} log The information to log.
 */
function send_log(log) {
    let url = endpoint_url;
    let sessionId = getCookie("sessionId");
    let header = {"sessionId": sessionId, "Content-Type": "application/json"};
    post(url, log, header);
}

/**
 * Delay function execution.
 */
var delay = (function () {
    let timer = 0;
    return function (callback, ms) {
        clearTimeout(timer);
        timer = setTimeout(callback, ms);
    }
})();

/**
 * Create an event handler.
 * @param event the Event to handel.
 */
let logHandler = function (event) {
    // reset the cookie when the user is interacting with the UI
    refreshSessionId();
    // Delayed trigger, the log event is triggered 2000ms after the chain of input events stops.
    if (event["type"] === "input") {
        delay(function () {
            log(event);
        }, 2000);
    }
    // else if (event["type"] === "mousemove") {
    //     delay(function () {
    //         log(event);
    //     }, 100);
    // }
    else {
        log(event);
    }
};

/**
 * Load event listeners on load
 */
// let eventsToLog = ["click", "input", "mouseover"];
// let eventsToLog = ["mousedown", "mouseup", "input", "mouseover"];
// let eventsToLog = ["input", "mouseover"];
// let eventsToLog = ["click", "mousemove"];

// document.addEventListener("DOMContentLoaded", function () {
//     let target = document.querySelector('body');
//     let observer = new MutationObserver(function (mutations) {
//         eventsToLog.forEach(eventToLog => {
//             document.addEventListener(eventToLog, logHandler);
//         });
//     });
//     let config = { attributes: true, childList: true, characterData: true }
//     observer.observe(target, config);
//
//     refreshSessionId();
// });

document.addEventListener("DOMContentLoaded", function (e) {
    console.log('DOM Loaded');
    refreshSessionId();
    $(document).ajaxStop(function () {
        console.log('AJAX Completed');
        var requirementTitles = document.querySelectorAll('.or-requirement-title');
        console.log(requirementTitles);
        var l = requirementTitles.length;
        for (var i = 0; i < l; i++) {
            requirementTitles[i].addEventListener('focus', (event) => {
                console.log("FOCUSED .or-requirement-title");
                log(event);
            }, true);

            requirementTitles[i].addEventListener('blur', (event) => {
                console.log("CHANGED TITLE");
                log(event);
            }, true);
        }

        var requirementTexts = document.querySelectorAll('.note-editable');
        console.log(requirementTexts);
        for (var i = 0; i < requirementTexts.length; i++) {
            requirementTexts[i].addEventListener('focus', (event) => {
                console.log("FOCUSED .note-editable");
                log(event);
            }, true);

            requirementTexts[i].addEventListener('blur', (event) => {
                console.log("CHANGED DESCRIPTION");
                log(event);
            }, true);
        }

        var requirementStatusDropDown = document.querySelectorAll('or-requirement-status-field .initialized');
        console.log(requirementStatusDropDown);
        for (var i = 0; i < requirementStatusDropDown.length; i++) {
            requirementStatusDropDown[i].addEventListener('change', (event) => {
                console.log("CHANGED STATUS");
                log(event);
            }, true);
        }

        var requirementStatusInput = document.querySelectorAll('.select-dropdown');
        console.log(requirementStatusInput);
        for (var i = 0; i < requirementStatusInput.length; i++) {
            requirementStatusInput[i].addEventListener('input', (event) => {
                console.log("CHANGED STATUS");
                log(event);
            }, true);
        }
    });
});

/***** DEVELOPER STUFF *****/

/***** DEVELOPER STUFF END *****/
