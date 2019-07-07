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
 * @property {boolean} bound
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
class RiLogging {
	/**
	 * Static property for the idle time between checking the queue for new event to process
	 * It can be adjusted via other modules or via console in Browser, any change to the value will be used right away
	 * @type {number}
	 */
	static idle_time = 1000;
	/**
	 * Static property for the binding offset for the case if the event should be bound delayed
	 * This is needed if the content with the needed selector will be provided via AJAX
	 * It can be adjusted via other modules or via console in Browser, any change to the value will be used right away
	 * @type {number}
	 */
	static binding_delay = 100;
	/**
	 * Saves all the instances of the actual web-page
	 * @type {RiLogging[]}
	 */
	static instances = [];
	/**
	 * Saves the instance ID, so the actual module can always be found between the instances
	 * @type {number}
	 */
	instance_id = 0;
	/**
	 * Saves the active configuration of the logging
	 * @type {RiLoggingConfiguration}
	 */
	configuration = {};
	/**
	 * Saves the messages in an array
	 * @type {string[]}
	 */
	log = [];
	/**
	 * Saves the state of the debugging
	 * @type {boolean}
	 */
	debug = false;
	/**
	 * Saves the events which need to be processed
	 * @type {{logging: RiLogging, target: RiLoggingTarget, event: jQuery.Event}[]}
	 */
	event_queue = [];
	/**
	 * Saves the state of queue, in case a link was clicked or tab was closed, queue filling should be stopped
	 * @type {boolean}
	 */
	event_queue_lock = false;
	/**
	 * Returns the instance of the class
	 * @returns {RiLogging}
	 */
	static getInstance = function () {
		let logging = new RiLogging();
		logging.instance_id = RiLogging.instances.length;
		RiLogging.instances.push(logging);
		return logging;
	};

	/**
	 * Enables debugging, in this case the messages will be written to console and not just stored in the class itself
	 */
	enableDebug() {
		this.debug = true;
		for (let p = 0; p < this.log.length; p++) {
			console.log(this.log[p]);
		}
	};

