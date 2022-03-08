var version="0.1.4";
// possible options for mp3-format:
var mp3_mono_fast=0;
var mp3_mono_medium=1;
var mp3_stereo_medium=2;
var mp3_stereo_best=3;


// possible options for mp3 quality;
var mp3_8kbit=6;
var mp3_16kbit=7;
var mp3_20kbit=8;
var mp3_24kbit=9;
var mp3_32kbit=10;
var mp3_48kbit=11;
var mp3_56kbit=12;
var mp3_64kbit=13;
var mp3_80kbit=14;
var mp3_112kbit=15;
var mp3_128kbit=16;
var mp3_160kbit=17;

var streamFormat=mp3_stereo_medium;
var streamCompress=mp3_160kbit;
var eventFormat=mp3_stereo_medium;
var eventCompress=mp3_160kbit;

var fontMap={};
var fontNameMap={};
var fontNamesMap={"_sans":"Arial"};
//var fontNamesMap={"_sans":"Arial", "Arial":"Arial"};
var embedChars="¡¡¢ííªñ¿º¢@~*£%^&*()_-+=|\<>,./?#~–−–—·×°-ÀÁÂÆÇÈÉÊËÌÍÎÏÑÒÓÔŒÙÚÛÜÝŸ àáâæçèéêëìíîïñòóôœùúûüýÿ’«»º€?²־1³ñ"
function updatePublishSettings() {
	var profileXML = new XML(fl.getDocumentDOM().exportPublishProfileString('Default'));

	for(var i=0; i<profileXML.PublishFlashProperties.length(); i++){
		profileXML.PublishFlashProperties[i].StreamFormat=streamFormat;
		profileXML.PublishFlashProperties[i].StreamCompress=streamCompress;
		profileXML.PublishFlashProperties[i].EventFormat=eventFormat;
		profileXML.PublishFlashProperties[i].EventCompress=eventCompress;
	}
	fl.getDocumentDOM().importPublishProfileString(profileXML.toXMLString());

}
var inputVersionStr="";

