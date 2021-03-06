from twisted.web import server, resource, http
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet import defer
import provenance as provenance
import json
import csv
import StringIO
import traceback
import datetime
from twisted.python import log
from prov.model import ProvDocument, Namespace, Literal, PROV, Identifier
from twisted.web.server import NOT_DONE_YET

 
 
 
def wait(seconds, result=None):
    """Returns a deferred that will be fired later"""
    d = defer.Deferred()
    
    reactor.callLater(seconds, d.callback, result)
    return d


class RootResource(resource.Resource):

    def __init__(self, provenanceStore):
        self.provenanceStore = provenanceStore
        resource.Resource.__init__(self)
        
        'Extraction and updates of activities relative to a specific run'
        self.putChild('activities', ActivitiesHandler(self.provenanceStore))
        'Extraction of overall information about submitted workflows and insertion of new traces'
        self.putChild('workflow', WorkflowHandler(self.provenanceStore))
        'Extraction of a lineage trace'
        self.putChild('wasDerivedFrom', TraceHandler(self.provenanceStore))
        self.putChild('derivedData', DerivedDataHandler(self.provenanceStore))
        ' Extraction of output metadata'
        self.putChild('entities', EntitiesHandler(self.provenanceStore))
        ' Creation of new processing metadata'
        self.putChild('solver', SolversHandler(self.provenanceStore))
         
        
              
 
    def getChild(self, path, request):
        return ShowRun(self.provenanceStore, "")

class SolversHandler(resource.Resource):

    def __init__(self, provenanceStore):
        self.provenanceStore = provenanceStore
        resource.Resource.__init__(self)
        
 
    def getChild(self, path, request):
        return AccessSolver(self.provenanceStore, path)

class EntitiesHandler(resource.Resource):

    def __init__(self, provenanceStore):
        self.provenanceStore = provenanceStore
        resource.Resource.__init__(self)
        
 
    def getChild(self, path, request):
        return ShowEntities(self.provenanceStore, path)
    
    #suport for rest query call on workflow resources   
    def render_GET(self, request):
        request.setHeader('Content-type', 'application/json')
        return json.dumps(self.provenanceStore.getEntities(**request.args))
    


class WorkflowHandler(resource.Resource):

    def __init__(self, provenanceStore):
        self.provenanceStore = provenanceStore
        resource.Resource.__init__(self)
        self.putChild('edit', editRun(self.provenanceStore))
        self.putChild('delete', deleteRun(self.provenanceStore))
        self.putChild('insert', insertData(self.provenanceStore))
        self.putChild('user', getUserRuns(self.provenanceStore))
        self.putChild('export', exportRunProvenance(self.provenanceStore))
        
        self.putChild('summaries', getSummaries(self.provenanceStore))
        
    #suport for rest query call on workflow resources   
    def render_GET(self, request):
        request.setHeader('Content-type', 'application/json')
        return json.dumps(self.provenanceStore.getWorkflows(**request.args))
    
    
    def render_POST(self, request):
        request.setHeader('Content-type', 'application/json')
        return json.dumps(self.provenanceStore.getWorkflows(**request.args))
    
        
    def getChild(self, path, request):
         
        return getRunInfo(self.provenanceStore, path)
    
    

 
 
    
class ActivitiesHandler(resource.Resource):

    def __init__(self, provenanceStore):
        self.provenanceStore = provenanceStore
        resource.Resource.__init__(self)
        
    
    def render_GET(self, request):
        request.setHeader('Content-type', 'application/json')
        
        id = request.args['run_id'][0]
        limit = request.args['limit'][0]
        start = request.args['start'][0]
        if logging == True : log.msg(str(datetime.datetime.now().time())+":GET ShowRun - "+id);
        
        return json.dumps(self.provenanceStore.getActivities(id,int(start),int(limit)))

         
 
    def getChild(self, path, request):
        
        return ShowRun(self.provenanceStore, path)

