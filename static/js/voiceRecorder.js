

(function(window) {
	var WORKER_PATH = "http://localhost:8100/static/js/worker.js";

	var Recorder = function(source, cfg) {
		var config = cfg || {};
		var bufferLen = config.bufferLen || 4096;
		this.context = source.context;
		if (!this.context.createScriptProcessor) {
			this.node = this.context.createJavaScriptNode(bufferLen, 2, 2);
		}
		else {
			this.node = this.context.createScriptProcessor(bufferLen, 2, 2);
		}

		var worker = new Worker(config.workerPath || WORKER_PATH);
		worker.postMessage({
			command: 'init',
			config: {
				sampleRate: this.context.sampleRate
			}
		});

		var recording = false;
		var currCallback;

		this.node.onaudioprocess = function(e) {
			if (!recording) {
				return;
			}
			worker.postMessage({
				command: 'record',
				buffer: [
					e.inputBuffer.getChannelData(0),
					e.inputBuffer.getChannelData(1)
				]
			});
		}

		this.configure = function(cfg) {
			for (var prop in cfg) {
				if (cfg.hasOwnProperty(prop)) {
					config[prop] = cfg[prop];
				}
			}
		}

		this.record = function() {
			recording = true;
		}

		this.stop = function() {
			recording = false;
		}

		this.clear = function() {
			worker.postMessage({
				command: 'clear'
			});
		}

		this.getBuffers = function(cb) {
			currCallback = cb || config.callback;
			worker.postMessage({
				command: 'getBuffers'
			});
		}

		this.exportWAV = function(cb, type) {
			currCallback = cb || config.callback;
			type = type || config.type || 'audio/wav';
			if (!currCallback) throw new Error('Callback not set');
			worker.postMessage({
				command: 'exportWAV',
				type: type
			});
		}

		this.exportMonoWAV = function(cb, type) {
			currCallback = cb || config.callback;
			type = type || config.type || 'audio/wav';
			if (!currCallback) throw new Error('Callback not set');
			worker.postMessage({
				command: 'exportMonoWAV',
				type: type
			});
		}

		this.exportPCM = function(cb, type) {
			currCallback = cb || config.callback;
			type = type || config.type || 'audio/x-pcm';
			if (!currCallback) throw new Error('Callback not set');
			worker.postMessage({
				command: 'exportPCM',
				type: type
			});
		}

		this.exportMonoPCM = function(cb, type) {
			currCallback = cb || config.callback;
			type = type || config.type || 'audio/x-pcm';
			if (!currCallback) throw new Error('Callback not set');
			worker.postMessage({
				command: 'exportMonoPCM',
				type: type
			});
		}

		worker.onmessage = function(e) {
			var blob = e.data;
			currCallback(blob);
		}

		source.connect(this.node);
		this.node.connect(this.context.destination);
	};

	Recorder.setupDownload = function(blob, filename) {
		var url = (window.URL || window.webkitURL).createObjectURL(blob);
		var link = document.getElementById("save");
		link.href = url;
		link.innerHTML = "Download: " + filename;
		formatIndex = filename.indexOf(".");
		format = filename.substring(formatIndex, formatIndex + 4)
		switch(format) {
			case ".wav":
				link.download = filename || "output.wav";
				break;
			case ".pcm":
				link.download = filename || "output.pcm";
				break;
		}
	}

	Recorder.setupPlayback = function(blob, filename) {
		var url = (window.URL || window.webkitURL).createObjectURL(blob);
		var player = document.getElementById("playback");
		player.src = url;
		player.load();
	}

	window.Recorder = Recorder;
	
})(window);