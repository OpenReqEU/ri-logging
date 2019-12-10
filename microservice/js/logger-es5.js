// generated with https://babeljs.io/repl
"use strict";

function _instanceof(left, right) {
    if (right != null && typeof Symbol !== "undefined" && right[Symbol.hasInstance]) {
        return !!right[Symbol.hasInstance](left);
    }
    else {
        return left instanceof right;
    }
}

function _typeof(obj) { if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _classCallCheck(instance, Constructor) { if (!_instanceof(instance, Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

/** Definitions of used object to avoid manual descriptions of objects */

/**
 * @typedef RiLoggingConfiguration
 * @property {string} receiver
 * @property {{enabled: boolean, console: {date: boolean, class: boolean}}} debug
 * @property {RiLoggingTarget[]} targets
 * @property {RiLoggingInformation[]} information
 */

/**
 * @typedef RiLoggingInformation
 * @property {string} id
 * @property {string} target_name
 * @property {string} timestamp_name
 * @property {RiLoggingField[]} header
 * @property {RiLoggingField[]} fields
 */

/**
 * @typedef RiLoggingTarget
 * @property {string} name
 * @property {string} type
 * @property {string} category
 * @property {string} selector
 * @property {number} [key]
 * @property {boolean} [key_alt]
 * @property {boolean} [key_shift]
 * @property {string} [information]
 * @property {string} [receiver]
 * @property {string[]} [targets]
 * @property {boolean} [bound]
 * @property {boolean} [delayed]
 */

/**
 * @typedef RiLoggingField
 * @property {string} name
 * @property {string} source
 * @property {string} value
 * @property {string} [datatype]
 * @property {string} [get]
 * @property {string} [parameter]
 * @property {string} [split]
 * @property {number} [position]
 * @property {number} [divisor]
 * @property {number} [element_parent]
 */

/**
 * Class for the logging im frontend
 */
var RiLogging =
/*#__PURE__*/
function () {
  function RiLogging() {
    _classCallCheck(this, RiLogging);

    _defineProperty(this, "instance_id", 0);

    _defineProperty(this, "configuration", {});

    _defineProperty(this, "log", []);

    _defineProperty(this, "debug", false);

    _defineProperty(this, "event_queue", []);

    _defineProperty(this, "event_queue_lock", false);
  }
  _createClass(RiLogging, [{
    key: "enableDebug",

    /**
     * Enables debugging, in this case the messages will be written to console and not just stored in the class itself
     */
    value: function enableDebug() {
      this.debug = true;

      for (var p = 0; p < this.log.length; p++) {
        console.log(this.log[p]);
      }
    }
  }, {
    key: "getDateTimeString",

    /**
     * Reformats the date into english format and returns it
     * @returns {string}
     */
    value: function getDateTimeString() {
      var dateString = "";
      var moment = new Date();
      var year = moment.getFullYear();
      var month = moment.getMonth() + 1;
      var day = moment.getDate();
      var hours = moment.getHours();
      var minutes = moment.getMinutes();
      var seconds = moment.getSeconds();
      var dateStringConfig = {
        "-": [year, month, day],
        ":": [hours, minutes, seconds]
      };
      var parts = [];

      for (var delimiter in dateStringConfig) {
        parts = [];

        if (dateStringConfig.hasOwnProperty(delimiter) === true) {
          for (var part = 0; part < dateStringConfig[delimiter].length; part++) {
            if (dateStringConfig[delimiter][part] < 10) {
              parts.push("0" + dateStringConfig[delimiter][part]);
            } else {
              parts.push(dateStringConfig[delimiter][part]);
            }
          }
        }

        dateString = dateString + parts.join(delimiter) + " ";
      }

      dateString = dateString.trim();
      return dateString;
    }
  }, {
    key: "message",

    /**
     * Method for logging the messages and state changes
     * If debug is enabled, it will also output the messages to the console
     * @param message
     */
    value: function message(_message) {
      var dateString = "";
      var className = "";

      if (this.configuration.debug.console.date === true) {
        dateString = "[" + this.getDateTimeString() + "]" + " ";
      }

      if (this.configuration.debug.console.date === true) {
        className = this.__proto__.constructor.name + " [instance  " + this.instance_id + "]";
      }

      var fullMessage = dateString + className + " : " + _message;
      this.log.push(fullMessage);

      if (this.debug === true) {
        console.log(fullMessage);
      }
    }
    /**
     * Starts the logging based on the configuration
     * @param {string|RiLoggingConfiguration} configuration
     */

  }, {
    key: "initialize",

    /**
     * Initializes the module, after that the events will be bound
     * @param {string} message
     */
    value: function initialize(message) {
      if (_typeof(this.configuration) === "object" && this.configuration.hasOwnProperty("debug") && _typeof(this.configuration.debug) === "object" && this.configuration.debug.hasOwnProperty("enabled") && this.configuration.debug.enabled === true) {
        this.enableDebug();
      }

      if (_typeof(this.configuration) === "object" && this.configuration.hasOwnProperty("receiver") && typeof this.configuration.receiver === "string" && this.configuration.receiver.length > 0) {
        this.message(message);
        this.message("start binding events to given targets");
        this.bindEvents();
      } else {
        this.message("initialization is denied because of invalid configuration");
      }
    }
  }, {
    key: "bindEvents",

    /**
     * Processes the logging targets and binds the events to them
     */
    value: function bindEvents() {
      var targets = this.configuration.targets;

      for (var t = 0; t < targets.length; t++) {
        /** @type {RiLoggingTarget} target */
        var target = targets[t];
        var doBindEvent = target.bound === false && typeof target.name === "string";

        for (var p = 0; p < targets.length; p++) {
          if (_typeof(targets[p].targets) === "object" && targets[p].targets.indexOf(target.name) >= 0) {
            doBindEvent = false;
            this.message("skip target \"" + target.name + "\" because of dependency");
            break;
          }
        }

        if (doBindEvent === true) {
          switch (target.type) {
            case "mouse":
            case "keyboard":
              this.bindTargetEvent(this, target);
              break;

            default:
              this.message("target type \"" + target.type + "\" in target \"" + target.name + "\" is not defined");
              break;
          }
        }
      }

      RiLogging.processQueue(this);
    }
  }, {
    key: "processBoundEvent",

    /**
     * Function for central processing of the events. Checks the condition for the events if any are given
     * @param {jQuery.Event|MouseEvent|KeyboardEvent} event
     * @param {RiLogging} logging
     * @param {RiLoggingTarget} loggingTarget
     */
    value: function processBoundEvent(event, logging, loggingTarget) {
      var processEvent = true;

      switch (loggingTarget.type) {
        case "keyboard":
          processEvent = processEvent === true && event.originalEvent.which === loggingTarget.key;
          processEvent = processEvent === true && (typeof loggingTarget.key_alt !== "boolean" || event.originalEvent.altKey === loggingTarget.key_alt);
          processEvent = processEvent === true && (typeof loggingTarget.key_shift !== "boolean" || event.originalEvent.shiftKey === loggingTarget.key_shift);
          break;
      }

      if (processEvent === true && logging.event_queue_lock === false) {
        logging.event_queue.push({
          logging: logging,
          target: loggingTarget,
          event: event
        });
      }
    }
  }, {
    key: "bindTargetEvent",

    /**
     * Binds en event on given target, which are triggered by mouse actions (like click, hover etc.)
     * Validates the parameters and forwards the data to central processing function
     * @param {RiLogging} logging
     * @param {RiLoggingTarget} target
     */
    value: function bindTargetEvent(logging, target) {
      var parameters = {
        "ri-logging": logging,
        "ri-logging-target": target
      };

      if ($(target.selector).length === 0 && typeof target.delayed === "boolean" && target.delayed === true) {
        logging.message("target \"" + target.name + "\" is not avialable yet, try again in " + RiLogging.binding_delay + "ms");
        setTimeout(logging.bindTargetEvent, RiLogging.binding_delay, logging, target);
      } else if (typeof $(target.selector)[target.category] === "function" && target.bound === false) {
        $(target.selector)[target.category](parameters, function (event) {
          var eventParameterGiven = _typeof(event.handleObj) === "object" && _typeof(event.handleObj.data) === "object" && event.handleObj.data !== null;
          var eventParameterValid = eventParameterGiven === true && _typeof(event.handleObj.data["ri-logging"]) === "object" && _typeof(event.handleObj.data["ri-logging-target"]) === "object";

          if (eventParameterValid === true) {
            /** @type RiLogging logging */
            var _logging = event.handleObj.data["ri-logging"];
            /** @type RiLoggingTarget loggingTarget */

            var loggingTarget = event.handleObj.data["ri-logging-target"]; // check if the event is a condition-event

            if (_typeof(loggingTarget.targets) === "object" && loggingTarget.targets.length > 0) {
              for (var i = 0; i < loggingTarget.targets.length; i++) {
                for (var t = 0; t < _logging.configuration.targets.length; t++) {
                  if (_logging.configuration.targets[t].bound === false && _logging.configuration.targets[t].name === loggingTarget.targets[i]) {
                    _logging.message("bind sub-events of target \"" + loggingTarget.name + "\"");

                    _logging.bindTargetEvent(_logging, _logging.configuration.targets[t]);

                    break;
                  }
                }
              }
            }

            if (typeof loggingTarget.information === "string" && loggingTarget.information.length > 0) {
              // redirecting to central event processing
              _logging.processBoundEvent(event, _logging, loggingTarget);
            }
          }
        });
        logging.message("bound event on target \"" + target.name + "\"");
        target.bound = true;
      }
    }
  }, {
    key: "trackEvent",

    /**
     * Tracks an event and sends it to the server
     * @param {jQuery.Event} event
     * @param {RiLoggingTarget} target
     */
    value: function trackEvent(event, target) {
      this.message("begin processing triggered target \"" + target.name + "\"");
      /** @type {RiLoggingInformation} loggingInformation */

      var loggingInformation = {}; // find the right information configuration

      for (var p = 0; p < this.configuration.information.length; p++) {
        if (target.information === this.configuration.information[p].id) {
          loggingInformation = this.configuration.information[p];
          break;
        }
      } // using the found configuration


      if (typeof loggingInformation.id === "string") {
        var information = this.collectInformation(target, loggingInformation, event);
        this.forwardInformation(target, loggingInformation, event, information);
      } else {
        this.message("no information for logging the target \"" + target.name + "\"");
      }
    }
  }, {
    key: "collectInformationRecursive",

    /**
     * Collects the information from the given object
     * @param {{}} source
     * @param {string} property
     * @returns {string|number|object}
     */
    value: function collectInformationRecursive(source, property) {
      var result = ""; // check if its a property of source object of if its property of sub-object of the source

      if (property.indexOf(".") >= 0) {
        var properties = property.split("."); // hasOwnProperty sometimes doesn't give right response, thats why double-check

        if (source.hasOwnProperty(properties[0]) === true || typeof source[properties[0]] !== "undefined") {
          property = properties[0];
          properties.splice(0, 1);
          result = this.collectInformationRecursive(source[property], properties.join("."));
        }
      } // access the needed property, if the property exists
      else if (source.hasOwnProperty(property) || typeof source[property] !== "undefined") {
          result = source[property];
        }

      return result;
    }
  }, {
    key: "collectInformationDate",

    /**
     * Collects the information from date object
     * @params {RiLoggingField} field
     * @returns {Date|string|number}
     */
    value: function collectInformationDate(field) {
      var result = "";
      var date = new Date(); // log of the object itself

      if ((typeof field.value !== "string" || field.value.length === 0) && (typeof field.get !== "string" || field.get.length === 0)) {
        result = date;
      } // log of a property of the object
      else if (typeof field.value === "string" && field.value.length > 0 && (date.hasOwnProperty(field.value) === true || typeof date[field.value] !== "undefined")) {
          result = date[field.value];
        } // log of a function result of the object
        else if (typeof field.get === "string" && field.get.length > 0) {
            // check if the function can be used as-is
            if (typeof date[field.get] === "function") {
              result = date[field.get]();
            } // check if the function should be called as getter
            else if (typeof date["get" + field.get[0].toUpperCase() + field.get.substring(1)] === "function") {
                result = date["get" + field.get[0].toUpperCase() + field.get.substring(1)]();
              }
          }

      return result;
    }
  }, {
    key: "collectInformationQuery",

    /**
     * Collects the information from HTML
     * @params {RiLoggingField} field
     * @returns {string|number}
     */
    value: function collectInformationQuery(field) {
      var result = "";
      var object = $(field.value);

      if (_typeof(object) === "object" && object !== null && object.length > 0) {
        if (typeof field.element_parent === "number" && field.element_parent > 0) {
          for (var p = 0; p < field.element_parent; p++) {
            object = object.parent();
          }
        }

        if (typeof field.get === "string" && field.get.length > 0) {
          // try to use the function as-is
          var functionName = field.get; // use getter for function in case as-is is not possible

          if (typeof object[functionName] !== "function") {
            functionName = "get" + field.get[0].toUpperCase() + field.get.substring(1);
          } // check if parameter needs to be passed


          if (typeof object[functionName] === "function") {
            if (typeof field.parameter === "undefined" || typeof field.parameter === "string" && field.parameter.length === 0 || field.parameter === null) {
              result = object[functionName]();
            } else {
              result = object[functionName](field.parameter);
            }
          }
        }
      }

      return result;
    }
  }, {
    key: "collectInformationCookie",

    /**
     * Collects the information from Cookie
     * @deprecated Only integrated because of compability of last version, cookies shouldnt be used in any way
     * @params {RiLoggingField} field
     * @returns {string}
     */
    value: function collectInformationCookie(field) {
      var result = "";
      var cookieObject = {};
      var cookie = document.cookie.trim();
      var cookieParts = cookie.split(";");

      for (var p = 0; p < cookieParts.length; p++) {
        var cookieKeyValue = cookieParts[p].trim().split("=");
        cookieObject[cookieKeyValue[0]] = cookieKeyValue[1];
      }

      if (cookieObject.hasOwnProperty(field.value) || typeof cookieObject[field.value] !== "undefined") {
        result = cookieObject[field.value];
      }

      return result;
    }
  }, {
    key: "collectInformationVariable",

    /**
     * Collects the information from Cookie
     * @params {RiLoggingField} field
     * @returns {string|number|object}
     */
    value: function collectInformationVariable(field) {
      var result = "";
      var variable = "";

      try {
        variable = eval(field.value);
      } catch (exception) {
        // if variable doesnt exists, ReferenceError is thrown, but nothing can be done
        this.message("information for field \"" + field.name + "\" couldn't be collected : " + exception.message);
      } finally {
        if (typeof variable !== "undefined") {
          result = variable;
        }
      }

      return result;
    }
  }, {
    key: "adjustInformationValue",

    /**
     * Collects the information from HTML
     * @params {RiLoggingField} field
     * @params {{}} information
     * @returns {string|number}
     */
    value: function adjustInformationValue(field, information) {
      if (typeof field.divisor === "number") {
        information[field.name] = Math.floor(information[field.name] / field.divisor);
      }

      if (typeof field.split === "string" && typeof field.position === "number") {
        var informationParts = information[field.name].split(field.split);
        information[field.name] = "";

        if (0 <= field.position && field.position < informationParts.length && _typeof(informationParts[field.position]) !== undefined) {
          information[field.name] = informationParts[field.position];
        }
      }
    }
  }, {
    key: "collectFieldInformation",

    /**
     * Collects information for given field
     * @param information
     * @param field
     * @param event
     */
    value: function collectFieldInformation(information, field, event) {
      switch (field.source) {
        case "event":
          information[field.name] = this.collectInformationRecursive(event, field.value);
          break;

        case "window":
          information[field.name] = this.collectInformationRecursive(window, field.value);
          break;

        case "date":
          information[field.name] = this.collectInformationDate(field);
          break;

        case "query":
          information[field.name] = this.collectInformationQuery(field);
          break;

        case "cookie":
          information[field.name] = this.collectInformationCookie(field);
          break;

        case "variable":
          information[field.name] = this.collectInformationVariable(field);
          break;

        case "constant":
          information[field.name] = field.value;
          break;
      }

      this.adjustInformationValue(field, information);
    }
  }, {
    key: "collectInformation",

    /**
     * Collects the information based on the configuration given
     * @param {RiLoggingTarget} target
     * @param {RiLoggingInformation} configuration
     * @param {jQuery.Event} event
     */
    value: function collectInformation(target, configuration, event) {
      var information = this.getDefaultInformation(target, configuration);

      if (_typeof(configuration.fields) === "object" && configuration.fields.length > 0) {
        for (var p = 0; p < configuration.fields.length; p++) {
          this.collectFieldInformation(information, configuration.fields[p], event);
        }
      }

      return information;
    }
  }, {
    key: "getDefaultInformation",

    /**
     * Returns the information object which will be filled with information fields based on the target configuration
     * @param {RiLoggingTarget} target
     * @param {RiLoggingInformation} configuration
     */
    value: function getDefaultInformation(target, configuration) {
      var information = {};

      if (typeof configuration.target_name === "string" && configuration.target_name.length > 0) {
        information[configuration.target_name] = target.name;
      }

      if (typeof configuration.timestamp_name === "string" && configuration.timestamp_name.length > 0) {
        information[configuration.timestamp_name] = this.getDateTimeString();
      }

      return information;
    }
  }, {
    key: "forwardInformation",

    /**
     * Forwards the collected information of the target to the server
     * @param {RiLoggingTarget} target
     * @param {RiLoggingInformation} configuration
     * @param {jQuery.Event} event
     * @param {{}} information
     */
    value: function forwardInformation(target, configuration, event, information) {
      var receiver = this.configuration.receiver;
      var headers = {
        "X-Ri-Logging-Instance": this.instance_id,
        "Content-Type": "application/json"
      };
      var data = JSON.stringify(information); // correct receiver if needed

      if (typeof target.receiver === "string" && target.receiver.length > 0) {
        receiver = target.receiver;
      } // correct request header if needed


      if (_typeof(configuration.header) === "object" && configuration.header.length > 0) {
        for (var h = 0; h < configuration.header.length; h++) {
          this.collectFieldInformation(headers, configuration.header[h], event);
        }
      } // send prepared request


      $.ajax({
        url: receiver,
        type: "post",
        data: data,
        headers: headers,
        dataType: "json",
        success: function success(response) {
          // this refers to the made request
          var instance_id = this.headers["X-Ri-Logging-Instance"];

          if (typeof instance_id === "number" && _typeof(RiLogging.instances[instance_id]) === "object" && RiLogging.instances[instance_id] !== null) {
            var logging = RiLogging.instances[instance_id];
            logging.handleResponse(this, response, true);
          }
        },
        error: function error(response) {
          // this refers to the made request
          var instance_id = this.headers["X-Ri-Logging-Instance"];

          if (typeof instance_id === "number" && _typeof(RiLogging.instances[instance_id]) === "object" && RiLogging.instances[instance_id] !== null) {
            var logging = RiLogging.instances[instance_id];
            logging.handleResponse(this, response, false);
          }
        }
      });
    }
  }, {
    key: "handleResponse",

    /**
     * Handles the response from server after sending the logging information
     * @param {{headers: {"X-Request-Source": number}}} request
     * @param {{message: string}} response
     * @param {boolean} success
     */
    value: function handleResponse(request, response) {
      var success = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : true;

      if (success === true) {
        this.message("data was sent successfully : " + response.message);
      } else {
        this.message("data could not be sent : " + response.message);
      } else if (typeof response === "object" && typeof response.message === "string") {
		this.message("data could not be sent : " + response.message);
      } else {
		this.message("data could not be sent : server not reachable");
	  }
	  // processing finished, so new event can be processed


      RiLogging.processQueue(this);
    }
  }], [{
    key: "processQueue",

    /**
     * Function for processing the queue
     * @param {RiLogging} logging
     */
    value: function processQueue(logging) {
      if (logging.event_queue.length === 0) {
        setTimeout(RiLogging.processQueue, RiLogging.idle_time, logging);
      } else {
        var eventConfig = logging.event_queue.shift();
        eventConfig.logging.trackEvent(eventConfig.event, eventConfig.target);
      }
    }
  }]);

  return RiLogging;
}();

_defineProperty(RiLogging, "idle_time", 1000);

_defineProperty(RiLogging, "binding_delay", 100);

_defineProperty(RiLogging, "instances", []);

_defineProperty(RiLogging, "getInstance", function () {
  var logging = new RiLogging();
  logging.instance_id = RiLogging.instances.length;
  RiLogging.instances.push(logging);
  return logging;
});

_defineProperty(RiLogging, "start", function (configuration) {
  var logging = RiLogging.getInstance(); // passed configuration is already object

  if (_typeof(configuration) === "object") {
    logging.configuration = configuration;
    logging.initialize("configuration loaded via object");
  } // configuration is supposed to be loaded via extern url
  else if (typeof configuration === "string" && configuration.indexOf("http") === 0) {
      $.get(configuration, function (response) {
        logging.configuration = response;
        logging.initialize("configuration loaded via extern URL");
      });
    } // configuration is supposed to be loaded via intern url (baseUrl is used)
    else if (typeof configuration === "string") {
        var baseUri = $("base").attr("href"); // avoid double-slash

        if (baseUri[baseUri.length - 1] === "/") {
          baseUri = baseUri.substr(0, baseUri.length - 1);
        }

        $.get(baseUri + configuration).success(function (response) {
          logging.configuration = response;
          logging.initialize("configuration loaded via intern URL");
        });
      }
});

$(document).ready(function () {// here creating instace of your logging module, examples below
  // starting via absolute URL
  // RiLogging.start("https://logging.my-website/uri/to/your/configuration/file.json");
  // starting via relative URL
  // RiLogging.start("/uri/to/your/configuration/file.json");
  // starting via json configuration
  // RiLogging.start(configuration);
});