function processDoc(replaceShapeTweens, switchAudioStreamsToEvent, publish, publishPath) {
	fontMap={};
	fontNameMap={};
	inputVersionStr="SWF was prepared by MW_PrepareLesson Thai 0.1.4"+fl.getDocumentDOM().pathURI; 	
	if(replaceShapeTweens || switchAudioStreamsToEvent){		
		var doc = fl.getDocumentDOM(); 
		var new_lib = doc.library;
		var libitems = new_lib.items;
		
		// find all fonts:
		for(var item_cnt=0; item_cnt<libitems.length; item_cnt++){
			var lib_item = libitems[item_cnt];
			//fl.trace(lib_item.itemType);
			if(lib_item.itemType=="font"){
				//fl.trace("found font "+lib_item.name+" font "+lib_item.font+" b "+lib_item.bold+" i "+lib_item.italic);
				var thisFontName=lib_item.name;
				/*if(fontNamesMap[thisFontName]){
					thisFontName=fontNamesMap[thisFontName];

				}*/
				var thisFontFont=lib_item.font;
				/*if(fontNamesMap[thisFontFont]){
					thisFontFont=fontNamesMap[thisFontFont];

				}*/
				if(!fontNameMap[thisFontName]){
					fontMap[thisFontFont]=fontNameMap[thisFontName]={};	
				}
				if(lib_item.bold && lib_item.italic){
					fontNameMap[thisFontName].boldItalic={item:lib_item, items:[]};					
				}
				else if(lib_item.bold && !lib_item.italic){
					fontNameMap[thisFontName].bold={item:lib_item, items:[]};								
				}
				else if(!lib_item.bold && lib_item.italic){
					fontNameMap[thisFontName].italic={item:lib_item, items:[]};								
				}
				else if(!lib_item.bold && !lib_item.italic){
					fontNameMap[thisFontName].standart={item:lib_item, items:[]};								
				}
					lib_item.embedRanges ="1|2|3|4|5|21|22|15";
					//	rangeEmbed:"1|2|3|4|5|21|22|15",
					lib_item.embeddedCharacters = embedChars;
			}
		}	
			
		
		var libitems = new_lib.items;
		
		for(var item_cnt=0; item_cnt<libitems.length; item_cnt++){
			var lib_item = libitems[item_cnt];			
			if((lib_item.itemType=="movie clip")||(lib_item.itemType=="graphic")||(lib_item.itemType=="button")){
				process_timeline(lib_item.timeline, replaceShapeTweens, switchAudioStreamsToEvent);
			}
			if(lib_item.itemType=="sound"){
     lib_item.compressionType="Default";				
}
		}	
		for(var item_cnt=0; item_cnt<doc.timelines.length; item_cnt++){
			process_timeline(doc.timelines[item_cnt], replaceShapeTweens, switchAudioStreamsToEvent, true);
		}
		
		// create new fonts if needed + take care that all texts are  connected to fonts
		
		for (var key in fontMap){
			/*
			fl.trace("fontmap"+fontMap[key]+key);
			fl.trace("fontmap"+fontMap[key].bold);
			fl.trace("fontmap"+fontMap[key].italic);
			fl.trace("fontmap"+fontMap[key].boldItalic);
			fl.trace("fontmap"+fontMap[key].standart);*/

			if(fontMap[key].bold){				
				if(!fontMap[key].bold.item){
					fl.trace("create bold font for "+key);
					fl.getDocumentDOM().library.addNewItem("font", key+"-bold");
					var fontIndex = fl.getDocumentDOM().library.findItemIndex( key+"-bold" );
					var fontItem = fl.getDocumentDOM().library.items[fontIndex];
					fontItem.font = key;
					fontItem.bold = true;
					fontItem.embedRanges = "1|2|3|4|5|21|22|15"
					fontItem.embeddedCharacters = embedChars;
				}
				for(var key2 in fontMap[key].bold.items){
					fontMap[key].bold.items[key2].setTextAttr("face", key);
					fontMap[key].bold.items[key2].setTextAttr("bold", true);
					fontMap[key].bold.items[key2].setTextAttr("italic", false)
				}
			}
			if(fontMap[key].italic){
				
				if(!fontMap[key].italic.item){
					fl.trace("create italic font for "+key);
					fl.getDocumentDOM().library.addNewItem("font", key+"-italic");
					var fontIndex = fl.getDocumentDOM().library.findItemIndex( key+"-italic" );
					var fontItem = fl.getDocumentDOM().library.items[fontIndex];
					fontItem.font = key;
					fontItem.italic = true;
					fontItem.embedRanges = "1|2|3|4|5|21|22|15";
					fontItem.embeddedCharacters = embedChars;
				}
				for(var key2 in fontMap[key].italic.items){
					fontMap[key].italic.items[key2].setTextAttr("face", key);
					fontMap[key].italic.items[key2].setTextAttr("bold", false);
					fontMap[key].italic.items[key2].setTextAttr("italic", true);
				}
			}
			if(fontMap[key].boldItalic){
				if(!fontMap[key].boldItalic.item){
					fl.trace("create boldItalic font for "+key);
					fl.getDocumentDOM().library.addNewItem("font", key+"-boldItalic");
					var fontIndex = fl.getDocumentDOM().library.findItemIndex( key+"-boldItalic" );
					var fontItem = fl.getDocumentDOM().library.items[fontIndex];
					fontItem.font = key;
					fontItem.italic = true;
					fontItem.bold = true;
					fontItem.embedRanges = "1|2|3|4|5|21|22|15";
					fontItem.embeddedCharacters = embedChars;
				}
				for(var key2 in fontMap[key].boldItalic.items){
					fontMap[key].boldItalic.items[key2].setTextAttr("face", key);
					fontMap[key].boldItalic.items[key2].setTextAttr("bold", true);
					fontMap[key].boldItalic.items[key2].setTextAttr("italic", true);
				}
			}
			if(fontMap[key].standart){
				fl.trace("fontmap"+fontMap[key].standart.item);
				if(!fontMap[key].standart.item){
					fl.trace("create standart font for "+key);
					fl.getDocumentDOM().library.addNewItem("font", key);
					var fontIndex = fl.getDocumentDOM().library.findItemIndex( key );
					var fontItem = fl.getDocumentDOM().library.items[fontIndex];
					fontItem.font = key;
					fontItem.embedRanges = "1|2|3|4|5|21|22|15";
					fontItem.embeddedCharacters = embedChars;
				}
				for(var key2 in fontMap[key].standart.items){
					fontMap[key].standart.items[key2].setTextAttr("face", key);
					fontMap[key].standart.items[key2].setTextAttr("bold", false);
					fontMap[key].standart.items[key2].setTextAttr("italic", false);
				}				
			}
		}
	}
	updatePublishSettings();
	if(publish){	
  		//fl.trace("publish document");		
		fl.getDocumentDOM().exportSWF(publishPath, true);
		//fl.getDocumentDOM().publish();
	}
}