	/**
	 * Reformats the date into english format and returns it
	 * @returns {string}
	 */
	getDateTimeString() {
		let dateString = "";
		let moment = new Date();
		let year = moment.getFullYear();
		let month = moment.getMonth() + 1;
		let day = moment.getDate();
		let hours = moment.getHours();
		let minutes = moment.getMinutes();
		let seconds = moment.getSeconds();
		let dateStringConfig = {"-": [year, month, day], ":": [hours, minutes, seconds]};
		let parts = [];
		for (let delimiter in dateStringConfig) {
			parts = [];
			if (dateStringConfig.hasOwnProperty(delimiter) === true) {
				for (let part = 0; part < dateStringConfig[delimiter].length; part++) {
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
	};

	/**
	 * Method for logging the messages and state changes
	 * If debug is enabled, it will also output the messages to the console
	 * @param message
	 */
	message(message) {
		let dateString = "";
		let className = "";
		if (this.configuration.debug.console.date === true) {
			dateString = "[" + this.getDateTimeString() + "]" + " ";
		}
		if (this.configuration.debug.console.date === true) {
			className = this.__proto__.constructor.name + " [instance  " + this.instance_id + "]";
		}
		let fullMessage = dateString + className + " : " + message;
		this.log.push(fullMessage);
		if (this.debug === true) {
			console.log(fullMessage);
		}
	}

	/**
	 * Starts the logging based on the configuration
	 * @param {string|RiLoggingConfiguration} configuration
	 */
	static start = function (configuration) {
		let logging = RiLogging.getInstance();
		// passed configuration is already object
		if (typeof configuration === "object") {
			logging.configuration = configuration;
			logging.message("configuration loaded via object");
			logging.initialize();
		}
		// configuration is supposed to be loaded via extern url
		else if (typeof configuration === "string" && configuration.indexOf("http") === 0) {
			$.get(configuration, function (response) {
				logging.configuration = response;
				logging.message("configuration loaded via extern URL");
				logging.initialize();
			});
		}
		// configuration is supposed to be loaded via intern url (baseUrl is used)
		else if (typeof configuration === "string") {
			let baseUri = $("base").attr("href");
			// avoid double-slash
			if (baseUri[baseUri.length - 1] === "/") {
				baseUri = baseUri.substr(0, baseUri.length - 1);
			}
			$.get(baseUri + configuration).success(function (response) {
				logging.configuration = response;
				logging.message("configuration loaded via extern URL");
				logging.initialize();
			});
		}
	};

	/**
	 * Initializes the module, after that the events will be bound
	 */
	initialize() {
		if (this.debug === false && this.configuration.debug.enabled === true) {
			this.enableDebug();
		}
		this.message("start binding events to given targets");
		this.bindEvents();
	};

	/**
	 * Processes the logging targets and binds the events to them
	 */
	bindEvents() {
		let targets = this.configuration.targets;
		for (let t = 0; t < targets.length; t++) {
			/** @type {RiLoggingTarget} target */
			let target = targets[t];
			let doBindEvent = target.bound === false;
			for (let p = 0; p < targets.length; p++) {
				if (typeof targets[p].targets === "object" && targets[p].targets.indexOf(target.name) >= 0) {
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
	};

	/**
	 * Function for central processing of the events. Checks the condition for the events if any are given
	 * @param {jQuery.Event|MouseEvent|KeyboardEvent} event
	 * @param {RiLogging} logging
	 * @param {RiLoggingTarget} loggingTarget
	 */
	processBoundEvent(event, logging, loggingTarget) {
		let processEvent = true;
		switch (loggingTarget.type) {
			case "keyboard":
				processEvent = processEvent === true && event.originalEvent.which === loggingTarget.key;
				processEvent = processEvent === true && (typeof loggingTarget.key_alt !== "boolean" || event.originalEvent.altKey === loggingTarget.key_alt);
				processEvent = processEvent === true && (typeof loggingTarget.key_shift !== "boolean" || event.originalEvent.shiftKey === loggingTarget.key_shift);
				break;
		}
		if (loggingTarget.type === "keyboard" && event.originalEvent.which === loggingTarget.key) {
			processEvent = true;
		}
		if (processEvent === true && logging.event_queue_lock === false) {
			logging.event_queue.push({logging: logging, target: loggingTarget, event: event});
		}
	};

	/**
	 * Binds en event on given target, which are triggered by mouse actions (like click, hover etc.)
	 * Validates the parameters and forwards the data to central processing function
	 * @param {RiLogging} logging
	 * @param {RiLoggingTarget} target
	 */
	bindTargetEvent(logging, target) {
		let parameters = {"ri-logging": logging, "ri-logging-target": target};
		if ($(target.selector).length === 0 && typeof target.delayed === "boolean" && target.delayed === true) {
			logging.message("target \"" + target.name + "\" is not avialable yet, try again in " + RiLogging.binding_delay + "ms");
			setTimeout(logging.bindTargetEvent, RiLogging.binding_delay, logging, target);
		} else if (typeof $(target.selector)[target.category] === "function" && target.bound === false) {
			$(target.selector)[target.category](parameters, function (event) {
			    /** @type JQuery.Event event */
				let eventParameterGiven = typeof event.handleObj === "object" && typeof event.handleObj.data === "object" && event.handleObj.data !== null;
				let eventParameterValid = eventParameterGiven === true && typeof event.handleObj.data["ri-logging"] === "object" && typeof event.handleObj.data["ri-logging-target"] === "object";
				if (eventParameterValid === true) {
					/** @type RiLogging logging */
					let logging = event.handleObj.data["ri-logging"];
					/** @type RiLoggingTarget loggingTarget */
					let loggingTarget = event.handleObj.data["ri-logging-target"];
					// check if the event is a condition-event
					if (typeof loggingTarget.targets === "object" && loggingTarget.targets.length > 0) {
						for (let i = 0; i < loggingTarget.targets.length; i++) {
							for (let t = 0; t < logging.configuration.targets.length; t++) {
								if (logging.configuration.targets[t].bound === false && logging.configuration.targets[t].name === loggingTarget.targets[i]) {
									logging.message("bind sub-events of target \"" + loggingTarget.name + "\"");
									logging.bindTargetEvent(logging, logging.configuration.targets[t]);
									break;
								}
							}
						}
					}
					if (typeof loggingTarget.information === "string" && loggingTarget.information.length > 0) {
						// redirecting to central event processing
						logging.processBoundEvent(event, logging, loggingTarget);
					}
				}
			});
			logging.message("bound event on target \"" + target.name + "\"");
			target.bound = true;
		}
	};

	/**
	 * Tracks an event and sends it to the server
	 * @param {jQuery.Event} event
	 * @param {RiLoggingTarget} target
	 */
	trackEvent(event, target) {
		this.message("begin processing triggered target \"" + target.name + "\"");
		/** @type {RiLoggingInformation} loggingInformation */
		let loggingInformation = {};
		// find the right information configuration
		for (let p = 0; p < this.configuration.information.length; p++) {
			if (target.information === this.configuration.information[p].id) {
				loggingInformation = this.configuration.information[p];
				break;
			}
		}
		// using the found configuration
		if (typeof loggingInformation.id === "string") {
			let information = this.collectInformation(target, loggingInformation, event);
			this.forwardInformation(target, loggingInformation, event, information);
		} else {
			this.message("no information for logging the target \"" + target.name + "\"");
		}
	};

	/**
	 * Collects the information from the given object
	 * @param {{}} source
	 * @param {string} property
	 * @returns {string|number|object}
	 */
	collectInformationRecursive(source, property) {
		let result = "";
		// check if its a property of source object of if its property of sub-object of the source
		if (property.indexOf(".") >= 0) {
			let properties = property.split(".");
			// hasOwnProperty sometimes doesn't give right response, that's why double-check
			if (source.hasOwnProperty(properties[0]) === true || typeof source[properties[0]] !== "undefined") {
				property = properties[0];
				properties.splice(0, 1);
				result = this.collectInformationRecursive(source[property], properties.join("."))
			}
		}
		// access the needed property, if the property exists
		else if (source.hasOwnProperty(property) || typeof source[property] !== "undefined") {
			result = source[property];
		}
		return result;
	};

	/**
	 * Collects the information from date object
	 * @params {RiLoggingField} field
	 * @returns {Date|string|number}
	 */
	collectInformationDate(field) {
		let result = "";
		let date = new Date();
		// log of the object itself
		if ((typeof field.value !== "string" || field.value.length === 0) && (typeof field.get !== "string" || field.get.length === 0)) {
			result = date;
		}
		// log of a property of the object
		else if (typeof field.value === "string" && field.value.length > 0 && (date.hasOwnProperty(field.value) === true || typeof date[field.value] !== "undefined")) {
			result = date[field.value];
		}
		// log of a function result of the object
		else if (typeof field.get === "string" && field.get.length > 0) {
			// check if the function can be used as-is
			if (typeof date[field.get] === "function") {
				result = date[field.get]();
			}
			// check if the function should be called as getter
			else if (typeof date["get" + field.get[0].toUpperCase() + field.get.substring(1)] === "function") {
				result = date["get" + field.get[0].toUpperCase() + field.get.substring(1)]();
			}
		}
		return result;
	};

	/**
	 * Collects the information from HTML
	 * @params {RiLoggingField} field
	 * @returns {string|number}
	 */
	collectInformationQuery(field) {
		let result = "";
		let object = $(field.value);
		if (typeof object === "object" && object !== null && object.length > 0) {
			if (typeof field.element_parent === "number" && field.element_parent > 0) {
				for (let p = 0; p < field.element_parent; p++) {
					object = object.parent();
				}
			}
			if (typeof field.get === "string" && field.get.length > 0) {
				// try to use the function as-is
				let functionName = field.get;
				// use getter for function in case as-is is not possible
				if (typeof object[functionName] !== "function") {
					functionName = "get" + field.get[0].toUpperCase() + field.get.substring(1);
				}
				// check if parameter needs to be passed
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
	};

	/**
	 * Collects the information from Cookie
	 * @deprecated Only integrated because of compability of last version, cookies shouldnt be used in any way
	 * @params {RiLoggingField} field
	 * @returns {string}
	 */
	collectInformationCookie(field) {
		let result = "";
		let cookieObject = {};
		let cookie = document.cookie.trim();
		let cookieParts = cookie.split(";");
		for (let p = 0; p < cookieParts.length; p++) {
			let cookieKeyValue = cookieParts[p].trim().split("=");
			cookieObject[cookieKeyValue[0]] = cookieKeyValue[1];
		}
		if (cookieObject.hasOwnProperty(field.value) || typeof cookieObject[field.value] !== "undefined") {
			result = cookieObject[field.value];
		}
		return result;
	};

	/**
	 * Collects the information from Cookie
	 * @params {RiLoggingField} field
	 * @returns {string|number|object}
	 */
	collectInformationVariable(field) {
		let result = "";
		let variable = "";
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
	};

	/**
	 * Collects the information from HTML
	 * @params {RiLoggingField} field
	 * @params {{}} information
	 * @returns {string|number}
	 */
	adjustInformationValue(field, information) {
		if (typeof field.divisor === "number") {
			information[field.name] = Math.floor(information[field.name] / field.divisor);
		}
		if (typeof field.split === "string" && typeof field.position === "number") {
			let informationParts = information[field.name].split(field.split);
			information[field.name] = "";
			if (0 <= field.position && field.position < informationParts.length && typeof informationParts[field.position] !== undefined) {
				information[field.name] = informationParts[field.position];
			}
		}
	};

	/**
	 * Collects information for given field
	 * @param information
	 * @param field
	 * @param event
	 */
	collectFieldInformation(information, field, event) {
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
	};

	/**
	 * Collects the information based on the configuration given
	 * @param {RiLoggingTarget} target
	 * @param {RiLoggingInformation} configuration
	 * @param {jQuery.Event} event
	 */
	collectInformation(target, configuration, event) {
		let information = this.getDefaultInformation(target, configuration);
		if (typeof configuration.fields === "object" && configuration.fields.length > 0) {
			for (let p = 0; p < configuration.fields.length; p++) {
				this.collectFieldInformation(information, configuration.fields[p], event);
			}
		}
		return information;
	};

	/**
	 * Returns the information object which will be filled with information fields based on the target configuration
	 * @param {RiLoggingTarget} target
	 * @param {RiLoggingInformation} configuration
	 */
	getDefaultInformation(target, configuration) {
		let information = {};
		if (typeof configuration.target_name === "string" && configuration.target_name.length > 0) {
			information[configuration.target_name] = target.name;
		}
		if (typeof configuration.timestamp_name === "string" && configuration.timestamp_name.length > 0) {
			information[configuration.timestamp_name] = this.getDateTimeString();
		}
		return information;
	};

	/**
	 * Forwards the collected information of the target to the server
	 * @param {RiLoggingTarget} target
	 * @param {RiLoggingInformation} configuration
	 * @param {jQuery.Event} event
	 * @param {{}} information
	 */
	forwardInformation(target, configuration, event, information) {
		let receiver = this.configuration.receiver;
		let headers = {"X-Ri-Logging-Instance": this.instance_id, "Content-Type": "application/json"};
		let data = JSON.stringify(information);
		// correct receiver if needed
		if (typeof target.receiver === "string" && target.receiver.length > 0) {
			receiver = target.receiver;
		}
		// correct request header if needed
		if (typeof configuration.header === "object" && configuration.header.length > 0) {
			for (let h = 0; h < configuration.header.length; h++) {
				this.collectFieldInformation(headers, configuration.header[h], event);
			}
		}
		// send prepared request
		$.ajax({
			url: receiver,
			type: "post",
			data: data,
			headers: headers,
			dataType: "json",
			success: function (response) {
				// this refers to the made request
				let instance_id = this.headers["X-Ri-Logging-Instance"];
				if (typeof instance_id === "number" && typeof RiLogging.instances[instance_id] === "object" && RiLogging.instances[instance_id] !== null) {
					let logging = RiLogging.instances[instance_id];
					logging.handleResponse(this, response, true);
				}
			},
			error: function (response) {
				// this refers to the made request
				let instance_id = this.headers["X-Ri-Logging-Instance"];
				if (typeof instance_id === "number" && typeof RiLogging.instances[instance_id] === "object" && RiLogging.instances[instance_id] !== null) {
					let logging = RiLogging.instances[instance_id];
					logging.handleResponse(this, response, false);
				}
			}
		});
	};

	/**
	 * Handles the response from server after sending the logging information
	 * @param {{headers: {"X-Request-Source": number}}} request
	 * @param {{message: string}} response
	 * @param {boolean} success
	 */
	handleResponse(request, response, success = true) {
		if (success === true) {
			this.message("data was sent successfully : " + response.message);
		} else {
			this.message("data could not be sent : " + response.message);
		}
		// processing finished, so new event can be processed
		RiLogging.processQueue(this);
	};

	/**
	 * Function for processing the queue
	 * @param {RiLogging} logging
	 */
	static processQueue(logging) {
		if (logging.event_queue.length === 0) {
			setTimeout(RiLogging.processQueue, RiLogging.idle_time, logging);
		} else {
			let eventConfig = logging.event_queue.shift();
			eventConfig.logging.trackEvent(eventConfig.event, eventConfig.target);
		}
	}
}

$(document).ready(function () {
	// here creating instance of your logging module, example below
	// RiLogging.start("https://logging.my-website/frontend_configuration");
	/**
	 * Configuration needed by the logging module
	 * @type {RiLoggingConfiguration} ri_logging_configuration
	 */
	let ri_logging_configuration =
		{
			"receiver": "https://api.openreq.eu/ri-logging/frontend/log",
			"debug": {
				"enabled": true,
				"console": {
					"date": true,
					"class": true
				}
			},
			"targets": [
				{
					"bound": false,
					"name": "body_click",
					"type": "mouse",
					"category": "click",
					"selector": "body",
					"information": "default"
				},
				{
					"bound": false,
					"name": "condition",
					"type": "mouse",
					"category": "mouseover",
					"selector": "body",
					"targets": [
						"FOCUSED .or-requirement-title",
						"UNFOCUSED .or-requirement-title",
						"FOCUSED .note-editable",
						"UNFOCUSED .note-editable"
					]
				},
				{
					"bound": false,
					"name": "FOCUSED .or-requirement-title",
					"type": "mouse",
					"category": "focus",
					"selector": ".or-requirement-title",
					"information": "default",
					"delayed": true
				},
				{
					"bound": false,
					"name": "UNFOCUSED .or-requirement-title",
					"type": "mouse",
					"category": "blur",
					"selector": ".or-requirement-title",
					"information": "default",
					"delayed": true
				},
				{
					"bound": false,
					"name": "FOCUSED .note-editable",
					"type": "mouse",
					"category": "focus",
					"selector": ".note-editable",
					"information": "default",
					"delayed": true
				},
				{
					"bound": false,
					"name": "UNFOCUSED .note-editable",
					"type": "mouse",
					"category": "blur",
					"selector": ".note-editable",
					"information": "default",
					"delayed": true
				}
			],
			"information": [
				{
					"id": "default",
					"target_name": "target_name",
					"timestamp_name": "timestamp_event",
					"header": [
						{
							"name": "sessionId",
							"source": "cookie",
							"value": "sessionId"
						},
						{
							"name": "Content-Type",
							"source": "constant",
							"value": "application/json"
						}
					],
					"fields": [
						{
							"name": "screenX",
							"source": "event",
							"value": "originalEvent.screenX"
						},
						{
							"name": "screenY",
							"source": "event",
							"value": "originalEvent.screenY"
						},
						{
							"name": "clientX",
							"source": "event",
							"value": "originalEvent.clientX"
						},
						{
							"name": "clientY",
							"source": "event",
							"value": "originalEvent.clientY"
						},
						{
							"name": "x",
							"source": "event",
							"value": "originalEvent.x"
						},
						{
							"name": "y",
							"source": "event",
							"value": "originalEvent.y"
						},
						{
							"name": "offsetX",
							"source": "event",
							"value": "originalEvent.offsetX"
						},
						{
							"name": "offsetY",
							"source": "event",
							"value": "originalEvent.offsetY"
						},
						{
							"name": "movementX",
							"source": "event",
							"value": "originalEvent.movementX"
						},
						{
							"name": "movementY",
							"source": "event",
							"value": "originalEvent.movementY"
						},
						{
							"name": "layerX",
							"source": "event",
							"value": "originalEvent.layerX"
						},
						{
							"name": "layerY",
							"source": "event",
							"value": "originalEvent.layerY"
						},
						{
							"name": "type",
							"source": "event",
							"value": "originalEvent.type"
						},
						{
							"name": "timeStamp",
							"source": "event",
							"value": "originalEvent.timeStamp"
						},
						{
							"name": "offsetTop",
							"source": "event",
							"value": "originalEvent.target.offsetTop"
						},
						{
							"name": "offsetLeft",
							"source": "event",
							"value": "originalEvent.target.offsetLeft"
						},
						{
							"name": "offsetWidth",
							"source": "event",
							"value": "originalEvent.target.offsetWidth"
						},
						{
							"name": "offsetHeight",
							"source": "event",
							"value": "originalEvent.target.offsetHeight"
						},
						{
							"name": "innerText",
							"source": "event",
							"value": "originalEvent.target.innerText"
						},
						{
							"name": "outerText",
							"source": "event",
							"value": "originalEvent.target.outerText"
						},
						{
							"name": "scrollTop",
							"source": "event",
							"value": "originalEvent.target.scrollTop"
						},
						{
							"name": "scrollLeft",
							"source": "event",
							"value": "originalEvent.target.scrollLeft"
						},
						{
							"name": "scrollWidth",
							"source": "event",
							"value": "originalEvent.target.scrollWidth"
						},
						{
							"name": "scrollHeight",
							"source": "event",
							"value": "originalEvent.target.scrollHeight"
						},
						{
							"name": "clientTop",
							"source": "event",
							"value": "originalEvent.target.clientTop"
						},
						{
							"name": "clientLeft",
							"source": "event",
							"value": "originalEvent.target.clientLeft"
						},
						{
							"name": "clientWidth",
							"source": "event",
							"value": "originalEvent.target.clientWidth"
						},
						{
							"name": "clientHeight",
							"source": "event",
							"value": "originalEvent.target.clientHeight"
						},
						{
							"name": "value",
							"source": "event",
							"value": "originalEvent.target.value"
						},
						{
							"name": "srcElementclassName",
							"source": "event",
							"value": "originalEvent.srcElement.className"
						},
						{
							"name": "srcElementId",
							"source": "event",
							"value": "originalEvent.srcElement.id"
						},
						{
							"name": "targetclassName",
							"source": "event",
							"value": "originalEvent.target.className"
						},
						{
							"name": "targetId",
							"source": "event",
							"value": "originalEvent.target.id"
						},
						{
							"name": "requirementId",
							"source": "constant",
							"value": "todo"
						},
						{
							"name": "url",
							"source": "window",
							"value": "location.href"
						},
						{
							"name": "isoTime",
							"source": "date",
							"value": ""
						},
						{
							"name": "unixTime",
							"source": "date",
							"value": "",
							"get": "time",
							"divisor": 1000
						},
						{
							"name": "projectId",
							"source": "window",
							"value": "location.href",
							"split": "/",
							"position": 5
						}
					]
				}
			]
		};
	RiLogging.start(ri_logging_configuration);
});