class insertData(resource.Resource):

    def __init__(self, provenanceStore):
        self.provenanceStore = provenanceStore
        resource.Resource.__init__(self)
    
    
    def render_POST(self, request):
        request.setHeader('Content-type', 'application/json')
        payload = request.args["prov"].pop(0) if "prov" in request.args else request.content.read()
        payload = json.loads(str(payload))
        res = self.provenanceStore.insertData(payload)

        if logging == True : log.msg(str(datetime.datetime.now().time())+":POST insertData  - ")
        return json.dumps(res)
    
        
    def getChild(self, path, request):
        
        return EmptyChild(path)
    
    
    
     
         
 
     


    
class TraceHandler(resource.Resource):

    def __init__(self, provenanceStore):
        self.provenanceStore = provenanceStore
        resource.Resource.__init__(self)
 
    def getChild(self, path, request):
        return ShowTrace(self.provenanceStore, path)


 
class DerivedDataHandler(resource.Resource):

    def __init__(self, provenanceStore):
        self.provenanceStore = provenanceStore
        resource.Resource.__init__(self)
 
    def getChild(self, path, request):
        return DerivedData(self.provenanceStore, path)

class EmptyChild(resource.Resource):
    def __init__(self, path):
        self.path = path
        resource.Resource.__init__(self)
 
    def render_GET(self, request):
        return ""
 
    def render_POST(self, request):
        return ""
 
    def getChild(self, path, request):
        
        return EmptyChild(path)
 

    
class AccessSolver(resource.Resource):

    def __init__(self, provenanceStore,path):
        self.provenanceStore = provenanceStore
        resource.Resource.__init__(self)
        self.path = path
 
    def getChild(self, path, request):
        return ShowTrace(self.provenanceStore, path)
    
    def render_GET(self, request):
        request.setHeader('Content-type', 'application/json')
        id = self.path
        if logging == True : log.msg(str(datetime.datetime.now().time())+":POST AccessSolver - "+self.path);
        return json.dumps(self.provenanceStore.getSolverConf(self.path, request))
    
    def getChild(self, path, request):
        return EmptyChild(path)
 
class ShowRun(resource.Resource):
    def __init__(self, provenanceStore, path):
        self.provenanceStore = provenanceStore
        self.path = path
        
        resource.Resource.__init__(self)
 
    def render_GET(self, request):
        request.setHeader('Content-type', 'application/json')
        id = self.path
        limit = request.args['limit'][0]
        start = request.args['start'][0]
        if logging == True : log.msg(str(datetime.datetime.now().time())+":GET ShowRun - "+self.path);
        
        return json.dumps(self.provenanceStore.getActivities(id,int(start),int(limit)))

    def render_POST(self, request):
        return ""
    
    def getChild(self, path, request):
        return EmptyChild(path)
    
    
