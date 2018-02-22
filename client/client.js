var connection = null
var clientID = 0

var WebSocket = WebSocket || MozWebSocket

// map for chaining commands over websocket
var pending = {}
var running_experiment = null
var loaded_experiment_tabs = false

function connect() {
  var serverUrl = `ws://${window.location.hostname}:8765`

  connection = new WebSocket(serverUrl)

  connection.onopen = function(evt) {
  	if (!loaded_experiment_tabs) {
	    // fetch experiment metadata
	    var ref = generateUID()
	    connection.send(JSON.stringify({
	    	'type': 'query',
	    	'query': 'experiment_metadata',
	    	'ref': ref,
	    	'args': {}
	    }))
	    pending[ref] = (data) => {
	    	data.result.forEach(createExperimentTab)
	    	loaded_experiment_tabs = true
	    }
	}
  }

  connection.onmessage = function(evt) {
  	var data = JSON.parse(evt.data)
  	console.log(data)

  	if (data.ref in pending) {
  		pending[data.ref](data)
  		delete pending[data.ref]
  	}

  	if (data.type=='progress') {
  		if (data.finished) {
  			setProgress(1,1)
  		} else {
  			setProgress(data.progress, data.max)
  		}
  	}

  	var message_box = document.getElementById('message_box')
  	if (data.type=='message' || data.type=='error') {
  		message_box.innerHTML+=
  			`<div class="${data.type}">${data.message}</div>`
  		message_box.scrollTop = message_box.scrollHeight
  	}
  }
}

function send() {
  connection.send(document.getElementById("text").value);
  document.getElementById("text").value = "";
}

function handleKey(evt) {
  if (evt.keyCode === 13 || evt.keyCode === 14) {
    if (!document.getElementById("send").disabled) {
      send();
    }
  }
}

function getParameters(experiment) {
	var parameters = {}
	document.getElementById(experiment).querySelectorAll('.parameters input').forEach(input => {
		parameters[input.name] = input.valueAsNumber
	})
	return parameters
}

function setProgress(progress, max) {
	var progressBar = document.getElementById(running_experiment).querySelector('progress')
  	progressBar.value = progress
  	progressBar.max = max
}

function abortExperiment(experiment) {
	// clear any pending operations
	pending = {}
	// TODO send an abort signal to system
}

function runExperiment(experiment, callback) {
	running_experiment = experiment
	parameters = getParameters(experiment)
	setProgress(0,1)
	var ref1 = generateUID()
	var ref2 = generateUID()
	connection.send(JSON.stringify({
		'type': 'command',
    	'command': 'set_parameters',
    	'ref': ref1,
    	'args': {
			'experiment_name': experiment,
			'parameters': parameters
		}
	}))
	pending[ref1] = data => {
		console.log('running experiment')
		connection.send(JSON.stringify({
			'type': 'command',
			'command': 'run',
			'ref': ref2,
			'args': {
				'experiment_name': experiment
			}
		}))
	}
	pending[ref2] = data => {
		var plotName = document.getElementById(experiment).querySelector('.plot-list').value
		plot(experiment, plotName, callback)
		running_experiment = null
	}
}

function runExperimentContinuously(experiment) {
	var loop = () => {
		runExperiment(experiment, loop)
	}
	loop()
}

function plot(experiment, plotName, callback) {
	var ref1 = generateUID()
	console.log('getting plot data')
	connection.send(JSON.stringify({
		'type': 'query',
		'query': 'plot',
		'ref': ref1,
		'args': {
			'experiment_name': experiment,
			'plot_name': plotName
		}
	}))
	pending[ref1] = response => {
		console.log(`plotting ${experiment} ${plotName}`)
		Plotly.newPlot(experiment+'_plot', response.result.data, response.result.layout)
		if (callback) {
			callback()
		}
	}
}

