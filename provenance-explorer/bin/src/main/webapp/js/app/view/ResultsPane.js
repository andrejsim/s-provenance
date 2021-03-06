
var currentRun

var level=1;

 var colour = {
      orange:"#EEB211",
      darkblue:"#21526a",
      purple:"#941e5e",
      limegreen:"#c1d72e",
      darkgreen:"#619b45",
      lightblue:"#009fc3",
      pink:"#d11b67",    
    }
 
function dephtree(data,graph,parent){
var col=colour.darkblue;
if (parent){
	 	col=colour.orange
		 
		}
		
//var node = graph.addNode(data["id"],{label:data["_id"].substring(0,5),'color':col, 'shape':'dot', 'radius':19,'alpha':1,mass:2})
//node.runId=data["runId"]
var nodea = graph.addNode(data["id"],{label:data["_id"].substring(0,5),'color':col, 'shape':'dot', 'radius':19,'alpha':1,mass:2})

if (parent){
	 	 
		graph.addEdge(parent,nodea,{length:0.75,directed: true})
 	   
		}       

if(data["derivationIds"].length>0 && typeof data["derivationIds"]!="undefined" )
{ 
for(var i=0;i<data["derivationIds"].length;i++)
{ 
  if(data["derivationIds"][i]["wasDerivedFrom"])
	 {  
	   dephtree(data["derivationIds"][i]["wasDerivedFrom"],graph,nodea)
 	 }
}
}	

 

};


function getMetadata(data,graph){
	 
/*var node = graph.addNode(data["streams"][0]["id"]+"meata",{label:data["streams"][0]["id"] })
graph.addEdge(node.name,data["streams"][0]["id"],{label:"wasGeneratedBy"})*/
if(data["artifacts"][0]["location"]!=""){
	var loc=data["artifacts"][0]["location"].replace(/file:\/\/[\w-]+[\w.\/]+[\w\/]+pub/,"/intermediate/")
//	loc=loc.replace(//,"")
 
	 
	var params = graph.addNode(data["artifacts"][0]["id"]+"loc",{label:JSON.stringify(data["artifacts"][0]["location"]),'color':colour.darkgreen,'link':loc})
	
    graph.addEdge(params.name,data["artifacts"][0]["id"],{label:"location"})
    }


}




function addBranch(url){

$.getJSON(url, function(data) {
dephtree(data,sys,null)
});
}



function newGraph(url){
sys.prune();
addBranch(url)
 
}



function addMeta(url){

$.getJSON(url, function(data) {
getMetadata(data,sys)
});
}



  				
 
var activityStore = Ext.create('CF.store.ActivityStore');

var artifactStore = Ext.create('CF.store.ArtifactStore');

var workflowStore = Ext.create('CF.store.WorkflowStore');

var action = Ext.create('Ext.Action', {
        text: 'Open Run',
        iconCls: 'icon-add',
        handler: function(){
            workflowStore.setProxy({
 											type: 'ajax',
  							  		        url: '/j2ep-1.0/prov/workflow/allruns',
  							          reader: {
   			  				             root: 'runIds',
  						                 totalProperty: 'totalCount'
  						           },
  						  simpleSortMode: true
    
     					   } 					    
    					);
         		workflowStore.load()
         		Ext.create('Ext.window.Window', {
  								   title:'Workflows Runs',
 								   height: 230,
								   width: 800,
							       layout: 'fit',
						           items:[ Ext.create('CF.view.WorlflowSelection')]
      			 			     	
								}).show();
        }
    });
    
var refreshAction = Ext.create('Ext.Action', {
        text: 'Refresh',
        iconCls: 'icon-add',
        handler: function(){
            activityStore.setProxy({
 											type: 'ajax',
  							  		        url: '/j2ep-1.0/prov/run/?id='+currentRun,
  							          reader: {
   			  				             root: 'activities',
  						                 totalProperty: 'totalCount'
  						           },
  						  simpleSortMode: true
    
     					   } 					    
    					);
         		activityStore.load()
         		 
        }
    });