class ShowEntities(resource.Resource):
    def __init__(self, provenanceStore, path):
        self.provenanceStore = provenanceStore
        self.path = path
        resource.Resource.__init__(self)
    #    print path
 
    def render_GET(self, request):
        request.setHeader('Content-type', 'application/json')
        keylist = None
        vluelist= None
        mxvaluelist= None
        mnvaluelist= None
        
        
        
        try:
            memory_file = StringIO.StringIO(request.args['keys'][0]);
            keylist = csv.reader(memory_file).next()
            
            
            #if (self.path=="values-range"):
            memory_file = StringIO.StringIO(request.args['maxvalues'][0]) if 'maxvalues' in request.args else None
            mxvaluelist = csv.reader(memory_file).next()
            memory_file2 = StringIO.StringIO(request.args['minvalues'][0]) if 'minvalues' in request.args else None
            mnvaluelist = csv.reader(memory_file2).next()
            memory_file2 = StringIO.StringIO(request.args['values'][0]) if 'values' in request.args else None
            vluelist = csv.reader(memory_file2).next()
        
        except Exception, err:
            None
        
        
    
        # BEGIN kept for backwards compatibility
        if logging == True : log.msg(str(datetime.datetime.now().time())+":GET ShowEntities - "+self.path);
        ' test http://localhost:8082/entities/hasAnchestor?dataId=lxa88-9865-09df5b44-8f1c-11e3-9f3a-bcaec52d20a2&keys=magnitude&values=3.49&_dc=&page=1&start=0&limit=300'        
        
        if (self.path=="hasAncestorWith"):
            return json.dumps(self.provenanceStore.hasAncestorWith(dataid,keylist,valuelist))
        # END kept for backwards compatibility
        
        
        return json.dumps(self.provenanceStore.getEntitiesBy(self.path,keylist,mxvaluelist,mnvaluelist,vluelist,**request.args))
    
    
    def render_POST(self, request):
        
        try:
            memory_file = StringIO.StringIO(request.args['ids'][0]);
            idlist = csv.reader(memory_file).next()
             
            memory_file = StringIO.StringIO(request.args['keys'][0]);
            keylist = csv.reader(memory_file).next()
             
            if (self.path=="values-range" or self.path=='filterOnAncestorsValuesRange'):
                memory_file = StringIO.StringIO(request.args['maxvalues'][0]);
                mxvaluelist = csv.reader(memory_file).next()
                memory_file2 = StringIO.StringIO(request.args['minvalues'][0]);
                mnvaluelist = csv.reader(memory_file2).next()
            else: 
                memory_file2 = StringIO.StringIO(request.args['values'][0]);
                vluelist = csv.reader(memory_file2).next()
        
        except Exception, err:
         if logging == True :   traceback.print_exc()
        
        if logging == True : log.msg(str(datetime.datetime.now().time())+":POST ShowEntities - "+self.path);
       
        if (self.path=="filterOnAncestorsMeta"):
            
            return json.dumps(self.provenanceStore.filterOnAncestorsMeta(idlist,keylist,valuelist))
            
            
        if (self.path=="filterOnAncestorsValuesRange"):
            
            return json.dumps(self.provenanceStore.filterOnAncestorsValuesRange(idlist,keylist,mnvaluelist,mxvaluelist))
            
            
        if (self.path=="filterOnMeta"):
            
            return json.dumps(self.provenanceStore.filterOnMeta(idlist,keylist,vluelist))

                
        
    
    
    
    def getChild(self, path, request):
        return EmptyChild(path)    

class getUserRuns(resource.Resource):
    def __init__(self, provenanceStore,path=None):
        self.provenanceStore = provenanceStore
        self.path=path
        resource.Resource.__init__(self)
 
    def render_GET(self, request):
        
        request.setHeader('Content-type', 'application/json')
        keylist = None
        vluelist= None
        mxvaluelist= None
        mnvaluelist= None
       
        limit = request.args['limit'][0]
        start = request.args['start'][0]
         
        try:
            memory_file = StringIO.StringIO(request.args['keys'][0]);
            keylist = csv.reader(memory_file).next()
            
            memory_file = StringIO.StringIO(request.args['maxvalues'][0]);
            mxvaluelist = csv.reader(memory_file).next()
            memory_file = StringIO.StringIO(request.args['minvalues'][0]);
            mnvaluelist = csv.reader(memory_file).next()
        
        except Exception, err:
            None
            
         
        if (keylist==None and 'activities' not in request.args):
            if logging == True : log.msg(str(datetime.datetime.now().time())+":GET getUserRuns - "+self.path);
            return json.dumps(self.provenanceStore.getUserRuns(self.path,**request.args))
            
        else:
            if logging == True : log.msg(str(datetime.datetime.now().time())+":GET getUserRunsValuesRange - "+self.path);
            return json.dumps(self.provenanceStore.getUserRunsValuesRange(self.path,keylist,mxvaluelist,mnvaluelist,**request.args))
        
    def getChild(self, path, request):
        return getUserRuns(self.provenanceStore, path)
    
    
class getSummaries(resource.Resource):
    def __init__(self, provenanceStore,path=None):
        self.provenanceStore = provenanceStore
        resource.Resource.__init__(self)
        
 
    def render_GET(self, request):
        
        request.setHeader('Content-type', 'application/json')
        if logging == True : log.msg(str(datetime.datetime.now().time())+":GET getSummaries - level="+request.args['level'][0]);
        
        return json.dumps(self.provenanceStore.getActivitiesSummaries(**request.args))
        
    def getChild(self, path, request):
        return EmptyChild(path)

