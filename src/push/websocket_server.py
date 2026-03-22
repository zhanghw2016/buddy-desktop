'''
Created on 2018-5-3

@author: yunify
'''

import uuid
import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.websocket
import threading
from contextlib import contextmanager
from constants import (
    PUSH_SERVER_WEB_SOCKET_PORT,
    REQ_SUBSCRIBE,
    REQ_UNSUBSCRIBE,
    REQ_PING,
    TOPIC_TYPE_JOB,
    TOPIC_JOB_SUB_TYPE_LIST,
    TOPIC_TYPE_MONITOR,
    TOPIC_MONITOR_SUB_TYPE_LIST,
    TOPIC_TYPE_EVENT,
    TOPIC_EVENT_SUB_TYPE_LIST
    )
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
from common import return_error, return_success
from send_request import check_session, send_push_server_request
from topic_manager import Subscriber
import context

class WebSocketApplication(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/websocket", WebSocketHandler),
            (r"/debug", DebugHandler),
        ]
        settings = dict(
            cookie_secret="da310dc9a3ed62ded4dea261779e0584",
            xsrf_cookies=True,
        )
        super(WebSocketApplication, self).__init__(handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        rep = return_error({}, Error(ErrorCodes.PUSH_SERVER_URI_ERROR, 
                                       ErrorMsg.ERR_MSG_PUSH_SERVER_URI_ERROR))
        self.write(rep)

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    subscriber = None

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}
    def check_origin(self, origin):
        return True

    def open(self):
        ''' new subscriber '''
        try:
            session_id = self.get_query_argument("session_id")
            user_id = self.get_query_argument("user_id")
            zone_id = self.get_query_argument("zone_id")
            
            if not (user_id and session_id and zone_id):
                logger.error(" request parameters error, [%s]", (user_id, session_id, zone_id))
                rep = return_error({}, Error(ErrorCodes.PUSH_SERVER_REQUEST_PARAMS_ERROR, 
                                           ErrorMsg.ERR_MSG_PUSH_SERVER_REQUEST_PARAMS_ERROR,
                                           ["user_id","session_id","zone_id"]))
                self.send_response(rep)
                return

            #check session
            if not check_session(user_id, session_id, zone_id):
                logger.error("check user[%s] session [%s] failed!", (user_id, session_id))
                rep = return_error({}, Error(ErrorCodes.PUSH_SERVER_REQUEST_SESSION_ERROR, 
                                           ErrorMsg.ERR_MSG_PLZ_LOGIN_AGAIN))
                self.send_response(rep)
                return

            #create subscriber
            uuid4 = str(uuid.uuid4())
            self.subscriber = Subscriber(user_id, session_id, zone_id, uuid4, self)
            ctx = context.instance()
            ctx.subscriber_mgr.add_subscriber(uuid4, self.subscriber)

            #return success
            rep = return_success({"action": "ConnectWebsocket"}, {"user_id": user_id})
            self.send_response(rep)
        except Exception,e:
            logger.error("open with exception: %s" % e)
            rep = return_error({}, Error(ErrorCodes.PUSH_SERVER_INTERNAL_ERROR, 
                                           ErrorMsg.ERR_MSG_PUSH_SERVER_INTERNAL_ERROR, e))
            self.send_response(rep)

    def on_close(self):
        ''' remove subscriber '''
        try:
            # close websocket connection
            topic_dict = {TOPIC_TYPE_JOB: TOPIC_JOB_SUB_TYPE_LIST,
                          TOPIC_TYPE_MONITOR: TOPIC_MONITOR_SUB_TYPE_LIST,
                          TOPIC_TYPE_EVENT: TOPIC_EVENT_SUB_TYPE_LIST}
            ctx = context.instance()
            ctx.topic_mgr.unsubscribe(self.subscriber.UUID4, topic_dict)
        except Exception,e:
            logger.error("open with exception: %s" % e)

    def send_response(self, rep):
        try:
            logger.info("response send: [%s]" % rep)
            self.write_message(rep)
        except Exception, e:
            logger.error("response with exception: %s" % e);
            self.on_close()

    def on_message(self, message):
        try:
            logger.info("request received: [%s]" % message)
            params = tornado.escape.json_decode(message)
            topic_dict = params.get("topic_dict")
            session_id = params.get("session_id")
            user_id = params.get("user_id")
            zone_id = params.get("zone_id")
            action = params.get("action")
            
            if not (user_id and session_id and zone_id and action):
                logger.error(" request parameters error, [%s]", [user_id, session_id, zone_id, action])
                rep = return_error({}, Error(ErrorCodes.PUSH_SERVER_REQUEST_PARAMS_ERROR, 
                                           ErrorMsg.ERR_MSG_PUSH_SERVER_REQUEST_PARAMS_ERROR,
                                           ["user_id","session_id","zone_id", "action"]))
                self.send_response(rep)
                return

            if action == REQ_PING:
                rep = {
                    "action": REQ_PING + "Response",
                    "ret_code": 0
                    }
                self.send_response(rep)
                return

            if not isinstance(topic_dict, dict):
                logger.error(" request parameter topic_dict is not dict, [%s]", [topic_dict])
                rep = return_error({}, Error(ErrorCodes.PUSH_SERVER_REQUEST_PARAMS_ERROR, 
                                           ErrorMsg.ERR_MSG_PUSH_SERVER_REQUEST_PARAMS_ERROR,
                                           ["topic_dict"]))
                self.send_response(rep)
                return

            if action not in [REQ_SUBSCRIBE, REQ_UNSUBSCRIBE]:
                rep = return_error({}, Error(ErrorCodes.PUSH_SERVER_REQUEST_PARAMS_ERROR, 
                                           ErrorMsg.ERR_MSG_PUSH_SERVER_REQUEST_PARAMS_ERROR,
                                           "action=" % action))
                self.send_response(rep)
                return

            #check session
            if not check_session(user_id, session_id, zone_id):
                logger.error("check user[%s] session [%s] failed!", (user_id, session_id))
                rep = return_error({}, Error(ErrorCodes.PUSH_SERVER_REQUEST_SESSION_ERROR, 
                                           ErrorMsg.ERR_MSG_PLZ_LOGIN_AGAIN))
                self.send_response(rep)
                return

            #send pull request
            req = {"action": action,
                   "subscriber": self.subscriber.UUID4,
                   "topic_dict": topic_dict
                   }
            ret = send_push_server_request(req, need_reply=False)
            if ret == None:
                rep = return_error({}, Error(ErrorCodes.PUSH_SERVER_WEBSOCKET_SUBSCRIBE_ERROR, 
                                           ErrorMsg.ERR_MSG_PUSH_SERVER_WEBSOCKET_SUBSCRIBE_ERROR))
            else:
                rep = return_success({"action": action}, {"user_id": user_id})
            self.send_response(rep)
        except Exception,e:
            logger.error("open with exception: %s" % e)
            rep = return_error({}, Error(ErrorCodes.PUSH_SERVER_INTERNAL_ERROR, 
                                           ErrorMsg.ERR_MSG_PUSH_SERVER_INTERNAL_ERROR, e))
            self.send_response(rep)

    @contextmanager
    def _lock(self):
        self.lock.acquire()
        try:
            yield
        except Exception, e:
            logger.error("lock with exception: %s" % e);
        self.lock.release()

