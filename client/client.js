var connection = null
var clientID = 0

var WebSocket = WebSocket || MozWebSocket

// map for chaining commands over websocket
var pending = {}
var running_experiment = null
var loaded_experiment_tabs = false

var temp_history = []
var temp_history_time = []

function connect() {
  var serverUrl = `ws://${window.location.hostname}:8765`

  connection = new ReconnectingWebSocket(serverUrl)

  connection.onopen = function(evt) {
  	if (!loaded_experiment_tabs) {
  	    // set up temperature control
  	    createTempControlTab()
  	    openExperimentTab('tempcontrol')

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
	    	refreshParSetList()
	    	loadLanguage('english')
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
  			replot(data.experiment)
  		}
  	}

  	if (data.type=='tempcontrol') {
  	  if (data.data.name=='temperature') {
  	    temp_history.push(data.data.value)
  	    if (temp_history_time.length==0) {temp_history_time.push(0)}
  	    else {temp_history_time.push(temp_history_time[temp_history_time.length-1]+10)}
  	    if (document.getElementById('tempcontrol_tablink').classList.contains('active')){
  	      d3plot(d3.select('#tempcontrol svg.plot'), {
  	          'data': [{
                'name': '',
                'type': 'scatter',
                'x': temp_history_time,
                'y': temp_history}],
              'layout': {
                'title': 'Temperature',
                'xaxis': {'title': 'time (s)'},
                'yaxis': {'title': 'Temperature (°C)'}
              }
  	      })
  	    }
  	  } else {
  	    data.type='message'
  	    data.message = 'temp control '+data.data.name+'='+data.data.value
  	  }
  	}

  	var message_boxes = document.querySelectorAll('.message-box')
  	if (data.type=='message' || data.type=='error') {
  	    message_boxes.forEach(message_box => {
            message_box.innerHTML+=
                `<div class="${data.type}">${data.message}</div>`
            message_box.scrollTop = message_box.scrollHeight
  		})
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
	var ref = generateUID()
	connection.send(JSON.stringify({
		'type': 'command',
    	'command': 'abort',
    	'ref': ref,
    	'args': {
			'experiment_name': experiment
		}
	}))
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
	    replot(experiment)
		if (callback) {
			callback()
		}
		running_experiment = null
	}
}

function runExperimentContinuously(experiment) {
	var loop = () => {
		runExperiment(experiment, loop)
	}
	loop()
}

function plot(experiment, plotNum, plotName, callback) {
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
		//Plotly.newPlot(experiment+'_plot_0', response.result.data, response.result.layout)
		d3plot(d3.select('#'+experiment+'_plot_'+plotNum+' svg'), response.result)
		if (callback) {
			callback()
		}
	}
}