class exportDataProvenance(resource.Resource):
    def __init__(self, provenanceStore,path=None):
        self.provenanceStore = provenanceStore
        self.id=path
        resource.Resource.__init__(self)
        
    def render_GET(self, request):
        
        id = self.id
        
        if logging == True : log.msg(str(datetime.datetime.now().time())+":GET exportDataTraces - "+self.id);
        
       
        out,count=self.provenanceStore.exportDataProvenance(id,**request.args)
            
        if 'format' in request.args and (request.args['format'][0]=='w3c-prov-xml' or request.args['format'][0]=='w3c-prov-json'):
            request.setHeader('Content-type', 'application/octet-stream')#   
                 
        elif 'format' in request.args and request.args['format'][0]=='png':
            request.setHeader('Content-type', 'image/png')
                
        else:
            request.setHeader('Content-type', 'application/octet-stream')
            
        return str(out)
    
    def getChild(self, path, request):
        return exportDataProvenance(self.provenanceStore, path)

class exportRunProvenance(resource.Resource):
    def __init__(self, provenanceStore,path=None):
        self.provenanceStore = provenanceStore
        self.id=path
        resource.Resource.__init__(self)
        self.putChild('data', exportDataProvenance(self.provenanceStore))
 
    def render_GET(self, request):
        
        id = self.id
        
        if 'all' in request.args and request.args['all'][0].upper()=='TRUE':
            if logging == True : log.msg(str(datetime.datetime.now().time())+":GET exportAllTraces - "+self.id);
        
       
            out,count=self.provenanceStore.exportRunProvenance(id,**request.args)
            
            if 'format' in request.args and (request.args['format'][0]=='w3c-prov-xml' or request.args['format'][0]=='w3c-prov-json'):
                request.setHeader('Content-type', 'application/octet-stream')#   
                 
            elif 'format' in request.args and request.args['format'][0]=='png':
                request.setHeader('Content-type', 'image/png')
                
            else:
                request.setHeader('Content-type', 'application/octet-stream')
            
            return str(out)
        #return NOT_DONE_YET
   
    @defer.inlineCallbacks     
    def process(self,request):
       id = self.id
       request.setHeader('Content-type', 'application/octet-stream')
       request.setHeader('Connection', 'Keep-Alive')

       count=0
        
       request.args.update({'start':[0]})
       request.args.update({'limit':[0]})
       out,count=self.provenanceStore.exportAllRunProvenance(id,**request.args)
       
        
       
       request.write('[{"totalCount":'+str(count)+',')
       request.write('"w3c-prov":[')
       i=0
       while i< count:
          
           
           request.args.update({'start':[i]})
           request.args.update({'limit':[50]})
           out,count=self.provenanceStore.exportAllRunProvenance(id,**request.args)
           
           
           for trace in out[0:len(out)-1]:
               request.write(json.dumps(trace))
               request.write(",")
           
           
           if 'format' not in request.args or request.args['format'][0].find('w3c-prov')!=-1:
                 
                request.write(json.dumps(out[len(out)-1]))
           else:
                 
                request.write(str(out[len(out)-1]))
           
               
           if i+50>count:
               i=count
                
           else:
               i=i+50
               request.write(",")
               
           
           yield wait(2)
           
           
       request.write(']}]')
       request.finish()
           
        
       
            
        
             
    def getChild(self, path, request):
        return exportRunProvenance(self.provenanceStore, path)

    
class getRunInfo(resource.Resource):
    def __init__(self, provenanceStore, path):
        self.provenanceStore = provenanceStore
        self.path = path
        resource.Resource.__init__(self)
 
    def render_GET(self, request):
        
        if logging == True : log.msg(str(datetime.datetime.now().time())+":GET runInfo - "+self.path);
        request.setHeader('Content-type', 'application/json')
        return json.dumps(self.provenanceStore.getRunInfo(self.path))
        
        
             
        
    def render_DELETE(self, request):
        request.setHeader('Content-type', 'application/json')
        
        if (len(self.path)<=40):
             
            res = self.provenanceStore.deleteRun(self.path)
        else: 
            res = {'success':False, 'error':'Invalid Run Id'}
            
        if logging == True : log.msg(str(datetime.datetime.now().time())+":DELETE WorkflowRunInfo - "+self.path);
        return json.dumps(res)
    
    def render_POST(self, request):
        request.setHeader('Content-type', 'application/json')
        if logging == True : log.msg(str(datetime.datetime.now().time())+":POST WorkflowRunInfo - "+self.path);
        
        if (self.path=='edit'):
            res = self.provenanceStore.editRun(self.path,json.loads(str(request.args["doc"].pop(0))))
        
        if (self.path=='delete'):
            res = self.provenanceStore.editRun(self.path,json.loads(str(request.args["doc"].pop(0))))
        
        return json.dumps(res)
    
    def getChild(self, path, request):
        return exportRunProvenance(self.provenanceStore, path)
    
    