class WebSocketServer(threading.Thread):
    ''' web socket server thread '''
    def __init__(self):
        super(WebSocketServer, self).__init__()

    def run(self):       
        app = WebSocketApplication()
        app.listen(PUSH_SERVER_WEB_SOCKET_PORT)
        tornado.ioloop.IOLoop.current().start()

# debug
class DebugHandler(tornado.web.RequestHandler):
    def get(self):
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>push_server debug</title>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>
    
    <style type="text/css"> 
        #input {color: #006400} 
        #output {color: #7B68EE;
                 background: #FFEFD5}
    </style> 

    <script src="https://code.jquery.com/jquery-3.3.1.min.js" type="text/javascript"></script>
    <script type="text/javascript">
        var ws = null;
        function startWebsocket() {
            var url = "ws://" + location.host + "/websocket?user_id=";
            url += document.getElementById("user_id").value;
            url += "&session_id=";
            url += document.getElementById("session_id").value;
            url += "&zone_id=";
            url += document.getElementById("zone_id").value;
            ws = new WebSocket(url);
            ws.onopen = function() {
            };
            ws.onmessage = function (msg) {
                var table = document.getElementById("result")
                var tr = document.createElement("tr");
                table.appendChild(tr);
                var td = document.createElement("td");
                tr.appendChild(td);
                var span = document.createElement("span");
                span.innerHTML = JSON.stringify(msg.data)
                td.appendChild(span);
            };
            ws.onclose = function() {
            };
            document.getElementById("start").disabled = true;
        }

        function submitRequest() {
            var req = new Object()
            req.user_id = document.getElementById("user_id").value;
            req.session_id = document.getElementById("session_id").value;
            req.zone_id = document.getElementById("zone_id").value;
            try {
                JSON.parse(document.getElementById("topic_dict").value);
                req.topic_dict = JSON.parse(document.getElementById("topic_dict").value);
            } catch (e) {
                 alert(e.name + ": " + e.message);
            }
            var radios = document.getElementsByName("radio");
            for(var i=0;i<3;i++){
                if(radios[i].checked){
                    req.action = radios[i].value;
                }
            }
            if(ws == null){
                alert("ws is null!");
            }
            ws.send(JSON.stringify(req));
        }

        function clearResult() {
            var table = document.getElementById("result");
            table.innerHTML = "";
        }
        
        $(document).ready(function() {
            document.getElementsByName("radio")[0].checked = true;
            document.getElementById("start").onclick = startWebsocket;
            document.getElementById("submit").onclick = submitRequest;
            document.getElementById("clear").onclick = clearResult;
        });
    </script>