function exportCSV(experiment, exportName, callback) {
	var ref1 = generateUID()
	console.log('getting export data')
	connection.send(JSON.stringify({
		'type': 'query',
		'query': 'export_csv',
		'ref': ref1,
		'args': {
			'experiment_name': experiment,
			'export_name': exportName
		}
	}))
	pending[ref1] = response => {
		console.log(`exporting ${experiment} ${exportName}`)
		downloadString(response.result, "text/csv", `${experiment}-${exportName}.csv`)
		if (callback) {
			callback()
		}
	}
}

function createExperimentTab(exp) {
	var tab = document.importNode(document.querySelector('#experiment_tab_template').content, true)
	var btn = tab.querySelector('button')
	btn.innerText = exp.name
	btn.addEventListener('click', e => {
		openExperimentTab(e, exp.name)
	}, false)
	document.getElementById('experiment_tabs').appendChild(tab)

	var pane = document.importNode(document.querySelector('#experiment_pane_template').content, true)
	pane.querySelector('div').id = exp.name
	pane.querySelector('.plot').id = exp.name+'_plot'
	pane.querySelector('.get-default-parameters').addEventListener('click', e => {
		var ref = generateUID()
		connection.send(JSON.stringify({
			'type': 'query',
	    	'query': 'default_parameters',
	    	'ref': ref,
	    	'args': {}
		}))
		pending[ref] = data => {
			document.getElementById(exp.name).querySelectorAll('.parameters input').forEach(input => {
				input.value = data.result[input.name]
			})
		}
	}, false)
	pane.querySelector('.run-experiment').addEventListener('click', e => {
		runExperiment(exp.name)
	}, false)
	pane.querySelector('.run-experiment-continuously').addEventListener('click', e => {
		runExperimentContinuously(exp.name)
	}, false)
	pane.querySelector('.abort-experiment').addEventListener('click', e => {
		abortExperiment(exp.name)
	}, false)
	var plotList = pane.querySelector('.plot-list')
	exp.plots.forEach(plotName => {
		var opt = document.createElement('option')
		opt.value = plotName
		opt.innerHTML = plotName
		plotList.appendChild(opt)
	})
	plotList.addEventListener('change', e => {
		plot(exp.name, e.target.value)
	})
	var exportList = pane.querySelector('.export-list')
	exp.exports.forEach(exportName => {
		var opt = document.createElement('option')
		opt.value = exportName
		opt.innerHTML = exportName
		exportList.appendChild(opt)
	})
	pane.querySelector('.btn-export').addEventListener('click', e => {
		exportCSV(exp.name, exportList.value)
	})
	Object.keys(exp.parameters).forEach(pName => {
		var par = document.importNode(document.querySelector('#parameter_template').content, true)
		par.querySelector('label').for = exp.name+'-'+pName
		par.querySelector('label').innerText = pName+':'
		var input = par.querySelector('input').id = exp.name+'-'+pName
		var input = par.querySelector('input').name = pName
		pane.querySelector('.parameters').appendChild(par)
	})
	document.getElementById('experiment_panes').appendChild(pane)
}

function openExperimentTab(event, experimentName) {
	// Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(experimentName).style.display = "block";
    event.currentTarget.className += " active";
}

function generateUID() {
    // I generate the UID from two parts here 
    // to ensure the random number provide enough bits.
    var firstPart = (Math.random() * 46656) | 0;
    var secondPart = (Math.random() * 46656) | 0;
    firstPart = ("000" + firstPart.toString(36)).slice(-3);
    secondPart = ("000" + secondPart.toString(36)).slice(-3);
    return firstPart + secondPart;
}

function downloadString(text, fileType, fileName) {
  	var blob = new Blob([text], { type: fileType });

  	var a = document.createElement('a');
  	a.download = fileName;
  	a.href = URL.createObjectURL(blob);
  	a.dataset.downloadurl = [fileType, a.download, a.href].join(':');
  	a.style.display = "none";
  	document.body.appendChild(a);
	a.click();
  	document.body.removeChild(a);
  	setTimeout(function() { URL.revokeObjectURL(a.href); }, 1500);
}