class editRun(resource.Resource):
    def __init__(self, provenanceStore,path=None):
        self.provenanceStore = provenanceStore
        self.path = path
        resource.Resource.__init__(self)
 
    
    
    def render_POST(self, request):
        request.setHeader('Content-type', 'application/json')
        if logging == True : log.msg(str(datetime.datetime.now().time())+":POST editRun - "+self.path);
        
        
        res = self.provenanceStore.editRun(self.path,json.loads(str(request.args["doc"].pop(0))))
        
        return json.dumps(res)
    
    def getChild(self, path, request):
        return editRun(self.provenanceStore, path)
    

class deleteRun(resource.Resource):
    def __init__(self, provenanceStore,path=None):
        self.provenanceStore = provenanceStore
        self.path = path
        resource.Resource.__init__(self)

    def render_POST(self, request):
        request.setHeader('Content-type', 'application/json')
        if logging == True : log.msg(str(datetime.datetime.now().time())+":POST deleteRun - "+self.path);
        
        
        res = self.provenanceStore.deleteRun(self.path)
        
        
        
        return json.dumps(res)
    
    def getChild(self, path, request):
        return deleteRun(self.provenanceStore, path)

 


class DerivedData(resource.Resource):
    def __init__(self, provenanceStore, path):
        self.provenanceStore = provenanceStore
        self.path = path
        resource.Resource.__init__(self)
 
    def render_GET(self, request):
        request.setHeader('Content-type', 'application/json')
        level = request.args['level'][0]
        if logging == True : log.msg(str(datetime.datetime.now().time())+":GET DerivedData - "+self.path);
        return json.dumps(self.provenanceStore.getDerivedDataTrace(self.path,int(level)))
        
    def getChild(self, path, request):
        return EmptyChild(path)

class ShowTrace(resource.Resource):
    def __init__(self, provenanceStore, path):
        self.provenanceStore = provenanceStore
        self.path = path
        resource.Resource.__init__(self)
 
    def render_GET(self, request):
        request.setHeader('Content-type', 'application/json')
        level = request.args['level'][0]
        if logging == True : log.msg(str(datetime.datetime.now().time())+":GET ShowTrace - "+self.path);
        return json.dumps(self.provenanceStore.getTrace(self.path,int(level)))
        
    def getChild(self, path, request):
        return EmptyChild(path)

 
    
 

class ShowStreamChunk(resource.Resource):
    def __init__(self, provenanceStore, path):
        self.provenanceStore = provenanceStore
        self.path = path
        resource.Resource.__init__(self)
 
    def render_GET(self, request):
        request.setHeader('Content-type', 'application/json')
        runid = request.args['runid'][0]
        id = request.args['id'][0]
        
        if logging == True : log.msg(str(datetime.datetime.now().time())+":GET ShowStreamChunk - "+self.path);
        return json.dumps(self.provenanceStore.getStreamChunk(runid,id))
        
    def getChild(self, path, request):
        return EmptyChild(path)
    
 
 
if __name__ == "__main__":
    import sys
    from twisted.internet import reactor
    provStore = provenance.ProvenanceStore(sys.argv[1])
    logging=False;
    try:
        if (sys.argv[2]=="True"):
            logging=True
            print("Logging to webserver.out")
            log.startLogging(open("webserver.out", 'a'))
        else:
            logging=True
            print("Logging to stdout")
            log.startLogging(sys.stdout)
    except:
       logging=False
    reactor.listenTCP(8082, server.Site(RootResource(provStore)))
    log.msg("Server running....")
    reactor.run()