</head>
<body>
    <form action="" method="">
        <table>
            <tr>
                  <td> &nbsp&nbsp&nbsp&nbsp&nbsp zone_id: <input id="zone_id" type="text" name="zone_id" value="desktop1" style="width:500px"> </td> 
            </tr>
            <tr>
                  <td> &nbsp&nbsp&nbsp&nbsp&nbsp user_id: <input id="user_id" type="text" name="user_id" value="global_admin" style="width:500px"> </td> 
            </tr>
            <tr>
                  <td> session_id: <input id="session_id" type="text" name="session_id" value="QHxLtjXluRAnnRSY3KqGu0ASl8sWhzCg" style="width:500px"> </td> 
            </tr>
            <tr>
                  <td style="padding-left:500px"> <input id="start" type="button" value="Start" >  </td> 
            </tr>
        <table>             
    </form> 
    <br><br>
    <div id="input">
        <form action="" method="">
          <table>
            <tr>
                  <td> topic_dict: <input id="topic_dict" type="text" name="topic_dict" style="width:500px"> </td> 
            </tr>
            <tr>
                <td>
                    <label style="padding-left:80px"></label>
                    <input id="subscribe" type="radio" name="radio" value="WebsocketSubscribe"> subscribe </input>
                    <input id="unsubscribe" type="radio" name="radio" value="WebsocketUnsubscribe"> unsubscribe </input>
                    <input id="ping" type="radio" name="radio" value="WebsocketPing"> ping </input>
                <td>
            </tr>
            <tr>
                  <td style="padding-left:500px"> <input id="submit" type="button" value="Submit"> </td>
            </tr>
          </table>
        </form>
    </div>
    <hr>
    <div id="output">
        <form action="" method="">
            <input id="clear" type="button" value="Clear">
        </form>
        <span>Result: </span>
         <table id="result">
         </table>
    </div>

</body>
</html>"""
        self.write(html)