function replot(experiment) {
  var plotCount = document.getElementById(experiment).querySelectorAll('.plot-box').length
  for (var i=0; i<plotCount; i++) {
    var plotName = document.getElementById(experiment+'_plot_'+i).querySelector('.plot-list').value
    plot(experiment, i, plotName)
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

function exportMATLAB(experiment, exportName, callback) {
	var ref1 = generateUID()
	console.log('getting export data')
	connection.send(JSON.stringify({
		'type': 'query',
		'query': 'export_matlab',
		'ref': ref1,
		'args': {
			'experiment_name': experiment,
			'export_name': exportName
		}
	}))
	pending[ref1] = response => {
		console.log(`exporting ${experiment} ${exportName}`)
		var bytes = Uint8Array.from(atob(response.result), c => c.charCodeAt(0))
		downloadBytes(bytes, `${experiment}-${exportName}.mat`)
		if (callback) {
			callback()
		}
	}
}

function refreshParSetList() {
    var ref1 = generateUID()
	console.log('fetching parameter sets')
	connection.send(JSON.stringify({
		'type': 'query',
		'query': 'list_parameter_sets',
		'ref': ref1,
		'args': {}
	}))
	pending[ref1] = response => {
	    parSetNames = response.result
		document.querySelectorAll('.par-list').forEach(parList => {
		    parList.innerHTML = '' // remove existing
		    parSetNames.forEach(parSetName => {
		        var opt = document.createElement('option')
                opt.value = parSetName
                opt.innerHTML = parSetName
                parList.appendChild(opt)
		    })
		})
	}
}

function createTempControlTab() {
  var btn = document.getElementById('tempcontrol_tablink')
  btn.addEventListener('click', e => {
    openExperimentTab('tempcontrol')
  }, false)

  var pane = document.getElementById('tempcontrol')
  var pars = {
    setpoint: {
      unit: '°C'
    },
    P: {},
    I: {}
  }
  Object.keys(pars).forEach(pName => {
    var par = document.importNode(document.querySelector('#parameter_template').content, true)
    par.querySelector('label').for = 'tempcontrol-'+pName
    par.querySelector('label .par-name').innerText = pName
    if ('unit' in pars[pName]) {
      par.querySelector('label .par-unit').innerText = '('+pars[pName]['unit']+')'
    }
    par.querySelector('input').id = 'tempcontrol-'+pName
    par.querySelector('input').name = pName
    pane.querySelector('.parameters').appendChild(par)
  })

  document.querySelector('#tempcontrol button.save').addEventListener('click', e=> {
    var parameters = {}
    document.getElementById('tempcontrol').querySelectorAll('.parameters input').forEach(input => {
		parameters[input.name] = input.valueAsNumber
	})
	var ref = generateUID()
	connection.send(JSON.stringify({
		'type': 'command',
		'command': 'set_tempcontrol',
		'ref': ref,
		'args': parameters
	}))
  })

  var ref = generateUID()
  connection.send(JSON.stringify({
      'type': 'query',
      'query': 'get_tempcontrol',
      'ref': ref,
      'args': {}
  }))
  pending[ref] = response => {
    var par_values = response.result
    Object.keys(pars).forEach(pName => {
      document.getElementById('tempcontrol-'+pName).value = par_values[pName]
    })
  }
}

function createExperimentTab(exp) {
	var tab = document.importNode(document.querySelector('#experiment_tab_template').content, true)
	var btn = tab.querySelector('button')
	btn.id = exp.name+'_tablink'
	btn.innerText = exp.name.replace(/_/g, ' ')
	btn.addEventListener('click', e => {
		openExperimentTab(exp.name)
	}, false)
	document.getElementById('experiment_tabs').appendChild(tab)

	var pane = document.importNode(document.querySelector('#experiment_pane_template').content, true)
	pane.querySelector('div').id = exp.name
	pane.querySelector('.par-list').id = exp.name+'_par_list'
	pane.querySelector('.par-list-input').setAttribute('list', exp.name+'_par_list')
	pane.querySelector('.btn-load-par').addEventListener('click', e => {
		var ref = generateUID()
		connection.send(JSON.stringify({
			'type': 'query',
	    	'query': 'load_parameter_set',
	    	'ref': ref,
	    	'args': {
	    	    'par_set_name': document.getElementById(exp.name).querySelector('.par-list-input').value
	    	}
		}))
		pending[ref] = data => {
			document.getElementById(exp.name).querySelectorAll('.parameters input').forEach(input => {
			    if (data.result[input.name]!==undefined && data.result[input.name]!==null) {
				    input.value = data.result[input.name]
				}
			})
		}
	}, false)
	pane.querySelector('.btn-save-par').addEventListener('click', e => {
		var ref = generateUID()
		connection.send(JSON.stringify({
			'type': 'command',
	    	'command': 'save_parameter_set',
	    	'ref': ref,
	    	'args': {
	    	    'par_set_name': document.getElementById(exp.name).querySelector('.par-list-input').value,
	    	    'parameters': getParameters(exp.name)
	    	}
		}))
		pending[ref] = data => {
			refreshParSetList()
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
	// add plots
	var plotCount = 1
	var defaultPlotsDefined = exp.defaults && exp.defaults.plots
	if (defaultPlotsDefined) {
	  plotCount = exp.defaults.plots.length
	}
	for (var i=0; i<plotCount; i++) {
	  (function (i) { // need a new scope to remember the current i
        var plotbox = document.importNode(document.querySelector('#plot_template').content, true)
        var plotboxID = exp.name+'_plot_'+i
        plotbox.querySelector('.plot-box').id = plotboxID
        var plotList = plotbox.querySelector('.plot-list')
        exp.plots.forEach(plotName => {
            var opt = document.createElement('option')
            opt.value = plotName
            opt.innerHTML = plotName
            plotList.appendChild(opt)
        });

        if (defaultPlotsDefined) {
          plotList.value = exp.defaults.plots[i]
        }

        plotList.addEventListener('change', e => {
          plot(exp.name, i, e.target.value)
        })
        plotbox.querySelector('.btn-plot-save').addEventListener('click', e => {
          if (document.querySelector('#'+plotboxID+' .plot-save-format').value==='png') {
            saveSvgAsPng(document.querySelector('#'+plotboxID+' svg.plot'), 'plot.png', {
              scale: 2,
              backgroundColor: 'white'
            })
          }
        }, false)

        pane.querySelector('.plots-container').appendChild(plotbox)
	  })(i)
	}
	var exportList = pane.querySelector('.export-list')
	exp.exports.forEach(exportName => {
		var opt = document.createElement('option')
		opt.value = exportName
		opt.innerHTML = exportName
		exportList.appendChild(opt)
	})
	pane.querySelector('.btn-export').addEventListener('click', e => {
	    switch(document.getElementById(exp.name).querySelector('.export-format').value) {
	        case 'mat':
	            exportMATLAB(exp.name, exportList.value)
	            break
	        case 'csv':
	        default:
	            exportCSV(exp.name, exportList.value)
	    }
	})
	Object.keys(exp.parameters).forEach(pName => {
		var par = document.importNode(document.querySelector('#parameter_template').content, true)
		par.querySelector('label').for = exp.name+'-'+pName
		par.querySelector('label .par-name').innerText = pName
		if ('unit' in exp.parameters[pName]) {
		    par.querySelector('label .par-unit').innerText = '('+exp.parameters[pName]['unit']+')'
		}
		par.querySelector('input').id = exp.name+'-'+pName
		par.querySelector('input').name = pName
		pane.querySelector('.parameters').appendChild(par)
	})

//	Split([
//	    pane.querySelector('.plots-container'),
//	    pane.querySelector('.controls-parameters-container')],
//	    {
//	        sizes: [50, 50],
//	        direction: 'vertical',
//	        onDrag: () => {
//	            //Plotly.Plots.resize(document.getElementById(exp.name+'_plot_0'))
//	            //Plotly.Plots.resize(document.getElementById(exp.name+'_plot_1'))
//	        }
//	    })
//	Split([
//	    pane.querySelector('.plot-0'),
//	    pane.querySelector('.plot-1')],
//	    {
//	        sizes: [50, 50],
//	        onDrag: () => {
//	            //Plotly.Plots.resize(document.getElementById(exp.name+'_plot_0'))
//	            //Plotly.Plots.resize(document.getElementById(exp.name+'_plot_1'))
//	        }
//	    })
//	Split([
//	    pane.querySelector('.controls-container'),
//	    pane.querySelector('.parameters-container')],
//	    {
//	        sizes: [50, 50]
//	    })
	//populate pane
	document.getElementById('experiment_panes').appendChild(pane)
	//create blank plot
	//Plotly.newPlot(exp.name+'_plot_0', {}, {})
	//Plotly.newPlot(exp.name+'_plot_1', {}, {})
}

function loadLanguage(lang_name) {
    var ref = generateUID()
    connection.send(JSON.stringify({
        'type': 'query',
        'query': 'load_language',
        'ref': ref,
        'args': {
            'lang_name': lang_name
        }
    }))
    pending[ref] = data => {
        var lang = data.result
        console.log(lang)
        document.querySelectorAll('.parameters li').forEach(par_li => {
            var par_name = par_li.querySelector('input').name
            if (par_name in lang['parameters']) {
                par_li.querySelector('label .par-name').innerText = lang['parameters'][par_name]['label']
            }
        })
    }
}

function openExperimentTab(experimentName) {
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
    document.getElementById(experimentName).style.display = "flex";
    document.getElementById(experimentName+'_tablink').className += " active";
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

function downloadBytes(bytes, fileName) {
    var blob = new Blob([bytes]);
    var link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = fileName;
    link.click();
}

// polyfills
if (window.NodeList && !NodeList.prototype.forEach) {
    NodeList.prototype.forEach = function (callback, thisArg) {
        thisArg = thisArg || window;
        for (var i = 0; i < this.length; i++) {
            callback.call(thisArg, this[i], i, this);
        }
    };
}


document.addEventListener('DOMContentLoaded', function() {
    connect()
}, false);