function process_timeline(_timeline, replaceShapeTweens, switchAudioStreamsToEvent, isScene) {
	var timeline = _timeline;
	var layerCount = timeline.layerCount;
	var lastFrameIsTween=false;
	var startFrame=0;
	var endFrame=0;
	var tweentype="";
	var kf=0;
	var frame=null;
	var frame2=null;
	var instance_names={};
	while (layerCount--){
		
		var layer = timeline.layers[layerCount];
		
		var frameCount = layer.frameCount;
		var lastFrameSyncedSound=null;
		for(var i=0; i<frameCount; i++){
			frame = layer.frames[i];
			if ( frame == undefined){
				continue;
			}
			if(isScene && inputVersionStr!="" && frame.actionScript && frame.actionScript!=""){
				var script=frame.actionScript;
				var checkScriptForVersionLog=script.split(");//AwayJSInternal");
				if(checkScriptForVersionLog.length>1){
					script=checkScriptForVersionLog.pop();					
				};
				frame.actionScript="trace('! "+inputVersionStr+"');//AwayJSInternal\n"+script;
				inputVersionStr="";					
			}
			if(switchAudioStreamsToEvent && frame.soundLibraryItem){
				if(frame.soundSync == 'stream'){
					frame.soundSync="event";	
					lastFrameSyncedSound=frame.soundLibraryItem;
					fl.trace("timeline "+timeline.name+" layer: "+layer.name+" frame-num: "+i+" found a Audio with sync=stream and changed it to sync=event");	
				};
			}
			else if(switchAudioStreamsToEvent && lastFrameSyncedSound){
				fl.trace("insert stop command for sound "+timeline.name+" layer: "+layer.name+" frame-num: "+i);
				frame.soundLibraryItem=lastFrameSyncedSound;
				frame.soundSync="stop";	
				lastFrameSyncedSound=null;
			}
			
			startFrame=i;
			endFrame=i+frame.duration;
			i+=frame.duration-1;
			tweentype = frame.tweenType;
			if(replaceShapeTweens && tweentype=="shape"){
				i++;
				//fl.trace("found shaapetween frame "+startFrame+" end "+endFrame);
				var numFrames=0
				for(kf=endFrame; kf<frameCount; kf++){
					
					frame2 = layer.frames[kf]
					if ( frame2 == undefined){
						//fl.trace("found undefined frame "+kf);
						//i=kf-1;
						break;
					}
					if(frame2.tweenType=="shape"){
						endFrame+=frame2.duration;
						//fl.trace("found another shape frame "+endFrame);
						kf+=frame2.duration-1;
						i=kf;
					}
					else{
						//fl.trace("stop");
						i=kf-1;
						break;							
					}
						
				}
				timeline.setSelectedLayers(layerCount);
				timeline.setSelectedFrames(startFrame, endFrame);
				timeline.convertToKeyframes(startFrame, endFrame);
				timeline.setFrameProperty('tweenType', 'none');
				fl.trace("timeline "+timeline.name+" layer: "+layer.name+" frame-range: "+startFrame+" - "+endFrame+" found a Shapetween and converted it to FrameByFrame-Animation");	
				
			}
			if(!instance_names[startFrame]){
				instance_names[startFrame]=[];
			}
			var elems = frame.elements;	
            var p = elems.length;
            while (p--){
                var child=elems[p];
				if(instance_names[startFrame].indexOf(child.name)!=-1){
					fl.trace("WARNING !!!: duplicate instance-name "+child.name+" in "+timeline.name+" frame "+startFrame);
				}
				instance_names[startFrame].push(child.name);
                if(child.elementType == "text")
                {
                    child.fontRenderingMode="standard";
                    var thisFontName=child.getTextAttr("face");
                    if(!thisFontName){
                        thisFontName="Arial";
                    }
					//fl.trace("found font on textfield "+thisFontName)
                    thisFontName=thisFontName.replace("*", "");
                    if(fontNamesMap[thisFontName]){
                        thisFontName=fontNamesMap[thisFontName];
                    }
					//fl.trace("found font on textfield2 "+thisFontName)
                    if(!fontMap[thisFontName] && !fontNameMap[thisFontName]){
                        fontMap[thisFontName]=fontNameMap[thisFontName]={};
                    }
                    var myFont=fontMap[thisFontName];
                    if(!myFont){
                        myFont=fontNameMap[thisFontName];
                    }
                    if(child.getTextAttr("bold") && child.getTextAttr("italic")){
                        if(!myFont.boldItalic){
                            myFont.boldItalic={item:null, items:[]};	
                        }		
                        myFont.boldItalic.items.push(child);
                    }
                    else if(child.getTextAttr("bold") && !child.getTextAttr("italic")){
                        if(!myFont.bold){
                            myFont.bold={item:null, items:[]};	
                        }					
                        myFont.bold.items.push(child);
                    }
                    else if(!child.getTextAttr("bold") && child.getTextAttr("italic")){
                        if(!myFont.italic){
                            myFont.italic={item:null, items:[]};	
                        }		
                        myFont.italic.items.push(child);		
                    }
                    else if(!child.getTextAttr("bold") && !child.getTextAttr("italic")){
                        if(!myFont.standart){
                            myFont.standart={item:null, items:[]};		
                        }			
                        myFont.standart.items.push(child);	
                    }
                }			
			}			
        }
	}
}