Ext.define('CF.view.WorlflowSelection', {
		
	 width: 780,
	  
	 height:200,
	extend: 'Ext.grid.Panel',
    
    id:'worklflowselection',
      requires: [
    	'CF.store.WorkflowStore',
    	'Ext.grid.plugin.BufferedRenderer'
    		],
    store:workflowStore,
    trackOver: true,
    autoScroll: true,
    verticalScroller: {
    xtype: 'paginggridscroller'
  },
  
  
        
 plugins : [{
            ptype: 'bufferedrenderer',
           }
            ],
            
            
    selModel: {
            pruneRemoved: false
        },
        
    initComponent: function() {
        Ext.apply(this, {
            border: false,
            
            loadMask: true,
		   
            columns: [
             
            {header: 'ID',   dataIndex:'runId', flex: 5, sortable: false},
             
            {header: 'Name',   dataIndex:'name', flex: 3, sortable: true,
            groupable: false}, // custom mapping
             
			],
		flex: 1,
		
 	
            
            
           
        });
        this.callParent(arguments);
       
        // store singleton selection model instance
       
         
    },
    
     viewConfig: {
    listeners: {
        itemdblclick: function(dataview, record, item, index, e) {
         
         		activityStore.setProxy({
          					         type: 'ajax',
  							          url: '/j2ep-1.0/prov/run/?id='+record.get("runId"),
  							          reader: {
   									             root: 'activities',
  									             totalProperty: 'totalCount'
  									          },
  									  simpleSortMode: true
    
     					   });
         		activityStore.load({ callback: function() {currentRun=record.get("runId")}})
            
        }
    }
}
    
    
});



  


Ext.define('CF.view.ActivityMonitor', {
		region: 'west',
	 width: '35%',
	 title: 'Processing Elements - Double Click on the PE to access the produced Sream Data',
	 height: '100%',
	extend: 'Ext.grid.Panel',
    alias : 'widget.activitymonitor',
    id:'activitymonitor',
      requires: [
    	'CF.store.ActivityStore',
    	'Ext.grid.plugin.BufferedRenderer'
    		],
  
    store:activityStore,
    trackOver: true,
    autoScroll: true,
    collapsible: true,
    verticalScroller: {
    xtype: 'paginggridscroller'
  },
  
  dockedItems: {
            itemId: 'toolbar',
            xtype: 'toolbar',
            items: [
                 
                action,
                refreshAction
            ]
        },
        
 plugins : [{
            ptype: 'bufferedrenderer',
           }
            ],
            
            
    selModel: {
            pruneRemoved: false
        },
        
    initComponent: function() {
        Ext.apply(this, {
            border: false,
            
            loadMask: true,
		   
            columns: [
             
            {header: 'Instance',   dataIndex:'instanceId', flex: 3, sortable: false},
             
            {header: 'Date',   dataIndex:'creationDate', flex: 3, sortable: true,
            groupable: false}, // custom mapping
            {header: 'Error',   dataIndex:'error', flex: 3, sortable: false}, // custom mapping
            {header: 'IterationIndex',   dataIndex:'iterationIndex', flex: 3, sortable: false} // custom mapping

			],
		flex: 1,
		
 	
            
            
           
        });
        this.callParent(arguments);
       
        // store singleton selection model instance
       
         
    },
    
     viewConfig: {
    listeners: {
        itemdblclick: function(dataview, record, item, index, e) {
         
         		artifactStore.setProxy({
 						           type : 'ajax',
  							       url: '/j2ep-1.0/prov/artifacts/generatedby?iterationid='+record.get("ID"),
  				         
 					               reader: {
   						             root: 'artifacts',
  						             totalProperty: 'totalCount'
  						        	  }
  						 			  
    
     					    
    					});
         		artifactStore.load()
            
        }
    }
}
    
    
});
			
			
function viewDataImage(url)
{var loc=url.replace(/file:\/\/[\w-]+[\w.\/]+[\w\/]+pub/,"/intermediate-nas/")
//	
Ext.create('Ext.window.Window', {
  								   title:'Data File',
 								   height: 500,
								   width: 900,
							       layout: 'fit',
						           items:[ {   overflowY: 'auto',
   										     overflowX: 'auto',
    	
 									       xtype: 'panel',
   										   html:'<img src="'+loc+'"/>'
    									} ]
      			 			     	
								}).show();
}
			
//activityStore.load();


var searchartifacts = Ext.create('Ext.Action', {
        text: 'Search',
        iconCls: 'icon-add',
        handler: function(){
      
         		Ext.create('Ext.window.Window', {
  								   title:'Search Stream Data',
 								   height: 230,
								   width: 400,
							       layout: 'fit',
						           items:[ {xtype:'form',
						           // The fields
  											  defaultType: 'textfield',
										    items: [{
  												      fieldLabel: 'Annotation keys (CSV)',
 												       name: 'keys',
 												       allowBlank: false
  													  },{
 											       fieldLabel: 'Annotation values (CSV)',
 											       name: 'values',
 											       allowBlank: false
  													  }],
						           			
						           	
						           			buttons: [ {
  											      text: 'Search',
     											   formBind: true, //only enabled once the form is valid
    											     
  											      handler: function() {
 										           var form = this.up('form').getForm();
  													          if (form.isValid()) {
   													              artifactStore.setProxy({
									 						           type : 'ajax',
  							      									   url: '/j2ep-1.0/prov/artifacts/annotations?'+form.getValues(true),
  				         
 					   									               reader: {
   						 											            root: 'artifacts',
  																	            totalProperty: 'totalCount'
  						        	  											}
  						 			  									});
        													 		artifactStore.load()
         														   }
   															     }
												    }]
      			 			     				}]
								}).show();
        }
    });		
 
