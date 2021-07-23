container_interval_id = 0;
password_interval_id = 0;
distro_image = 'ubuntu.svg';

// Shows a message
// Leave text empty to hide message
// error is a boolean deciding whether or not to add an error class
function message(text, error) {
    var message = document.getElementById('message');
    message.innerHTML = text;
    message.className = text ? (error ? 'error' : '') : 'hidden';
}

// Shows an error
function show_error(text) {
	message(text, true);
	// Stop the script on error
	throw new Error();
}

// Center the main login container
function centerContainer() {
    var container = document.getElementById("box");
    // Set absolute top to be half of viewport height minus half of container height
    container.style.top = (document.documentElement.clientHeight / 2) - (container.offsetHeight / 2) + 'px';
    // Set absolute left to be half of viewport width minus half of container width
    container.style.left = (document.documentElement.clientWidth / 2) - (container.offsetWidth / 2) + 'px';
}

// Centers the main container on container resize
// Time to build a custom resize event emulator thingy!
function centerContainerOnResize() {
    onResize(document.getElementById('box'), centerContainer);
}

// Executes a callback when an element is resized
function onResize(el, callback) {
    var width = el.offsetWidth;
    var height = el.offsetHeight;

    container_interval_id = setInterval(function() {
        // If the width or height don't match up
        if( el.offsetWidth != width || el.offsetHeight != height ) {
            // Remove the old task (with the old width/height)
            clearInterval(container_interval_id);
            // Execute the callback
            if(callback) callback();
            // And bind a new resize event (this makes sure we're always checking against the new width/height)
            onResize(el, callback);
        }
    },250);
}

// This is called by lightdm when the auth request is completed
function authentication_complete() {
    if (lightdm.is_authenticated) {
        //lightdm.login (lightdm.authentication_user, lightdm.default_session);
	lightdm.login (lightdm.authentication_user, lightdm.start_session_sync, 'xfce4'); //lightdm-webkit2-greeter
    } else {
        message("Authentication failed", true);
        lightdm.cancel_authentication();
    }
}

// Ignore requests for timed logins
function timed_login(user) {}

// Attempts to log in with lightdm
// Executes on form submit
function attemptLogin() {
    message("Logging in...");
    // Cancel weird timed logins
    lightdm.cancel_timed_login();
    // Pass on user to lightdm
    var user = document.getElementById('user').value;
    lightdm.start_authentication(user);
}

// Called by lightdm when it wants us to show a password prompt
// We wait until this is called to sen dlightdm our password
function show_prompt(text) {
    // Pass on password to lightdm once we have actually started authenticating
	if(password_interval_id > 0) clearInterval(password_interval_id);
	password_interval_id = setInterval(function() {
        var password = document.getElementById('password').value;
        lightdm.provide_secret(password);
	}, 250);
}

// Updates elements with content like time, etc.
function initializeWidgets() {
    // Start up the clock
   // initializeClockWidget();
    // Start up the hostname widget
    //initializeHostnameWidget();
    // Start up the distro widget
    //initializeDistroWidget();
}

function initializeDistroWidget() {	
	// If we have a distro image
	if(distro_image) {
		// Add in the distro logo
		var el = document.getElementById('distro-widget');
		var img = document.createElement('img');
		
		el.appendChild(img);
		
		img.src = 'img/distro/'+distro_image;
		
		// Center the form elements in #form after the image has loaded
		img.onload = function() {
			var form = document.getElementById('form');
			var content = document.getElementById('content');
			// Set #form top margin to half of #content height minus half of #form height
			form.style.marginTop = ((content.offsetHeight / 2) - (form.offsetHeight / 2)) + 'px';
		}
	}
}

function initializeClockWidget() {
    updateClockWidget();
    setInterval(updateClockWidget, 1000);
}

function initializeHostnameWidget() {
    var el = document.getElementById("hostname-widget");
    el.innerHTML = lightdm.hostname;
}

function updateClockWidget() {
    var el = document.getElementById("clock-widget");
    var date = new Date();

    var days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
    var months = ['January','February','March','April','May','June','July','August','September','October','November','December'];

    var dateString = '<span>' + (date.getHours()<10?'0':'') + date.getHours() + ':' + (date.getMinutes()<10?'0':'') + date.getMinutes() + '</span>'; 
    el.innerHTML = dateString;
}

//If we have a logged in user, add his username to the user field
function initializeUsers() {
    var el = document.getElementById('user');

    // Loop through users
    for (var i = 0; i < lightdm.users.length; i++) {
        var user = lightdm.users[i];
        if(user.logged_in) {
            el.value = user.name;
        }
    }
}

// Loads actions like suspend, reboot, etc.
function initializeActions() {
    var el = document.getElementById('actions-inner');
    el.innerHTML = '';

    if (lightdm.can_suspend) {
        var node = document.createElement('a');
        node.className = 'iconic moon_fill';
        node.onclick = function(e) {
            lightdm.suspend();
            e.stopPropagation();
            e.preventDefault(true);
            return false;
        };
        el.appendChild(node);
    }

    if (lightdm.can_restart) {
        var node = document.createElement('a');
        node.className = 'iconic spin';
        node.onclick = function(e) {
            lightdm.restart();
            e.stopPropagation();
            e.preventDefault(true);
            return false;
        };
        el.appendChild(node);
    }

    if (lightdm.can_shutdown) {
        var node = document.createElement('a');
        node.className = 'iconic x';
        node.onclick = function(e) {
            lightdm.shutdown();
            e.stopPropagation();
            e.preventDefault(true);
            return false;
        };
        el.appendChild(node);
    }

}

// Focuses the user field (if empty), else focuses the password field
function handleFocus() {
	var user = document.getElementById('user');
	if(user.value == 'undefined' || user.value == '') {
		user.focus();
	}else{
		document.getElementById('password').focus();
	}
}

// Initializes the script
(function initialize() {
    // Center container initially
    centerContainer();
    // Center container again on container resize
    centerContainerOnResize();
    // Update elements that contain informations like time, date, hostname, etc.
    // initializeWidgets();
    // Load the list of users
    initializeUsers();
    // Load actions (suspend, reboot, shutdown, etc.)
    // initializeActions();
    // Handle focusing
    handleFocus();
})();