// xmlPanel returns an Object with values of the dialog. 
fl.trace(fl.configURI);
fl.outputPanel.clear();
if(fl.getDocumentDOM()==null){
	fl.trace("No Active Document");
}
else{
	
	var xmlPanelOutput = fl.getDocumentDOM().xmlPanel(fl.configURI + "/Commands/MWPrepareLessonDialog.xml");
	if (xmlPanelOutput.dismiss == "accept") // user confirms dialog
	{
  		fl.trace("starting script");
		fl.trace("replace Shapetweens:            "+xmlPanelOutput.convertShapeTweens);
		fl.trace("switch Audio-Streams to Events: "+xmlPanelOutput.switchSounds );	
		fl.trace("process main-lesson FLAs: "+xmlPanelOutput.mainLessons );	
		fl.trace("process sound FLAs: "+xmlPanelOutput.soundFlas );	
		fl.trace("process paper-based FLAs: "+xmlPanelOutput.paperBased );	
        fl.trace("publish:                        "+xmlPanelOutput.publishDoc );	
        
		if(xmlPanelOutput.convertShapeTweens=="false" && xmlPanelOutput.switchSounds=="false" && xmlPanelOutput.publishDoc=="false"){				
			fl.trace("\nnothing to do");
		}
		else if(xmlPanelOutput.onlyOpenDoc && xmlPanelOutput.onlyOpenDoc!="false"){			
			var filePathURI = fl.getDocumentDOM().pathURI; 		
			if(filePathURI==null || filePathURI==undefined){
				fl.trace("Save your document first");
			}
			else{
				fl.trace("\nActing on active document");
				filePathURI=filePathURI.replace(".fla", ".swf");
				processDoc(xmlPanelOutput.convertShapeTweens=="true" , xmlPanelOutput.switchSounds=="true", xmlPanelOutput.publishDoc=="true", filePathURI);			
				fl.trace("DONE!");		
			}
		}
		else {			
			//var folder = "file:///D|/away2017/mw_repo/mw_swf/bin/swf/mw_swf_next100";
			var folder = fl.browseForFolderURL("Choose a input folder");
			fl.trace(folder);
			if(folder){				
				var directories = FLfile.listFolder(folder, "directories"); //folders 
				for (dir in directories) {
					var curDir = directories[dir];
					fl.trace("\nProcessing Direcoty: "+curDir);			
					var files = FLfile.listFolder(folder+"/"+curDir + "/*.fla", "files");
					var level=-1;
					var flaName="";
					var audioflaName="";
					for (file in files) {
						var curFile = files[file];
						curFile=curFile.replace(".fla", "");
						//fl.trace("found a fla "+curFile);	
						var hasSameName =curFile.indexOf(curDir);
						if(hasSameName==0){
							// the file-name starts with the dir-name
							var suffix=curFile.replace(curDir, "");
							if(suffix==""){
								if(level==-1){
									flaName=curFile;		
									//fl.trace("no suffix "+flaName);								
								}								
							}
							else if(suffix=="specialcase"){
								level=1000000;
								flaName=curFile;
								//fl.trace("specialcase suffix higher than all others "+flaName);		
							}
							else{
								suffix=suffix.replace(/[^0-9.]/g, "");
								var newLevel=parseInt(suffix);
								//fl.trace("newLevel "+newLevel);	
								if(newLevel>=level){
									level=newLevel;
									flaName=curFile;		
									//fl.trace("higher suffix "+flaName);		
								}											
								
							}							
						}
						else{
							// the file-name does not start with the dir-name - could still be a sound fla
							curFile=curFile.replace("As", "Ax");
							var hasSameName =curFile.indexOf(curDir);
							if(hasSameName==0){
								audioflaName=curFile=curFile.replace("Ax", "As");
							}
							
							
						}
					}
					if(xmlPanelOutput.mainLessons=="true"){						
						if(flaName==""){
							fl.trace("Could not find a lesson-fla for the directory "+curDir);
						}
						else{
							fl.trace("processing lesson-fla "+flaName);

							fl.openDocument(folder+"/"+curDir+"/"+flaName+".fla");
							//processDoc(xmlPanelOutput.convertShapeTweens=="true" , xmlPanelOutput.switchSounds=="true", xmlPanelOutput.publishDoc=="true", folder+"/"+curDir+"/"+curDir+".swf");
								processDoc(xmlPanelOutput.convertShapeTweens=="true" , xmlPanelOutput.switchSounds=="true", xmlPanelOutput.publishDoc=="true", "file:///C|/CMP/EX/"+"/"+curDir+".swf");
							fl.getDocumentDOM().revert();
							fl.closeDocument(fl.getDocumentDOM());
							
							
						}
					}
					if(xmlPanelOutput.soundFlas=="true"){		
										
						if(flaName==""){
							fl.trace("Could not find a lesson-fla for the directory "+curDir);
						}
						else{
							if(audioflaName){
								fl.trace("processing audio-fla "+audioflaName);
								fl.openDocument(folder+"/"+curDir+"/"+audioflaName+".fla");							
								processDoc(false , false, xmlPanelOutput.publishDoc=="true", folder+"/"+curDir+"/"+audioflaName+".swf");
								fl.getDocumentDOM().revert();
								fl.closeDocument(fl.getDocumentDOM());							
							}
						}
					}
					if(xmlPanelOutput.paperBased=="true"){		
										
						var subDirectories = FLfile.listFolder(folder+"/"+curDir, "directories"); //folders 
						for (subDir in subDirectories) {
							var curSubDir = subDirectories[subDir];
							if(curSubDir=="paper-based"){								
								var pbFiles = FLfile.listFolder(folder+"/"+curDir+"/"+curSubDir + "/*.fla", "files");
								for (pbFile in pbFiles) {
									var curPbFile = pbFiles[pbFile];
									curPbFile=curPbFile.replace(".fla", "");
									fl.openDocument(folder+"/"+curDir+"/"+curSubDir+"/"+curPbFile+".fla");							

									processDoc(xmlPanelOutput.convertShapeTweens=="true" , xmlPanelOutput.switchSounds=="true", xmlPanelOutput.publishDoc=="true", "file:///C|/CMP/PB_NEW/"+curPbFile+".swf");
									fl.getDocumentDOM().revert();
									fl.closeDocument(fl.getDocumentDOM());	
								}
							}
						}
					}
					
					
				}
			}		
			fl.trace("DONE!");		
		}
		
		
	}
	else // user canceled dialog
	{
	  
	}
}
//updatePublishSettings();