function renderStream(value, p, record) {
        return Ext.String.format(
            '<div class="search-item" style="border:2px solid; box-shadow: 10px 10px 5px #888888;"><br/>'+
            '<strong>Chunk ID: <a href="javascript:newGraph(\'/j2ep-1.0/prov/trace/{0}?level='+level+'\')">{0} </a></strong> <br/> <br/>'+
            '<strong>Generated By :</strong> {1} <br/> <br/>'+
            '<strong>Run Id :</strong> {6} <br/> <br/>'+
            '<strong>Parameters :</strong>{2}<br/> <br/>'+
            '<strong>Annotations :</strong>{3}<br/> <br/>'+
            '<strong>Location :</strong><a href="javascript:viewDataImage(\'{4}\')">{4}</a><br/> <br/>'+
            '<strong>Content:</strong><div style="height:350px;background-color:#6495ed; color:white; border:2px solid; box-shadow: 10px 10px 5px #888888;overflow: auto; width :700px; max-height:100px;"> {5}</div><br/>'+
        	'</div>',
            record.data.ID,
            record.data.wasGeneratedBy,
            record.data.parameters,
            record.data.annotations,
            record.data.location,
            record.data.content,
            record.data.runId
        );		
        }
			
Ext.define('CF.view.ArtifactView', {
     extend:'Ext.grid.Panel',
     region: 'south',
     width: '65%',
     store: artifactStore,
     hideHeaders: true,
     split: true,
     collapsible: true,
     title: 'Stream Data - Double Click to navigate the Data Derivation Graph',
     alias: 'widget.artifactview',
       requires: [
    	'CF.store.ArtifactStore',
    	'Ext.grid.plugin.BufferedRenderer'
    		],
   	 height: 200,
     autoSroll:true,
   	 plugins : [{
            ptype: 'bufferedrenderer',
           }
            ],
   	 
   	  columns: [
             
            { dataIndex: 'ID', field: 'ID', flex:3, renderer: renderStream}
            ],
   
     dockedItems: {
            itemId: 'toolbar',
            xtype: 'toolbar',
            items: [
                 
                searchartifacts
                 
            ]
        },
       
    });
 

 

Ext.define('CF.view.ResultsPane', {
     extend:'Ext.panel.Panel',
     alias: 'widget.resultpane',
    
    
    // configure how to read the XML Data
  			region: 'center',
            title: 'Data Derivations Graph',
            split: true,
		    collapsible: true, 
    		 require: ['Ext.layout.container.Fit',
 			   'Ext.toolbar.Paging',
 			   'Ext.ux.form.SearchField',
  				'Ext.ux.DataTip'],
  		 	 height: 800,
 		    autoSroll:true,
   
     layout: 'fit',
   
    items: [ 
    {   overflowY: 'auto',
        overflowX: 'auto',
    	
    	region: 'center',
    	 
        xtype: 'panel',
        html:'<strong>Double Click on the Yellow Dots to expand. Right Click to see the content</strong><center> <div style="width:100%" height="700"><canvas id="viewportprov" width="1200" height="500"></canvas></div></center>'
    }
    
   ],
   
   listeners: {
        render: function() {
        
        	$(viewportprov).bind('contextmenu', function(e){
            var pos = $(this).offset();
            var p = {x:e.pageX-pos.left, y:e.pageY-pos.top}
            selected = nearest = dragged = sys.nearest(p);
           
            if (selected.node !== null){
            // dragged.node.tempMass = 10000
                dragged.node.fixed = true;
             //   addMeta('/j2ep-1.0/prov/streamchunk/?runid='+currentRun+'&id='+selected.node.name)
            	
                artifactStore.setProxy({
 						           type : 'ajax',
  							       url: '/j2ep-1.0/prov/artifacts/run?runid='+currentRun+'&dataid='+selected.node.name,
  				         
 					               reader: {
   						             root: 'artifacts',
  						             totalProperty: 'totalCount'
  						        	  }
  						 			  
    
     					    
    					});
         		artifactStore.load()
            
            }
            return false;
        })
 

		$(viewportprov).bind('dblclick', function(e){
            var pos = $(this).offset();
            var p = {x:e.pageX-pos.left, y:e.pageY-pos.top}
            selected = nearest = dragged = sys.nearest(p);
           
            if (selected.node !== null){
            // dragged.node.tempMass = 10000
                dragged.node.fixed = true;
                addBranch('/j2ep-1.0/prov/trace/'+selected.node.name+"?level="+level)
            }
            return false;
        })
            sys.renderer = Renderer("#viewportprov");
	//		
        }
    }
});

    
