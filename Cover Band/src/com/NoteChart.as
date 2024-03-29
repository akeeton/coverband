package com {
	import flash.display.Shape;
	import flash.events.*;
	import flash.net.*;
	import flash.utils.Dictionary;
	import flash.utils.getTimer;
	
	import mx.core.UIComponent;
	import mx.managers.IFocusManagerComponent;
	
	[Bindable]
	public class NoteChart extends UIComponent implements IFocusManagerComponent {
		public static const RED:uint = 0xff0000;
		public static const YELLOW:uint = 0xffff00;
		public static const BLUE:uint = 0x0000ff;
		public static const GREEN:uint = 0x00ff00;
		public static const ORANGE:uint = 0xff9900;
		
		public static const DRUMS:uint = 0;
		public static const GUITAR:uint = 1;
		public static const BASS:uint = 2;
		// TODO: Make this better.
		public static const LANE_COLORS:Array = [
			[RED, YELLOW, BLUE, GREEN, ORANGE],
			[GREEN, RED, YELLOW, BLUE, ORANGE],
			[GREEN, RED, YELLOW, BLUE, ORANGE]];
		
		private const LINE_WIDTH:uint = 2;
		private const LINE_COLOR:uint = 0xffffff;
		private const HEIGHT_RATIO:Number = 0.5;
		
/* 		private const MILLISECONDS_PER_TICK:Number = 1000.0/10.0;
		private const SECONDS_PER_TICK:Number = MILLISECONDS_PER_TICK / 1000.0;
		private const TICKS_PER_SECOND:Number = 1.0 / SECONDS_PER_TICK;
 */		
		private const TICKS_PER_SECOND:Number = 16.0;
		private const SECONDS_PER_TICK:Number = 1.0 / TICKS_PER_SECOND;
		private const MILLISECONDS_PER_TICK:Number = SECONDS_PER_TICK * 1000.0;
		
		private const NOTE_HIT_WINDOW_TICKS:Number = TICKS_PER_SECOND / 2.0;
		
		private var _backgroundColor:uint = 0x000000;
		private var _laneWidth:Number;
		private var _chartFilename:String;
		private var _paused:Boolean = true;
		
		// Mapping from characters to lane number.
		private var keys:Dictionary = new Dictionary();
		// Array of indices that correspond to the nearest note in the notes
		// array for each lane.
		private var nearestNoteIndices:Array = [0, 0, 0, 0, 0];
		private var notes:Array;
		private var instrument:uint;
		private var numLanes:uint;
		private var prevTime:int = 0;
		
		// TODO: Make this private again.
		public var curTick:Number = 0;
		// Keep track of the height of the notes to avoid always getting it.
		private var noteHeight:Number;
		// y-coordinate of where the 0 tick begins.
		private var yZeroCoord:Number;
		
		// TODO: Make this private again?
		public var score:Score = new Score();

		/**
		 * Not much to do here.  Most of the initialization happens in init
		 * and finishInit, which deal with URL requests to get the necessary
		 * data.  init must be called separately.
		 * 
		 */		
		public function NoteChart() {
			super();
			// TODO: Make this better.
			// Default keys for each lane.
			keys['a'] = 0;
			keys['s'] = 1;
			keys['d'] = 2;
			keys['f'] = 3;
			keys['g'] = 4;
			// The rest of the functionality is handled by init.
		}
		
		/**
		 * Perform the real initialization here.  NoteChart depends on data
		 * that isn't present at creation time.  A lot of the work is passed
		 * off to completeURLRequestHandler since the rest depends on the chart
		 * file first being loaded.
		 * 
		 */		
		public function init(instrument:uint):void {
			this.instrument = instrument;
			yZeroCoord = height / 2.0;
			
			var loader:URLLoader = new URLLoader();
			configureURLLoaderListeners(loader);
			
			var chartPath:String = "../src/charts/" + _chartFilename + ".chart";
			trace("Attempting to load chart file: " + chartPath);
			var request:URLRequest = new URLRequest(chartPath);
				
			try {
				loader.load(request);
			} catch (error:Error) {
				trace("Unable to load requested document.");
			}
		}
		
		/**
		 * Finish the initialization that couldn't be done without the chart
		 * file data.
		 *  
		 * @param chartData Array of strings representing lines in the chart
		 * file.
		 * 
		 */		
		public function finishInit(chartData:Array):void {
			// Parse the file and create the notes.
			parseChartData(chartData);
			
			// Add a line where the 0-tick starts.
			var hitLine:Shape = new Shape();
			hitLine.graphics.moveTo(0, yZeroCoord);
			hitLine.graphics.lineStyle(LINE_WIDTH * 2, LINE_COLOR, 1, true);
			hitLine.graphics.lineTo(width, yZeroCoord);
			addChild(hitLine);
			
			// Add the graphical lane lines.
			var numLines:uint = numLanes + 1;
			for(var lineNum:uint = 0; lineNum < numLines; lineNum++) {
				var lineShape:Shape = new Shape();
				
				// Add one pixel to make everything line up properly.
				var x:uint = lineNum * (_laneWidth + LINE_WIDTH) + 1;
				lineShape.graphics.lineStyle(LINE_WIDTH, LINE_COLOR, 1, true);
				lineShape.graphics.moveTo(x, 0);
				lineShape.graphics.lineTo(x, height);
				
				addChild(lineShape);
			}
			
			focusManager.setFocus(this);
			// Setup the main updating event handler.
			addEventListener(Event.ENTER_FRAME, update);
			prevTime = getTimer();
		}
		
		/**
		 * Start (unpause) the game.
		 * 
		 */		
		public function play():void {
			_paused = false;
		}
		
		/**
		 * Pause the game.
		 * 
		 */
		public function pause():void {
			_paused = true;
		}
		
		/**
		 * Try to hit a note with the given key.
		 * 
		 * @param key A string representing the keyboard key the player hit.
		 * 
		 */
		public function tryHit(key:String):void {
			if (keys[key] != undefined) {
				var lane:uint = keys[key];
				var nearestNote:Note = getNearestNote(lane);
				var nearestNoteDelta:uint = Math.abs(
					nearestNote.tick - curTick);
					
				if (nearestNote.enabled &&
					nearestNoteDelta < NOTE_HIT_WINDOW_TICKS) {
					hitNote(nearestNote);
				} else {
					miss();
				}
			}
		}
		
		// TODO: Finish me.
		private function hitNote(note:Note):void {
			note.hit();
			score.addToScore(note);
		}

		private function miss():void {
			score.resetStreak();
		}
		
		/**
		 * Main game updating logic.  Called each frame.
		 * 
		 */
		private function update(event:Event):void {
			var curTime:int = getTimer();
			var diffTime:int = curTime - prevTime;
			var ticks:Number = diffTime / MILLISECONDS_PER_TICK;
			var dy:Number = ticks * noteHeight;
			
			prevTime = curTime;
			
			if (!_paused) {
				curTick += ticks;
					
				for (var laneNum:uint = 0; laneNum < notes.length; laneNum++) {
					var lane:Array = notes[laneNum];
					var nearestNoteIndex:uint = nearestNoteIndices[laneNum];
					var nearestNote:Note = lane[nearestNoteIndex];
					
					// Nothing to do -- no notes here.
					if (!nearestNote) continue;
					
					// Default: if the nearest note has been disabled, don't
					// let it be a contender for nearest note.
					var nearestNoteDelta:Number = Number.MAX_VALUE;
					
					// If the nearest note is still enabled then it might still
					// be the nearest this update.
					if (nearestNote.enabled)
						nearestNoteDelta = Math.abs(curTick - nearestNote.tick);
					
					for (var noteNum:uint = 0; noteNum < lane.length; noteNum++) {
						var note:Note = lane[noteNum];
						
						if (note.enabled) {
							var noteTicks:Number = Math.abs(curTick - note.tick);
							if (noteTicks < nearestNoteDelta) {
								nearestNoteDelta = noteTicks;
								nearestNoteIndex = noteNum;
							}
							note.centerY += dy;
							note.draw();
						}
					}
					
					nearestNoteIndices[laneNum] = nearestNoteIndex;
					// TODO: Remove this.
					(lane[nearestNoteIndex] as Note).highlight();
				}
			}
		}
		
		/**
		 * Unravel the chart file data and pass it to finishInit.
		 * 
		 * @param event Event containing the chart file data from the URL
		 * request.
		 * 
		 */		
		private function completeURLRequestHandler(event:Event):void {
			var loader:URLLoader = URLLoader(event.target);
			
			// Remove newlines (\n) and carriage returns (\r).  Do this in two
			// stages since the file may not contain carriage returns.
			var chartData:Array = (loader.data as String).split("\n");
			for (var i:uint = 0; i < chartData.length; i++)
				chartData[i] = (chartData[i] as String).replace("\r", "");
			
			finishInit(chartData);
		}

		/**
		 * Parse the chart file and create notes. 
		 * 
		 * @param chartData Lines from the chart file without newline
		 * characters.
		 * 
		 */
		private function parseChartData(chartData:Array):void {
			var tick:uint = 0;
			var curLine:String;
			
			var commentRE:RegExp = /\s*#.*/;
			var blankLineRE:RegExp = /^\s*$/;
			var multiplierRE:RegExp = /x[0-9]*/;
			
			for (var lineNum:uint = 0; lineNum < chartData.length; lineNum++) {
				var line:String = chartData[lineNum];
				var multiplier:uint = 1;
				
				// The number of lanes is a number at the beginning of the file.
				// Initialize the multi-dimensional Array of lanes X notes.
				if (lineNum == 0) {
					numLanes = parseInt(line);
					var numLines:uint = numLanes + 1;
					
					_laneWidth = (width - numLines * LINE_WIDTH) / numLanes;
					notes = new Array(numLanes);
					for (var i:uint = 0; i < numLanes; i++)
						notes[i] = new Array();
						
					continue;
				}
								
				if (line.match(commentRE) || line.match(blankLineRE)) {
					trace("Comment or blank line detected:\n" + line);
					continue;
				}
				
				// Get the multiplier (number of times to execute this line).
				var searchIndex:int = line.search(multiplierRE);
				if (searchIndex != -1) {
					var substring:String = line.substr(searchIndex);
					multiplier = parseInt(substring.substr(1));
				}
				
				// From here on out, each line should represent notes.
				// There must be at least as many notes as there are lanes.
				if (line.length < numLanes)
					throw new Error("Invalid chart file");
				
				// Extract the note data multiple times.
				for (var mult:uint = 0; mult < multiplier; mult++) {
					for (var lane:uint = 0; lane < numLanes; lane++) {
						var char:String = line.charAt(lane);
						
						if (char == '-')		// Blank note.
							continue;
						else if (char == 'n')	// Regular note.
							addNote(tick, lane);
						else					// TODO: Add more stuff!
							continue;
					}
					
					tick++;
				}
			}
		}
		
		private function addNote(tick:uint, lane:uint):void {
			var noteWidth:Number = _laneWidth;
			var noteHeight:Number = noteWidth * HEIGHT_RATIO;
			this.noteHeight = noteHeight;	// Save this for later.
			
			// +2 so everything lines up properly.
			var x:Number = lane * (LINE_WIDTH + _laneWidth) + 2;
			var centerY:Number = -(tick * noteHeight) + yZeroCoord;
			var note:Note = new Note(tick, lane, LANE_COLORS[instrument][lane],
				noteWidth, noteHeight, x, 0);
			note.centerY = centerY;
			(notes[lane] as Array).push(note);
			addChild(note);
		}
		
		private function configureURLLoaderListeners(dispatcher:IEventDispatcher):void {
			dispatcher.addEventListener(Event.COMPLETE, completeURLRequestHandler);
			dispatcher.addEventListener(IOErrorEvent.IO_ERROR, ioErrorHandler);
            /*
			dispatcher.addEventListener(Event.OPEN, openHandler);
			dispatcher.addEventListener(ProgressEvent.PROGRESS, progressHandler);
			dispatcher.addEventListener(SecurityErrorEvent.SECURITY_ERROR, securityErrorHandler);
			dispatcher.addEventListener(HTTPStatusEvent.HTTP_STATUS, httpStatusHandler);
            */
		}
		
        private function getNearestNote(lane:uint):Note {
			return notes[lane][nearestNoteIndices[lane]];
		}
		
		private function ioErrorHandler(event:IOErrorEvent):void {
			trace("ioErrorHandler: " + event.text);
		}
		
		public function get paused():Boolean {
			return _paused;
		}
		
		public function set backgroundColor(value:uint):void {
			_backgroundColor = value;
		}
		
		public function set chartFilename(value:String):void {
			_chartFilename = value;
		}
		
		override protected function updateDisplayList(unscaledWidth:Number, unscaledHeight:Number):void {
			super.updateDisplayList(unscaledWidth, unscaledHeight);
			graphics.clear();
			graphics.beginFill(_backgroundColor, alpha);
			graphics.drawRect(0, 0, unscaledWidth, unscaledHeight);
		}
		
		/**
		 * Placeholder for now.
		 * 
		 */		
		override protected function createChildren():void {
		}
	}
}